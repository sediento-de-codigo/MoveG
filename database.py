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
