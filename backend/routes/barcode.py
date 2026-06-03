from flask import Blueprint, render_template
from database.db import get_db

barcode_bp = Blueprint("barcode", __name__)

@barcode_bp.route("/barcodes")
def barcodes():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, stock_number, barcode_path
        FROM stones
        ORDER BY id ASC
    """)

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return render_template("barcodes.html", stones=rows)