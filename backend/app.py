from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import csv
import io

app = Flask(__name__)

allowed_fields = [
    "stock_number", "status", "shape", "weight", "size",
    "color_grade", "clarity", "cut_grade", "polish", "symmetry",
    "fluorescence_strength", "fluorescence_color",
    "fancy_color", "fancy_intensity", "overtone",
    "measurements", "depth_percent", "table_percent",
    "girdle", "culet",
    "crown_height", "crown_angle",
    "pavilion_depth", "pavilion_angle",
    "rapaport_price_per_carat", "rapaport_discount",
    "price_per_carat", "total_price",
    "eye_clean", "bgm", "black", "milky", "open_inclusions",
    "pair_number", "pair_stock_number", "pair_separable",
    "picture_link", "video_link"
]

required_fields = [
    "stock_number", "status", "shape",
    "weight", "size", "color_grade",
    "clarity", "measurements"
]

# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect(url_for("inventory"))

# ---------------- INVENTORY ----------------

@app.route("/inventory", methods=["GET"])
def inventory():
    conn = None
    try:
        conn = sqlite3.connect("./database/app.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stones ORDER BY id DESC")
        stones = cursor.fetchall()

        return render_template("inventory.html", stones=[dict(s) for s in stones])

    finally:
        if conn:
            conn.close()

# ---------------- ADD SINGLE STONE ----------------

@app.route("/add-stone", methods=["POST"])
def add_stone():
    conn = sqlite3.connect("./database/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        data = request.form

        for f in required_fields:
            if f not in data or data[f].strip() == "":
                return {"error": f"{f} required"}, 400

        filtered = {
            k: v for k, v in data.items()
            if k in allowed_fields and v != ""
        }

        filtered["size"] = get_size_from_weight(filtered["weight"])

        cols = ", ".join(filtered.keys())
        qs = ", ".join(["?"] * len(filtered))

        cursor.execute(
            f"INSERT INTO stones ({cols}) VALUES ({qs})",
            list(filtered.values())
        )

        stone_id = cursor.lastrowid

        cursor.execute("SELECT * FROM stones WHERE id = ?", (stone_id,))
        stone = cursor.fetchone()

        recalculate_stone_price(cursor, stone)

        conn.commit()
        return redirect(url_for("inventory"))

    finally:
        conn.close()

# ---------------- ADD CSV STONES ----------------

@app.route("/add-stones", methods=["POST"])
def add_stones():
    conn = sqlite3.connect("./database/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        file = request.files["file"]
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        for row in reader:

            filtered = {
                k: v for k, v in row.items()
                if k in allowed_fields and v != ""
            }

            if not all(f in filtered for f in required_fields):
                return {"error": "Missing fields in CSV"}, 400

            filtered["size"] = get_size_from_weight(filtered["weight"])

            cols = ", ".join(filtered.keys())
            qs = ", ".join(["?"] * len(filtered))

            cursor.execute(
                f"INSERT INTO stones ({cols}) VALUES ({qs})",
                list(filtered.values())
            )

            stone_id = cursor.lastrowid
            cursor.execute("SELECT * FROM stones WHERE id = ?", (stone_id,))
            stone = cursor.fetchone()

            recalculate_stone_price(cursor, stone)

        conn.commit()
        return redirect(url_for("inventory"))

    finally:
        conn.close()

# ---------------- RAPAPORT UPLOAD ----------------

@app.route("/upload-rapaport", methods=["POST"])
def upload_rapaport():
    conn = sqlite3.connect("./database/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        round_file = request.files["round_file"]
        pear_file = request.files["pear_file"]

        cursor.execute("DELETE FROM rapaport_prices")

        process_rapaport_file(round_file, cursor)
        process_rapaport_file(pear_file, cursor)

        cursor.execute("SELECT * FROM stones")
        stones = cursor.fetchall()

        for stone in stones:
            recalculate_stone_price(cursor, stone)

        conn.commit()
        return redirect(url_for("inventory"))

    finally:
        conn.close()

# ---------------- STONE DISCOUNT UPDATE ----------------

@app.route("/update-stone-discount", methods=["POST"])
def update_stone_discount():
    conn = sqlite3.connect("./database/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        stone_id = request.form["stone_id"]
        discount = request.form["discount"]

        apply_discount_to_stone(cursor, stone_id, discount)

        conn.commit()
        return redirect(url_for("inventory"))

    finally:
        conn.close()

# ---------------- INVENTORY DISCOUNT UPDATE ----------------
@app.route("/update-inventory-discount", methods=["POST"])
def update_inventory_discount():
    conn = sqlite3.connect("./database/app.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        delta = request.form.get("delta", "0")

        try:
            delta = float(delta)
        except:
            delta = 0
        
        cursor.execute("SELECT * FROM stones")
        stones = [dict(r) for r in cursor.fetchall()]

        for stone in stones:
            old = stone.get("rapaport_discount") or 0

            try:
                old = float(old)
            except:
                old = 0
            
            new_discount = old + delta

            cursor.execute("""UPDATE stones SET rapaport_discount = ? WHERE id = ?""", (new_discount, stone["id"]))

            cursor.execute("SELECT * FROM stones WHERE id = ?", (stone["id"]))
            updated_stone = dict(cursor.fetchone())
            recalculate_stone_price(cursor, updated_stone)
        
        conn.commit()
        return redirect(url_for("inventory"))

    finally:
        conn.close()

# ---------------- CORE DISCOUNT APPLY ----------------

def apply_discount_to_stone(cursor, stone_id, discount):
    cursor.execute("""
        UPDATE stones
        SET rapaport_discount = ?
        WHERE id = ?
    """, (discount, stone_id))

    cursor.execute("SELECT * FROM stones WHERE id = ?", (stone_id,))
    stone = cursor.fetchone()

    recalculate_stone_price(cursor, stone)

# ---------------- RAPAPORT PARSER ----------------

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

# ---------------- PRICE ENGINE ----------------
def recalculate_stone_price(cursor, stone):

    stone = dict(stone)

    try:
        fancy = stone.get("fancy_color") or ""

        if fancy.strip():
            set_null(cursor, stone["id"])
            return

        rap_shape = get_rapaport_shape(stone["shape"], fancy)

        if not rap_shape:
            set_null(cursor, stone["id"])
            return

        weight = float(stone["weight"])

        cursor.execute("""
            SELECT price_per_carat
            FROM rapaport_prices
            WHERE shape = ?
              AND clarity = ?
              AND color = ?
              AND ? BETWEEN min_weight AND max_weight
            ORDER BY price_date DESC
            LIMIT 1
        """, (
            rap_shape,
            stone["clarity"],
            stone["color_grade"],
            weight
        ))

        rap = cursor.fetchone()

        if not rap:
            set_null(cursor, stone["id"])
            return

        rap_price = float(rap["price_per_carat"])

        discount = stone.get("rapaport_discount")
        try:
            discount = float(discount) if discount not in (None, "", "None") else 0
        except:
            discount = 0

        final_ppc = round(rap_price * (1 - discount / 100), 2)
        total = round(final_ppc * weight, 2)

        cursor.execute("""
            UPDATE stones
            SET rapaport_price_per_carat = ?,
                price_per_carat = ?,
                total_price = ?
            WHERE id = ?
        """, (rap_price, final_ppc, total, stone["id"]))

    except Exception as e:
        print("PRICE ENGINE ERROR:", e)
        set_null(cursor, stone["id"])

# ---------------- FORCE CLEAR ----------------
def set_null(cursor, stone_id):
    cursor.execute("""
        UPDATE stones
        SET rapaport_price_per_carat = NULL,
            price_per_carat = NULL,
            total_price = NULL
        WHERE id = ?
    """, (stone_id,))

# ---------------- HELPERS ----------------

def get_rapaport_shape(shape, fancy_color):
    if fancy_color and fancy_color.strip():
        return None
    return "BR" if shape.lower() == "round" else "PS"

def get_size_from_weight(weight):
    weight = float(weight)

    ranges = [
        (0.01,0.03,"0.01+"), (0.04,0.07,"0.04+"),
        (0.08,0.14,"0.08+"), (0.15,0.17,"0.15+"),
        (0.18,0.22,"0.18+"), (0.23,0.29,"0.23+"),
        (0.30,0.39,"0.30+"), (0.40,0.44,"0.40+"),
        (0.45,0.49,"0.45+"), (0.50,0.57,"0.50+"),
        (0.58,0.69,"0.58+"), (0.70,0.77,"0.70+"),
        (0.78,0.89,"0.78+"), (0.90,0.94,"0.90+"),
        (0.95,0.99,"0.95+"), (1.00,1.19,"1.00+"),
        (1.20,1.49,"1.20+"), (1.50,1.99,"1.50+"),
        (2.00,2.99,"2.00+"), (3.00,3.99,"3.00+"),
        (4.00,4.99,"4.00+")
    ]

    for a,b,label in ranges:
        if a <= weight <= b:
            return label

    return f"{int(weight)}.00+"

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)