import threading
import time
import asyncio
import logging
from app.base_datos import GestorDB
from app.services.protocols.snmp_client import SNMPClient
from app.extensions import socketio

logger = logging.getLogger(__name__)

class MonitoringService(threading.Thread):
    def __init__(self, interval=5):
        super().__init__()
        self.interval = interval
        self.running = True
        self.db = GestorDB()
        self.daemon = True 

    def run(self):
        logger.info("Iniciando servicio de monitoreo SNMP...")
        while self.running:
            try:
                self._poll_devices()
            except Exception as e:
                logger.error(f"Error en ciclo de monitoreo: {e}")
            
            time.sleep(self.interval)

    def _poll_devices(self):
        # Ejecutar la parte asíncrona
        try:
             asyncio.run(self._async_poll())
        except Exception as e:
             logger.error(f"Error ejecutando poll async: {e}")

    async def _async_poll(self):
        try:
            # Obtener dispositivos cada vez para detectar cambios
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
        # Si el puerto es 502 (default Modbus) o None, usamos 161 para SNMP
        port = dev['port'] if (dev['port'] and dev['port'] != 502) else 161
        dev_id = dev['id']
        
        logger.info(f"Checking device {dev['nombre']} at {ip}:{port}...")
        
        try:
            # Default community public 
            client = SNMPClient(community='public', port=port)
            
            data = await client.get_ups_data(ip)
            logger.info(f"Data for {ip}: {data}")
            
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
                    'corriente_out': data.get('output_current', 0),
                    # Carga
                    'carga_pct': data.get('output_load', 0),
                    # Batería
                    'bateria_pct': data.get('battery_capacity', 0),
                    'voltaje_bateria': data.get('battery_voltage', 0),
                    'corriente_bateria': data.get('battery_current', 0),
                    # Temperatura
                    'temperatura': data.get('temperature', 0),
                }
            else:
                status = 'offline'
                mapped_data = {}
                
            payload = {
                'id': dev_id,
                'status': status,
                'ip': ip,
                'nombre': dev['nombre'],
                'data': mapped_data
            }
            
            logger.info(f"Emitting update for {ip}: {status}")
            socketio.emit('ups_update', payload)
            
        except Exception as e:
            logger.error(f"Error checking {ip}: {e}")
