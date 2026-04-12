import os
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from database import obtener_conexion
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "medina"
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/")
def index():
    # 1. Usamos .get() para evitar el KeyError si la llave no existe
    user_id = session.get("user_id")
    rol = session.get("rol")
    # Si ya sabemos quién es, lo mandamos a su lugar
    if "user_id" and rol:
        if "rol" == "conductor":
            return redirect(url_for("panel_conductor", id=session["user_id"]))
        else:
            return redirect(url_for("panel_pasajero", id=session["user_id"]))

    # Si no hay sesión, mostramos el selector de opciones
    return render_template("index.html")


# from flask import session  # <--- Importante añadir este import
# Asegúrate de que tu función de registro_conductor esté dentro del bloque de código de Flask (dentro del app.py) y que el import de session esté presente al inicio del archivo. Esto permitirá que puedas usar session para guardar la información del usuario después de registrarlo exitosamente.


@app.route("/registro_conductor", methods=["GET", "POST"])
def registro_conductor():
    if request.method == "POST":
        try:
            # 1. Captura de datos (con valores por defecto para evitar NoneType Error)
            nombre = request.form.get("nombre_cople", "")
            tel = request.form.get("telefono", "")
            anio = request.form.get("aniovan", "0")

            # Limpieza de placa (Evita el error .upper() de las imágenes anteriores)
            placa_raw = request.form.get("placa_vehiculo", "").upper().replace(" ", "")
            placa = placa_raw.upper().replace(" ", "")
            # 2. Fecha actual para la columna 'fecha_registro'
            fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 2. Procesamiento de Imágenes
            rutas_fotos = {}
            campos_fotos = [
                "foto_rostro",
                "foto_vehiculo",
                "foto_cedula",
                "foto_licencia",
            ]

            for campo in campos_fotos:
                archivo = request.files.get(campo)
                if archivo and archivo.filename != "":
                    filename = secure_filename(f"{placa}_{campo}.jpg")
                    archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    rutas_fotos[campo] = filename
                else:
                    rutas_fotos[campo] = None  # O una imagen por defecto

            # 3. Inserción en Base de Datos
            db = obtener_conexion()
            cursor = db.cursor()

            sql = """INSERT INTO conductores 
                     (nombre_completo,correo,rol foto_rostro, foto_vehiculo, foto_cedula, foto_licencia, 
                      aniovan, telefono, placa_vehiculo, estado, fecha_registro) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            valores = (
                nombre,
                rutas_fotos["foto_rostro"],
                rutas_fotos["foto_vehiculo"],
                rutas_fotos["foto_cedula"],
                rutas_fotos["foto_licencia"],
                anio,
                tel,
                placa,
                "desconectado",
                fecha_registro,
            )

            cursor.execute(sql, valores)
            nuevo_id = cursor.lastrowid
            # --- AQUÍ VA EL GUARDADO DE SESIÓN ---
            session["user_id"] = nuevo_id
            session["rol"] = "conductor"
            # -------------------------------------

            print(f"✅ Registro exitoso. ID: {nuevo_id}")
            return redirect(url_for("panel_conductor", id=nuevo_id))

        except Exception as e:
            # print(f"❌ ERROR CRÍTICO: {e}")
            # Si el error es por duplicado (código 1062)
            if "1062" in str(e):
                return (
                    "<h1>Error: Esta placa ya está registrada.</h1><p>Por favor, verifica los datos o contacta a soporte.</p><a href='/registro_conductor'>Volver</a>",
                    400,
                )

            print(f"❌ ERROR: {e}")
            return f"Error en el servidor: {e}", 500
        finally:

            # Si la conexión se llegó a abrir, la cerramos aquí
            if db:
                db.close()
                print("🔌 Conexión a BD cerrada correctamente.")

    # Si es GET, simplemente muestra el formulario
    return render_template("registro_conductor.html")


@app.route("/panel_conductor/<int:id>")
def panel_conductor(id):
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


@app.route("/cambiar_estado/<int:id>", methods=["GET", "POST"])
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

        if request.method == "POST":
            return jsonify({"error": "Conductor no encontrado"}), 404
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
        return redirect(url_for("panel_conductor.html", id=id))


@app.route("/registro_pasajero", methods=["GET", "POST"])
def registro_pasajero():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        email = request.form.get("correo")
        clave = request.form.get("clave")
        db = None
        if not clave:
            return "Error: La contraseña es obligatoria", 400
        try:
            db = obtener_conexion()
            with db.cursor() as cursor:
                sql = """INSERT INTO pasajeros (nombre_completo, telefono, correo, password_hash) 
                         VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (nombre, telefono, email, clave))
                nuevo_id = cursor.lastrowid

                # --- ACTIVAMOS LA SESIÓN ---
                session["user_id"] = nuevo_id
                session["rol"] = "pasajero"

            print(f"✅ Pasajero registrado con ID: {nuevo_id}")
            # Redirigimos a un panel de pasajeros (que crearemos luego)
            return redirect(url_for("panel_pasajero", id=nuevo_id))

        except Exception as e:
            if "1062" in str(e):
                return "<h1>Error: El correo ya está registrado.</h1>", 400
            return f"Error en el registro: {e}", 500
        finally:
            if db:
                db.close()

    return render_template("registro_pasajero.html")


@app.route("/logout")
def logout():
    session.clear()  # Borra toda la información de la sesión actual
    return redirect(url_for("index"))  # Te manda de vuelta al selector de roles


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return "<h1>404</h1><p>La ruta que buscas no existe en MovilGroup.</p>", 404


@app.route("/login_conductor", methods=["GET", "POST"])
def login_conductor():
    if request.method == "POST":
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")

        db = obtener_conexion()
        try:
            with db.cursor() as cursor:
                # Buscamos si existe un conductor con ese correo y teléfono
                sql = "SELECT id, nombre_completo, rol FROM conductores WHERE correo = %s AND telefono = %s"
                cursor.execute(sql, (correo, telefono))
                usuario = cursor.fetchone()

                if usuario:
                    # ✅ CREDENCIALES CORRECTAS
                    session["user_id"] = usuario["id"]
                    session["nombre"] = usuario["nombre_completo"]
                    session["rol"] = usuario.get(
                        "rol", "conductor"
                    )  # Asegura que el rol se guarde en la sesión
                    print(
                        f"✅ Login exitoso: {usuario['nombre_completo']} (ID: {usuario['id']})"
                    )
                    return redirect(url_for("panel_conductor", id=usuario["id"]))
                else:
                    # ❌ DATOS INCORRECTOS
                    print("⚠️ Intento de login fallido: Credenciales no coinciden.")
                    return "<h1>Error: Datos no encontrados</h1><p>Verifica tu correo y teléfono.</p><a href='/login_conductor'>Volver a intentar</a>"

        except Exception as e:
            # print(f"❌ Error en Login: {e}")
            # return "Error interno en el servidor", 500

            print(
                f"DEBUG: El error exacto es: {e}"
            )  # <-- Esto saldrá en la terminal negra
            return (
                f"Error técnico: {e}",
                500,
            )  # <-- Esto saldrá en el navegador para que lo leas
        finally:
            if db:
                db.close()

    return render_template("login_conductor.html")


@app.route("/login_pasajero", methods=["GET", "POST"])
def login_pasajero():
    if request.method == "POST":
        correo = request.form["correo"]
        clave = request.form["clave"]

        db = obtener_conexion()
        # Usamos dictionary=True para manejar los resultados como un objeto de Python
        cursor = db.cursor()

        query = "SELECT * FROM pasajeros WHERE correo = %s AND password_hash = %s"
        cursor.execute(query, (correo, clave))
        pasajero = cursor.fetchone()

        db.close()

        if pasajero:
            # Creamos la sesión del usuario
            session["user_id"] = pasajero["id"]
            session["user_name"] = pasajero["nombre_completo"]
            session["user_role"] = "pasajero"

            return redirect(url_for("panel_pasajero"))
        else:
            return render_template(
                "login_pasajero.html", error="Correo o clave incorrectos"
            )

    return render_template("login_pasajero.html")


@app.route("/panel_pasajero")
def panel_pasajero():
    if "user_id" in session and session.get("user_role") == "pasajero":
        return f"<h1>Bienvenido al Panel de Pasajeros, {session['user_name']}</h1><a href='/logout'>Cerrar Sesión</a>"

    return redirect(url_for("registro_pasajero"))


from flask import Flask, request, jsonify
from database import conectar_db
from motor_logica import validar_cupo_y_ruta  # Importamos el "cerebro"


@app.route("/buscar_viaje", methods=["POST"])
def buscar_viaje():
    datos = request.json
    # Coordenadas que envía el celular del pasajero por USB
    lat_usuario = datos.get("lat")
    lng_usuario = datos.get("lng")
    asientos_pedidos = datos.get("asientos", 1)

    solicitud = {
        "lat_inicio": lat_usuario,
        "lng_inicio": lng_usuario,
        "asientos_pedidos": asientos_pedidos,
    }

    conexion = conectar_db()
    if not conexion:
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conexion.cursor(dictionary=True)
        # Buscamos vehículos activos (Esto simula los que están en ruta)
        # En una fase real, aquí filtraríamos por 'estatus = en_ruta'
        cursor.execute("SELECT * FROM vehiculos")
        vehiculos_candidatos = cursor.fetchall()

        for v in vehiculos_candidatos:
            # Simulamos datos de ruta activa (esto vendría de otra tabla o de la RAM)
            # Por ahora, usamos una ubicación fija de prueba
            v["lat_actual"] = 10.1870  # Ejemplo: Cerca de Los Guayos
            v["lng_actual"] = -67.9390
            v["asientos_ocupados"] = 4  # Simulación de carga actual

            exito, resultado = validar_cupo_y_ruta(solicitud, v)

            if exito:
                return jsonify(
                    {
                        "estado": "coincidencia_encontrada",
                        "vehiculo_id": v["id"],
                        "modelo": v["modelo"],
                        "precio_ahorro": resultado["precio"],
                        "distancia_km": resultado["distancia_recogida"],
                        "mensaje": resultado["mensaje"],
                    }
                )

        return jsonify(
            {
                "estado": "no_hay_rutas",
                "mensaje": "Por ahora no hay rutas cerca, ¿deseas un viaje Express?",
            }
        )

    finally:
        conexion.close()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
