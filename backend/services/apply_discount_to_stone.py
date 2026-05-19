def apply_discount_to_stone(cursor, stone_id, discount):
    cursor.execute("""
        UPDATE stones
        SET rapaport_discount = ?
        WHERE id = ?
    """, (discount, stone_id))

    cursor.execute("SELECT * FROM stones WHERE id = ?", (stone_id,))
    stone = cursor.fetchone()

    recalculate_stone_price(cursor, stone)