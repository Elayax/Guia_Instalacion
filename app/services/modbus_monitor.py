import threading
import time
from pymodbus.client import ModbusTcpClient
from app.services.influx_db import influx_service
from app.base_datos import GestorDB
from app.extensions import socketio

class ModbusMonitor:
    def __init__(self):
        self.running = False
        self.db = GestorDB()
        self.thread = None

    def start_background_task(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print("Servicio de Monitoreo Modbus Iniciado (Threading)")

    def _monitor_loop(self):
        while self.running:
            try:
                # GestorDB handles its own connections per call
                devices = self.db.obtener_monitoreo_ups()
                
                for dev in devices:
                    self._process_device(dev)
                    time.sleep(0.1) # Yield slightly
                    
            except Exception as e:
                print(f"Error en ciclo de monitoreo: {e}")
            
            time.sleep(5)

    def _process_device(self, dev):
        ip = dev['ip']
        port = dev['port']
        slave = dev['slave_id']
        name = dev['nombre']
        
        # Timeout aumentado a 5s para conexiones VPN/ZeroTier/Satélite
        client = ModbusTcpClient(ip, port=port, timeout=5)
        connected = False
        try:
            connected = client.connect()
        except:
            connected = False
        
        data = {}
        status = 'offline'

        if connected:
            try:
                # Lectura de Holding Registers (40001 -> address 0)
                # Simularemos registros estandar de UPS:
                # 0: V_In, 1: V_Out, 2: Hz, 3: Load%, 4: Batt%
                rr = client.read_holding_registers(0, 10, slave=slave)
                
                if not rr.isError():
                    regs = rr.registers
                    # Entrada: registros 0-3 (V_L1, V_L2, V_L3, Freq_in)
                    data['voltaje_in_l1'] = float(regs[0])
                    data['voltaje_in_l2'] = float(regs[1])
                    data['voltaje_in_l3'] = float(regs[2])
                    data['frecuencia_in'] = float(regs[3]) / 10.0
                    # Salida: registros 4-8 (V_L1, V_L2, V_L3, Freq_out, Current)
                    data['voltaje_out_l1'] = float(regs[4])
                    data['voltaje_out_l2'] = float(regs[5]) if len(regs) > 5 else float(regs[4])
                    data['voltaje_out_l3'] = float(regs[6]) if len(regs) > 6 else float(regs[4])
                    data['frecuencia_out'] = float(regs[7]) / 10.0 if len(regs) > 7 else data['frecuencia_in']
                    data['corriente_out'] = float(regs[8]) / 10.0 if len(regs) > 8 else 0
                    data['carga_pct'] = float(regs[9]) if len(regs) > 9 else 0
                    # Batería: leer segundo bloque
                    rr2 = client.read_holding_registers(10, 5, slave=slave)
                    if not rr2.isError():
                        data['bateria_pct'] = float(rr2.registers[0])
                        data['voltaje_bateria'] = float(rr2.registers[1]) / 10.0
                        data['corriente_bateria'] = float(rr2.registers[2]) / 10.0
                        data['temperatura'] = float(rr2.registers[3]) / 10.0
                    else:
                        data['bateria_pct'] = 0
                        data['voltaje_bateria'] = 0
                        data['corriente_bateria'] = 0
                        data['temperatura'] = 0
                    status = 'online'
                    
                    # Escribir a Influx
                    influx_service.write_ups_data(name, ip, data)
                else:
                    # Fallback para pruebas si no hay dispositivo real
                    pass
                    
            except Exception as e:
                print(f"Error lectura Modbus {ip}: {e}")
            finally:
                client.close()
        
        # MOCK DATA FOR TESTING IF OFFLINE (Optional/Dev mode)
        # Uncomment to test UI without real Modbus device
        # status = 'online'
        # import random
        # data = {
        #    'voltaje_in': 220 + random.uniform(-5, 5),
        #    'voltaje_out': 220,
        #    'bateria_pct': 100 - random.uniform(0, 20),
        #    'carga_pct': 50 + random.uniform(-10, 10)
        # }

        payload = {
            'id': dev['id'],
            'ip': ip,
            'name': name,
            'status': status,
            'data': data,
            'timestamp': time.time()
        }
        socketio.emit('ups_update', payload)

monitor_service = ModbusMonitor()
