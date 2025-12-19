from flask import Flask
from flask_cors import CORS
from .api.auth import bp as auth_bp
from .api.health_check import bp as health_bp
from .api.measurements import bp as measurements_bp
from .db import init_db


def create_app():
    app = Flask(__name__)
    init_db()
    # Enable CORS for API routes so front-end can call the backend during development
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    # Register health check under /api to match client expectations (e.g. /api/health_check)
    app.register_blueprint(health_bp, url_prefix="/api")
    # Measurements and sensors API (lab8)
    app.register_blueprint(measurements_bp, url_prefix="/api")
    return app
