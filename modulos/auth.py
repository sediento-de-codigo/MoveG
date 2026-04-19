import os
from datetime import datetime
from flask import (
    Blueprint,
    app,
    flash,
    render_template,
    request,
    session,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename
from utils import login_required
from flask import render_template, session
from database import obtener_conexion
from flask import send_from_directory

# Definimos el Blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro_pasajero", methods=["GET", "POST"])
def registro_pasajero():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        correo = request.form.get("email")
        clave = request.form.get("clave")
        db = None
        try:
            db = obtener_conexion()
            with db.cursor() as cursor:
                sql = "INSERT INTO pasajeros (nombre_completo, telefono, correo, password_hash) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (nombre, telefono, correo, clave))
                db.commit()
                session["user_id"] = cursor.lastrowid
                session["rol"] = "pasajero"
            return redirect(url_for("viajes.panel_pasajero"))
        finally:
            if db:
                db.close()
    return render_template("registro_pasajero.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        correo = request.form.get("correo")
        clave = request.form.get("clave")
        # --- DEBUG: IMPRIME ESTO EN LA CONSOLA ---
        print(
            f"DEBUG: Intentando autenticar | Correo recibido: '{correo}' | Clave recibida: '{clave}'"
        )
        db = obtener_conexion()
        cursor = db.cursor()

        sql = "SELECT * FROM conductores WHERE correo = %s AND telefono= %s"
        cursor.execute(sql, (correo, clave))
        usuario = cursor.fetchone()
        db.close()

        if usuario:
            print(
                f"DEBUG: ¡Usuario encontrado en DB! ID: {usuario['id']}"
            )  # Confirmación
            session["user_id"] = usuario["id"]
            session["user_name"] = usuario["nombre_completo"]

            return redirect(url_for("conductores.panel"))
        else:
            print(
                "DEBUG: ¡ALERTA! El usuario no existe en la base de datos o la clave es incorrecta."
            )
        flash("Credenciales incorrectas")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/registro_conductor", methods=["GET", "POST"])
def registro_conductor():
    datos_conductor = None
    if request.method == "POST":
        try:
            # 1. Captura de datos (con valores por defecto para evitar NoneType Error)
            nombre = request.form.get("nombre_completo", "")
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
                     (nombre_completo,correo,rol, foto_rostro, foto_vehiculo, foto_cedula, foto_licencia,
                      aniovan, telefono, placa_vehiculo, estado, fecha_registro)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

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
            db.close()
            # CORRECCIÓN DE BUILDERROR: Apuntamos al endpoint correcto del blueprint

            print(f"✅ Registro exitoso. ID: {nuevo_id}")
            return redirect(url_for("conductores.panel", id=nuevo_id))

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
    return render_template("panel_conductor.html", c=datos_conductor)
