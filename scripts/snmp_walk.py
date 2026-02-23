import asyncio
from pysnmp.hlapi.asyncio import *

async def run_snmp_walk(target_ip, community='public'):
    print(f"Starting SNMP Walk on {target_ip} with community '{community}'...")
    
    try:
        # Pysnmp 7.x / v3arch async usage
        iterator = walk_cmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),
            await UdpTransportTarget.create((target_ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1')),
            lexicographicMode=True
        )

        current_oid = None
        count = 0
        
        async for errorIndication, errorStatus, errorIndex, varBinds in iterator:
            if errorIndication:
                print(f"Error: {errorIndication}")
                break
            elif errorStatus:
                print(f"Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
                break
            else:
                for varBind in varBinds:
                    oid, val = varBind
                    print(f'{oid.prettyPrint()} = {val.prettyPrint()}')
                    count += 1
                    
        print(f"\nTotal items retrieved: {count}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    target_ip = input("Ingrese la IP del dispositivo SNMP: ").strip()
    if not target_ip:
        print("IP invalida.")
        return

    # default community is public, typically sufficient for basic test. 
    # Could ask user for it too if needed, but request only mentioned IP.
    
    try:
        asyncio.run(run_snmp_walk(target_ip))
    except KeyboardInterrupt:
        print("\nOperacion cancelada por el usuario.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
