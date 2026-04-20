# modulos/conductores.py


from flask import Blueprint, render_template, session, redirect, url_for
from utils import login_required
from flask import Blueprint
from database import obtener_conexion
from flask import request, jsonify

conductores_bp = Blueprint("conductores", __name__)


@conductores_bp.route("/panel_conductor", methods=["GET", "POST"])
@login_required  # <--- Solo los conductores pueden entrar aquí
def panel():

    # Validar que es conductor (¡Seguridad ante todo!)
    user_id = session.get("user_id")

    if "user_id" not in session:
        print("DEBUG: Acceso denegado, no hay user_id en sesión")
        return redirect(url_for("auth.login"))
    else:

        # Aquí irá tu lógica para listar solicitudes pendientes
        try:
            db = obtener_conexion()
            # <-- Verifica que este nombre sea igual al del paso 1
            # 2. CREAMOS EL CURSOR (¡Aquí está la clave!)
            with db.cursor() as cursor:
                # Ahora el cursor sí tiene el método .execute()
                sql = "SELECT * FROM conductores WHERE id = %s"
                cursor.execute(sql, (user_id,))
                conductor = cursor.fetchone()
            return render_template("panel_conductor.html", c=conductor)
        except Exception as e:
            return f"Error en la consulta: {e}"

        finally:
            # 4. Cerramos la conexión siempre
            if db:
                db.close()


@conductores_bp.route("/actualizar_estado", methods=["POST"])
def actualizar_estado():
    # Obtenemos los datos que envía JavaScript
    data = request.get_json()
    nuevo_estado = data.get("status")  # 'ON' o 'OFF'
    user_id = session.get("user_id")
    # SEGURIDAD: Solo el dueño del panel (o un admin) debería poder cambiar su estado
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401
    db = obtener_conexion()
    try:

        with db.cursor() as cursor:
            # 1. Consultar estado actual
            sql = "UPDATE conductores SET estado = %s WHERE id = %s"
            cursor.execute(sql, (nuevo_estado, user_id))
            return jsonify({"success": True, "message": "Estado actualizado"})

    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": "estado cambiado a:" + str(nuevo_estado)}
            ),
        )
    finally:
        if db:
            db.close()  # Asegura cerrar la conexión
