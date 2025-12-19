import sqlite3
from pathlib import Path
import random
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parents[1] / "users.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn, name: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def init_db():
    """Initialize database with users, sensors and measurements tables.
    If sensors or measurements are empty, insert sample data.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()

    # users table (existing)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        salt TEXT NOT NULL
    );
    """)

    # sensors table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS sensors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location TEXT
    );
    """)

    # measurements table: time series for sensors with common metrics
    conn.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id INTEGER NOT NULL,
        ts TEXT NOT NULL,
        temperature REAL,
        humidity REAL,
        voltage REAL,
        co REAL,
        light REAL,
        no2 REAL,
        FOREIGN KEY(sensor_id) REFERENCES sensors(id)
    );
    """)

    conn.commit()

    # Seed sensors if empty
    cur = conn.execute("SELECT COUNT(1) as c FROM sensors")
    row = cur.fetchone()
    sensors_count = row[0] if row is not None else 0
    if sensors_count == 0:
        sample_sensors = [
            ("Outdoor-1", "Courtyard"),
            ("Indoor-1", "Office"),
            ("Outdoor-2", "Roof"),
            ("Greenhouse-1", "Greenhouse"),
        ]
        conn.executemany("INSERT INTO sensors (name, location) VALUES (?, ?)", sample_sensors)
        conn.commit()

    # Seed measurements if empty
    cur = conn.execute("SELECT COUNT(1) as c FROM measurements")
    row = cur.fetchone()
    measurements_count = row[0] if row is not None else 0
    if measurements_count == 0:
        # fetch sensor ids
        sensor_rows = conn.execute("SELECT id FROM sensors").fetchall()
        sensor_ids = [r[0] for r in sensor_rows]
        now = datetime.utcnow()

        metrics_keys = ["temperature", "humidity", "voltage", "co", "light", "no2"]

        inserts = []
        # generate 24 samples per sensor (hourly)
        for sid in sensor_ids:
            for i in range(24):
                ts = (now - timedelta(hours=(23 - i))).isoformat()
                # pragmatic ranges for each metric
                temperature = round(random.uniform(10.0, 30.0), 2)
                humidity = round(random.uniform(20.0, 80.0), 2)
                voltage = round(random.uniform(3.0, 4.2), 3)
                co = round(random.uniform(0.0, 10.0), 3)
                light = round(random.uniform(0.0, 1000.0), 1)
                no2 = round(random.uniform(0.0, 0.2), 4)
                inserts.append((sid, ts, temperature, humidity, voltage, co, light, no2))

        conn.executemany(
            "INSERT INTO measurements (sensor_id, ts, temperature, humidity, voltage, co, light, no2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            inserts,
        )
        conn.commit()

    conn.close()
