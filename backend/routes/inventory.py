from flask import Blueprint, render_template
from database.db import get_db

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory", methods=["GET"])
def inventory():
    conn = get_db()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                *

            FROM stones
            LEFT JOIN grading_reports
                ON grading_reports.stone_id = stones.id
            ORDER BY stones.id
        """)

        stones = cursor.fetchall()

        rows = [dict(r) for r in stones]

        return render_template(
            "inventory.html",
            stones=rows
        )

    finally:
        conn.close()