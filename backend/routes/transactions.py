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
from utils.generate_transaction_number import generate_transaction_number
import sqlite3

transactions_bp = Blueprint("transactions", __name__)

@transactions_bp.route("/create-memo", methods=["POST"])
def create_memo():

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    form = request.form

    client_id = form.get("client_id")
    person = form.get("person")
    phone = form.get("phone")

    if not client_id:
        return "Missing client", 400

    if not person:
        return "Missing person (required)", 400

    stone_ids = form.getlist("stone_ids")
    if not stone_ids:
        return "No stones selected", 400

    # fallback shipping logic
    ship_to_address = form.get("ship_to_address") or ""

    transaction_number = generate_transaction_number(
    cursor,
    "memo"
)

    cursor.execute("""
INSERT INTO transactions (
    transaction_number,
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
    purchase_order_number
)
VALUES (
    ?, ?, 'memo', 'draft',
    ?, ?, ?, ?, ?, ?, ?, ?, ?
)
""", (
    transaction_number,
    client_id,
    person,
    phone,
    form.get("fax"),
    form.get("date"),
    form.get("terms"),
    form.get("carrier"),
    form.get("shipment_type"),
    form.get("ship_charge"),
    form.get("purchase_order_number")
))

    transaction_id = cursor.lastrowid

    for stone_id in stone_ids:

        cursor.execute("""
            SELECT
                s.stock_number,
                g.id AS grading_report_id,
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
            AND g.active = 1
        """, (stone_id,))

        data = cursor.fetchone()

        if not data:
            continue

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
            VALUES (?, ?, ?, 'draft', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction_id,
            stone_id,
            data["grading_report_id"],
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

        cursor.execute("""
            UPDATE stones
            SET status = 'FM'
            WHERE id = ?
        """, (stone_id,))

    conn.commit()
    conn.close()

    return redirect("/transactions")

@transactions_bp.route("/transactions", methods=["GET"])
def transactions():

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
    WHERE t.status != 'cancelled'
    GROUP BY t.id
    ORDER BY t.id DESC
""")

    transactions = cursor.fetchall()

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
        "transactions/transactions.html",
        transactions=transactions,
        available_stones=available_stones
    )

@transactions_bp.route("/clients/by-code/<client_code>")
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

@transactions_bp.route("/transactions/<int:transaction_id>/confirm", methods=["POST"])
def confirm_transaction(transaction_id):

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT type
        FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    tx = cursor.fetchone()

    if not tx:
        conn.close()
        return redirect("/transactions")

    # ONLY memo requires confirmation
    if tx["type"] != "memo":
        conn.close()
        return redirect("/transactions")

    cursor.execute("""
        UPDATE transactions
        SET status = 'active'
        WHERE id = ?
    """, (transaction_id,))

    cursor.execute("""
        UPDATE transaction_items
        SET status = 'active'
        WHERE transaction_id = ?
    """, (transaction_id,))

    cursor.execute("""
        SELECT stone_id
        FROM transaction_items
        WHERE transaction_id = ?
    """, (transaction_id,))

    stones = cursor.fetchall()

    for stone in stones:
        cursor.execute("""
            UPDATE stones
            SET status = 'M'
            WHERE id = ?
        """, (stone["stone_id"],))

    conn.commit()
    conn.close()

    return redirect("/transactions")

@transactions_bp.route("/transactions/<int:transaction_id>")
def view_transaction(transaction_id):

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            t.*,
            c.name AS client_name
        FROM transactions t
        JOIN clients c
            ON c.id = t.client_id
        WHERE t.id = ?
    """, (transaction_id,))

    transaction = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM transaction_items
        WHERE transaction_id = ?
        ORDER BY stock_number
    """, (transaction_id,))

    stones = cursor.fetchall()

    conn.close()

    return render_template(
        "transactions/transaction_detail.html",
        transaction=transaction,
        stones=stones
    )

@transactions_bp.route("/transactions/<int:transaction_id>/return", methods=["POST"])
def return_stones(transaction_id):

    stone_ids = request.form.getlist("stone_ids")

    conn = get_db()
    cursor = conn.cursor()

    for stone_id in stone_ids:

        cursor.execute("""
            UPDATE transaction_items
            SET status = 'return'
            WHERE transaction_id = ?
            AND stone_id = ?
        """, (transaction_id, stone_id))

        cursor.execute("""
            UPDATE stones
            SET status = 'B'
            WHERE id = ?
        """, (stone_id,))

    cursor.execute("""
    SELECT stone_id, status
    FROM transaction_items
    WHERE transaction_id = ?
""", (transaction_id,))

    print("ITEM STATUSES:")
    for row in cursor.fetchall():
        print(row)

    cursor.execute("""
        SELECT COUNT(*)
        FROM transaction_items
        WHERE transaction_id = ?
        AND status = 'active'
    """, (transaction_id,))

    active_remaining = cursor.fetchone()[0]
    print("ACTIVE REMAINING =", active_remaining)

    if active_remaining == 0:

        cursor.execute("""
            UPDATE transactions
            SET status = 'return'
            WHERE id = ?
        """, (transaction_id,))

    conn.commit()
    conn.close()

    return redirect(f"/transactions/{transaction_id}")

@transactions_bp.route("/transactions/<int:transaction_id>/receive", methods=["POST"])
def receive_return(transaction_id):

    stone_ids = request.form.getlist("stone_ids")

    conn = get_db()
    cursor = conn.cursor()

    for stone_id in stone_ids:

        cursor.execute("""
            UPDATE transaction_items
            SET status = 'returned'
            WHERE transaction_id = ?
            AND stone_id = ?
        """, (transaction_id, stone_id))

        cursor.execute("""
            UPDATE stones
            SET status = 'Y'
            WHERE id = ?
        """, (stone_id,))

    cursor.execute("""
        SELECT COUNT(*)
        FROM transaction_items
        WHERE transaction_id = ?
        AND status != 'returned'
    """, (transaction_id,))

    remaining = cursor.fetchone()[0]

    if remaining == 0:

        cursor.execute("""
            UPDATE transactions
            SET status = 'cancelled'
            WHERE id = ?
        """, (transaction_id,))

    conn.commit()
    conn.close()

    return redirect(f"/transactions/{transaction_id}")

@transactions_bp.route("/transaction/<int:transaction_id>/create-invoice", methods=["POST"])
def create_invoice(transaction_id):

    print("HIT create_invoice")

    print("FORM:", request.form)
    print("ARGS:", request.args)
    print("JSON:", request.get_json(silent=True))

    stone_ids = request.form.getlist("stone_ids")
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT type, status
        FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    tx = cursor.fetchone()

    if not tx:
        conn.close()
        return redirect("/transactions")

    if tx["type"] != "memo":
        conn.close()
        return "Only memos can be invoiced", 400
    
    cursor.execute("""
    SELECT COUNT(*)
    FROM transaction_items
    WHERE transaction_id = ?
    AND status = 'active'
""", (transaction_id,))

    count = cursor.fetchone()[0]

    if count == 0:
        conn.close()
        return "No active stones to invoice", 400
    
    cursor.execute("""
    SELECT *
    FROM transactions
    WHERE id = ?
""", (transaction_id,))

    memo = cursor.fetchone()

    cursor.execute("""
    INSERT INTO transactions (
        transaction_number,
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
        purchase_order_number
    )
    VALUES (
        ?, ?, 'invoice', 'active',
        ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
""", (
    generate_transaction_number(cursor, "invoice"),
    memo["client_id"],
    memo["person"],
    memo["phone"],
    memo["fax"],
    memo["date"],
    memo["terms"],
    memo["carrier"],
    memo["shipment_type"],
    memo["ship_charge"],
    memo["purchase_order_number"]
))
    
    cursor.execute("""
    SELECT *
    FROM transaction_items
    WHERE transaction_id = ?
    AND status = 'active'
""", (transaction_id,))

    items = cursor.fetchall()

    for item in items:
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
            VALUES (?, ?, ?, 'active',
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            item["stone_id"],
            item["grading_report_id"],
            item["stock_number"],
            item["report_number"],
            item["lab"],
            item["shape"],
            item["weight"],
            item["color"],
            item["clarity"],
            item["cut"],
            item["polish"],
            item["symmetry"],
            item["fluorescence_intensity"],
            item["price_per_carat"],
            item["total_price"]
        ))

    cursor.execute("""
    UPDATE transactions
    SET status = 'completed'
    WHERE id = ?
""", (transaction_id,))
    
    conn.commit()
    conn.close()

    return redirect("/transactions")

@transactions_bp.route("/transactions/<int:transaction_id>/create-invoice", methods=["POST"])
def create_invoice_from_memo(transaction_id):
    print("HIT create_invoice_from_memo")

    print("HEADERS:", request.headers)
    print("FORM:", request.form)
    print("VALUES:", request.values)

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    memo = cursor.fetchone()

    if not memo or memo["type"] != "memo":
        conn.close()
        return "Invalid memo", 400
    
    stone_ids = request.form.getlist("stone_ids")
    if not stone_ids:
        conn.close()
        return "No stones selected", 400
    
    cursor.execute(f"""
    SELECT *
    FROM transaction_items
    WHERE transaction_id = ?
    AND stone_id IN ({",".join(["?"]*len(stone_ids))})
    AND status = 'active'
""", (transaction_id, *stone_ids))

    items = cursor.fetchall()

    if not items:
        conn.close()
        return "No valid active stones selected", 400
    
    cursor.execute("""
    INSERT INTO transactions (
        transaction_number,
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
        purchase_order_number
    )
    VALUES (?, ?, 'invoice', 'active',
            ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    generate_transaction_number(cursor, "invoice"),
    memo["client_id"],
    memo["person"],
    memo["phone"],
    memo["fax"],
    memo["date"],
    memo["terms"],
    memo["carrier"],
    memo["shipment_type"],
    memo["ship_charge"],
    memo["purchase_order_number"]
))
    
    invoice_id = cursor.lastrowid

    for item in items:
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
            VALUES (?, ?, ?, 'active',
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            item["stone_id"],
            item["grading_report_id"],
            item["stock_number"],
            item["report_number"],
            item["lab"],
            item["shape"],
            item["weight"],
            item["color"],
            item["clarity"],
            item["cut"],
            item["polish"],
            item["symmetry"],
            item["fluorescence_intensity"],
            item["price_per_carat"],
            item["total_price"]
        ))

        # mark stones as SOLD in stones table
    for item in items:
        cursor.execute("""
            UPDATE stones
            SET status = 'S'
            WHERE id = ?
        """, (item["stone_id"],))

    cursor.execute("""
    UPDATE transactions
    SET status = 'completed'
    WHERE id = ?
""", (transaction_id,))
    
    conn.commit()
    conn.close()

    return redirect("/transactions")