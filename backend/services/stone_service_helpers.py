def insert_stone(cursor, data):

    cols = ", ".join(data.keys())
    qs = ", ".join(["?"] * len(data))

    cursor.execute(
        f"INSERT INTO stones ({cols}) VALUES ({qs})",
        list(data.values())
    )

    return cursor.lastrowid

from constants.stone_fields import allowed_stones_fields

def filter_stone_data(data):

    return {
        k: v
        for k, v in data.items()
        if k in allowed_stones_fields and v != ""
    }

from constants.stone_fields import required_stones_fields

def validate_required_fields(data):

    for field in required_stones_fields:
        if field not in data or str(data[field]).strip() == "":
            raise ValueError(f"{field} is required")