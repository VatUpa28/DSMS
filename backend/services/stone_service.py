from constants.stone_fields import allowed_stone_fields
from utils.stone_utils import get_size_from_weight
from services.pricing_service import recalculate_stone_price
from services.stone_service_helpers import (
    filter_stone_data,
    insert_stone
)
from utils.generate_stock_number import generate_stock_number


def create_stone(cursor, data):


    filtered = filter_stone_data(data)

    filtered["size"] = get_size_from_weight(filtered["weight"])

    filtered["stock_number"] = generate_stock_number(
        cursor,
        filtered["shape"]
    )

    stone_id = insert_stone(cursor, filtered)

    cursor.execute(
        "SELECT * FROM stones WHERE id = ?",
        (stone_id,)
    )
    stone = cursor.fetchone()

    recalculate_stone_price(cursor, stone)

    return stone_id