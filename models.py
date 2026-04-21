# models.py


class Solicitud:
    def __init__(self, usuario_id, tipo_servicio, asientos, origen, destino):
        self.usuario_id = usuario_id
        self.tipo_servicio = tipo_servicio  # 'Express' o 'Nodo'
        self.asientos = asientos
        self.origen = origen
        self.destino = destino
        self.estatus = "pendiente"
        self.precio = self.calcular_precio_base()

    def calcular_precio_base(self):
        # Tu lógica de TSU aquí
        precio_base = 10  # Ejemplo
        if self.tipo_servicio == "Nodo":
            return precio_base * 0.8  # 20% descuento
        return precio_base
