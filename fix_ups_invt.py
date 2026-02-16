# -*- coding: utf-8 -*-
"""
Actualizar UPS a INVT Enterprise (es el que funciona)
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'Equipos.db')
    
    print("="*60)
    print("  ACTUALIZANDO UPS 192.168.0.100 A INVT ENTERPRISE")
    print("="*60)
    print()
    print("RAZON: El UPS NO soporta OIDs UPS-MIB estandar.")
    print("       Solo responde a OIDs INVT Enterprise personalizados.")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Actualizar a INVT
        cursor.execute("""
            UPDATE monitoreo_config 
            SET snmp_version = 0, 
                ups_type = 'invt_enterprise'
            WHERE ip = ?
        """, ('192.168.0.100',))
        
        conn.commit()
        
        print("[OK] UPS actualizado!")
        print()
        print("Configuracion aplicada:")
        print("  - snmp_version: 0 (SNMPv1)")
        print("  - ups_type: invt_enterprise")
        print()
        print("="*60)
        print("  EL SERVIDOR SE REINICIARA AUTOMATICAMENTE")
        print("  ESPERA 10 SEGUNDOS Y REFRESCA EL NAVEGADOR")
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
