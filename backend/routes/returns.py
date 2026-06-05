from flask import Blueprint, request, jsonify
from database.db import get_db

return_bp = Blueprint("return", __name__)

@return_bp.route("/receive-stones", methods=["POST"])
def receive_stones():

    conn = get_db()
    cursor = conn.cursor()

    data = request.get_json()

    stone_ids = data.get("stone_ids", [])

    if not stone_ids:
        conn.close()
        return jsonify({"error": "No stones provided"}), 400

    cursor.executemany("""
        UPDATE stones
        SET status = 'Y'
        WHERE id = ?
          AND status = 'B'
    """, [(sid,) for sid in stone_ids])

    conn.commit()
    conn.close()

    return jsonify({"success": True})