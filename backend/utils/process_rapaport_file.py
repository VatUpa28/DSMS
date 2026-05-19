import csv

def process_rapaport_file(file, cursor):
    lines = file.stream.read().decode("utf-8").splitlines()
    reader = csv.reader(lines)

    for row in reader:
        if len(row) < 7:
            continue

        if row[0].lower().strip() == "shape":
            continue

        shape, clarity, color = row[0], row[1], row[2]
        min_w, max_w = float(row[3]), float(row[4])

        if min_w == 5.00 and max_w == 5.99:
            max_w = 9.99

        price = float(row[5])
        date = row[6]

        cursor.execute("""
            INSERT INTO rapaport_prices (
                shape, clarity, color,
                min_weight, max_weight,
                price_per_carat, price_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (shape, clarity, color, min_w, max_w, price, date))