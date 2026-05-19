from flask import Blueprint, render_template, redirect, url_for
from routes.inventory import inventory_bp

home_bp = Blueprint("home", __name__)

home_bp.register_blueprint(inventory_bp)

@home_bp.route("/")
def home():
    return redirect(url_for("inventory.inventory"))