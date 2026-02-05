import threading
import time
import asyncio
import logging
from app.base_datos import GestorDB
from app.services.protocols.snmp_client import SNMPClient
from app.extensions import socketio
from app.utils.ups_oids import FAST_POLL_GROUPS, SLOW_POLL_GROUPS, ALARM_LABELS

logger = logging.getLogger(__name__)


class MonitoringService(threading.Thread):
    def __init__(self, interval=5):
        super().__init__()
        self.interval = interval
        self.running = True
        self.db = GestorDB()
        self.daemon = True
        self._poll_count = 0
        # Cache de info (slow poll) por dispositivo
        self._device_info_cache = {}

    def run(self):
        logger.info("Iniciando servicio de monitoreo SNMP...")
        while self.running:
            try:
                self._poll_devices()
            except Exception as e:
                logger.error(f"Error en ciclo de monitoreo: {e}")

            time.sleep(self.interval)

    def _poll_devices(self):
        try:
            asyncio.run(self._async_poll())
        except Exception as e:
            logger.error(f"Error ejecutando poll async: {e}")
        self._poll_count += 1

    async def _async_poll(self):
        try:
            devices = self.db.obtener_monitoreo_ups()
        except Exception as e:
            logger.error(f"Error leyendo DB: {e}")
            return

        tasks = []
        for dev in devices:
            tasks.append(self._check_device(dev))

        if tasks:
            await asyncio.gather(*tasks)

    async def _check_device(self, dev):
        ip = dev['ip']
        port = dev['port'] if (dev['port'] and dev['port'] != 502) else 161
        community = dev.get('community', 'public') or 'public'
        dev_id = dev['id']

        logger.info(f"Checking device {dev['nombre']} at {ip}:{port}...")

        try:
            client = SNMPClient(community=community, port=port)

            # Determinar grupos a consultar
            groups = list(FAST_POLL_GROUPS)
            if self._poll_count % 12 == 0:  # Cada ~60s
                groups.extend(SLOW_POLL_GROUPS)

            data = await client.get_ups_data_full(ip, groups)
            logger.info(f"Data for {ip}: {len(data)} groups received")

            if data:
                status = 'online'

                # Datos por grupo
                inp = data.get('data_input', {})
                out = data.get('data_output', {})
                bat = data.get('data_battery', {})
                st = data.get('status', {})
                internal = data.get('internal', {})

                # Backward-compatible flat mapping
                legacy_data = {
                    'voltaje_in': inp.get('voltage_a', 0),
                    'voltaje_out': out.get('voltage_a', 0),
                    'carga_pct': out.get('load_a', 0),
                    'bateria_pct': bat.get('capacity', 0),
                    'temperatura': bat.get('temperature', 0),
                    'voltaje_bateria': bat.get('voltage', 0),
                }

                # Procesar alarmas activas
                active_alarms = []
                alarm_data = data.get('alarm', {})
                for alarm_key, alarm_val in alarm_data.items():
                    try:
                        if int(alarm_val) == 1:
                            active_alarms.append({
                                'key': alarm_key,
                                'label': ALARM_LABELS.get(alarm_key, alarm_key)
                            })
                    except (ValueError, TypeError):
                        pass

                # Cache de info del dispositivo
                if 'info' in data:
                    self._device_info_cache[dev_id] = data['info']

                device_info = self._device_info_cache.get(dev_id, {})
            else:
                status = 'offline'
                legacy_data = {}
                data = {}
                active_alarms = []
                device_info = self._device_info_cache.get(dev_id, {})

            payload = {
                'id': dev_id,
                'status': status,
                'ip': ip,
                'nombre': dev['nombre'],
                'data': legacy_data,
                'full_data': data,
                'alarms': active_alarms,
                'device_info': device_info,
                'timestamp': time.time(),
            }

            logger.info(f"Emitting update for {ip}: {status} ({len(active_alarms)} alarms)")
            socketio.emit('ups_update', payload)

        except Exception as e:
            logger.error(f"Error checking {ip}: {e}")
