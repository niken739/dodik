from flask import Blueprint, request, jsonify
from ..db import get_connection
from ..security import generate_salt, hash_password
from ..schemas import LoginRequest, RegistrationRequest

bp = Blueprint("auth", __name__)


@bp.post("/registration")
def registration():

    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    try:
        data = RegistrationRequest(**request.get_json())
    except Exception as e:
        return jsonify({"error": "validation", "details": str(e)}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE login = ?", (data.login,))
    if cur.fetchone():
        conn.close()
        return jsonify({"error": "user_exists"}), 400

    salt = generate_salt()
    password_hash = hash_password(data.password, salt)
    cur.execute("INSERT INTO users (login, password, salt) VALUES (?, ?, ?)", (data.login, password_hash, salt))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"}), 201


@bp.post("/login")
def login():
    try:
        data = LoginRequest(**request.get_json())
    except Exception as e:
        return jsonify({"error": "validation", "details": str(e)}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password, salt FROM users WHERE login = ?", (data.login,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "invalid_credentials"}), 401

    stored_hash = row["password"]
    salt = row["salt"]
    if hash_password(data.password, salt) == stored_hash:
        return jsonify({"status": "ok"}), 200

    return jsonify({"error": "invalid_credentials"}), 401
