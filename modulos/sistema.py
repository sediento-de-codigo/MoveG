from flask import Blueprint, send_from_directory

# Blueprint para cosas globales o de sistema
sistema_bp = Blueprint("sistema", __name__)


@sistema_bp.route("/sw.js")
def service_worker():
    # El archivo está en la raíz, por eso usamos '.'
    return send_from_directory(".", "sw.js")


# @sistema_bp.route("/robots.txt")
# def robots():
#     return send_from_directory(".", "robots.txt")
