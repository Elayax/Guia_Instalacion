import asyncio
import sys
import os

# Aseguramos que Python encuentre tu carpeta 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from pysnmp.hlapi.asyncio import (
        SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
        ObjectType, ObjectIdentity, get_cmd
    )
except ImportError:
    from pysnmp.hlapi.asyncio import *

async def probar_ups_netagent(ip):
    print(f"\n📡 --- LECTURA DE UPS (Protocolo NetAgent/Megatec) ---")
    print(f"🎯 IP: {ip}")
    
    # Estos son los OIDs específicos para la rama .935 (NetAgent)
    oids = {
        "Fabricante": "1.3.6.1.4.1.935.1.1.1.1.1.1.0",
        "Modelo": "1.3.6.1.4.1.935.1.1.1.1.1.2.0",
        "Voltaje Batería": "1.3.6.1.4.1.935.1.1.1.2.2.2.0", # Valor en 0.1V (ej: 240 = 24V)
        "Carga Batería %": "1.3.6.1.4.1.935.1.1.1.2.2.1.0",
        "Voltaje Entrada": "1.3.6.1.4.1.935.1.1.1.3.2.1.0", # Valor en 0.1V
        "Voltaje Salida": "1.3.6.1.4.1.935.1.1.1.4.2.1.0",  # Valor en 0.1V
        "Carga Salida %": "1.3.6.1.4.1.935.1.1.1.4.2.3.0",
        "Temperatura": "1.3.6.1.4.1.935.1.1.1.2.2.3.0"      # Celsius
    }

    try:
        transport = await UdpTransportTarget.create((ip, 161), timeout=2, retries=1)
        objetos = [ObjectType(ObjectIdentity(oid)) for oid in oids.values()]

        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            CommunityData('public', mpModel=1),
            transport,
            ContextData(),
            *objetos
        )

        if errorIndication:
            print(f"❌ Error: {errorIndication}")
        elif errorStatus:
            print(f"❌ Error UPS: {errorStatus.prettyPrint()}")
        else:
            print("✅ ¡DATOS RECIBIDOS! \n")
            nombres = list(oids.keys())
            for i, varBind in enumerate(varBinds):
                valor = varBind[1].prettyPrint()
                # Limpieza de datos (algunos vienen multiplicados por 10)
                nombre = nombres[i]
                if "Voltaje" in nombre and valor.isdigit():
                    print(f"   🔹 {nombre:15}: {float(valor)/10} V")
                else:
                    print(f"   🔹 {nombre:15}: {valor}")

    except Exception as e:
        print(f"❌ Fallo: {e}")

if __name__ == "__main__":
    # Usamos la IP que ya confirmaste que responde
    IP_UPS = "192.168.10.198" 
    asyncio.run(probar_ups_netagent(IP_UPS))