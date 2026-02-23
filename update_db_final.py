"""
Actualizar UPS 192.168.0.100 a invt_minimal (Megatec v1) en PostgreSQL
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from app.config import BaseConfig


def update():
    print("Conectando a PostgreSQL...")

    try:
        conn = psycopg2.connect(BaseConfig.DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            UPDATE monitoreo_config
            SET ups_type = 'invt_minimal',
                snmp_version = 0,
                protocolo = 'snmp',
                snmp_community = 'public'
            WHERE ip = %s
        """, ('192.168.0.100',))

        if cur.rowcount > 0:
            print("[OK] UPS 192.168.0.100 actualizado correctamente a 'invt_minimal' (Megatec v1)")
        else:
            print("[WARN] No encontrado, insertando nuevo...")
            cur.execute("""
                INSERT INTO monitoreo_config (nombre, ip, port, snmp_port, snmp_community, snmp_version, ups_type, protocolo)
                VALUES ('UPS Megatec', '192.168.0.100', 161, 161, 'public', 0, 'invt_minimal', 'snmp')
            """)
            print("[OK] UPS Creado.")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update()
