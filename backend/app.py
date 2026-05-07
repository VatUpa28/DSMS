from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/add-stone", methods=["POST"])
def add_stone():
    conn = sqlite3.connect("./database/app.db")
    cursor = conn.cursor()

    data = request.get_json()

    if not data:
        return "No JSON provided"
    
    allowed_fields = ["stock_number", "status", "shape", "weight", "size", "color", "clarity", "cut_grade", "polish", "symmetry","fluorescence_strength", "fluorescence_color", "fancy_color", "fancy_intensity", "overtone", "measurements", "depth_percent", "table_percent","girdle", "culet", "crown_height", "crown_angle", "pavilion_depth", "pavilion_angle", "rapnet_price_per_carat", "rapnet_discount", "eye_clean","bgm", "black", "milky", "open_inclusions", "pair_number", "pair_stock_number", "pair_separable", "picture_link", "video_link"]

    required_fields = ["stock_number", "shape", "weight", "size", "color", "clarity", "measurements"]
    
    for field in required_fields:
        if field not in data:
            return {"error": f"{field} is required"}, 400
        
    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

    columns = ", ".join(filtered_data.keys())
    placeholders = ", ".join(["?"] * len(filtered_data))
    values = list(filtered_data.values())
    sql = f"INSERT INTO stones ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, values)

    conn.commit()
    conn.close()
    return {"message": "Stone added"}, 201

if __name__ == "__main__":
    app.run(debug=True)