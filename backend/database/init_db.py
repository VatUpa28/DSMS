import os
import sqlite3

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "app.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
        cursor.executescript(schema)

    conn.commit()
    conn.close()

    print("Database created successfully.")

if __name__ == "__main__":
    init_db()