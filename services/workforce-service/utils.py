from flask import jsonify
from flask_bcrypt import bcrypt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

from extensions import db
from models import Workforce

ALL_FIELDS = {"email", "display_name", "password_hash", "role", "is_active"}
REQUIRED_FIELDS = {"email", "display_name", "password", "role"}

def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def validate_user_payload(data: dict):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    missing_fields = list(REQUIRED_FIELDS - set(data.keys()))
    if missing_fields:
        return None, f"Required fields for creating users missing: {", ".join(missing_fields)}"

    verified_data = {}
    for property, value in data.items():
        if property != "is_active" and not isinstance(value, str):
            return None, f"Value for {property} must be of type string!"
        if property == "is_active" and not isinstance(value, bool):
            return None, f"Value for {property} must be of type boolean!"
        if property in ALL_FIELDS and property != "password":
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

def asset_to_dictionary(user: Workforce):
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
    }