# -*- coding: utf-8 -*-
"""
Script para actualizar el UPS 192.168.0.100 a ups_mib_standard
Usa PostgreSQL (configurado en app/config.py)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg
from psycopg.rows import dict_row
from app.config import BaseConfig


def get_connection():
    return psycopg.connect(BaseConfig.DATABASE_URL)


def main():
    print("=" * 60)
    print("  ACTUALIZANDO UPS 192.168.0.100 A UPS-MIB STANDARD")
    print("=" * 60)
    print()

    try:
        conn = get_connection()
        cursor = conn.cursor(row_factory=dict_row)

        cursor.execute("SELECT * FROM monitoreo_config WHERE ip = %s", ('192.168.0.100',))
        device = cursor.fetchone()

        if not device:
            print("ERROR: No se encontro el UPS 192.168.0.100")
            return

        print("Dispositivo encontrado:")
        print("  * ID: {}".format(device['id']))
        print("  * IP: {}".format(device['ip']))
        print("  * Nombre: {}".format(device.get('nombre') or 'Sin nombre'))

        current_type = device.get('ups_type', 'No definido')
        print("  * Tipo actual: {}".format(current_type))
        print()

        confirm = input("Actualizar a 'ups_mib_standard' (monofasico)? (s/n): ")
        if confirm.lower() != 's':
            print("Cancelado.")
            return

        cursor.execute("""
            UPDATE monitoreo_config
            SET ups_type = 'ups_mib_standard'
            WHERE ip = %s
        """, ('192.168.0.100',))

        conn.commit()

        print()
        print("OK - UPS actualizado a ups_mib_standard!")
        print()
        print("El sistema ahora:")
        print("  * Usara UPSMIBClient (optimizado)")
        print("  * Solo consultara los 35 OIDs disponibles")
        print("  * Detectara automaticamente que es monofasico")
        print("  * Mostrara solo L1 en el dashboard")
        print()
        print("El cambio surtira efecto en unos segundos.")
        print("Ve a http://localhost:5000/monitoreo")

    except Exception as e:
        print("ERROR: {}".format(e))
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
