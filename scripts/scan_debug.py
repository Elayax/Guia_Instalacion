
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def scan():
    ip = '192.168.0.100'
    community = 'public'
    
    print(f"Escaneando {ip}...")
    
    # Probar SNMPv1
    print("Probando SNMPv1...")
    await run_scan(ip, community, 0)

async def run_scan(ip, community, version):
    # Empezar desde INVT root si es posible, o MIB-2 system
    # INVT OID: 1.3.6.1.4.1.56788
    # system: 1.3.6.1.2.1.1
    
    roots = ['1.3.6.1.2.1.1', '1.3.6.1.4.1.56788'] 
    
    for root_oid in roots:
        print(f"--- Escaneando desde {root_oid} ---")
        try:
            op = await next_cmd(
                SnmpEngine(),
                CommunityData(community, mpModel=version),
                await UdpTransportTarget.create((ip, 161), timeout=1.0, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(root_oid))
            )
            
            # next_cmd en pysnmp v6 es async generator si se itera? NO.
            # wait, la documentacion de pysnmp v6 next_cmd es confusa entre versiones.
            # Vamos a usar el estilo iterador manual con get_next si es necesario, 
            # o asumir que next_cmd retorna una estructura iterable.
            
            # En la version instalada (probablemente pyasn1/pysnmp reciente), next_cmd es:
            # errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(...) 
            # ESTO ES SOLO UN PASO (GetNext). Para hacer WALK hay que hacerlo en bucle.
            
            current_oid = ObjectType(ObjectIdentity(root_oid))
            
            for i in range(20): # Scanear 20 items
                errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
                    SnmpEngine(),
                    CommunityData(community, mpModel=version),
                    await UdpTransportTarget.create((ip, 161), timeout=1.0, retries=0),
                    ContextData(),
                    current_oid
                )
                
                if errorIndication:
                    print(f"Error conexion: {errorIndication}")
                    break
                if errorStatus:
                    print(f"Error SNMP: {errorStatus.prettyPrint()}")
                    break
                if not varBinds:
                    print("Fin MIB")
                    break
                    
                for varBind in varBinds:
                    oid = varBind[0]
                    val = varBind[1]
                    print(f"{oid} = {val.prettyPrint()}")
                    current_oid = ObjectType(oid)
                    
        except Exception as e:
            print(f"Excepcion: {e}")

if __name__ == '__main__':
    asyncio.run(scan())
