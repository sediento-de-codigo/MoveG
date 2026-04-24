# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# models.py
# Asegúrate de importar aquí la función que conecta a tu BD
from database import obtener_conexion


class Conductor:
    @staticmethod
    def actualizar_estado_bd(user_id, nuevo_estado):
        """
        Esta función encapsula toda la lógica de SQL.
        Devuelve True si tuvo éxito, False si hubo un error.
        """
        db = obtener_conexion()
        try:
            with db.cursor() as cursor:
                sql = "UPDATE conductores SET estado = %s WHERE id = %s"
                cursor.execute(sql, (nuevo_estado, user_id))
                db.commit()  # ¡Guardamos el cambio!
                return True
        except Exception as e:
            print(f"Error en la base de datos: {e}")
            return False
        finally:
            if db:
                db.close()


class Nodo(db.Model):
    __tablename__ = "nodos"
    id = db.Column(db.Integer, primary_key=True)
    nombre_parada = db.Column(db.String(100), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    sector = db.Column(db.String(50))
    # Relación hacia la tabla de asociación
    rutas_vinculadas = db.relationship("RutaNodo", back_populates="nodo")


class Ruta(db.Model):
    __tablename__ = "rutas"
    id = db.Column(db.Integer, primary_key=True)
    nombre_ruta = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    # Relación para acceder a los nodos ordenados
    nodos_vinculados = db.relationship(
        "RutaNodo", back_populates="ruta", order_by="RutaNodo.orden"
    )


class RutaNodo(db.Model):
    __tablename__ = "ruta_nodos"
    id = db.Column(db.Integer, primary_key=True)
    ruta_id = db.Column(db.Integer, db.ForeignKey("rutas.id"), nullable=False)
    nodo_id = db.Column(db.Integer, db.ForeignKey("nodos.id"), nullable=False)
    orden = db.Column(
        db.Integer, nullable=False
    )  # Define el orden en la ruta (1, 2, 3...)

    # Relaciones de vuelta
    ruta = db.relationship("Ruta", back_populates="nodos_vinculados")
    nodo = db.relationship("Nodo", back_populates="rutas_vinculadas")


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
