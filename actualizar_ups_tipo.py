# -*- coding: utf-8 -*-
"""
Script para actualizar el UPS 192.168.0.100 a ups_mib_standard
"""

import sys
import os
import sqlite3

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    # Conectar a la BD
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'Equipos.db')
    
    print("="*60)
    print("  ACTUALIZANDO UPS 192.168.0.100 A UPS-MIB STANDARD")
    print("="*60)
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Buscar el dispositivo
        cursor.execute("SELECT * FROM monitoreo_config WHERE ip = ?", ('192.168.0.100',))
        device = cursor.fetchone()
        
        if not device:
            print("ERROR: No se encontro el UPS 192.168.0.100")
            return
        
        print("Dispositivo encontrado:")
        print("  * ID: {}".format(device['id']))
        print("  * IP: {}".format(device['ip']))
        print("  * Nombre: {}".format(device['nombre'] or 'Sin nombre'))
       
        try:
            current_type = device['ups_type']
        except (IndexError, KeyError):
            current_type = 'No definido'
        
        print("  * Tipo actual: {}".format(current_type))
        print()
        
        confirm = input("Actualizar a 'ups_mib_standard' (monofasico)? (s/n): ")
        if confirm.lower() != 's':
            print("Cancelado.")
            return
        
        # Actualizar a ups_mib_standard
        cursor.execute("""
            UPDATE monitoreo_config 
            SET ups_type = 'ups_mib_standard'
            WHERE ip = ?
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
