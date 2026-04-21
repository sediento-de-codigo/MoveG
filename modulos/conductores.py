# modulos/conductores.py


from flask import Blueprint, render_template, session, redirect, url_for
from utils import login_required
from flask import Blueprint
from database import obtener_conexion
from flask import request, jsonify

conductores_bp = Blueprint("conductores", __name__)


@conductores_bp.route("/panel_conductor", methods=["GET", "POST"])
@login_required
def panel():
    print(">>> CANARIO: Entrando en panel()...")
    user_id = session.get("user_id")

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = None
    try:
        db = obtener_conexion()
        with db.cursor() as cursor:
            # 1. Obtenemos los datosl conductor
            sql_conductor = "SELECT * FROM conductores WHERE id = %s"
            cursor.execute(sql_conductor, (user_id,))
            conductor = cursor.fetchone()

            # 2. AQUÍ ESTABA EL VACÍO: Obtenemos las solicitudes
            # (Asegúrate de que tu tabla se llame 'solicitudes' o 'viajes')
            sql_solicitudes = (
                "SELECT * FROM solicitudes WHERE estado_viaje = 'pendiente'"
            )
            cursor.execute(sql_solicitudes)
            solicitudes = (
                cursor.fetchall()
            )  # Esto guarda todas las solicitudes en una lista

            # 3. Imprimimos para depurar (mira tu terminal tras recargar)
            print(f"DEBUG: Se encontraron {len(solicitudes)} solicitudes.")

        # 4. Enviamos AMBAS variables al HTML
        return render_template(
            "panel_conductor.html", c=conductor, solicitudes=solicitudes
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Error en la consulta: {e}"

    finally:
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


@conductores_bp.route("/panel_conductor")
def ver_solicitudes():
    conn = obtener_conexion()
    if not conn:
        return "Error de conexión a la BD"

    solicitudes = []  # Inicializamos la lista vacía por seguridad
    # --- AGREGA ESTO PARA DEPURAR ---
    with conn.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"DEBUG: ESTOY CONECTADO A LA BD: {db_name}")
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT solicitudes.*, usuarios.nombre 
                FROM solicitudes 
                LEFT JOIN usuarios ON solicitudes.usuario_id = usuarios.id 
                WHERE solicitudes.estado_viaje = 'pendiente'
         """
            # IMPORTANTE: Aquí agregamos la variable 'sql' para que se ejecute
        cursor.execute(sql)
        solicitudes = cursor.fetchall()

        # DEBUG: Imprime en tu terminal para confirmar qué está llegando
        print(f"DEBUG: Se han recuperado {len(solicitudes)} solicitudes.")
        for s in solicitudes:
            print(f"DEBUG: Solicitud encontrada: {s}")

    except Exception as e:
        print(f"❌ Error al ejecutar la consulta: {e}")
        # Aquí podrías retornar un mensaje de error o una página vacía

    finally:
        # El finally asegura que la conexión se cierre SIEMPRE,
        # incluso si la consulta falla. Esto es vital en servidores web.
        conn.close()

    return render_template("panel_conductor.html", solicitudes=solicitudes)
