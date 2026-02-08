"""
Servicio de monitoreo unificado para UPS INVT.
Orquesta SNMP y Modbus segun la configuracion de cada dispositivo.
"""

import threading
import time
import asyncio
import logging
from app.base_datos import GestorDB
from app.services.protocols.snmp_client import SNMPClient
from app.services.modbus_monitor import ModbusMonitor
from app.extensions import socketio

logger = logging.getLogger(__name__)


class MonitoringService(threading.Thread):
    def __init__(self, interval=2):
        super().__init__()
        self.interval = interval
        self.running = True
        self.db = GestorDB()
        self.daemon = True
        self.modbus_monitor = ModbusMonitor()
        self._cycle_count = 0

    def run(self):
        logger.info("Iniciando servicio de monitoreo unificado (SNMP + Modbus)...")
        # Iniciar monitor Modbus en su propio hilo
        self.modbus_monitor.start_background_task()

        # Este hilo maneja SNMP
        while self.running:
            try:
                self._poll_snmp_devices()
            except Exception as e:
                logger.error(f"Error en ciclo de monitoreo SNMP: {e}")

            self._cycle_count += 1
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        self.modbus_monitor.stop()

    def _poll_snmp_devices(self):
        try:
            asyncio.run(self._async_poll())
        except Exception as e:
            logger.error(f"Error ejecutando poll async SNMP: {e}")

    async def _async_poll(self):
        try:
            devices = self.db.obtener_monitoreo_ups()
        except Exception as e:
            logger.error(f"Error leyendo DB: {e}")
            return

        # Filtrar solo dispositivos SNMP
        snmp_devices = [d for d in devices if d.get('protocolo', 'modbus') == 'snmp']

        tasks = []
        for dev in snmp_devices:
            tasks.append(self._check_device(dev))

        if tasks:
            await asyncio.gather(*tasks)

    async def _check_device(self, dev):
        ip = dev['ip']
        port = dev.get('snmp_port', 161) or 161
        community = dev.get('snmp_community', 'public') or 'public'
        dev_id = dev['id']

        try:
            client = SNMPClient(community=community, port=port)
            data = await client.get_ups_data(ip)

            if data:
                status = 'online'
                mapped_data = {
                    # Voltajes de entrada por fase
                    'voltaje_in_l1': data.get('input_voltage_l1', 0),
                    'voltaje_in_l2': data.get('input_voltage_l2', 0),
                    'voltaje_in_l3': data.get('input_voltage_l3', 0),
                    'frecuencia_in': data.get('input_frequency', 0),
                    # Voltajes de salida por fase
                    'voltaje_out_l1': data.get('output_voltage_l1', 0),
                    'voltaje_out_l2': data.get('output_voltage_l2', 0),
                    'voltaje_out_l3': data.get('output_voltage_l3', 0),
                    'frecuencia_out': data.get('output_frequency', 0),
                    # Corrientes por fase
                    'corriente_out_l1': data.get('output_current_l1', data.get('output_current', 0)),
                    'corriente_out_l2': data.get('output_current_l2', 0),
                    'corriente_out_l3': data.get('output_current_l3', 0),
                    # Potencia
                    'power_factor': data.get('power_factor', 0),
                    'active_power': data.get('active_power', 0),
                    'apparent_power': data.get('apparent_power', 0),
                    # Carga
                    'carga_pct': data.get('output_load', 0),
                    # Bateria
                    'bateria_pct': data.get('battery_capacity', 0),
                    'voltaje_bateria': data.get('battery_voltage', 0),
                    'corriente_bateria': data.get('battery_current', 0),
                    'temperatura': data.get('temperature', 0),
                    'battery_remain_time': data.get('battery_runtime', 0),
                    # Estado
                    'power_mode': data.get('power_source', ''),
                    'battery_status': data.get('battery_status', ''),
                    # Metadatos
                    'phases': data.get('_phases', 1),
                }
                # Generar alarmas SNMP
                alarms = self._check_snmp_alarms(mapped_data)
            else:
                status = 'offline'
                mapped_data = {}
                alarms = []

            payload = {
                'id': dev_id,
                'status': status,
                'ip': ip,
                'nombre': dev['nombre'],
                'protocol': 'snmp',
                'data': mapped_data,
                'alarms': alarms,
            }

            socketio.emit('ups_update', payload)

        except Exception as e:
            logger.error(f"Error checking SNMP device {ip}: {e}")

    def _check_snmp_alarms(self, data):
        """Genera alarmas basadas en datos SNMP."""
        alarms = []

        vin = data.get('voltaje_in_l1', 0)
        if 0 < vin < 180:
            alarms.append({'level': 'critical', 'code': 'INPUT_V_LOW', 'msg': f'Voltaje entrada bajo: {vin:.1f}V'})

        bat = data.get('bateria_pct', 0)
        if 0 < bat < 20:
            alarms.append({'level': 'critical', 'code': 'BAT_CRITICAL', 'msg': f'Bateria critica: {bat:.1f}%'})
        elif 0 < bat < 50:
            alarms.append({'level': 'warning', 'code': 'BAT_LOW', 'msg': f'Bateria baja: {bat:.1f}%'})

        temp = data.get('temperatura', 0)
        if temp > 45:
            alarms.append({'level': 'critical', 'code': 'BAT_OVERTEMP', 'msg': f'Sobretemperatura: {temp:.1f}C'})

        load = data.get('carga_pct', 0)
        if load > 90:
            alarms.append({'level': 'critical', 'code': 'OVERLOAD', 'msg': f'Sobrecarga: {load:.1f}%'})
        elif load > 70:
            alarms.append({'level': 'warning', 'code': 'LOAD_HIGH', 'msg': f'Carga alta: {load:.1f}%'})

        return alarms
