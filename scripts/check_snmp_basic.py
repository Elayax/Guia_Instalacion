
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def scan():
    ip = '192.168.0.100'
    community = 'public'
    
    print(f"Probando conexion basica a {ip}...")
    
    # Prueba sysDescr (1.3.6.1.2.1.1.1.0)
    # y sysName (1.3.6.1.2.1.1.5.0)
    oids = [
        ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.1.5.0'))
    ]
    
    try:
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0), # v1
            await UdpTransportTarget.create((ip, 161), timeout=2.0, retries=1),
            ContextData(),
            *oids
        )
        
        if errorIndication:
            print(f"Error Indication: {errorIndication}")
        elif errorStatus:
            print(f"Error Status: {errorStatus.prettyPrint()}")
        else:
            for name, val in varBinds:
                print(f"{name.prettyPrint()} = {val.prettyPrint()}")
                
    except Exception as e:
        print(f"Excepcion get_cmd: {e}")
        
    print("-" * 20)
    
    # Prueba Walk manual (scaneo)
    root = '1.3.6.1.2.1.1' # System Group
    print(f"Escaneando desde {root}...")
    
    current_oid = ObjectType(ObjectIdentity(root))
    
    for i in range(10):
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
            print(f"NEXT: {oid.prettyPrint()} = {val.prettyPrint()}")
            
            current_oid = ObjectType(oid)
            
        except Exception as e:
            print(f"Excepcion walk: {e}")
            break

if __name__ == '__main__':
    asyncio.run(scan())
