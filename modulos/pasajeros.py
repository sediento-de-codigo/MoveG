from flask import Blueprint, render_template, session, redirect, url_for
from utils import login_required
from database import obtener_conexion

pasajeros_bp = Blueprint("pasajeros", __name__)


@pasajeros_bp.route("/panel")
@login_required
def panel():
    if "user_id" in session and session.get("user_rol") == "pasajero":
        # return f"<h1>Bienvenido al Panel de Pasajeros, {session['user_name']}</h1><a href='/logout'>Cerrar Sesión</a>"

        return render_template("panel_pasajero.html", nombre=session.get("user_name"))

    return redirect(url_for("auth.login"))
    return render_template("panel_pasajero.html")
