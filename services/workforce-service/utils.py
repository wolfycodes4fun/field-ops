from flask import jsonify, request
from flask_bcrypt import bcrypt
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from datetime import datetime, timezone, timedelta

import jwt
import os

from extensions import db
from models import Workforce

ALL_FIELDS = {"email", "display_name", "password_hash", "role", "is_active"}
REQUIRED_FIELDS = {"email", "display_name", "password", "role"}

def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def validate_user_payload(data: dict, is_update: bool = False):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    if not is_update:
        missing_fields = list(REQUIRED_FIELDS - set(data.keys()))
        if missing_fields:
            return None, f"Required fields for creating users missing: {", ".join(missing_fields)}"

    if is_update and not data:
        return  None, f"Provide at least one property from {list(ALL_FIELDS)} to update user"

    verified_data = {}
    for property, value in data.items():
        if property != "is_active" and not isinstance(value, str):
            return None, f"Value for {property} must be of type string!"
        if property == "is_active" and not isinstance(value, bool):
            return None, f"Value for {property} must be of type boolean!"
        if property == "role":
            verified_data[property] = value.lower()
        if property in ALL_FIELDS and property != "password_hash" and property != "role":
            verified_data[property] = value

    return verified_data, None

def commit_to_database(workforce_obj):
    db.session.add(workforce_obj)
    db.session.commit()
    db.session.refresh(workforce_obj)

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

def user_to_dictionary(user: Workforce):
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
    }

def grant_token(user: Workforce, current_app):
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
                user = db.session.get(Workforce, user_id)
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

