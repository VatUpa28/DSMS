from flask import Flask, request, render_template, redirect, url_for
from routes.inventory import inventory_bp
from routes.home import home_bp
from routes.add import add_stone_bp, add_stones_bp
#from routes.update import update_stone_discount_bp, update_inventory_discount_bp
from routes.upload_rapaport import upload_rapaport_bp
import sqlite3
import csv
import io

app = Flask(__name__)

app.register_blueprint(home_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(add_stone_bp)
app.register_blueprint(add_stones_bp)
#app.register_blueprint(update_stone_discount_bp)
#app.register_blueprint(update_inventory_discount_bp)
app.register_blueprint(upload_rapaport_bp)

if __name__ == "__main__":
    app.run(debug=True)
    