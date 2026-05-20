from constants.stone_fields import (
    allowed_stones_fields,
    required_stones_fields
)
from services.stone_service_helpers import (
    validate_required_fields,
    filter_stone_data,
    insert_stone
)
from services.grading_service import (insert_grading, validate_grading_required_fields)
from services.stone_data_splitter import split_data

from utils.stone_utils import get_size_from_weight
from services.pricing_service import recalculate_stone_price


def create_stone(cursor, data):
    stone_data, grading_data = split_data(data)

    validate_required_fields(stone_data)

    validate_grading_required_fields(grading_data)

    stone_id = insert_stone(cursor, stone_data)

    grading_data["stone_id"] = stone_id

    insert_grading(cursor, grading_data)

    return stone_id