import json
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

from database import init_db
from routes.upload_routes import upload_bp
from routes.analysis_routes import analysis_bp
from routes.demo_routes import demo_bp
from routes.report_routes import report_bp

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
DEMO_DIR = BASE_DIR / "demo_data" / "demo_visas"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Enable CORS for all API routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Ensure directories exist
UPLOADS_DIR.mkdir(exist_ok=True)
DEMO_DIR.mkdir(parents=True, exist_ok=True)

# Initialize database
init_db()

# Register Blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(demo_bp)
app.register_blueprint(report_bp)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "system": "DAKSH Visa Document Screening Hub",
        "mode": "demo_prototype",
        "version": "1.0.0"
    })


if __name__ == "__main__":
    print("Starting DAKSH Visa Screening Backend on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
