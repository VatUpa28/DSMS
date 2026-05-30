def apply_discount_row(cursor, row, mode):
    
    row = {k.strip().lower(): v for k, v in row.items()}

    discount = float(row["discount"])

    where_parts = []
    where_params = []

    for field, value in row.items():

        if field == "discount":
            continue

        value = (value or "").strip()

        if value:
            where_parts.append(f"{field} = ?")
            where_params.append(value)

    where_clause = ""

    if where_parts:
        where_clause = "WHERE " + " AND ".join(where_parts)

    # DEBUG
    print("WHERE:", where_clause)
    print("PARAMS:", where_params)
    print("DISCOUNT:", discount)

    if mode == "set":

        sql = f"""
        UPDATE grading_reports
        SET rapaport_discount = ?
        {where_clause}
        """

        cursor.execute(sql, [discount] + where_params)

    elif mode == "offset":

        sql = f"""
        UPDATE grading_reports
        SET rapaport_discount = COALESCE(rapaport_discount, 0) + ?
        {where_clause}
        """

        cursor.execute(sql, [discount] + where_params)

    # DEBUG
    cursor.execute(
        f"SELECT COUNT(*) FROM grading_reports {where_clause}",
        where_params
    )

    print("MATCHED:", cursor.fetchone()[0])