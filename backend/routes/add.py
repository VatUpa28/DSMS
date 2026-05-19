from flask import Blueprint, request, redirect, url_for
from database.db import get_db
from services.stone_service import create_stone

add_stone_bp = Blueprint("add_stone", __name__)

@add_stone_bp.route("/add-stone", methods=["POST"])
def add_stone():

    conn = get_db()

    try:
        cursor = conn.cursor()

        create_stone(cursor, request.form)

        conn.commit()

        return redirect(url_for("inventory.inventory"))

    finally:
        conn.close()

add_stones_bp = Blueprint("add_stones", __name__)

@add_stones_bp.route("/add-stones", methods=["POST"])
def add_stones():
    conn = get_db()

    try:
        cursor = conn.cursor()

        file = request.files["file"]
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        for row in reader:

            filtered = {
                k: v for k, v in row.items()
                if k in allowed_fields and v != ""
            }

            if not all(f in filtered for f in required_fields):
                return {"error": "Missing fields in CSV"}, 400

            filtered["size"] = get_size_from_weight(filtered["weight"])

            cols = ", ".join(filtered.keys())
            qs = ", ".join(["?"] * len(filtered))

            cursor.execute(
                f"INSERT INTO stones ({cols}) VALUES ({qs})",
                list(filtered.values())
            )

            stone_id = cursor.lastrowid
            cursor.execute("SELECT * FROM stones WHERE id = ?", (stone_id,))
            stone = cursor.fetchone()

            recalculate_stone_price(cursor, stone)

        conn.commit()
        return redirect(url_for("inventory"))

    finally:
        conn.close()