"""
Rutas de Diagnóstico de Red y UPS
Herramientas integradas para probar conectividad y protocolos
"""

from flask import Blueprint, render_template, request, jsonify
import asyncio
import socket
import subprocess
import platform
import re
from datetime import datetime

diagnostic_bp = Blueprint('diagnostic', __name__)


@diagnostic_bp.route('/diagnostico')
def index():
    """Página principal de diagnóstico"""
    return render_template('diagnostico.html')


@diagnostic_bp.route('/api/diagnostic/ping', methods=['POST'])
def test_ping():
    """Test de ping a una IP"""
    data = request.json
    ip = data.get('ip', '')
    
    if not ip:
        return jsonify({'error': 'IP requerida'}), 400
    
    try:
        # Determinar comando según OS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '4', ip]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        return jsonify({
            'success': success,
            'output': output,
            'ip': ip
        })
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'output': f'Timeout: No se recibió respuesta de {ip} en 10 segundos',
            'ip': ip
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'Error: {str(e)}',
            'ip': ip
        })


@diagnostic_bp.route('/api/diagnostic/port', methods=['POST'])
def test_port():
    """Test de conectividad a un puerto específico"""
    data = request.json
    ip = data.get('ip', '')
    port = data.get('port', 0)
    
    if not ip or not port:
        return jsonify({'error': 'IP y puerto requeridos'}), 400
    
    try:
        # Crear socket con timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        
        start_time = datetime.now()
        result = sock.connect_ex((ip, int(port)))
        end_time = datetime.now()
        
        sock.close()
        
        elapsed_ms = (end_time - start_time).total_seconds() * 1000
        
        if result == 0:
            return jsonify({
                'success': True,
                'output': f'✅ Puerto {port} ABIERTO en {ip}\nTiempo de respuesta: {elapsed_ms:.2f}ms',
                'ip': ip,
                'port': port,
                'open': True,
                'elapsed_ms': round(elapsed_ms, 2)
            })
        else:
            return jsonify({
                'success': False,
                'output': f'❌ Puerto {port} CERRADO o FILTRADO en {ip}\nError code: {result}',
                'ip': ip,
                'port': port,
                'open': False
            })
            
    except socket.timeout:
        return jsonify({
            'success': False,
            'output': f'⏱️ Timeout: Puerto {port} no responde en {ip}',
            'ip': ip,
            'port': port,
            'open': False
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'❌ Error: {str(e)}',
            'ip': ip,
            'port': port
        })


@diagnostic_bp.route('/api/diagnostic/snmp', methods=['POST'])
def test_snmp():
    """Test de conexión SNMP"""
    data = request.json
    ip = data.get('ip', '')
    community = data.get('community', 'public')
    port = data.get('port', 161)
    
    if not ip:
        return jsonify({'error': 'IP requerida'}), 400
    
    try:
        # Importar el cliente SNMP
        from app.services.protocols.snmp_client import SNMPClient
        
        async def run_test():
            client = SNMPClient(community=community, port=int(port))
            return await client.get_ups_data(ip)
        
        # Ejecutar test async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_test())
        loop.close()
        
        if result:
            # Formatear resultado para mostrar
            output_lines = [
                f'✅ CONEXIÓN SNMP EXITOSA a {ip}:{port}',
                f'Community: {community}',
                '',
                '📊 Datos obtenidos:',
                '─' * 50
            ]
            
            # Agrupar por categorías
            categories = {
                'Entrada': ['input_voltage', 'input_frequency'],
                'Salida': ['output_voltage', 'output_current', 'output_load', 'output_frequency'],
                'Batería': ['battery_voltage', 'battery_capacity', 'battery_status', 'battery_runtime'],
                'Potencia': ['active_power', 'apparent_power', 'power_factor'],
                'Estado': ['power_source', 'temperature']
            }
            
            for category, keys in categories.items():
                found_data = False
                for key in keys:
                    # Buscar con sufijos L1, L2, L3
                    for suffix in ['', '_l1', '_l2', '_l3']:
                        full_key = f'{key}{suffix}'
                        if full_key in result and result[full_key] is not None:
                            if not found_data:
                                output_lines.append(f'\n{category}:')
                                found_data = True
                            output_lines.append(f'  {full_key:25s}: {result[full_key]}')
            
            return jsonify({
                'success': True,
                'output': '\n'.join(output_lines),
                'data': result,
                'ip': ip,
                'port': port,
                'community': community
            })
        else:
            return jsonify({
                'success': False,
                'output': f'❌ Sin respuesta SNMP de {ip}:{port}\n\nPosibles causas:\n- SNMP no habilitado en el dispositivo\n- Community string incorrecta (probaste: {community})\n- Puerto bloqueado por firewall\n- Dispositivo no alcanzable',
                'ip': ip,
                'port': port,
                'community': community
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'❌ Error en prueba SNMP:\n{str(e)}\n\nVerifica:\n- Módulo pysnmp instalado\n- IP correcta\n- Firewall no bloqueando puerto {port}',
            'ip': ip,
            'port': port
        })


@diagnostic_bp.route('/api/diagnostic/modbus', methods=['POST'])
def test_modbus():
    """Test de conexión Modbus TCP"""
    data = request.json
    ip = data.get('ip', '')
    port = data.get('port', 502)
    slave_id = data.get('slave_id', 1)
    
    if not ip:
        return jsonify({'error': 'IP requerida'}), 400
    
    try:
        from pymodbus.client import ModbusTcpClient
        
        output_lines = [
            f'🔍 Probando conexión Modbus TCP...',
            f'IP: {ip}:{port}',
            f'Slave ID: {slave_id}',
            ''
        ]
        
        # Crear cliente Modbus
        client = ModbusTcpClient(ip, port=int(port), timeout=3)
        
        # Intentar conexión
        connection = client.connect()
        
        if connection:
            output_lines.append(f'✅ Conexión Modbus establecida!')
            
            # Intentar leer algunos registros de prueba
            try:
                # Leer registro 0 (común en muchos dispositivos)
                result = client.read_holding_registers(0, 1, slave=int(slave_id))
                
                if not result.isError():
                    output_lines.append(f'✅ Lectura de registro exitosa')
                    output_lines.append(f'   Registro 0: {result.registers[0]}')
                else:
                    output_lines.append(f'⚠️  Registro no disponible (normal si no existe)')
                    
            except Exception as e:
                output_lines.append(f'⚠️  No se pudieron leer registros: {e}')
            
            client.close()
            
            output_lines.extend([
                '',
                '✅ El dispositivo responde a Modbus TCP',
                'Ahora necesitas:',
                '1. Configurar los registros correctos del UPS',
                '2. Verificar el Slave ID correcto'
            ])
            
            return jsonify({
                'success': True,
                'output': '\n'.join(output_lines),
                'ip': ip,
                'port': port,
                'slave_id': slave_id
            })
        else:
            output_lines.extend([
                f'❌ No se pudo conectar via Modbus TCP',
                '',
                'Posibles causas:',
                '- Puerto Modbus no habilitado en el UPS',
                '- Puerto bloqueado por firewall',
                '- IP o Puerto incorrectos',
                f'- Slave ID incorrecto (probaste: {slave_id})'
            ])
            
            return jsonify({
                'success': False,
                'output': '\n'.join(output_lines),
                'ip': ip,
                'port': port,
                'slave_id': slave_id
            })
            
    except ImportError:
        return jsonify({
            'success': False,
            'output': '❌ Error: Módulo pymodbus no instalado\n\nInstala con: pip install pymodbus',
            'ip': ip
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'❌ Error en prueba Modbus:\n{str(e)}',
            'ip': ip,
            'port': port
        })


@diagnostic_bp.route('/api/diagnostic/scan', methods=['POST'])
def scan_ip_range():
    """Escaneo rápido de IPs en un rango"""
    data = request.json
    network = data.get('network', '192.168.0')  # ej: 192.168.0
    start = data.get('start', 1)
    end = data.get('end', 254)
    
    try:
        output_lines = [
            f'🔍 Escaneando red {network}.{start}-{end}...',
            f'Buscando hosts activos y puertos comunes (502, 161)',
            ''
        ]
        
        hosts_found = []
        
        # Escaneo simple de ping
        for i in range(int(start), min(int(end) + 1, 255)):
            ip = f'{network}.{i}'
            
            # Ping simple
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', '-w', '500', ip]
            
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                if result.returncode == 0:
                    output_lines.append(f'✅ {ip} - ACTIVO')
                    
                    # Probar puertos comunes
                    ports_info = []
                    for port in [502, 161, 80]:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        if sock.connect_ex((ip, port)) == 0:
                            port_name = {502: 'Modbus', 161: 'SNMP', 80: 'HTTP'}.get(port, str(port))
                            ports_info.append(f'{port_name}:{port}')
                        sock.close()
                    
                    if ports_info:
                        output_lines.append(f'   Puertos abiertos: {", ".join(ports_info)}')
                        
                    hosts_found.append({
                        'ip': ip,
                        'ports': ports_info
                    })
                    
            except (subprocess.TimeoutExpired, Exception):
                continue
        
        output_lines.extend([
            '',
            f'─' * 50,
            f'Total de hosts encontrados: {len(hosts_found)}'
        ])
        
        return jsonify({
            'success': True,
            'output': '\n'.join(output_lines),
            'hosts': hosts_found
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'❌ Error en escaneo: {str(e)}'
        })


@diagnostic_bp.route('/api/diagnostic/route', methods=['POST'])
def test_route():
    """Muestra la tabla de rutas del sistema"""
    try:
        if platform.system().lower() == 'windows':
            command = ['route', 'print']
        else:
            command = ['ip', 'route']
            
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return jsonify({
            'success': True,
            'output': result.stdout + result.stderr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'❌ Error obteniendo rutas: {str(e)}'
        })


@diagnostic_bp.route('/api/diagnostic/interfaces', methods=['GET'])
def get_interfaces():
    """Lista las interfaces de red del sistema"""
    try:
        if platform.system().lower() == 'windows':
            command = ['ipconfig', '/all']
        else:
            command = ['ip', 'addr']
            
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return jsonify({
            'success': True,
            'output': result.stdout + result.stderr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'❌ Error obteniendo interfaces: {str(e)}'
        })
