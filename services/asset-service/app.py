from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db =  SQLAlchemy()

def create_app():
    app = Flask(__name__)

    return app

app = create_app()

@app.route("/api/v1/assets/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "asset-service",
        "language": "python"
    }), 200

@app.route("/api/v1/assets/add-asset", methods=["POST"])
def add_assets():
    pass



if __name__ == "__main__":
    app.run("0.0.0.0", port=5010, debug=True)
