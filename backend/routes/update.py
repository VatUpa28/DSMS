from flask import Blueprint, request, redirect, url_for
from database.db import get_db
from services.apply_discount_to_stone import apply_discount_to_stone
from services.pricing_service import recalculate_stone_price

update_stone_discount_bp = Blueprint("update_stone_discount", __name__)


@update_stone_discount_bp.route("/update-stone-discount", methods=["POST"])
def update_stone_discount():
    conn = get_db()
    try:
        cursor = conn.cursor()

        stone_id = request.form["stone_id"]
        discount = request.form["discount"]

        apply_discount_to_stone(cursor, stone_id, discount)

        conn.commit()
        return redirect(url_for("inventory.inventory"))
    finally:
        conn.close()