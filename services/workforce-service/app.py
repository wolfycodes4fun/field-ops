from flask import Flask, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from dotenv import load_dotenv

import os

from models import Workforce
from extensions import db, migrate
from utils import (
    hash_and_check_password_constraints, 
    validate_user_payload, 
    commit_to_database, 
    database_error_response, 
    user_to_dictionary,
    grant_token,
    verify_jwt_token,
    require_roles
)


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:5432/workforce"
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ISSUER"] = os.getenv("WORKFORCE_JWT_ISSUER")
    app.config["JWT_AUDIENCE"] = os.getenv("WORKFORCE_JWT_AUDIENCE")

    db.init_app(app)
    migrate.init_app(app, db)
    return app

app = create_app()

@app.route("/api/v1/workforce/health", methods=["GET"])
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        return jsonify({
            "service status": "healthy",
            "service": "workforce-service",
            "language": "python",
            "database status": "disconnected"
        }), 500

    return jsonify({
        "service status": "healthy",
        "service": "workforce-service",
        "language": "python",
        "database status": db_status
    }), 200

@app.route("/api/v1/workforce/users", methods=["POST"])
@require_roles("administrator")
def create_user():
    data = request.get_json()

    # Validate data & hash password
    password = data.pop("password", None)
    data["password_hash"], password_err = hash_and_check_password_constraints(password)
    if password_err:
        return jsonify({
            "code": "invalid_request",
            "message": password_err
        }), 400

    verified_data, error = validate_user_payload(data)
    if error:
        return jsonify({
            "code": "invalid_object",
            "message": str(error)
        }), 400
    print(verified_data)

    # Unpacks payload to a Workforce object
    user = Workforce(**verified_data)
    try:
        commit_to_database(user)
    except SQLAlchemyError as e:
        return database_error_response(e)

    return jsonify(user_to_dictionary(user)), 201

@app.route("/api/v1/workforce/login", methods=["POST"])
def user_login():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "code": "invalid_request",
            "message": "Request body must be a JSON object."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if ((not isinstance(email, str) or not email) or (not isinstance(password, str) or not password)):
        return jsonify({
            "code": "invalid_request",
            "message": "Both 'email' and 'password' fields are mandatory!"
        }), 400

    try:
        query = db.select(Workforce).where(Workforce.email == email)
        user: Workforce = db.session.execute(query).scalar_one_or_none()
    except SQLAlchemyError as e:
        return database_error_response(e)

    if not user or not user.is_active or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({
            "code": "invalid_request",
            "message": "Email or password is incorrect"
        }), 401

    auth_token = grant_token(user, current_app)
    return jsonify({
        "access_token": auth_token,
        "token_type": "Bearer",
        "expires_in": 900
    }), 200

@app.route("/api/v1/workforce/me", methods=["GET"])
def whoami():
    auth_header = request.headers.get("Authorization", "")
    scheme, _, jwt_token = auth_header.partition(" ")

    if scheme.lower() != "bearer" or not jwt_token:
        return jsonify({
            "code": "unauthorized_request",
            "message": "A Bearer access token is required to carry this function!"
        }), 401

    jwt_token = verify_jwt_token(jwt_token)
    if not jwt_token:
        return jsonify({
            "code": "unauthorized_request",
            "message": "The Bearer token is expired or invalid!"
        }), 401
    user_id = jwt_token.get("sub")

    try:
        user = db.session.get(Workforce, user_id)
        if user is not None and user.is_active:
            return jsonify({
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.role
            }), 200
        else: 
            return jsonify({
                "code": "unauthorized_request",
                "message": "User is unavailable"
            }), 401
    except SQLAlchemyError as e:
        return database_error_response(e)

@app.route("/api/v1/workforce/users", methods=["GET"])
@require_roles("administrator", "manager")
def search_and_filter_users():
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({
            "code": "invalid_request",
            "message": "Please pass limit & offset as integers"
        }), 400

    try:
        stmt = db.select(Workforce)

        role = (request.args.get("role") or "")
        if role:
            if not isinstance(role, str):
                return jsonify({
                    "code": "invalid_request",
                    "message": "A String value must be passed to filter users by roles."
                }), 400
            if role.lower() not in {"admin", "manager", "technician"}:
                return jsonify({
                    "code": "invalid_request",
                    "message": "role must be filtered with 'Admin', 'Manager' or 'Technician'"
                }), 400
            stmt = stmt.where(Workforce.role == role.strip())

        match_email_or_name = request.args.get("name_or_email_pattern", "")
        if not isinstance(match_email_or_name, str):
            return jsonify({
                "code": "invalid_request",
                "message": "A String value must be passed to filter users by name or email."
            }), 400
        if match_email_or_name:
            pattern = f"%{match_email_or_name.strip()}%"
            stmt = stmt.where(or_(
                Workforce.display_name.ilike(pattern),
                Workforce.email.ilike(pattern)
            ))

        active = request.args.get("is_active")
        if active:
            if not isinstance(active, str):
                return jsonify({
                    "code": "invalid_request",
                    "message": "A String value must be passed to filter users by activity status."
                }), 400
            if active.lower() not in {"true", "false"}:
                return jsonify({
                    "code": "invalid_request",
                    "message": "activity status must be filtered with either 'true' or 'false'"
                }), 400
            stmt = stmt.where(Workforce.is_active == (active.lower() == "true"))

        stmt = stmt.order_by(Workforce.id.asc())
        users = db.session.execute(stmt).scalars()

        return jsonify({
            "users": [
                {"id": user.id, "name": user.display_name, "email": user.email, "role": user.role, "created_at": user.created_at}
                for user in users
            ]
        }), 200

    except SQLAlchemyError as e:
        return database_error_response(e)

@app.route("/api/v1/workforce/users/<uuid:user_id>", methods=["GET"])
@require_roles("administrator", "manager")
def view_user(user_id):
    try:
        user: Workforce = db.session.get(Workforce, user_id)
    except SQLAlchemyError as e:
        return database_error_response(e)

    if user is None:
        return jsonify({
            "code": "user_not_found",
            "message": "User is not available"
        }), 404

    return jsonify({
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at
    })

@app.route("/api/v1/workforce/users/<uuid:user_id>", methods=["PATCH"])
@require_roles("administrator")
def update_user_details(user_id):
    data = request.get_json()
    verified_data, error = validate_user_payload(data, True)

    if error:
        return jsonify({
            "code": "invalid_request",
            "message": str(error)
        }), 400

    try:
        user = db.session.get(Workforce, user_id)
        if user is None:
            return jsonify({
                "code": "user_unavailable",
                "message": "The requested user is not available"
            }), 404
        
        for property, value in verified_data.items():
            setattr(user, property, value)

        commit_to_database(user)
    except SQLAlchemyError as e:
        return database_error_response(e)

    return jsonify(user_to_dictionary(user)), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
