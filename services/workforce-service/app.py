from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/v1/workforce/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "workforce-service",
        "language": "python"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
