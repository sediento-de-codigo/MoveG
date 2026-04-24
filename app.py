import pymysql
from flask import send_from_directory
import os
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
import math
from datetime import datetime
from modulos.auth import auth_bp
from modulos.conductores import conductores_bp
from modulos.pasajeros import pasajeros_bp
from database import obtener_conexion
from modulos.sistema import sistema_bp
from modulos.viajes import viajes_bp  # Importación
from utils import login_required
from modulos.main import main_bp
from models import db
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:" "@localhost/movilgroup"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.register_blueprint(auth_bp)
app.register_blueprint(conductores_bp)
app.register_blueprint(pasajeros_bp)
app.register_blueprint(sistema_bp)
app.register_blueprint(viajes_bp)
app.register_blueprint(main_bp)
from werkzeug.utils import secure_filename

# Aquí conectas 'db' con tu 'app'
db.init_app(app)


with app.app_context():
    print("\n--- MAPA DE RUTAS ACTUAL ---")
    for rule in app.url_map.iter_rules():
        print(f"Ruta: {rule.rule:30} | Endpoint: {rule.endpoint}")
    print("----------------------------\n")
# app.py


app.secret_key = "medina"
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
from modulos.conductores import conductores_bp

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return "<h1>404</h1><p>La ruta que buscas no existe en MovilGroup.</p>", 404


from motor_logica import validar_cupo_y_ruta  # Importamos el "cerebro"


@app.route("/buscar_viaje", methods=["POST"])
def buscar_viaje():
    datos = request.json
    # Coordenadas que envía el celular del pasajero por USB
    lat_usuario = datos.get("lat")
    lng_usuario = datos.get("lng")
    asientos_pedidos = datos.get("asientos", 1)

    # 1. Define el radio en kilómetros (ejemplo: 10km para ser más flexible en Los Guayos)
    RADIO_MAXIMO_KM = 10.0

    solicitud = {
        "lat_inicio": lat_usuario,
        "lng_inicio": lng_usuario,
        "asientos_pedidos": asientos_pedidos,
    }

    conexion = obtener_conexion()
    if not conexion:
        return jsonify({"error": "Error de conexión"}), 500

    try:
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        # Buscamos vehículos activos (Esto simula los que están en ruta)
        # En una fase real, aquí filtraríamos por 'estatus = en_ruta'
        cursor.execute("SELECT * FROM vehiculos WHERE estatus = 'activo'")
        vehiculos = cursor.fetchall()

        coincidencias = []

        for v in vehiculos:
            # Simulamos datos de ruta activa (esto vendría de otra tabla o de la RAM)
            # Por ahora, usamos una ubicación fija de prueba
            v["lat_actual"] = 10.1870  # Ejemplo: Cerca de Los Guayos
            v["lng_actual"] = -67.9390
            v["asientos_ocupados"] = 4  # Simulación de carga actual
            distancia = calcular_distancia(
                lat_usuario, lng_usuario, v["lat_actual"], v["lng_actual"]
            )

            if distancia <= RADIO_MAXIMO_KM:
                v["distancia_km"] = round(distancia, 2)
                coincidencias.append(v)

        coincidencias.sort(key=lambda x: x["distancia_km"])

        for v in coincidencias:
            exito, resultado = validar_cupo_y_ruta(solicitud, v)
            if exito:
                return jsonify(
                    {
                        "estado": "coincidencia_encontrada",
                        "vehiculo_id": v["id"],
                        "modelo": v.get("modelo"),
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


@app.route("/api/obtener_solicitudes")
def obtener_solicitudes():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # IMPORTANTE: Usamos los nombres de tu tabla 'solicitudes'
        query = """
            SELECT s.id, u.nombre as pasajero, s.tipo_servicio, 
                   s.direccion_destino, s.precio_estimado
            FROM solicitudes s
            JOIN usuarios u ON s.usuario_id = u.id
            WHERE s.estatus = 'pendiente'
        """
        cursor.execute(query)
        return jsonify(cursor.fetchall())
    finally:
        conexion.close()


@app.route("/crear_solicitud", methods=["POST"])
def crear_solicitud():
    # 1. Seguridad: Verificar que el usuario esté logueado
    if "user_id" not in session:
        return redirect(url_for("login_pasajero"))

    # 2. Captura de datos del formulario (names del HTML)
    usuario_id = session["user_id"]
    direccion_destino = request.form.get("direccion_destino")
    cantidad_asientos = request.form.get("cantidad_asientos", 1)
    precio_oferta = request.form.get("precio_estimado")

    # Valores técnicos por defecto (puedes hacerlos dinámicos luego con el mapa)
    lat_inicio = 10.1880
    lng_inicio = -67.9400
    tipo_servicio = "Express"

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # 3. Query de Inserción
        # El estatus siempre empieza en 'pendiente'
        query = """
            INSERT INTO solicitudes 
            (usuario_id, tipo_servicio, cantidad_asientos, lat_inicio, lng_inicio, 
             direccion_destino, precio_estimado, estatus) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendiente')
        """

        valores = (
            usuario_id,
            tipo_servicio,
            cantidad_asientos,
            lat_inicio,
            lng_inicio,
            direccion_destino,
            precio_oferta,
        )

        cursor.execute(query, valores)
        conexion.commit()  # ¡Importante para guardar cambios!

        print(f"✅ Nueva solicitud creada por el usuario {usuario_id}")

    except Exception as e:
        print(f"❌ Error en DB: {e}")
        return "Error interno del servidor", 500
    finally:
        conexion.close()

    # 4. Redirigir de vuelta al panel para esperar al conductor
    return redirect(url_for("panel_pasajero"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
