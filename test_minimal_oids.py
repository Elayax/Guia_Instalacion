# -*- coding: utf-8 -*-
"""
Test directo de los 5 OIDs minimos con SNMPv1
"""

import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def test_minimal_oids():
    ip = '192.168.0.100'
    community = 'public'
    port = 161
    
    # Los 5 OIDs que supuestamente funcionan
    oids = {
        'Model': '1.3.6.1.4.1.56788.1.1.1.0',
        'Serial': '1.3.6.1.4.1.56788.1.1.2.0',
        'Input Voltage A': '1.3.6.1.4.1.56788.1.3.1.2.1',
        'Output Voltage A': '1.3.6.1.4.1.56788.1.4.1.2.1',
        'Battery Voltage': '1.3.6.1.4.1.56788.1.6.1.0',
    }
    
    print("="*70)
    print(f"  PROBANDO 5 OIDS MINIMOS EN {ip} (SNMPv1)")
    print("="*70)
    print()
    
    # Probar UNO POR UNO
    for name, oid in oids.items():
        try:
            # get_cmd es la funcion correcta en pysnmp v6+
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                SnmpEngine(),
                CommunityData(community, mpModel=0),  # SNMPv1
                await UdpTransportTarget.create((ip, port)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            if errorIndication:
                print(f"[ERROR] {name:20s} -> Conexion fallida: {errorIndication}")
            elif errorStatus:
                print(f"[ERROR] {name:20s} -> SNMP error: {errorStatus}")
            else:
                value = varBinds[0][1].prettyPrint()
                if 'No Such' in value:
                    print(f"[X] {name:20s} -> NO EXISTE en el UPS")
                else:
                    print(f"[OK] {name:20s} -> {value}")
        except Exception as e:
            print(f"[ERROR] {name:20s} -> Exception: {e}")
        
        # Pequena pausa entre consultas
        await asyncio.sleep(0.2)
    
    print()
    print("="*70)
    print("  Si todos marcan [X] NO EXISTE, el UPS no responde SNMP")
    print("  o la community/IP/puerto esta mal")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(test_minimal_oids())
