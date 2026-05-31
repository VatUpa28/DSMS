from datetime import datetime


def generate_transaction_number(cursor, transaction_type):

    prefixes = {
        "memo": "M",
        "invoice": "I",
        "credit_invoice": "CI"
    }

    prefix = prefixes[transaction_type]

    today = datetime.now().strftime("%y%m%d")

    search_prefix = f"{prefix}{today}"

    cursor.execute("""
        SELECT transaction_number
        FROM transactions
        WHERE transaction_number LIKE ?
        ORDER BY transaction_number DESC
        LIMIT 1
    """, (f"{search_prefix}%",))

    row = cursor.fetchone()

    if row:
        last_number = int(row["transaction_number"][-3:])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{search_prefix}{next_number:03d}"