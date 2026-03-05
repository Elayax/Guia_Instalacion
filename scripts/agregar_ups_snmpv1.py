# -*- coding: utf-8 -*-
"""
Script para agregar el UPS 192.168.0.100 con SNMPv1
Usa los datos detectados por la auto-detección
"""

import sys
import os

# Agregar el directorio actual al path para importar app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.base_datos import GestorDB

def main():
    db = GestorDB()
    
    # Datos del UPS detectado
    datos = {
        'ip': '192.168.0.100',
        'nombre': 'UPS Segundo',
        'protocolo': 'snmp',
        'snmp_port': 161,
        'snmp_community': 'public',
        'snmp_version': 0,  # 0 = SNMPv1, 1 = SNMPv2c
        'port': 161,  # Para consistencia
        'slave_id': 1  # No se usa en SNMP pero es requerido por la tabla
    }
    
    print("="*60)
    print("  AGREGANDO UPS 192.168.0.100 CON SNMPV1")
    print("="*60)
    print()
    print("Configuracion detectada:")
    print("  * IP: {}".format(datos['ip']))
    print("  * Nombre: {}".format(datos['nombre']))
    print("  * Protocolo: {}".format(datos['protocolo'].upper()))
    print("  * Puerto: {}".format(datos['snmp_port']))
    print("  * Community: {}".format(datos['snmp_community']))
    print("  * Version: SNMPv1")
    print()
    
    confirm = input("Deseas agregar este UPS? (s/n): ")
    if confirm.lower() != 's':
        print("Cancelado.")
        return
    
    if db.agregar_monitoreo_ups(datos):
        print()
        print("OK - UPS agregado exitosamente!")
        print()
        print("Siguientes pasos:")
        print("  1. Abre: http://localhost:5000/monitoreo")
        print("  2. Deberias ver el UPS conectandose automaticamente")
        print("  3. Si no aparece, reinicia el servidor: python run.py")
        print()
    else:
        print("ERROR - al agregar el UPS (posiblemente ya existe)")
        print()
        print("Si ya existe y quieres actualizarlo:")
        print("  1. Ve a http://localhost:5000/monitoreo")
        print("  2. Elimina el dispositivo existente")
        print("  3. Ejecuta este script nuevamente")

if __name__ == '__main__':
    main()
