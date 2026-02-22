
import sqlite3
import os

def check():
    path = os.path.join('app', 'Equipos.db')
    if not os.path.exists(path):
        print(f"Error: {path} no existe")
        return
        
    conn = sqlite3.connect(path)
    # PRAGMA para ver columnas
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(monitoreo_config)")
    rows = cur.fetchall()
    print("Tabla monitoreo_config:")
    for r in rows:
        print(f" - {r[1]} ({r[2]}) {r[4]}") # name, type, dflt_value
        
    # Ver datos actuales del UPS
    cur.execute("SELECT * FROM monitoreo_config WHERE ip = '192.168.0.100'")
    ups = cur.fetchone()
    if ups:
        print("\nDatos actuales UPS 192.168.0.100:")
        # Mapear columnas a valores
        cols = [r[1] for r in rows]
        for i, val in enumerate(ups):
            print(f" {cols[i]}: {val}")
    else:
        print("\nUPS 192.168.0.100 no encontrado en BD")

    conn.close()

if __name__ == '__main__':
    check()
