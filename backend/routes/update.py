from flask import Blueprint, request, redirect, url_for
from database.db import get_db
from services.apply_discount_to_stone import apply_discount_to_stone
from utils.recalculate_stone_price import recalculate_stone_price

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
        return redirect(url_for("inventory"))

    finally:
        conn.close()

update_inventory_discount_bp = Blueprint("update_inventory_discount", __name__)

@update_inventory_discount_bp.route("/update-inventory-discount", methods=["POST"])
def update_inventory_discount():
    conn = get_db()

    try:
        cursor = conn.cursor()
        delta = request.form.get("delta", "0")

        try:
            delta = float(delta)
        except:
            delta = 0
        
        cursor.execute("SELECT * FROM stones")
        stones = [dict(r) for r in cursor.fetchall()]

        for stone in stones:
            old = stone.get("rapaport_discount") or 0

            try:
                old = float(old)
            except:
                old = 0
            
            new_discount = old + delta

            cursor.execute("""UPDATE stones SET rapaport_discount = ? WHERE id = ?""", (new_discount, stone["id"]))

            cursor.execute("SELECT * FROM stones WHERE id = ?", (stone["id"]))
            updated_stone = dict(cursor.fetchone())
            recalculate_stone_price(cursor, updated_stone)
        
        conn.commit()
        return redirect(url_for("inventory"))

    finally:
        conn.close()