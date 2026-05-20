def insert_grading(cursor, data):

    cols = ", ".join(data.keys())
    qs = ", ".join(["?"] * len(data))

    cursor.execute(
        f"INSERT INTO grading_reports ({cols}) VALUES ({qs})",
        list(data.values())
    )

from constants.grading_fields import required_grading_fields

def validate_grading_required_fields(data):

    for field in required_grading_fields:
        if field not in data or str(data[field]).strip() == "":
            raise ValueError(f"{field} is required")