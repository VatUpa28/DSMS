from services.apply_discount_row import apply_discount_row
from services.pricing_service import recalculate_stone_price
from database.db import get_db
import csv
import io


def process_discount_csv(file, mode):

    text = file.read().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))

    conn = get_db()
    cursor = conn.cursor()

    try:

        for row in rows:
            apply_discount_row(cursor, row, mode)

        cursor.execute("SELECT * FROM stones")

        for stone in cursor.fetchall():
            recalculate_stone_price(cursor, stone)

        conn.commit()

    finally:
        conn.close()