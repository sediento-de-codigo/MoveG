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
