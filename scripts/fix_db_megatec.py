"""
Fix para UPS Megatec: actualizar configuracion en PostgreSQL
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from app.config import BaseConfig


def fix_db():
    print("Conectando a PostgreSQL...")

    try:
        conn = psycopg2.connect(BaseConfig.DATABASE_URL)
        cursor = conn.cursor()

        print("Actualizando 192.168.0.100 a 'invt_minimal' (Megatec) + SNMPv1...")

        cursor.execute("""
            UPDATE monitoreo_config
            SET ups_type = 'invt_minimal',
                snmp_version = 0,
                port = 161,
                community = 'public'
            WHERE ip = %s
        """, ('192.168.0.100',))

        if cursor.rowcount > 0:
            print("Actualizacion exitosa en BD.")
        else:
            print("No se encontro el dispositivo en la BD. Creando...")
            cursor.execute("""
                INSERT INTO monitoreo_config (nombre, ip, port, community, snmp_version, ups_type, protocolo)
                VALUES ('UPS Megatec', '192.168.0.100', 161, 'public', 0, 'invt_minimal', 'snmp')
            """)
            print("Dispositivo creado.")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error SQL: {e}")

if __name__ == '__main__':
    fix_db()
