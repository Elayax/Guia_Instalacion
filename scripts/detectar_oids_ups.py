# -*- coding: utf-8 -*-
"""
Script para detectar OIDs disponibles en el UPS y guardar la configuracion
"""

import sys
import os
import json
import asyncio

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.protocols.snmp_scanner import SNMPScanner

async def main():
    ip = '192.168.0.100'
    
    print("="*60)
    print("  DETECTANDO OIDS DISPONIBLES EN UPS {}".format(ip))
    print("="*60)
    print()
    
    scanner = SNMPScanner(ip=ip, port=161, timeout=3)
    
    print("Ejecutando auto-deteccion...")
    print("Esto tomara unos 15-20 segundos...")
    print()
    
    config = await scanner.auto_detect()
    
    # Mostrar resultados
    print()
    print("="*60)
    print("  RESULTADOS")
    print("="*60)
    print()
    
    if config.get('success'):
        mp_model = config.get('mp_model', 1)
        print("Version SNMP: {}".format('SNMPv1' if mp_model == 0 else 'SNMPv2c'))
        print("Community: {}".format(config.get('community', 'public')))
        print("Tipo UPS: {}".format(config.get('ups_type', 'Desconocido')))
        print("Total OIDs funcionando: {}".format(len(config.get('working_oids', []))))
        print()
        
        # Guardar configuracion a archivo
        output_file = 'oids_detectados_192.168.0.100.json'
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("Configuracion guardada en: {}".format(output_file))
        print()
        
        # Mostrar OIDs por categoria
        working_oids = config.get('working_oids', [])
        
        print("OIDs detectados por categoria:")
        print()
        
        # Separar por tipo
        mib2_oids = [o for o in working_oids if o['oid'].startswith('1.3.6.1.2.1') and not o['oid'].startswith('1.3.6.1.2.1.33')]
        ups_mib_oids = [o for o in working_oids if o['oid'].startswith('1.3.6.1.2.1.33')]
        invt_oids = [o for o in working_oids if o['oid'].startswith('1.3.6.1.4.1.56788')]
        other_oids = [o for o in working_oids if o not in mib2_oids + ups_mib_oids + invt_oids]
        
        if mib2_oids:
            print("MIB-II Basico ({} OIDs):".format(len(mib2_oids)))
            for oid in mib2_oids[:10]:  # Primeros 10
                print("  - {}: {}".format(oid['name'], oid['value'][:50] if len(oid['value']) > 50 else oid['value']))
            if len(mib2_oids) > 10:
                print("  ... y {} mas".format(len(mib2_oids) - 10))
            print()
        
        if ups_mib_oids:
            print("UPS-MIB RFC 1628 ({} OIDs):".format(len(ups_mib_oids)))
            for oid in ups_mib_oids:
                print("  - {}: {}".format(oid['name'], oid['value'][:50] if len(oid['value']) > 50 else oid['value']))
            print()
        
        if invt_oids:
            print("INVT Enterprise ({} OIDs):".format(len(invt_oids)))
            for oid in invt_oids:
                print("  - {}: {}".format(oid['name'], oid['value'][:50] if len(oid['value']) > 50 else oid['value']))
            print()
        
        if other_oids:
            print("Otros ({} OIDs):".format(len(other_oids)))
            for oid in other_oids[:5]:
                print("  - {}: {}".format(oid['name'], oid['value'][:50] if len(oid['value']) > 50 else oid['value']))
            print()
        
        print("="*60)
        print()
        print("SIGUIENTE PASO:")
        print("  1. Revisa el archivo: {}".format(output_file))
        print("  2. El sistema usara estos OIDs para monitoreo")
        print()
        
    else:
        print("ERROR: No se pudo detectar la configuracion")
        print("Mensaje: {}".format(config.get('message', 'Desconocido')))

if __name__ == '__main__':
    asyncio.run(main())
