from flask import json, current_app
from flask_login import login_required
from . import api_bp


@api_bp.route('/api/buscar-pedido/<pedido>')
@login_required
def buscar_pedido(pedido):
    db = current_app.db
    proyecto = db.obtener_proyecto_por_pedido(pedido)
    if proyecto:
        return json.dumps(dict(proyecto))
    return json.dumps({}), 404


@api_bp.route('/api/sucursales/<cliente>')
@login_required
def get_sucursales(cliente):
    db = current_app.db
    sucursales = db.obtener_sucursales_por_cliente(cliente)
    return json.dumps(sucursales)


@api_bp.route('/api/ups/<int:id_ups>')
@login_required
def get_ups_details(id_ups):
    db = current_app.db
    ups = db.obtener_ups_id(id_ups)
    if ups:
        return json.dumps(dict(ups))
    return json.dumps({}), 404


@api_bp.route('/api/bateria/<int:id_bat>')
@login_required
def get_bateria_details(id_bat):
    db = current_app.db
    bat = db.obtener_bateria_id(id_bat)
    if bat:
        return json.dumps(bat)
    return json.dumps({}), 404


@api_bp.route('/api/bateria/<int:id_bat>/curvas')
@login_required
def get_bateria_curvas(id_bat):
    db = current_app.db
    curvas = db.obtener_curvas_por_bateria(id_bat)
    return json.dumps(curvas)


@api_bp.route('/api/tipos-ventilacion')
@login_required
def get_tipos_ventilacion():
    db = current_app.db
    tipos = db.obtener_tipos_ventilacion()
    return json.dumps(tipos)
