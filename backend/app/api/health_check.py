from flask import Blueprint, jsonify

bp = Blueprint("health_check", __name__)


@bp.get("/health_check")
def health_check():
    return jsonify({"status": "ok", "message": "alive"}), 200
