from flask import Blueprint, render_template, session, redirect, url_for
from utils import login_required

viajes_bp = Blueprint("viajes", __name__)


@viajes_bp.route("/panel_conductor")
def panel_conductor():
    # Validar que el usuario logueado sea el dueño del panel
    if "user_id" not in session or session["user_id"] != id:
        return (
            "<h1>Acceso denegado</h1><p>No tienes permiso para ver este panel.</p>",
            403,
        )
    db = None
    try:
        db = obtener_conexion()  # <-- Verifica que este nombre sea igual al del paso 1
        with db.cursor() as cursor:
            # Usamos id_conductor porque así suele llamarse la llave primaria
            sql = "SELECT * FROM conductores WHERE id = %s"
            cursor.execute(sql, (id,))
            conductor = cursor.fetchone()

        if conductor:
            return render_template("panel_conductor.html", c=conductor)
        else:
            return "<h1>Error: Conductor no encontrado en la base de datos.</h1>", 404
    except Exception as e:
        return f"Error en el panel: {str(e)}"
    finally:
        if db:
            db.close()
