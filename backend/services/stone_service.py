from constants.stone_fields import (
    allowed_stones_fields,
    required_stones_fields
)

from utils.stone_utils import get_size_from_weight
from services.pricing_service import recalculate_stone_price


def create_stone(cursor, data):

    validate_required_fields(data)

    filtered = filter_stone_data(data)

    filtered["size"] = get_size_from_weight(filtered["weight"])

    stone_id = insert_stone(cursor, filtered)

    cursor.execute(
        "SELECT * FROM stones WHERE id = ?",
        (stone_id,)
    )

    stone = cursor.fetchone()

    recalculate_stone_price(cursor, stone)

    return stone_id