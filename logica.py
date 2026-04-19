from database import obtener_conexion
import math
import pymysql
from flask import request, jsonify
from motor_logica import calcular_distancia, validar_cupo_y_ruta

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
