from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from dotenv import load_dotenv

from models import Workforce
from extensions import db, migrate
from utils import hash_password, validate_user_payload, commit_to_database, database_error_response, asset_to_dictionary

import os

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:5432/workforce"

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

@app.route("/api/v1/workforce/add-user", methods=["POST"])
def create_user():
    data = request.get_json()

    # Validate data & hash password
    if data["password"]:
        data["password_hash"] = hash_password(data["password"])
    verified_data, error = validate_user_payload(data)

    if error:
        return jsonify({
            "code": "invalid_object",
            "message": str(error)
        }), 400

    # Unpacks payload to a Workforce object
    user = Workforce(**verified_data)
    try:
        commit_to_database(user)
    except SQLAlchemyError as e:
        return database_error_response(e)

    return jsonify(asset_to_dictionary(user)), 201

@app.route("/api/v1/workforce/auth/token", methods=["POST"])
def grant_token():
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "code": "invalid_request",
            "message": "Request body must be a JSON object."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if (not isinstance(email, str) or not email) or (not isinstance(password, str) or not password):
        return jsonify({
            "code": "invalid_request",
            "message": "Both 'email' and 'password' fields are mandatory!"
        }), 400

    query = db.select(Workforce).where(Workforce.email == email)
    user = db.session.execute(query).scalar_one_or_none

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
