from flask import Blueprint, render_template
from database.db import get_db

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory", methods=["GET"])
def inventory():
    conn = get_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM stones
            LEFT JOIN grading_reports
            ON grading_reports.id = (
                SELECT id
                FROM grading_reports gr2
                WHERE gr2.stone_id = stones.id
                ORDER BY id DESC
                LIMIT 1
            )
            ORDER BY stones.id DESC
        """)

        rows = cursor.fetchall()

        return render_template(
            "inventory.html",
            stones=[dict(r) for r in rows]
        )

    finally:
        conn.close()