# -*- coding: utf-8 -*-
"""
Script para verificar y corregir configuracion del UPS
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'Equipos.db')
    
    print("="*60)
    print("  VERIFICANDO CONFIGURACION DE UPS 192.168.0.100")
    print("="*60)
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar TODOS los UPS con esa IP
        cursor.execute("SELECT * FROM monitoreo_config WHERE ip = ?", ('192.168.0.100',))
        devices = cursor.fetchall()
        
        if not devices:
            print("ERROR: No se encontro ningun UPS con IP 192.168.0.100")
            return
        
        print(f"Se encontraron {len(devices)} dispositivo(s) con esa IP:\n")
        
        for dev in devices:
            print(f"Dispositivo ID: {dev['id']}")
            print(f"   IP: {dev['ip']}")
            print(f"   Nombre: {dev['nombre'] or 'Sin nombre'}")
            print(f"   Protocolo: {dev['protocolo']}")
            
            # Verificar que existan los campos
            try:
                snmp_version = dev['snmp_version']
                print(f"   SNMP Version: {snmp_version} ({'SNMPv1' if snmp_version == 0 else 'SNMPv2c'})")
            except:
                print(f"   SNMP Version: NO DEFINIDO")
                snmp_version = None
            
            try:
                ups_type = dev['ups_type']
                print(f"   UPS Type: {ups_type}")
            except:
                print(f"   UPS Type: NO DEFINIDO")
                ups_type = None
            
            print()
            
            # Determinar si necesita actualizacion
            needs_update = False
            updates = []
            
            if snmp_version is None or snmp_version != 0:
                needs_update = True
                updates.append("snmp_version = 0")
                print("   [!] SNMP Version debe ser 0 (SNMPv1)")
            
            if ups_type is None or ups_type != 'ups_mib_standard':
                needs_update = True
                updates.append("ups_type = 'ups_mib_standard'")
                print("   [!] UPS Type debe ser 'ups_mib_standard'")
            
            if needs_update:
                print()
                print(f"Este dispositivo NECESITA actualizacion:")
                for update in updates:
                    print(f"   - {update}")
                print()
                
                confirm = input(f"Actualizar dispositivo ID {dev['id']}? (s/n): ")
                if confirm.lower() == 's':
                    cursor.execute("""
                        UPDATE monitoreo_config 
                        SET snmp_version = 0, ups_type = 'ups_mib_standard'
                        WHERE id = ?
                    """, (dev['id'],))
                    conn.commit()
                    print(f"[OK] Dispositivo ID {dev['id']} actualizado!")
                else:
                    print("[X] Actualizacion cancelada")
            else:
                print("[OK] Este dispositivo ya tiene la configuracion correcta!")
            
            print("-" * 60)
            print()
        
        # Verificar configuracion final
        print("\n" + "="*60)
        print("  CONFIGURACION FINAL")
        print("="*60)
        
        cursor.execute("SELECT * FROM monitoreo_config WHERE ip = ?", ('192.168.0.100',))
        devices = cursor.fetchall()
        
        for dev in devices:
            print(f"\nID {dev['id']}: {dev['nombre'] or dev['ip']}")
            print(f"  snmp_version: {dev.get('snmp_version', 'N/A')}")
            print(f"  ups_type: {dev.get('ups_type', 'N/A')}")
        
        print("\n" + "="*60)
        print("  REINICIA EL SERVIDOR PARA APLICAR CAMBIOS")
        print("="*60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
