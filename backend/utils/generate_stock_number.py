def generate_stock_number(cursor, shape):

    cursor.execute("""
        SELECT last_number
        FROM stock_number_sequence
        WHERE shape = ?
    """, (shape,))

    row = cursor.fetchone()

    if row is None:
        cursor.execute("""
            INSERT INTO stock_number_sequence
            (shape, last_number)
            VALUES (?, 1)
        """, (shape,))

        seq = 1

    else:
        seq = row["last_number"] + 1

        cursor.execute("""
            UPDATE stock_number_sequence
            SET last_number = ?
            WHERE shape = ?
        """, (seq, shape))

    return f"{shape}{seq:06d}"