from flask import Blueprint, request, jsonify
from ..db import get_connection

bp = Blueprint("measurements", __name__)


def table_exists(conn, name: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def get_table_columns(conn, table: str):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


@bp.get("/locations")
def locations():
    conn = get_connection()
    try:
        if table_exists(conn, "sensors"):
            cols = get_table_columns(conn, "sensors")
            if "location" in cols:
                rows = conn.execute("SELECT DISTINCT location FROM sensors ORDER BY location").fetchall()
                locs = [r[0] for r in rows]
                return jsonify(locs), 200
        return jsonify([]), 200
    finally:
        conn.close()


@bp.get("/sensors")
def sensors():
    location = request.args.get("location")
    conn = get_connection()
    try:
        if not table_exists(conn, "sensors"):
            return jsonify([]), 200
        cols = get_table_columns(conn, "sensors")
        select_cols = ",".join(cols)
        if location:
            rows = conn.execute(f"SELECT {select_cols} FROM sensors WHERE location=?", (location,)).fetchall()
        else:
            rows = conn.execute(f"SELECT {select_cols} FROM sensors").fetchall()
        result = [dict(row) for row in rows]
        return jsonify(result), 200
    finally:
        conn.close()


def find_measurement_table(conn):
    candidates = ["measurements", "measurement", "readings", "data"]
    for t in candidates:
        if table_exists(conn, t):
            return t
    # fallback: find any table containing column 'ts'
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    for r in rows:
        tname = r[0]
        try:
            cols = get_table_columns(conn, tname)
        except Exception:
            cols = []
        if "ts" in cols:
            return tname
    return None


@bp.get("/measurements/<int:sensor_id>/timestamps")
def sensor_timestamps(sensor_id: int):
    conn = get_connection()
    try:
        table = find_measurement_table(conn)
        if not table:
            return jsonify([]), 200
        rows = conn.execute(f"SELECT ts FROM {table} WHERE sensor_id=? ORDER BY ts", (sensor_id,)).fetchall()
        ts = [r[0] for r in rows]
        return jsonify(ts), 200
    finally:
        conn.close()


@bp.get("/measurements/<int:sensor_id>")
def measurements(sensor_id: int):
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")
    conn = get_connection()
    try:
        table = find_measurement_table(conn)
        if not table:
            return jsonify([]), 200
        cols = get_table_columns(conn, table)
        select_cols = ",".join(cols)
        sql = f"SELECT {select_cols} FROM {table} WHERE sensor_id=?"
        params = [sensor_id]
        if from_ts and to_ts:
            sql += " AND ts BETWEEN ? AND ?"
            params.extend([from_ts, to_ts])
        sql += " ORDER BY ts"
        rows = conn.execute(sql, params).fetchall()
        result = [dict(row) for row in rows]
        return jsonify(result), 200
    finally:
        conn.close()
