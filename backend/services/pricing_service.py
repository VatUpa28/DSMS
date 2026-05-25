from utils.set_null import set_null
from utils.get_rapaport_shape import get_rapaport_shape


def recalculate_stone_price(cursor, stone):

    stone = dict(stone)

    try:
        cursor.execute("""
            SELECT shape, weight, clarity, color
            FROM grading_reports
            WHERE id = ?
        """, (stone["id"],))

        g = cursor.fetchone()

        if not g:
            print("[NO GRADING REPORT]", stone["id"])
            set_null(cursor, stone["id"])
            return

        fancy = (stone.get("fancy_color") or "").strip()

        if fancy:
            set_null(cursor, stone["id"])
            return

        rap_shape = get_rapaport_shape(g["shape"], fancy)
        weight = float(g["weight"])

        cursor.execute("""
            SELECT price_per_carat
            FROM rapaport_prices
            WHERE shape = ?
              AND clarity = ?
              AND color = ?
              AND ? BETWEEN min_weight AND max_weight
            ORDER BY price_date DESC
            LIMIT 1
        """, (
            rap_shape,
            g["clarity"],
            g["color"],
            weight
        ))

        rap = cursor.fetchone()

        if not rap:
            set_null(cursor, stone["id"])
            return

        rap_price = float(rap["price_per_carat"])

        discount = stone.get("rapaport_discount")
        try:
            discount = float(discount) if discount not in (None, "", "None") else 0
        except:
            discount = 0

        final_ppc = round(rap_price * (1 - discount / 100), 2)
        total = round(final_ppc * weight, 2)

        cursor.execute("""
            UPDATE grading_reports
            SET rapaport_price_per_carat = ?,
                price_per_carat = ?,
                total_price = ?
            WHERE id = ?
        """, (rap_price, final_ppc, total, stone["id"]))

    except Exception as e:
        print("PRICE ENGINE ERROR:", repr(e))
        set_null(cursor, stone["id"])