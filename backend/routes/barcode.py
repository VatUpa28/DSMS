from flask import Blueprint, render_template, request, send_file
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from database.db import get_db
import tempfile
import os

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

@barcode_bp.route("/barcodes/pdf")
def generate_pdf():

    ids = request.args.get("stone_ids", "")

    if not ids:
        return "No stones selected", 400

    stone_ids = [x.strip() for x in ids.split(",")]

    conn = get_db()
    cursor = conn.cursor()

    placeholders = ",".join(["?"] * len(stone_ids))

    cursor.execute(f"""
        SELECT
            id,
            stock_number,
            barcode_path
        FROM stones
        WHERE id IN ({placeholders})
        ORDER BY stock_number
    """, stone_ids)

    stones = [dict(r) for r in cursor.fetchall()]
    conn.close()

    pdf_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    doc = SimpleDocTemplate(pdf_file.name)

    styles = getSampleStyleSheet()
    elements = []

    for stone in stones:

        elements.append(
            Paragraph(
                f"<b>{stone['stock_number']}</b>",
                styles["Heading4"]
            )
        )

        image_path = os.path.join(
            "static",
            stone["barcode_path"]
        )

        if os.path.exists(image_path):
            elements.append(
                Image(
                    image_path,
                    width=250,
                    height=60
                )
            )

        elements.append(Spacer(1, 12))

    doc.build(elements)

    return send_file(
        pdf_file.name,
        as_attachment=True,
        download_name="barcodes.pdf",
        mimetype="application/pdf"
    )