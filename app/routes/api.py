from flask import Blueprint, json
from app.base_datos import GestorDB
from . import api_bp

db = GestorDB()

# --- API: BUSCAR PEDIDO ---
@api_bp.route('/api/buscar-pedido/<pedido>')
def buscar_pedido(pedido):
    proyecto = db.obtener_proyecto_por_pedido(pedido)
    if proyecto:
        return json.dumps(dict(proyecto))
    return json.dumps({}), 404

# --- API: OBTENER SUCURSALES ---
@api_bp.route('/api/sucursales/<cliente>')
def get_sucursales(cliente):
    sucursales = db.obtener_sucursales_por_cliente(cliente)
    return json.dumps(sucursales)

# --- API: DETALLES UPS ---
@api_bp.route('/api/ups/<int:id_ups>')
def get_ups_details(id_ups):
    ups = db.obtener_ups_id(id_ups)
    if ups:
        return json.dumps(dict(ups))
    return json.dumps({}), 404

# --- API: DETALLES BATERIAS ---
@api_bp.route('/api/bateria/<int:id_bat>')
def get_bateria_details(id_bat):
    bat = db.obtener_bateria_id(id_bat)
    if bat:
        return json.dumps(bat)
    return json.dumps({}), 404

@api_bp.route('/api/bateria/<int:id_bat>/curvas')
def get_bateria_curvas(id_bat):
    curvas = db.obtener_curvas_por_bateria(id_bat)
    return json.dumps(curvas)

# --- API: TIPOS DE VENTILACION ---
@api_bp.route('/api/tipos-ventilacion')
def get_tipos_ventilacion():
    tipos = db.obtener_tipos_ventilacion()
    return json.dumps(tipos)
