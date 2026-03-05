
import json
import os

# Simular carga de entorno de la app
# (Asumiendo json simple DB para este ejemplo rapido, o conectando a la logica real)
# Voy a usar la logica de 'devices.json' si existe, o la base de datos que usa tu sistema.

JSON_FILE = 'devices.json'

def fix_config():
    if not os.path.exists(JSON_FILE):
        print(f"No se encontro {JSON_FILE}")
        return

    try:
        with open(JSON_FILE, 'r') as f:
            devices = json.load(f)
            
        found = False
        for dev in devices:
            if dev.get('ip') == '192.168.0.100':
                print("Dispositivo encontrado 192.168.0.100")
                dev['phases'] = 1             # FORZAR MONOFASICO
                dev['ups_type'] = 'invt_enterprise' # Usar el cliente Minimalista que actualice
                dev['snmp_version'] = 0       # SNMPv1
                dev['port'] = 161
                dev['community'] = 'public'
                found = True
                print(" -> Configuración ACTUALIZADA a Monofásico / INVT Minimal")
                
        if found:
            with open(JSON_FILE, 'w') as f:
                json.dump(devices, f, indent=4)
            print("Guardado exitoso.")
        else:
            print("No se encontró el UPS 192.168.0.100 en devices.json")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_config()
