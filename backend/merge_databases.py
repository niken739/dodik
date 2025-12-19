import sqlite3
from pathlib import Path
import sys

"""
Merge tables from a measurement SQLite database into the project's `users.db`.

Usage:
  python merge_databases.py /path/to/measurement.sqlite

If no path is provided, the script will look for `measurement.sqlite` next to this script.
"""

THIS_DIR = Path(__file__).resolve().parent
USERS_DB = THIS_DIR / "users.db"
MEAS_DB = Path(sys.argv[1]) if len(sys.argv) > 1 else THIS_DIR / "measurement.sqlite"


def main():
    if not USERS_DB.exists():
        print(f"Users DB not found at {USERS_DB}")
        return
    if not MEAS_DB.exists():
        print(f"Measurement DB not found at {MEAS_DB}")
        return

    conn = sqlite3.connect(str(USERS_DB))
    cur = conn.cursor()
    cur.execute("ATTACH DATABASE ? AS meas", (str(MEAS_DB),))
    tables = cur.execute(
        """
        SELECT name, sql
        FROM meas.sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%';
        """
    ).fetchall()

    for name, create_sql in tables:
        print(f"Processing table: {name!r}")
        exists = cur.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = ?;
            """,
            (name,),
        ).fetchone()
        if not exists:
            if create_sql:
                print(f" Creating table {name!r} in users.db")
                cur.execute(create_sql)
            else:
                print(f" Table {name!r} has no CREATE SQL, skipping")
        try:
            print(f" Copying data from meas.{name} into {name}")
            cur.execute(f"INSERT INTO {name} SELECT * FROM meas.{name};")
        except sqlite3.Error as e:
            print(f" ERROR copying table {name}: {e}")
    conn.commit()
    cur.execute("DETACH DATABASE meas")
    conn.close()


if __name__ == "__main__":
    main()
