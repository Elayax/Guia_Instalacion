"""
Servicio de monitoreo unificado para UPS.
Orquesta SNMP y Modbus segun la configuracion de cada dispositivo.

Features:
- Conexión ZeroTier dual-method (port-forward + ruta directa)
- Grabación histórica configurable por UPS
- Alertas persistentes con deduplicación y auto-resolve
- Detección de offline por fallos consecutivos
"""

import threading
import time
import asyncio
import logging
from datetime import datetime
from app.base_datos import GestorDB
from app.services.protocols.snmp_client import SNMPClient
from app.services.modbus_monitor import ModbusMonitor
from app.extensions import socketio

logger = logging.getLogger(__name__)

# Número de fallos consecutivos para marcar offline
OFFLINE_THRESHOLD = 3
# Cada N ciclos, reintentar el método primario de conexión
RETRY_PRIMARY_EVERY = 10


class MonitoringService(threading.Thread):
    def __init__(self, interval=2):
        super().__init__()
        self.interval = interval
        self.running = True
        self.db = GestorDB()
        self.daemon = True
        self.modbus_monitor = ModbusMonitor()
        self._cycle_count = 0
        # Trackers por dispositivo
        self._fail_counters = {}      # device_id → int (fallos consecutivos)
        self._last_recorded = {}      # device_id → timestamp de última grabación
        self._active_alarms = {}      # device_id → set(codes) activos en memoria
        self._was_offline = set()     # device_ids que estaban offline

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

    def _resolve_connection(self, dev):
        """
        Determina IP y puerto para conectar al dispositivo.
        Estrategia dual-method:
          1. Port-forward ZeroTier (ip_zt:snmp_port_zt) — preferido
          2. Ruta directa (ip_local o ip : snmp_port) — fallback
        """
        dev_id = dev['id']
        fail_count = self._fail_counters.get(dev_id, 0)
        ip_zt = dev.get('ip_zt')
        snmp_port_zt = dev.get('snmp_port_zt') or 10161
        ip_local = dev.get('ip_local')
        ip_direct = ip_local or dev.get('ip')
        snmp_port = dev.get('snmp_port') or 161

        # Si no hay IP ZT configurada, usar directo
        if not ip_zt:
            return ip_direct, snmp_port, 'direct'

        # Si hay demasiados fallos en port-forward, intentar directo
        use_fallback = fail_count > OFFLINE_THRESHOLD and ip_direct

        # Pero cada RETRY_PRIMARY_EVERY ciclos, reintentar el primario
        if use_fallback and (self._cycle_count % RETRY_PRIMARY_EVERY == 0):
            use_fallback = False

        if use_fallback:
            return ip_direct, snmp_port, 'direct'
        else:
            return ip_zt, snmp_port_zt, 'port_forward'

    async def _check_device(self, dev):
        # Resolver conexión dual-method
        ip, port, conn_method = self._resolve_connection(dev)
        if not ip:
            return

        community = dev.get('snmp_community', 'public') or 'public'
        snmp_version_raw = dev.get('snmp_version')
        if snmp_version_raw is None or snmp_version_raw == '':
            snmp_version = 1  # Default SNMPv2c
        else:
            snmp_version = int(snmp_version_raw)

        ups_type = dev.get('ups_type', 'invt_enterprise')
        dev_id = dev['id']

        try:
            # Seleccionar cliente según tipo de UPS
            if ups_type == 'ups_mib_standard' or ups_type == 'hybrid':
                from app.services.protocols.snmp_upsmib_client import UPSMIBClient
                client = UPSMIBClient(
                    ip_address=ip,
                    community=community,
                    port=port,
                    mp_model=int(snmp_version),
                    include_invt=(ups_type == 'hybrid')
                )
            else:
                from app.services.protocols.snmp_minimal_client import MinimalSNMPClient
                client = MinimalSNMPClient(community=community, port=port, mp_model=int(snmp_version))

            data = await client.get_ups_data(ip)

            if data:
                # === ÉXITO: Dispositivo respondió ===
                self._fail_counters[dev_id] = 0
                now = datetime.now()

                # Actualizar estado en BD
                try:
                    self.db.actualizar_estado_dispositivo(dev_id, 0, now, conn_method)
                except Exception as e:
                    logger.error(f"Error actualizando estado de {ip}: {e}")

                # Si estaba offline, generar alerta de reconexión
                if dev_id in self._was_offline:
                    self._was_offline.discard(dev_id)
                    try:
                        self.db.guardar_alerta_ups(dev_id, 'info', 'DEVICE_ONLINE',
                                                   f'{dev.get("nombre", "UPS")} reconectado via {conn_method}')
                        self.db.resolver_alerta_por_codigo(dev_id, 'DEVICE_OFFLINE')
                    except Exception as e:
                        logger.error(f"Error registrando reconexión: {e}")

                status = 'online'
                data['device_id'] = dev_id
                data['ip'] = ip
                data['nombre'] = dev.get('nombre', 'UPS')
                data['estado'] = 'ONLINE'

                version_name = 'SNMPv1' if snmp_version == 0 else 'SNMPv2c'
                data['snmp_version'] = version_name

                socketio.emit('ups_data', data, namespace='/monitor')
                logger.info(f"✅ {ip} ({conn_method}): {data.get('input_voltage_l1', 0)}V entrada, {data.get('battery_capacity', 0)}% batería")

                # Mapear datos a formato normalizado
                mapped_data = {
                    'voltaje_in_l1': data.get('input_voltage_l1', 0),
                    'voltaje_in_l2': data.get('input_voltage_l2', 0),
                    'voltaje_in_l3': data.get('input_voltage_l3', 0),
                    'frecuencia_in': data.get('input_frequency', 0),
                    'voltaje_out_l1': data.get('output_voltage_l1', 0),
                    'voltaje_out_l2': data.get('output_voltage_l2', 0),
                    'voltaje_out_l3': data.get('output_voltage_l3', 0),
                    'frecuencia_out': data.get('output_frequency', 0),
                    'corriente_out_l1': data.get('output_current_l1', data.get('output_current', 0)),
                    'corriente_out_l2': data.get('output_current_l2', 0),
                    'corriente_out_l3': data.get('output_current_l3', 0),
                    'power_factor': data.get('power_factor', 0),
                    'active_power': data.get('active_power', 0),
                    'apparent_power': data.get('apparent_power', 0),
                    'carga_pct': data.get('output_load', 0),
                    'bateria_pct': data.get('battery_capacity', 0),
                    'voltaje_bateria': data.get('battery_voltage', 0),
                    'corriente_bateria': data.get('battery_current', 0),
                    'temperatura': data.get('temperature', 0),
                    'battery_remain_time': data.get('battery_runtime', 0),
                    'power_mode': data.get('power_source', ''),
                    'battery_status': data.get('battery_status', ''),
                    'phases': data.get('_phases', 1),
                }

                # Generar y persistir alarmas
                alarms = self._check_snmp_alarms(mapped_data)
                self._persist_alarms(dev_id, dev.get('nombre', 'UPS'), alarms)

                # Grabación histórica (si recording=True y ha pasado el intervalo)
                self._maybe_record(dev, dev_id, mapped_data)

            else:
                # === FALLO: Sin datos ===
                status = 'offline'
                mapped_data = {}
                alarms = []
                self._handle_failure(dev, dev_id, conn_method)

            payload = {
                'id': dev_id,
                'status': status,
                'ip': ip,
                'nombre': dev['nombre'],
                'protocol': 'snmp',
                'connection_method': conn_method,
                'recording': dev.get('recording', False),
                'data': mapped_data,
                'alarms': alarms,
            }

            socketio.emit('ups_update', payload)

        except Exception as e:
            logger.error(f"Error checking SNMP device {ip}: {e}")
            self._handle_failure(dev, dev_id, conn_method)

    def _handle_failure(self, dev, dev_id, conn_method):
        """Maneja un fallo de conexión: incrementa contador y genera alerta si supera umbral."""
        self._fail_counters[dev_id] = self._fail_counters.get(dev_id, 0) + 1
        fail_count = self._fail_counters[dev_id]

        try:
            self.db.actualizar_estado_dispositivo(dev_id, fail_count, None, conn_method)
        except Exception:
            pass

        if fail_count >= OFFLINE_THRESHOLD and dev_id not in self._was_offline:
            self._was_offline.add(dev_id)
            try:
                self.db.guardar_alerta_ups(dev_id, 'critical', 'DEVICE_OFFLINE',
                                           f'{dev.get("nombre", "UPS")} sin respuesta ({fail_count} intentos)')
            except Exception as e:
                logger.error(f"Error registrando alerta offline: {e}")

    def _maybe_record(self, dev, dev_id, mapped_data):
        """Graba lectura en BD si recording está activo y ha pasado el intervalo."""
        if not dev.get('recording', False):
            return

        interval = dev.get('recording_interval', 30) or 30
        now = time.time()
        last = self._last_recorded.get(dev_id, 0)

        if now - last >= interval:
            try:
                self.db.guardar_lectura_ups(dev_id, mapped_data)
                self._last_recorded[dev_id] = now
            except Exception as e:
                logger.error(f"Error grabando lectura de {dev.get('nombre', 'UPS')}: {e}")

    def _persist_alarms(self, dev_id, dev_name, alarms):
        """Persiste alarmas nuevas y auto-resuelve las que ya no aplican."""
        current_codes = {a['code'] for a in alarms}
        prev_codes = self._active_alarms.get(dev_id, set())

        # Nuevas alarmas (no estaban antes)
        for alarm in alarms:
            if alarm['code'] not in prev_codes:
                try:
                    self.db.guardar_alerta_ups(dev_id, alarm['level'], alarm['code'], alarm['msg'])
                except Exception as e:
                    logger.error(f"Error persistiendo alerta {alarm['code']}: {e}")

        # Alarmas resueltas (estaban antes, ya no están)
        resolved_codes = prev_codes - current_codes
        for code in resolved_codes:
            try:
                self.db.resolver_alerta_por_codigo(dev_id, code)
            except Exception as e:
                logger.error(f"Error resolviendo alerta {code}: {e}")

        self._active_alarms[dev_id] = current_codes

    def _check_snmp_alarms(self, data):
        """Genera alarmas basadas en datos SNMP."""
        alarms = []

        # Voltaje de entrada (rango México: 90-140V para 120VAC)
        vin = data.get('voltaje_in_l1', 0)
        if vin and 0 < vin < 90:
            alarms.append({'level': 'critical', 'code': 'INPUT_V_LOW', 'msg': f'Voltaje entrada bajo: {vin:.1f}V'})
        elif vin and 0 < vin < 100:
            alarms.append({'level': 'warning', 'code': 'INPUT_V_LOW', 'msg': f'Voltaje entrada bajo: {vin:.1f}V'})
        elif vin and vin > 140:
            alarms.append({'level': 'warning', 'code': 'INPUT_V_HIGH', 'msg': f'Voltaje entrada alto: {vin:.1f}V'})

        # Batería
        bat = data.get('bateria_pct', 0)
        if bat and 0 < bat < 15:
            alarms.append({'level': 'critical', 'code': 'BAT_CRITICAL', 'msg': f'Bateria critica: {bat:.1f}%'})
        elif bat and 0 < bat < 30:
            alarms.append({'level': 'warning', 'code': 'BAT_LOW', 'msg': f'Bateria baja: {bat:.1f}%'})

        # Temperatura
        temp = data.get('temperatura', 0)
        if temp and temp > 40:
            alarms.append({'level': 'critical', 'code': 'BAT_OVERTEMP', 'msg': f'Sobretemperatura: {temp:.1f}C'})

        # Carga
        load = data.get('carga_pct', 0)
        if load and load > 95:
            alarms.append({'level': 'critical', 'code': 'OVERLOAD', 'msg': f'Sobrecarga critica: {load:.1f}%'})
        elif load and load > 80:
            alarms.append({'level': 'warning', 'code': 'LOAD_HIGH', 'msg': f'Carga alta: {load:.1f}%'})

        # Modo batería (UPS en batería = falla de red eléctrica)
        power_mode = str(data.get('power_mode', '')).lower()
        if 'battery' in power_mode or 'batt' in power_mode:
            alarms.append({'level': 'critical', 'code': 'ON_BATTERY', 'msg': 'UPS operando en modo batería'})

        return alarms
