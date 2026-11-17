from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from dotenv import load_dotenv

from models import Asset
from extensions import db, migrate
from utils import validate_asset_payload, commit_asset, database_error_response, asset_to_dictionary

import os

# Load env variables file
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:5432/assets"

    db.init_app(app)
    migrate.init_app(app, db)
    return app

app = create_app()

@app.route("/api/v1/assets/health", methods=["GET"])
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception as e:

        return jsonify({
            "service status": "healthy",
            "service": "asset-service",
            "language": "python",
            "database status": "unreachable"
        }), 500

    return jsonify({
        "service status": "healthy",
        "service": "asset-service",
        "language": "python",
        "database status": db_status
    }), 200

@app.route("/api/v1/assets/", methods=["POST"])
def add_assets():
    data = request.get_json()
    values, error = validate_asset_payload(data, False)

    if error:
        return jsonify(error={
            "code": "invalid_requests",
            "message": error
            }), 400
    asset = Asset(**values)

    try:
        commit_asset(asset)
    except SQLAlchemyError as e:
        return database_error_response(e)

    return jsonify(asset_to_dictionary(asset)), 201

@app.route("/api/v1/assets/<uuid:asset_id>", methods=["PATCH"])
def update_assets(asset_id):
    data = request.get_json()
    values, error = validate_asset_payload(data, True)

    if error:
        return jsonify({
            "code": "invalid_request",
            "message": error
        }), 400

    asset = db.session.get(Asset, asset_id)

    if not asset:
        return jsonify({
            "code": "invalid_object",
            "message": "Asset does not currently exist in the system"
        })

    for property, value in values.items():
        setattr(asset, property, value)

    try:
        commit_asset(asset)
    except SQLAlchemyError as e:
        return database_error_response(e)

    return jsonify(asset_to_dictionary(asset)), 201

if __name__ == "__main__":
    app.run("0.0.0.0", port=5010, debug=True)
