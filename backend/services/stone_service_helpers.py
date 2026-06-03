from constants.stone_fields import allowed_stone_fields

def insert_stone(cursor, data):
    cols = ", ".join(data.keys())
    qs = ", ".join(["?"] * len(data))

    cursor.execute(
        f"INSERT INTO stones ({cols}) VALUES ({qs})",
        list(data.values())
    )
    return cursor.lastrowid


def filter_stone_data(data):
    return {
        k: v
        for k, v in data.items()
        if k in allowed_stone_fields and v != ""
    }