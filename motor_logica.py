import math


def calcular_distancia(lat1, lng1, lat2, lng2):
    if lat1 is None or lng1 is None or lat2 is None or lng2 is None:
        return float("inf")

    try:
        lat1 = float(lat1)
        lng1 = float(lng1)
        lat2 = float(lat2)
        lng2 = float(lng2)
    except (TypeError, ValueError):
        return float("inf")

    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def validar_cupo_y_ruta(solicitud_nueva, vehiculo_activo, margen_km=1.5):
    """
    Verifica si una solicitud puede unirse a un vehículo en movimiento.
    """
    # 1. Validar Espacio (Capacidad)
    asientos_necesarios = solicitud_nueva["asientos_pedidos"]
    # Si el usuario pidió 'asiento doble' por comodidad, asientos_necesarios será 2

    asientos_disponibles = (
        vehiculo_activo["capacidad_total"] - vehiculo_activo["asientos_ocupados"]
    )

    if asientos_necesarios > asientos_disponibles:
        return False, "Vehículo lleno o espacio insuficiente para tu preferencia."

    # 2. Validar Cercanía Geográfica
    distancia = calcular_distancia(
        solicitud_nueva["lat_inicio"],
        solicitud_nueva["lng_inicio"],
        vehiculo_activo["lat_actual"],
        vehiculo_activo["lng_actual"],
    )

    if distancia <= margen_km:
        # 3. Calcular Ahorro (Lógica de MoveG)
        # Si el vehículo ya lleva gente, el costo se divide proporcionalmente
        tarifa_base = 2.0  # Ejemplo: $2
        descuento = 0.40  # 40% de ahorro por ser "Ruta Compartida"
        precio_final = tarifa_base * (1 - descuento)

        return True, {
            "precio": precio_final,
            "distancia_recogida": round(distancia, 2),
            "mensaje": "¡Coincidencia encontrada! Ahorras un 40%.",
        }

    return False, "No hay rutas cercanas en este momento."
