import asyncio
import socket
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from pysnmp.hlapi.asyncio import (
        SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
        ObjectType, ObjectIdentity, get_cmd
    )
except ImportError:
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
            print(f"ENCONTRADO! IP: {ip} ==> {desc}")
            return True
    except Exception:
        pass
    return False

async def barrido_red():
    subnets = ["10.138.22.", "10.10.10."]
    
    tasks = []
    print(f"Iniciando escaneo en subredes: {', '.join([s+'x' for s in subnets])}...")
    
    for base_ip in subnets:
        for i in range(1, 255):
            ip = f"{base_ip}{i}"
            tasks.append(check_ip(ip))
    
    await asyncio.gather(*tasks)
    print("Fin del barrido.")

if __name__ == "__main__":
    asyncio.run(barrido_red())