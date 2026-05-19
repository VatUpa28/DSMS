from flask import Blueprint, render_template
from database.db import get_db

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.route("/inventory", methods=["GET"])
def inventory():
    conn = get_db()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stones JOIN grading_reports ON stones.id = grading_reports.stone_id ORDER BY id DESC")
        
        stones = cursor.fetchall()

        return render_template("inventory.html", stones=[dict(s) for s in stones])

    finally:
        if conn:
            conn.close()