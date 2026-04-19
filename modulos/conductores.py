# modulos/conductores.py


from flask import Blueprint, render_template, session, redirect, url_for
from utils import login_required
from flask import Blueprint
from database import obtener_conexion

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


@conductores_bp.route("/cambiar_estado/<int:id>", methods=["GET", "POST"])
def cambiar_estado(id):
    # SEGURIDAD: Solo el dueño del panel (o un admin) debería poder cambiar su estado
    if "user_id" not in session or session.get("user_id") != id:
        return jsonify({"error": "No autorizado"}), 403
    db = None
    nuevo_estado = None
    try:
        db = obtener_conexion()
        with db.cursor() as cursor:
            # 1. Consultar estado actual
            cursor.execute("SELECT estado FROM conductores WHERE id = %s", (id,))
            conductor = cursor.fetchone()
            if not conductor:
                return jsonify({"error": "Conductor no encontrado"}), 404
        # 2. Lógica de conmutación (Toggle)
        estado_actual = str(conductor["estado"]).strip().lower()
        nuevo_estado = (
            "conectado" if estado_actual == "desconectado" else "desconectado"
        )

        print(f"DEBUG: Cambiando ID {id} de [{estado_actual}] a [{nuevo_estado}]")

        # 3. Actualizar en la base de datos
        cursor.execute(
            "UPDATE conductores SET estado = %s WHERE id = %s", (nuevo_estado, id)
        )

    except Exception as e:
        print(f"❌ Error al cambiar estado: {e}")
        if db:
            db.rollback()  # Cancela si hay error
        if request.method == "POST":
            return jsonify({"error": str(e)}), 500
    finally:
        if db:
            db.close()  # Asegura cerrar la conexión

    if request.method == "POST":
        return jsonify({"estado": nuevo_estado})
    else:
        # 4. Redirigir al panel (esto forzará a la página a leer el nuevo valor)
        return redirect(url_for("panel_conductor", id=id))
