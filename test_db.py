import sys
import mysql.connector

print("--- INICIANDO PRUEBA DE CONEXIÓN ---")

try:
    config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "movilgroup",
    }
    print(f"Intentando conectar a {config['database']}...")

    conn = mysql.connector.connect(**config)

    if conn.is_connected():
        print("✅ ¡CONEXIÓN EXITOSA!")
        conn.close()
    else:
        print("❌ La conexión falló sin error específico.")

except mysql.connector.Error as err:
    print(f"❌ ERROR DE MYSQL: {err}")
except Exception as e:
    print(f"❌ OTRO ERROR: {e}")

print("--- FIN DEL SCRIPT ---")
