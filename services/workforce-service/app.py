from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from dotenv import load_dotenv

from extensions import db, migrate

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
        db_status = "disconnected"
    return jsonify({
        "service status": "healthy",
        "service": "workforce-service",
        "language": "python",
        "database status": db_status
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
