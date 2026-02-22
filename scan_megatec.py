
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def scan_megatec():
    ip = '192.168.0.100'
    community = 'public'
    root = '1.3.6.1.4.1.935' # Megatec Branch
    
    print(f"Escaneando Megatec branch ({root}) en {ip}...")
    
    current_oid = ObjectType(ObjectIdentity(root))
    
    for i in range(50):
        try:
            errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
                SnmpEngine(),
                CommunityData(community, mpModel=0), # v1
                await UdpTransportTarget.create((ip, 161), timeout=1.0, retries=0),
                ContextData(),
                current_oid
            )
            
            if errorIndication or errorStatus:
                print(f"Stop: {errorIndication or errorStatus}")
                break
                
            var = varBinds[0]
            oid, val = var[0], var[1]
            print(f"{oid.prettyPrint()} = {val.prettyPrint()}")
            
            current_oid = ObjectType(oid)
            
        except Exception as e:
            print(f"Excepcion: {e}")
            break

if __name__ == '__main__':
    asyncio.run(scan_megatec())
