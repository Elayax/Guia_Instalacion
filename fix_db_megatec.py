
import sqlite3
import os

def fix_db():
    db_path = os.path.join('app', 'Equipos.db')
    
    if not os.path.exists(db_path):
        print(f"Error: No existe {db_path}")
        return

    print(f"Conectando a {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si existe fases/phases
        try:
            cursor.execute("SELECT phases FROM monitoreo_config LIMIT 1")
        except sqlite3.OperationalError:
            print("Columna 'phases' no existe. Se agregará si es necesario (o usar ups_type).")
        
        # Actualizar 192.168.0.100
        # Usamos 'invt_minimal' como ups_type para que el Frontend detecte monofasico (ver monitoreo.html)
        # Y el Backend usara MinimalSNMPClient porque no es 'ups_mib_standard'
        print("Actualizando 192.168.0.100 a 'invt_minimal' (Megatec) + SNMPv1...")
        
        cursor.execute("""
            UPDATE monitoreo_config 
            SET ups_type = 'invt_minimal', 
                snmp_version = 0,
                port = 161,
                community = 'public'
            WHERE ip = '192.168.0.100'
        """)
        
        if cursor.rowcount > 0:
            print("✅ Actualización exitosa en BD.")
        else:
            print("⚠️ No se encontró el dispositivo en la BD. Creando...")
            # Insertar si no existe
            cursor.execute("""
                INSERT INTO monitoreo_config (nombre, ip, port, community, snmp_version, ups_type, protocolo)
                VALUES ('UPS Megatec', '192.168.0.100', 161, 'public', 0, 'invt_minimal', 'snmp')
            """)
            print("✅ Dispositivo creado.")
            
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error SQL: {e}")

if __name__ == '__main__':
    fix_db()
