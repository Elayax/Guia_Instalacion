# -*- coding: utf-8 -*-
"""
Actualizar UPS a INVT Enterprise (es el que funciona)
Usa PostgreSQL (configurado en app/config.py)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from app.config import BaseConfig


def main():
    print("=" * 60)
    print("  ACTUALIZANDO UPS 192.168.0.100 A INVT ENTERPRISE")
    print("=" * 60)
    print()
    print("RAZON: El UPS NO soporta OIDs UPS-MIB estandar.")
    print("       Solo responde a OIDs INVT Enterprise personalizados.")
    print()

    try:
        conn = psycopg2.connect(BaseConfig.DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE monitoreo_config
            SET snmp_version = 0,
                ups_type = 'invt_enterprise'
            WHERE ip = %s
        """, ('192.168.0.100',))

        conn.commit()

        print("[OK] UPS actualizado!")
        print()
        print("Configuracion aplicada:")
        print("  - snmp_version: 0 (SNMPv1)")
        print("  - ups_type: invt_enterprise")
        print()
        print("=" * 60)
        print("  EL SERVIDOR SE REINICIARA AUTOMATICAMENTE")
        print("  ESPERA 10 SEGUNDOS Y REFRESCA EL NAVEGADOR")
        print("=" * 60)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
