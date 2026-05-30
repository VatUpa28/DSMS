from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify
)
from database.db import get_db
from datetime import datetime

memos_bp = Blueprint("memos", __name__)

@memos_bp.route("/create-memo", methods=["POST"])
def create_memo():

    conn = get_db()
    cursor = conn.cursor()

    form = request.form

    print("===== FORM DATA =====")
    print(dict(form))
    print("=====================")

    client_id = form.get("client_id")

    if not client_id:
        return "Missing client", 400

    stone_ids = form.getlist("stone_ids")  # IMPORTANT FIX

    if not stone_ids:
        return "No stones selected", 400

    cursor.execute("""
        INSERT INTO transactions (
            client_id,
            type,
            status,
            person,
            phone,
            fax,
            date,
            terms,
            carrier,
            shipment_type,
            ship_charge,
            ship_to_address_id,
            purchase_order_number
        )
        VALUES (?, 'memo', 'active', ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)
    """, (
        client_id,
        form.get("person"),
        form.get("phone"),
        form.get("fax"),
        form.get("date"),
        form.get("terms"),
        form.get("carrier"),
        form.get("shipment_type"),
        form.get("ship_charge"),
        form.get("purchase_order_number")
    ))

    transaction_id = cursor.lastrowid

    # insert items
    for stone_id in stone_ids:

        cursor.execute("""
            SELECT
                s.stock_number,
                g.report_number,
                g.lab,
                g.shape,
                g.weight,
                g.color,
                g.clarity,
                g.cut,
                g.polish,
                g.symmetry,
                g.fluorescence_intensity,
                g.price_per_carat,
                g.total_price
            FROM stones s
            JOIN grading_reports g ON g.stone_id = s.id
            WHERE s.id = ?
        """, (stone_id,))

        data = cursor.fetchone()

        cursor.execute("""
            INSERT INTO transaction_items (
                transaction_id,
                stone_id,
                grading_report_id,
                status,
                stock_number,
                report_number,
                lab,
                shape,
                weight,
                color,
                clarity,
                cut,
                polish,
                symmetry,
                fluorescence_intensity,
                price_per_carat,
                total_price
            )
            VALUES (?, ?, ?, 'memo', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_id,
            stone_id,
            data["stone_id"] if data else None,
            data["stock_number"],
            data["report_number"],
            data["lab"],
            data["shape"],
            data["weight"],
            data["color"],
            data["clarity"],
            data["cut"],
            data["polish"],
            data["symmetry"],
            data["fluorescence_intensity"],
            data["price_per_carat"],
            data["total_price"]
        ))

    conn.commit()
    conn.close()

    return redirect("/memos")

@memos_bp.route("/memos", methods=["GET"])
def memos():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            t.*,
            c.name AS client_name,
            COUNT(ti.id) AS stone_count
        FROM transactions t

        LEFT JOIN clients c
            ON c.id = t.client_id

        LEFT JOIN transaction_items ti
            ON ti.transaction_id = t.id

        WHERE t.type = 'memo'

        GROUP BY t.id

        ORDER BY t.id DESC
    """)

    memos = cursor.fetchall()

    cursor.execute("""
        SELECT
            s.id,
            s.stock_number,

            gr.shape,
            gr.weight,
            gr.color,
            gr.clarity,

            gr.price_per_carat,
            gr.total_price

        FROM stones s

        JOIN grading_reports gr
            ON gr.stone_id = s.id

        WHERE s.status = 'Y'
        AND gr.active = 1

        ORDER BY s.stock_number
    """)

    available_stones = cursor.fetchall()

    conn.close()

    return render_template(
        "memos.html",
        memos=memos,
        available_stones=available_stones
    )

@memos_bp.route("/clients/by-code/<client_code>")
def get_client_by_code(client_code):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM clients
        WHERE code = ?
    """, (client_code,))

    client = cursor.fetchone()

    conn.close()

    if not client:
        return jsonify({
            "error": "Client not found"
        }), 404

    return jsonify(dict(client))