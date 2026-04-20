from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # Obtenemos el tipo de usuario marcado en la sesión
    tipo = session.get("tipo_usuario")
    user_id = session.get("user_id")

    # Si hay un usuario logueado
    if user_id:
        if tipo == "conductor":
            return redirect(url_for("conductores.panel"))
        else:
            return redirect(url_for("viajes.panel_conductor"))  # O la ruta de pasajeros

    return render_template("index.html")
