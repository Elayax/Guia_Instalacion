
import sqlite3
import os

def update():
    path = os.path.join(os.getcwd(), 'app', 'Equipos.db')
    if not os.path.exists(path):
         # Try internal path if running from root
         path = os.path.join(os.getcwd(), 'app', 'Equipos.db')
    
    print(f"Conectando a {path}...")
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    
    # ups_type -> 'invt_minimal' (para que el frontend detecte monofasico y backend use MinimalClient)
    # snmp_version -> 0 (v1)
    
    cur.execute("""
        UPDATE monitoreo_config
        SET ups_type = 'invt_minimal',
            snmp_version = 0,
            protocolo = 'snmp',
            snmp_community = 'public'
        WHERE ip = '192.168.0.100'
    """)
    
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

if __name__ == '__main__':
    update()
