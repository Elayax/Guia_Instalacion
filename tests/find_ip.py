import asyncio
import socket
from pysnmp.hlapi.asyncio import *

async def check_ip(ip):
    try:
        # Preguntamos por el "SysDescr" (Descripción del sistema)
        # Si es el UPS, responderá algo diferente a "Linux RUT956"
        transport = await UdpTransportTarget.create((ip, 161), timeout=0.5, retries=0)
        
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            CommunityData('public', mpModel=0), # Probamos v1
            transport,
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
        )

        if not errorIndication and not errorStatus:
            desc = varBinds[0][1].prettyPrint()
            print(f"✅ ¡ENCONTRADO! IP: {ip} ==> {desc}")
            return True
    except:
        pass
    return False

async def barrido_red():
    # Asumiendo que la red es 10.138.22.x (basado en la IP del router)
    base_ip = "10.138.22." 
    print(f"📡 Escaneando red {base_ip}1 a {base_ip}254...")
    
    tasks = []
    for i in range(1, 255):
        ip = f"{base_ip}{i}"
        tasks.append(check_ip(ip))
    
    await asyncio.gather(*tasks)
    print("🏁 Fin del barrido.")

if __name__ == "__main__":
    asyncio.run(barrido_red())