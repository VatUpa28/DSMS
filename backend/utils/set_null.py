def set_null(cursor, stone_id):
    cursor.execute("""
        UPDATE stones
        SET rapaport_price_per_carat = NULL,
            price_per_carat = NULL,
            total_price = NULL
        WHERE id = ?
    """, (stone_id,))