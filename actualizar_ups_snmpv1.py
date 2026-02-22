# -*- coding: utf-8 -*-
"""
Script para actualizar el UPS 192.168.0.100 de SNMPv2c a SNMPv1
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
    print("  ACTUALIZANDO UPS 192.168.0.100 A SNMPV1")
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
            print("ERROR: No se encontro el UPS 192.168.0.100 en la base de datos")
            print()
            print("Opciones:")
            print("  1. Verifica que el UPS este agregado en /monitoreo")
            print("  2. Ejecuta: python agregar_ups_snmpv1.py")
            return
        
        print("Dispositivo encontrado:")
        print("  * ID: {}".format(device['id']))
        print("  * IP: {}".format(device['ip']))
        print("  * Nombre: {}".format(device['nombre'] or 'Sin nombre'))
        print("  * Protocolo: {}".format(device['protocolo']))
        
        # Acceso seguro a columnas que pueden no existir
        try:
            community = device['snmp_community']
        except (IndexError, KeyError):
            community = 'public'
        
        try:
            version = device['snmp_version']
            version_str = 'SNMPv1' if version == 0 else 'SNMPv2c' if version == 1 else 'No definida'
        except (IndexError, KeyError):
            version_str = 'No definida'
        
        print("  * Community: {}".format(community))
        print("  * Version actual: {}".format(version_str))
        print()
        
        confirm = input("Actualizar a SNMPv1? (s/n): ")
        if confirm.lower() != 's':
            print("Cancelado.")
            return
        
        # Actualizar a SNMPv1
        cursor.execute("""
            UPDATE monitoreo_config 
            SET snmp_version = 0
            WHERE ip = ?
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
