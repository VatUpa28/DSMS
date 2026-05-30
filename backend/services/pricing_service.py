from utils.set_null import set_null
from utils.get_rapaport_shape import get_rapaport_shape


def safe_float(v, default=0.0):
    try:
        if v in (None, "", "None"):
            return default
        return float(v)
    except:
        return default


def recalculate_stone_price(cursor, stone):

    stone = dict(stone)
    stone_id = stone["id"]

    try:
        cursor.execute("""
            SELECT shape, weight, clarity, color, rapaport_discount
            FROM grading_reports
            WHERE id = ?
        """, (stone_id,))

        g = cursor.fetchone()
        if not g:
            set_null(cursor, stone_id)
            return

        fancy = (stone.get("fancy_color") or "").strip()
        if fancy:
            set_null(cursor, stone_id)
            return

        weight = safe_float(g["weight"])
        rap_shape = get_rapaport_shape(g["shape"], fancy)

        cursor.execute("""
            SELECT price_per_carat
            FROM rapaport_prices
            WHERE shape = ?
              AND clarity = ?
              AND color = ?
              AND ? BETWEEN min_weight AND max_weight
            ORDER BY price_date DESC
            LIMIT 1
        """, (rap_shape, g["clarity"], g["color"], weight))

        rap = cursor.fetchone()
        if not rap:
            set_null(cursor, stone_id)
            return

        rap_price = safe_float(rap["price_per_carat"])

        # NEW RULE:
        # +discount = markup
        # -discount = markdown

        disc = safe_float(g["rapaport_discount"])

        # apply formula:
        # markup (+) increases price
        # markdown (-) decreases price
        ppc = round(rap_price * (1 + disc / 100), 2)

        total = round(ppc * weight, 2)

        print(f"DEBUG {stone_id}: RAP={rap_price} DISC={disc} PPC={ppc} TOTAL={total}")

        cursor.execute("""
            UPDATE grading_reports
            SET rapaport_price_per_carat = ?,
                price_per_carat = ?,
                total_price = ?
            WHERE id = ?
        """, (rap_price, ppc, total, stone_id))

        cursor.execute("""
            SELECT rapaport_price_per_carat,
                   rapaport_discount,
                   price_per_carat,
                   total_price
            FROM grading_reports
            WHERE id = ?
        """, (stone_id,))

        print("[POST-UPDATE CHECK]", cursor.fetchone())

    except Exception as e:
        print("PRICE ENGINE ERROR:", repr(e))
        set_null(cursor, stone_id)