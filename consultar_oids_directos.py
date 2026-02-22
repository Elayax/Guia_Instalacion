# -*- coding: utf-8 -*-
"""
Consultar OIDs funcionales directamente
"""

import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def consultar_oids():
    ip = '192.168.0.100'
    community = 'public'
    port = 161
    
    # OIDs que sabemos que funcionan, segun el JSON
    oids_funcionales = {
        # SISTEMA
        'sysDescr': '1.3.6.1.2.1.1.1.0',
        'sysObjectID': '1.3.6.1.2.1.1.2.0',
        'sysUpTime': '1.3.6.1.2.1.1.3.0',
        'sysContact': '1.3.6.1.2.1.1.4.0',
        'sysName': '1.3.6.1.2.1.1.5.0',
        'sysLocation': '1.3.6.1.2.1.1.6.0',
        
        # UPS-MIB que funcionan
        'ups_ident_manufacturer': '1.3.6.1.2.1.33.1.1.1.0',
        'ups_ident_model': '1.3.6.1.2.1.33.1.1.2.0',
        'ups_ident_sw_version': '1.3.6.1.2.1.33.1.1.3.0',
        'ups_ident_agent_sw_version': '1.3.6.1.2.1.33.1.1.4.0',
        'ups_battery_status': '1.3.6.1.2.1.33.1.2.1.0',
        
        # INVT que funcionan
        'invt_model': '1.3.6.1.4.1.56788.1.1.1.0',
        'invt_serial': '1.3.6.1.4.1.56788.1.1.2.0',
        'invt_input_voltage_a': '1.3.6.1.4.1.56788.1.3.1.2.1',
        'invt_output_voltage_a': '1.3.6.1.4.1.56788.1.4.1.2.1',
        'invt_battery_voltage': '1.3.6.1.4.1.56788.1.6.1.0',
       
        # MAS UPS-MIB que pueden funcionar
        'ups_seconds_on_battery': '1.3.6.1.2.1.33.1.2.2.0',
        'ups_estimated_minutes_remaining': '1.3.6.1.2.1.33.1.2.3.0',
        'ups_estimated_charge_remaining': '1.3.6.1.2.1.33.1.2.4.0',
        'ups_battery_voltage': '1.3.6.1.2.1.33.1.2.5.0',
        'ups_battery_current': '1.3.6.1.2.1.33.1.2.6.0',
        'ups_battery_temperature': '1.3.6.1.2.1.33.1.2.7.0',
        'ups_input_line_bads': '1.3.6.1.2.1.33.1.3.1.0',
        'ups_input_num_lines': '1.3.6.1.2.1.33.1.3.2.0',
        'ups_input_frequency': '1.3.6.1.2.1.33.1.3.3.1.2.1',
        'ups_input_voltage': '1.3.6.1.2.1.33.1.3.3.1.3.1',
        'ups_input_current': '1.3.6.1.2.1.33.1.3.3.1.4.1',
        'ups_input_true_power': '1.3.6.1.2.1.33.1.3.3.1.5.1',
        'ups_output_source': '1.3.6.1.2.1.33.1.4.1.0',
        'ups_output_frequency': '1.3.6.1.2.1.33.1.4.2.0',
        'ups_output_num_lines': '1.3.6.1.2.1.33.1.4.3.0',
        'ups_output_voltage': '1.3.6.1.2.1.33.1.4.4.1.2.1',
        'ups_output_current': '1.3.6.1.2.1.33.1.4.4.1.3.1',
        'ups_output_power': '1.3.6.1.2.1.33.1.4.4.1.4.1',
        'ups_output_percent_load': '1.3.6.1.2.1.33.1.4.4.1.5.1',
    }
    
    print("="*80)
    print("  CONSULTANDO OIDS FUNCIONALES EN 192.168.0.100 (SNMPv1)")
    print("="*80)
    print()
    
    # Crear lista de OIDs
    oids_list = [(name, ObjectType(ObjectIdentity(oid))) for name, oid in oids_funcionales.items()]
    
    # Usar SNMPv1
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),  # mpModel=0 es SNMPv1
        await UdpTransportTarget.create((ip, port)),
        ContextData(),
        *[oid[1] for oid in oids_list]
    )
    
    if errorIndication:
        print(f"Error de conexion: {errorIndication}")
        return
    
    if errorStatus:
        print(f"Error SNMP: {errorStatus.prettyPrint()}")
    
    print(f"Resultados ({len(varBinds)} valores):\n")
    
    for i, varBind in enumerate(varBinds):
        oid_name = oids_list[i][0]
        oid_value = varBind[1].prettyPrint()
        
        # Filtrar "No Such Object"
        if 'No Such' in oid_value or 'null' in oid_value.lower():
            print(f"[X] {oid_name:35s} -> NO EXISTE")
        else:
            print(f"[OK] {oid_name:35s} -> {oid_value}")
    
    print()
    print("="*80)

if __name__ == '__main__':
    asyncio.run(consultar_oids())
