from flask import Blueprint, jsonify
from database.db import get_db

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/stone-by-stock/<stock_number>")
def stone_by_stock(stock_number):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            stock_number,
            status
        FROM stones
        WHERE stock_number = ?
    """, (stock_number,))

    stone = cursor.fetchone()

    conn.close()

    if not stone:
        return jsonify({
            "error": "Stone not found"
        }), 404

    return jsonify(dict(stone))