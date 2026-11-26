from flask import jsonify, request
from flask_bcrypt import bcrypt
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from datetime import datetime, timezone, timedelta

import jwt
import os

from extensions import db
from models import User

EDITABLE_FIELDS = {"email", "display_name", "role", "is_active"}
REQUIRED_FIELDS = {"email", "display_name", "role"}

def hash_and_check_password_constraints(password):

    password_min_length = 10
    password_max_length = 64

    if (not isinstance(password, str) or
        len(password) < password_min_length or
        len(password) > password_max_length or
        not any(ch.isupper() for ch in password) or
        not any(ch.islower() for ch in password) or
        not any(ch.isdigit() for ch in password)
        ):
        return None, f"Please pass a password of length between {password_min_length} and {password_max_length} with a mix of lowercase, uppercase and number characters"

    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8'), None

def validate_user_payload(data: dict, mode):
    REQUIRED_USER_FIELDS = {"email", "display_name", "role", "password_hash", "profile"}
    EDITABLE_USER_FIELDS = {"email", "display_name", "role", "is_active"}
    REQUIRED_PROFILE_FIELDS = {"full_name", "job_title", "employee_number"}
    PROFILE_FIELDS = {"full_name", "job_title", "team", "phone", "employee_number"}

    if not isinstance(data, dict):
        return None, "The payload must be a JSON object :("

    match mode:
        case "create":
            missing_user_fields = REQUIRED_USER_FIELDS - set(data.keys())
            if missing_user_fields:
                return None, f"To create a user, please pass the fields ({", ".join(missing_user_fields)})"
            missing_profile_fields = REQUIRED_PROFILE_FIELDS - set(data.get("profile").keys())
            if missing_profile_fields:
                return None, f"To create a user, please pass the fields ({", ".join(missing_profile_fields)}) under 'profile' attribute"

        case "update_user":
            has_overlap = any(property in EDITABLE_USER_FIELDS for property in data)
            if not has_overlap:
                return None, f"To update a user, please pass at least one attribute to update from ({", ".join(EDITABLE_USER_FIELDS)})"

        case "update_profile":
            if not isinstance(data.get("profile"), dict) or not data.get("profile"):
                return None, f"To update a user profile, please pass the attributes in JSON format :("
            has_overlap = any(property in PROFILE_FIELDS for property in data.get("profile"))
            if not has_overlap:
                return None, f"To update a user profile, please pass at least one attribute from ({", ".join(PROFILE_FIELDS)})"

    verified_data = {}
    for property, value in data.items():
        if property == "is_active" and not isinstance(value, bool):
            return None, f"Attribute {property} not correct data type(Bool) :("
        elif property == "profile":
            for profile_property, profile_value in value.items():
                if not isinstance(profile_value, str) or profile_property not in PROFILE_FIELDS:
                    return None, f"Attribute under 'profile', {profile_property} is rejected/not correct data type(String) :("
        elif (
            property not in (REQUIRED_USER_FIELDS | EDITABLE_USER_FIELDS) or
            not isinstance(value, str)
        ):
            return None, f"Attribute {property} is rejected/not correct data type(String) :("
        verified_data[property] = value

    return verified_data, None

def commit_to_database(user_obj):
    db.session.add(user_obj)
    db.session.commit()
    db.session.refresh(user_obj)

def database_error_response(e: SQLAlchemyError):
    db.session.rollback()

    if isinstance(e, IntegrityError):
        return jsonify({
            "code": "user_conflict",
            "message": "New user details conflict with exisiting user records"
        }), 409

    if isinstance(e, OperationalError):
        return jsonify({
            "code": "database_unavailable",
            "message": "The database service is temporarily unavailable"
        }), 503

    return jsonify({
        "code": "database_error",
        "message": str(e)
    }), 500

def user_to_dictionary(user: User):
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
    }

def grant_token(user: User, current_app):
    token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "iat": datetime.now(timezone.utc), # Records when token was created
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15), # Records when token needs to expire
            "iss": current_app.config["JWT_ISSUER"],
            "aud": current_app.config["JWT_AUDIENCE"]
        },
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )
    return token

def verify_jwt_token(jwt_token):
    try:
        return jwt.decode(
            jwt_token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=["HS256"],
            issuer=os.getenv("WORKFORCE_JWT_ISSUER"),
            audience=os.getenv("WORKFORCE_JWT_AUDIENCE")
        )
    except jwt.InvalidTokenError:
        return None

def require_roles(*allowed_roles: str):
    def inner_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            scheme, _, jwt_token = auth_header.partition(" ")

            if scheme.lower() != "bearer" or not jwt_token:
                return jsonify({
                    "code": "unauthorized_request",
                    "message": "A Bearer access token is required to carry this function!"
                }), 401

            jwt_token = verify_jwt_token(jwt_token)
            if jwt_token is None:
                return jsonify({
                    "code": "unauthorized_request",
                    "message": "The Bearer token is expired or invalid."
                }), 401
            user_id = jwt_token.get("sub")

            try:
                user = db.session.get(User, user_id)
            except SQLAlchemyError as e:
                return database_error_response(e)

            if user is None or not user.is_active:
                return jsonify({
                    "code": "unauthorized_request",
                    "message": "User not available"
                }), 403

            if user.role not in allowed_roles:
                return jsonify({
                    "code": "forbidden",
                    "message": "You do not have permission to perform this action"
                }), 403

            return func(*args, **kwargs)
        return wrapper
    return inner_func

