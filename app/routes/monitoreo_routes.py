from flask import Blueprint, render_template, request, jsonify
from app.base_datos import GestorDB

monitoreo_bp = Blueprint('monitoreo', __name__)
db = GestorDB()


@monitoreo_bp.route('/monitoreo')
def index():
    return render_template('monitoreo.html')


@monitoreo_bp.route('/api/monitoreo/list', methods=['GET'])
def list_devices():
    devices = db.obtener_monitoreo_ups()
    return jsonify(devices)


@monitoreo_bp.route('/api/monitoreo/add', methods=['POST'])
def add_device():
    data = request.json
    if not data or 'ip' not in data:
        return jsonify({'error': 'Faltan datos (ip requerida)'}), 400

    # Asegurar que el protocolo se guarde
    if 'protocolo' not in data:
        data['protocolo'] = 'modbus'

    success = db.agregar_monitoreo_ups(data)
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'error': 'Error agregando dispositivo (posible duplicado)'}), 500


@monitoreo_bp.route('/api/monitoreo/delete/<int:id_device>', methods=['DELETE'])
def delete_device(id_device):
    db.eliminar_monitoreo_ups(id_device)
    return jsonify({'status': 'ok'})
