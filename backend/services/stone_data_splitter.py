from constants.stone_fields import allowed_stone_fields


def split_data(data):
    stone_data = {}
    grading_data = {}

    for k, v in data.items():
        if k in allowed_stone_fields:
            stone_data[k] = v
        else:
            grading_data[k] = v

    return stone_data, grading_data