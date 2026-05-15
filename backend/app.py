from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

allowed_fields = ["stock_number", "status", "shape", "weight", "size", "color_grade", "clarity", "cut_grade", "polish", "symmetry","fluorescence_strength", "fluorescence_color", "fancy_color", "fancy_intensity", "overtone", "measurements", "depth_percent", "table_percent","girdle", "culet", "crown_height", "crown_angle", "pavilion_depth", "pavilion_angle", "rapaport_price_per_carat", "rapaport_discount", "eye_clean","bgm", "black", "milky", "open_inclusions", "pair_number", "pair_stock_number", "pair_separable", "picture_link", "video_link"]

required_fields = ["stock_number", "status", "shape", "weight", "size", "color_grade", "clarity", "measurements"]

@app.route("/add-stone", methods=["POST"])
def add_stone():
    conn = None
    try:
        conn = sqlite3.connect("./database/app.db")
        cursor = conn.cursor()

        data = request.form

        if not data:
            return {"error": "No JSON provided"}, 400
        
        for field in required_fields:
            if field not in data:
                return {"error": f"{field} is required"}, 400
            
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not filtered_data:
            return {"error": "No valid fields provided"}, 400

        columns = ", ".join(filtered_data.keys())
        placeholders = ", ".join(["?"] * len(filtered_data))
        values = list(filtered_data.values())
        sql = f"INSERT INTO stones ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)

        conn.commit()
        return render_template("index.html")
    except Exception as e:
        return {"error": str(e)}, 400
    finally:
        if conn:
            conn.close()

# @app.route("add-stones", methods=["POST"])
# def add_stones():
#     conn = none
#     try:
#         conn.commit()
#     except Exception as e:
#         return {"error": str(e)}, 400


@app.route("/inventory", methods=["GET"])
def inventory():
    conn = None
    try:
        conn = sqlite3.connect("./database/app.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stones")
        rows = cursor.fetchall()

        inventory_data = [dict(row) for row in rows]

        return render_template("inventory.html", stones=inventory_data)

    except Exception as e:
        return {"error": str(e)}, 400

    finally:
        if conn:
            conn.close()

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)