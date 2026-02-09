from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required

monitoreo_bp = Blueprint('monitoreo', __name__)


@monitoreo_bp.route('/monitoreo')
@login_required
def index():
    return render_template('monitoreo.html')


@monitoreo_bp.route('/api/monitoreo/list', methods=['GET'])
@login_required
def list_devices():
    db = current_app.db
    devices = db.obtener_monitoreo_ups()
    return jsonify(devices)


@monitoreo_bp.route('/api/monitoreo/add', methods=['POST'])
@login_required
def add_device():
    db = current_app.db
    data = request.json
    if not data or 'ip' not in data:
        return jsonify({'error': 'Faltan datos (ip requerida)'}), 400

    if 'protocolo' not in data:
        data['protocolo'] = 'modbus'

    success = db.agregar_monitoreo_ups(data)
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'error': 'Error agregando dispositivo (posible duplicado)'}), 500


@monitoreo_bp.route('/api/monitoreo/delete/<int:id_device>', methods=['DELETE'])
@login_required
def delete_device(id_device):
    db = current_app.db
    db.eliminar_monitoreo_ups(id_device)
    return jsonify({'status': 'ok'})
