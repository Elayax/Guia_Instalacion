#!/usr/bin/env python3
"""
Mantenimiento periódico de BD para LBS Monitor.
Limpia datos históricos antiguos y optimiza tablas.

Uso manual:  python3 scripts/db_maintenance.py
Cron:        0 3 * * 0 cd /home/elayax/dev/LBS/Guia_Instalacion && python3 scripts/db_maintenance.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db_connection import ConnectionPool

READINGS_RETENTION_DAYS = 90
ALERTS_RETENTION_DAYS = 180


def main():
    pool = ConnectionPool.get_instance()

    # Eliminar lecturas antiguas
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM ups_readings WHERE timestamp < NOW() - INTERVAL '%s days'",
                (READINGS_RETENTION_DAYS,)
            )
            deleted_readings = cur.rowcount
        conn.commit()
    print(f"Lecturas eliminadas (>{READINGS_RETENTION_DAYS} días): {deleted_readings}")

    # Eliminar alertas resueltas antiguas
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM ups_alerts WHERE resolved = TRUE AND timestamp < NOW() - INTERVAL '%s days'",
                (ALERTS_RETENTION_DAYS,)
            )
            deleted_alerts = cur.rowcount
        conn.commit()
    print(f"Alertas resueltas eliminadas (>{ALERTS_RETENTION_DAYS} días): {deleted_alerts}")

    # VACUUM ANALYZE
    with pool.connection() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            for table in ['ups_readings', 'ups_alerts']:
                try:
                    cur.execute(f"VACUUM ANALYZE {table}")
                    print(f"VACUUM ANALYZE {table}: OK")
                except Exception as e:
                    print(f"VACUUM ANALYZE {table}: {e}")

    print("Mantenimiento completado.")


if __name__ == '__main__':
    main()
