"""
Verificar esquema de la tabla monitoreo_config en PostgreSQL
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from app.config import BaseConfig


def check():
    try:
        conn = psycopg2.connect(BaseConfig.DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'monitoreo_config'
            ORDER BY ordinal_position
        """)
        rows = cur.fetchall()

        if not rows:
            print("Tabla monitoreo_config no encontrada en PostgreSQL")
            return

        print("Tabla monitoreo_config:")
        for r in rows:
            print(f" - {r[0]} ({r[1]}) default={r[2]}")

        cur.execute("SELECT * FROM monitoreo_config WHERE ip = '192.168.0.100'")
        ups = cur.fetchone()
        if ups:
            print("\nDatos actuales UPS 192.168.0.100:")
            col_names = [desc[0] for desc in cur.description]
            for i, val in enumerate(ups):
                print(f" {col_names[i]}: {val}")
        else:
            print("\nUPS 192.168.0.100 no encontrado en BD")

        conn.close()

    except Exception as e:
        print(f"Error conectando a PostgreSQL: {e}")

if __name__ == '__main__':
    check()
