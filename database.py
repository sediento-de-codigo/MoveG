import pymysql

# Configuramos los datos una sola vez
CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "movilgroup",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,  # Esto te ahorra el db.commit() en cada insert/update
}


def obtener_conexion():

    try:
        return pymysql.connect(**CONFIG)
    except pymysql.MySQLError as e:
        print(f"❌ Error de conexión: {e}")
        return None


# database.py (Fragmento para el modelo de Solicitud)


class Solicitud:
    def __init__(self, usuario_id, tipo_servicio, asientos, origen, destino):
        self.usuario_id = usuario_id
        self.tipo_servicio = tipo_servicio  # 'Express' o 'Nodo'
        self.asientos = asientos  # Por si paga 2 asientos
        self.origen = origen  # JSON o Tupla (lat, lng)
        self.destino = destino  # Nodo de llegada
        self.estatus = "pendiente"
        self.precio = self.calcular_precio_base()

    def calcular_precio_base(self):
        # Aquí irá tu lógica de TSU:
        # Si es Express -> Precio Full
        # Si es Nodo -> Aplicar descuento de grupo
        pass
