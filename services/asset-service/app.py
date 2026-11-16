from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from dotenv import load_dotenv

from models import Asset
from extensions import db, migrate
from utils import validate_asset_payload

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
        db_status = "unreachable"
    return jsonify({
        "service status": "healthy",
        "service": "asset-service",
        "language": "python",
        "database status": db_status
    }), 200

@app.route("/api/v1/assets/add-asset", methods=["POST"])
def add_assets():
    data = request.get_json()
    values, error = validate_asset_payload(data)

    return values

if __name__ == "__main__":
    app.run("0.0.0.0", port=5010, debug=True)
