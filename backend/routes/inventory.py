from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from database.db import get_db

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory", methods=["GET"])
def inventory():
    conn = get_db()
    try:
        cursor = conn.cursor()

        filters = {
            "shape": request.args.getlist("shape"),
            "size": request.args.getlist("size"),
            "color": request.args.getlist("color"),
            "clarity": request.args.getlist("clarity"),
            "lab": request.args.getlist("lab"),
            "cut": request.args.getlist("cut"),
            "polish": request.args.getlist("polish"),
            "symmetry": request.args.getlist("symmetry"),
            "fluorescence_intensity": request.args.getlist("fluorescence_intensity"),
            "status": request.args.getlist("status"),
        }

        filter_columns = {
            "shape": "grading_reports.shape",
            "size": "grading_reports.size",
            "color": "grading_reports.color",
            "clarity": "grading_reports.clarity",
            "lab": "grading_reports.lab",
            "cut": "grading_reports.cut",
            "polish": "grading_reports.polish",
            "symmetry": "grading_reports.symmetry",
            "fluorescence_intensity": "grading_reports.fluorescence_intensity",
            "status": "stones.status",
        }

        ranges = {
            "weight": (request.args.get("weight_min"), request.args.get("weight_max")),
            "depth_percent": (request.args.get("depth_min"), request.args.get("depth_max")),
            "table_percent": (request.args.get("table_min"), request.args.get("table_max")),
            "price_per_carat": (request.args.get("ppc_min"), request.args.get("ppc_max")),
            "total_price": (request.args.get("total_min"), request.args.get("total_max")),
            "rapaport_discount": (request.args.get("discount_min"), request.args.get("discount_max"))
        }

        query = """
            SELECT
                *

            FROM stones
            LEFT JOIN grading_reports
                ON grading_reports.stone_id = stones.id
            WHERE 1=1
        """

        params = []

        stock_numbers = request.args.get("stock_numbers", "").strip()

        if stock_numbers:
            stock_list = [
                s.strip()
                for s in stock_numbers.splitlines()
                if s.strip()
            ]

            if stock_list:
                placeholders = ",".join(["?"] * len(stock_list))

                query += f"""
                    AND stones.stock_number IN ({placeholders})
                """

                params.extend(stock_list)

        for field, values in filters.items():
            if values:
                placeholders = ",".join(["?"] * len(values))

                query += f" AND {filter_columns[field]} IN ({placeholders})"

                params.extend(values)

        for field, (min_value, max_value) in ranges.items():
            
            if min_value:
                query += f" AND grading_reports.{field} >= ?"
                params.append(min_value)

            if max_value:
                query += f" AND grading_reports.{field} <= ?"
                params.append(max_value)

        query += " ORDER BY stones.id"

        cursor.execute(query, params)

        stones = cursor.fetchall()

        rows = [dict(r) for r in stones]

        display_columns = [
            "stock_number",
            "status",
            "shape",
            "size",
            "weight",
            "color",
            "clarity",
            "rapaport_price_per_carat",
            "rapaport_discount",
            "price_per_carat",
            "total_price", 
            "lab", 
            "cut", 
            "polish", 
            "symmetry", 
            "fluorescence_intensity", 
            "fluorescence_color", 
            "depth_percent", 
            "table_percent", 
            "measurements", 
            "report_number", 
            "fancy_color", 
            "fancy_intensity", 
            "overtone", 
            "girdle_tn", 
            "girdle_thick", 
            "girdle_percent", 
            "girdle_condition", 
            "culet_size", 
            "picture_link", 
            "video_link", 
            "certificate_image_link", 
            "pair_number", 
            "pair_stock_number", 
            "pair_separable", 
            "shade", 
            "milky", 
            "eye_clean", 
            "bgm", 
            "black", 
            "open_inclusion", 
            "laser_inscription", 
            "lab_comments", 
            "key_to_symbols", 
            "internal_comments", 
            "current_country", 
            "current_state", 
            "current_city"
        ]

        return render_template(
            "inventory.html",
            stones=rows,
            display_columns=display_columns
        )

    finally:
        conn.close()

@inventory_bp.route("/hold-stones", methods=["POST"])
def hold_stones():

    client_id = request.form.get("client_id")
    stone_ids = request.form.getlist("stone_ids")

    if not client_id:
        return "Client required", 400

    if not stone_ids:
        return "No stones selected", 400

    conn = get_db()
    cursor = conn.cursor()

    placeholders = ",".join(["?"] * len(stone_ids))

    cursor.execute(f"""
    UPDATE stones
    SET status = 'H',
        hold_client_id = ?
    WHERE id IN ({placeholders})
""", [client_id] + stone_ids)

    conn.commit()
    conn.close()

    return redirect(url_for("inventory.inventory"))

@inventory_bp.route("/inventory/hold-info/<int:stone_id>")
def hold_info(stone_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.name
        FROM stones s
        JOIN clients c ON c.id = s.hold_client_id
        WHERE s.id = ?
          AND s.hold_client_id IS NOT NULL
    """, (stone_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "No active hold"}), 404

    return jsonify({
        "client_name": row["name"]
    })