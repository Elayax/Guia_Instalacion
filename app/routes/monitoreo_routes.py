import io
import csv
import subprocess
import logging
from flask import Blueprint, render_template, request, jsonify, current_app, Response
from flask_login import login_required
from app.permisos import permiso_requerido

logger = logging.getLogger(__name__)

monitoreo_bp = Blueprint('monitoreo', __name__)


# =========================================================================
# VISTAS HTML
# =========================================================================
@monitoreo_bp.route('/monitoreo')
@login_required
@permiso_requerido('scada')
def index():
    return render_template('monitoreo.html')


@monitoreo_bp.route('/topologia')
@login_required
@permiso_requerido('scada')
def topologia():
    return render_template('topologia.html')


# =========================================================================
# DISPOSITIVOS — CRUD
# =========================================================================
@monitoreo_bp.route('/api/monitoreo/list', methods=['GET'])
@login_required
@permiso_requerido('scada')
def list_devices():
    db = current_app.db
    devices = db.obtener_monitoreo_ups()
    return jsonify(devices)


@monitoreo_bp.route('/api/monitoreo/add', methods=['POST'])
@login_required
@permiso_requerido('scada')
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


@monitoreo_bp.route('/api/monitoreo/<int:id_device>', methods=['PUT'])
@login_required
@permiso_requerido('scada')
def update_device(id_device):
    db = current_app.db
    data = request.json
    if not data:
        return jsonify({'error': 'Sin datos'}), 400
    success = db.actualizar_dispositivo(id_device, data)
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'error': 'Error actualizando dispositivo'}), 500


@monitoreo_bp.route('/api/monitoreo/delete/<int:id_device>', methods=['DELETE'])
@login_required
@permiso_requerido('scada')
def delete_device(id_device):
    db = current_app.db
    db.eliminar_monitoreo_ups(id_device)
    return jsonify({'status': 'ok'})


# =========================================================================
# GRABACIÓN HISTÓRICA
# =========================================================================
@monitoreo_bp.route('/api/monitoreo/<int:id_device>/recording', methods=['POST'])
@login_required
@permiso_requerido('scada')
def toggle_recording(id_device):
    db = current_app.db
    data = request.json or {}
    recording = data.get('recording', False)
    interval = data.get('interval')
    db.actualizar_recording(id_device, recording, interval)
    return jsonify({'status': 'ok', 'recording': recording})


@monitoreo_bp.route('/api/monitoreo/<int:id_device>/history', methods=['GET'])
@login_required
@permiso_requerido('scada')
def get_history(id_device):
    db = current_app.db
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    limit = int(request.args.get('limit', 1000))
    readings = db.obtener_lecturas_ups(id_device, desde, hasta, min(limit, 10000))
    # Serializar timestamps
    for r in readings:
        if r.get('timestamp'):
            r['timestamp'] = r['timestamp'].isoformat()
    return jsonify(readings)


@monitoreo_bp.route('/api/monitoreo/<int:id_device>/history/csv', methods=['GET'])
@login_required
@permiso_requerido('scada')
def export_history_csv(id_device):
    db = current_app.db
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    limit = int(request.args.get('limit', 50000))
    readings = db.obtener_lecturas_ups(id_device, desde, hasta, min(limit, 50000))

    if not readings:
        return jsonify({'error': 'Sin datos para exportar'}), 404

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=readings[0].keys())
    writer.writeheader()
    for row in readings:
        # Serializar timestamps para CSV
        if row.get('timestamp'):
            row['timestamp'] = row['timestamp'].isoformat()
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=ups_{id_device}_history.csv'}
    )


# =========================================================================
# ALERTAS
# =========================================================================
@monitoreo_bp.route('/api/monitoreo/alerts', methods=['GET'])
@login_required
@permiso_requerido('scada')
def get_alerts():
    db = current_app.db
    device_id = request.args.get('device_id', type=int)
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    limit = int(request.args.get('limit', 100))
    alerts = db.obtener_alertas(device_id, active_only, min(limit, 500))
    for a in alerts:
        if a.get('timestamp'):
            a['timestamp'] = a['timestamp'].isoformat()
        if a.get('resolved_at'):
            a['resolved_at'] = a['resolved_at'].isoformat()
    return jsonify(alerts)


@monitoreo_bp.route('/api/monitoreo/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required
@permiso_requerido('scada')
def resolve_alert(alert_id):
    db = current_app.db
    db.resolver_alerta(alert_id)
    return jsonify({'status': 'ok'})


# =========================================================================
# SITIOS
# =========================================================================
@monitoreo_bp.route('/api/monitoreo/sites', methods=['GET'])
@login_required
@permiso_requerido('scada')
def get_sites():
    db = current_app.db
    sites = db.obtener_sitios()
    for s in sites:
        if s.get('created_at'):
            s['created_at'] = s['created_at'].isoformat()
    return jsonify(sites)


@monitoreo_bp.route('/api/monitoreo/sites', methods=['POST'])
@login_required
@permiso_requerido('scada')
def add_site():
    db = current_app.db
    data = request.json
    if not data or 'nombre' not in data or 'numero' not in data:
        return jsonify({'error': 'nombre y numero son requeridos'}), 400
    success = db.agregar_sitio(data)
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'error': 'Error agregando sitio (posible duplicado)'}), 500


@monitoreo_bp.route('/api/monitoreo/sites/<int:site_id>', methods=['PUT'])
@login_required
@permiso_requerido('scada')
def update_site(site_id):
    db = current_app.db
    data = request.json
    if not data:
        return jsonify({'error': 'Sin datos'}), 400
    success = db.actualizar_sitio(site_id, data)
    if success:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'error': 'Error actualizando sitio'}), 500


@monitoreo_bp.route('/api/monitoreo/sites/<int:site_id>', methods=['DELETE'])
@login_required
@permiso_requerido('scada')
def delete_site(site_id):
    db = current_app.db
    db.eliminar_sitio(site_id)
    return jsonify({'status': 'ok'})


# =========================================================================
# TOPOLOGÍA
# =========================================================================
@monitoreo_bp.route('/api/monitoreo/topology', methods=['GET'])
@login_required
@permiso_requerido('scada')
def get_topology():
    db = current_app.db
    topology = db.obtener_topologia()
    # Serializar timestamps
    for site in topology.get('sites', []):
        if site.get('created_at'):
            site['created_at'] = site['created_at'].isoformat()
        for dev in site.get('devices', []):
            if dev.get('last_seen'):
                dev['last_seen'] = dev['last_seen'].isoformat()
            if dev.get('fecha_registro'):
                dev['fecha_registro'] = dev['fecha_registro'].isoformat()
    for dev in topology.get('unassigned_devices', []):
        if dev.get('last_seen'):
            dev['last_seen'] = dev['last_seen'].isoformat()
        if dev.get('fecha_registro'):
            dev['fecha_registro'] = dev['fecha_registro'].isoformat()

    # Agregar info del servidor
    zt_status = _get_zerotier_status()
    topology['servidor'] = {
        'ip': '10.216.124.126',
        'zerotier': zt_status,
    }
    return jsonify(topology)


# =========================================================================
# DIAGNÓSTICO DE RED
# =========================================================================
@monitoreo_bp.route('/api/monitoreo/network-status', methods=['GET'])
@login_required
@permiso_requerido('scada')
def network_status():
    db = current_app.db

    # Estado ZeroTier
    zt_status = _get_zerotier_status()

    # Ping a routers de cada sitio
    sites = db.obtener_sitios()
    site_status = []
    for site in sites:
        ip = site.get('ip_zt_router')
        reachable = False
        if ip:
            reachable = _ping(ip)
        site_status.append({
            'id': site['id'],
            'nombre': site['nombre'],
            'numero': site['numero'],
            'ip_zt_router': ip,
            'reachable': reachable,
        })

    return jsonify({
        'zerotier': zt_status,
        'sites': site_status,
    })


# =========================================================================
# AUTO-DISCOVERY DE OIDs
# =========================================================================
@monitoreo_bp.route('/api/monitoreo/discover', methods=['POST'])
@login_required
@permiso_requerido('scada')
def discover_oids():
    data = request.json or {}
    ip = data.get('ip')
    port = int(data.get('port', 161))
    community = data.get('community', 'public')

    if not ip:
        return jsonify({'error': 'ip es requerida'}), 400

    try:
        from app.services.protocols.oid_discovery import OIDDiscoveryService
        discovery = OIDDiscoveryService()
        import asyncio
        result = asyncio.run(discovery.discover(ip, port, community))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error en discovery: {e}")
        return jsonify({'error': str(e)}), 500


# =========================================================================
# UTILIDADES INTERNAS
# =========================================================================
def _get_zerotier_status():
    """Obtiene estado de ZeroTier via CLI."""
    try:
        result = subprocess.run(
            ['sudo', 'zerotier-cli', 'info'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            return {
                'status': 'ONLINE' if 'ONLINE' in result.stdout else 'OFFLINE',
                'node_id': parts[2] if len(parts) > 2 else '',
                'version': parts[3] if len(parts) > 3 else '',
            }
    except Exception:
        pass
    return {'status': 'UNKNOWN', 'node_id': '', 'version': ''}


def _ping(ip, timeout=3):
    """Ping rápido a una IP. Retorna True si responde."""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(timeout), ip],
            capture_output=True, timeout=timeout + 2
        )
        return result.returncode == 0
    except Exception:
        return False
