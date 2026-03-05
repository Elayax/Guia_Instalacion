
import asyncio
import sys
import os

# Asegurar que podemos importar modulos de la app
sys.path.append(os.getcwd())

try:
    from app.services.protocols.snmp_minimal_client import MinimalSNMPClient
except ImportError:
    print("Error importando MinimalSNMPClient. Verificando path...")
    # Fallback si falla import directo
    sys.path.append('e:\\Dev\\Proyectos\\GuiaInstalacion')
    from app.services.protocols.snmp_minimal_client import MinimalSNMPClient

async def debug():
    ip = '192.168.0.100'
    print(f"Probando MinimalSNMPClient (Megatec) contra {ip}...")
    
    client = MinimalSNMPClient(community='public', port=161, mp_model=0)
    
    print("Enviando petición SNMP...")
    data = await client.get_ups_data(ip)
    
    print("\n" + "="*40)
    print("  RESULTADO DE LA LECTURA")
    print("="*40)
    
    if not data:
        print("[X] NO SE RECIBIERON DATOS (Diccionario vacio)")
        print("Posibles causas:")
        print(" - IP incorrecta")
        print(" - Comunidad incorrecta (public)")
        print(" - OIDs Megatec no soportados por este dispositivo")
    else:
        print("[OK] DATOS RECIBIDOS CORRECTAMENTE!")
        for k, v in data.items():
            if not k.startswith('_'): # Ocultar metadatos internos
                print(f"{k:25s}: {v}")
        
        print("-" * 40)
        print(f"Voltaje Entrada L1  : {data.get('input_voltage_l1')} V")
        print(f"Voltaje Salida L1   : {data.get('output_voltage_l1')} V")
        print(f"Bateria V           : {data.get('battery_voltage')} V")
        print(f"Fases detectadas    : {data.get('_phases')}")

if __name__ == '__main__':
    # Fix para asyncio en Windows sies necesario
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(debug())
