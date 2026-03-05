# -*- coding: utf-8 -*-
"""
Script para actualizar el UPS 192.168.0.100 de SNMPv2c a SNMPv1
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
    print("  ACTUALIZANDO UPS 192.168.0.100 A SNMPV1")
    print("=" * 60)
    print()

    try:
        conn = get_connection()
        cursor = conn.cursor(row_factory=dict_row)

        cursor.execute("SELECT * FROM monitoreo_config WHERE ip = %s", ('192.168.0.100',))
        device = cursor.fetchone()

        if not device:
            print("ERROR: No se encontro el UPS 192.168.0.100 en la base de datos")
            print()
            print("Opciones:")
            print("  1. Verifica que el UPS este agregado en /monitoreo")
            print("  2. Ejecuta: python agregar_ups_snmpv1.py")
            return

        print("Dispositivo encontrado:")
        print("  * ID: {}".format(device['id']))
        print("  * IP: {}".format(device['ip']))
        print("  * Nombre: {}".format(device.get('nombre') or 'Sin nombre'))
        print("  * Protocolo: {}".format(device.get('protocolo')))

        community = device.get('snmp_community', 'public')
        version = device.get('snmp_version')
        if version is not None:
            version_str = 'SNMPv1' if version == 0 else 'SNMPv2c' if version == 1 else 'No definida'
        else:
            version_str = 'No definida'

        print("  * Community: {}".format(community))
        print("  * Version actual: {}".format(version_str))
        print()

        confirm = input("Actualizar a SNMPv1? (s/n): ")
        if confirm.lower() != 's':
            print("Cancelado.")
            return

        cursor.execute("""
            UPDATE monitoreo_config
            SET snmp_version = 0
            WHERE ip = %s
        """, ('192.168.0.100',))

        conn.commit()

        print()
        print("OK - UPS actualizado a SNMPv1!")
        print()
        print("El cambio surtira efecto en unos segundos.")
        print("Ve a http://localhost:5000/monitoreo")
        print()
        print("Deberas ver el UPS conectandose automaticamente.")

    except Exception as e:
        print("ERROR: {}".format(e))
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
