from flask import Blueprint, request, redirect, url_for
from database.db import get_db
from services.stone_service import create_stone
from utils.stone_utils import get_size_from_weight
from constants.stone_fields import (
    allowed_stone_fields,
    required_stone_fields
)
from constants.csv_to_db import csv_to_db
import io, csv

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

            # -------------------------
            # STEP 1: normalize + map CSV
            # -------------------------
            mapped = {}

            for k, v in row.items():
                if not k:
                    continue

                key = k.strip()

                if key in csv_to_db and v != "":
                    mapped[csv_to_db[key]] = v

            # -------------------------
            # STEP 2: split tables
            # -------------------------
            stone_data = {
                k: v for k, v in mapped.items()
                if k in allowed_stone_fields
            }

            grading_data = {
                k: v for k, v in mapped.items()
                if k not in allowed_stone_fields
            }

            # -------------------------
            # STEP 3: validate stone fields
            # -------------------------
            for field in required_stone_fields:
                if field not in stone_data or str(stone_data[field]).strip() == "":
                    return {"error": f"Missing required field: {field}"}, 400

            # -------------------------
            # STEP 4: handle weight (GRADING TABLE)
            # -------------------------
            weight = grading_data.get("weight")

            if weight is None or str(weight).strip() == "":
                return {"error": "Missing weight in CSV row"}, 400

            try:
                weight = float(weight)
            except:
                return {"error": f"Invalid weight: {weight}"}, 400

            grading_data["weight"] = weight
            grading_data["size"] = get_size_from_weight(weight)

            # -------------------------
            # STEP 5: insert stone
            # -------------------------
            cols = ", ".join(stone_data.keys())
            qs = ", ".join(["?"] * len(stone_data))

            cursor.execute(
                f"INSERT INTO stones ({cols}) VALUES ({qs})",
                list(stone_data.values())
            )

            stone_id = cursor.lastrowid

            # -------------------------
            # STEP 6: insert grading report
            # -------------------------
            if grading_data:
                grading_data["stone_id"] = stone_id

                cols = ", ".join(grading_data.keys())
                qs = ", ".join(["?"] * len(grading_data))

                cursor.execute(
                    f"INSERT INTO grading_reports ({cols}) VALUES ({qs})",
                    list(grading_data.values())
                )

        conn.commit()
        return redirect(url_for("inventory.inventory"))

    finally:
        conn.close()