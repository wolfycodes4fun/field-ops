from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/v1/work-order/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "work-order-service",
        "language": "python"
    }), 200

if __name__ == "__main__":
    app.run("0.0.0.0", port=5020, debug=True)
