"""
Script Rápido para Agregar el Segundo UPS
Configuración automática del nuevo UPS 192.168.0.100
"""

import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.base_datos import GestorDB

def agregar_ups_nuevo():
    """Agrega el nuevo UPS (192.168.0.100) a la configuración"""
    
    print("\n" + "="*60)
    print("🔧 CONFIGURACIÓN DE NUEVO UPS")
    print("="*60 + "\n")
    
    # Configuración del nuevo UPS
    print("📝 Ingresa los datos del nuevo UPS:\n")
    
    # IP por defecto o personalizada
    ip = input("IP del UPS [192.168.0.100]: ").strip() or "192.168.0.100"
    
    # Nombre descriptivo
    nombre = input("Nombre descriptivo [UPS-Nuevo]: ").strip() or "UPS-Nuevo"
    
    # Protocolo
    print("\nProtocolo:")
    print("  1. Modbus TCP (puerto 502)")
    print("  2. SNMP v2 (puerto 161)")
    protocolo_opt = input("Selecciona (1/2) [1]: ").strip() or "1"
    
    if protocolo_opt == "2":
        protocolo = "snmp"
        snmp_port = input("Puerto SNMP [161]: ").strip()
        snmp_port = int(snmp_port) if snmp_port else 161
        community = input("Community string [public]: ").strip() or "public"
        port = snmp_port
        slave_id = 1
    else:
        protocolo = "modbus"
        port = input("Puerto Modbus [502]: ").strip()
        port = int(port) if port else 502
        slave_id = input("Slave ID [1]: ").strip()
        slave_id = int(slave_id) if slave_id else 1
        community = "public"
        snmp_port = 161
    
    # Preparar datos
    datos = {
        'ip': ip,
        'port': port,
        'slave_id': slave_id,
        'nombre': nombre,
        'protocolo': protocolo,
        'snmp_community': community,
        'snmp_port': snmp_port
    }
    
    # Mostrar resumen
    print("\n" + "-"*60)
    print("📋 RESUMEN DE CONFIGURACIÓN:")
    print("-"*60)
    print(f"  Nombre:     {datos['nombre']}")
    print(f"  IP:         {datos['ip']}")
    print(f"  Protocolo:  {datos['protocolo'].upper()}")
    
    if protocolo == "snmp":
        print(f"  Puerto:     {datos['snmp_port']}")
        print(f"  Community:  {datos['snmp_community']}")
    else:
        print(f"  Puerto:     {datos['port']}")
        print(f"  Slave ID:   {datos['slave_id']}")
    
    print("-"*60)
    
    # Confirmar
    confirmar = input("\n¿Agregar este UPS a la configuración? (s/n) [s]: ").strip().lower()
    
    if confirmar in ['', 's', 'si', 'y', 'yes']:
        db = GestorDB()
        
        try:
            success = db.agregar_monitoreo_ups(datos)
            
            if success:
                print("\n✅ UPS agregado correctamente!")
                print(f"\n📊 Ahora puedes:")
                print(f"   1. Acceder a http://localhost:5000/monitoreo")
                print(f"   2. Verás '{nombre}' en la lista lateral")
                print(f"   3. Haz clic para visualizar sus datos en tiempo real")
                
                # Mostrar todos los dispositivos configurados
                print(f"\n📋 Dispositivos configurados actualmente:")
                dispositivos = db.obtener_monitoreo_ups()
                for i, dev in enumerate(dispositivos, 1):
                    proto = dev.get('protocolo', 'modbus').upper()
                    print(f"   {i}. {dev['nombre']:20s} | {dev['ip']:15s} | {proto}")
                
                return True
            else:
                print("\n❌ Error al agregar el UPS")
                print("   Posible causa: IP duplicada en la base de datos")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False
    else:
        print("\n⚠️  Operación cancelada")
        return False

def listar_ups_configurados():
    """Lista todos los UPS configurados"""
    db = GestorDB()
    dispositivos = db.obtener_monitoreo_ups()
    
    if not dispositivos:
        print("\n⚠️  No hay dispositivos UPS configurados")
        print("   Usa este script para agregar uno")
        return
    
    print("\n" + "="*60)
    print("📋 DISPOSITIVOS UPS CONFIGURADOS")
    print("="*60 + "\n")
    
    for dev in dispositivos:
        proto = dev.get('protocolo', 'modbus').upper()
        print(f"ID: {dev['id']}")
        print(f"  Nombre:     {dev['nombre']}")
        print(f"  IP:         {dev['ip']}")
        print(f"  Protocolo:  {proto}")
        
        if proto == "SNMP":
            print(f"  Puerto:     {dev.get('snmp_port', 161)}")
            print(f"  Community:  {dev.get('snmp_community', 'public')}")
        else:
            print(f"  Puerto:     {dev.get('port', 502)}")
            print(f"  Slave ID:   {dev.get('slave_id', 1)}")
        
        print(f"  Estado:     {dev.get('estado', 'inactivo')}")
        print()

def main():
    print("\n🔧 GESTIÓN DE DISPOSITIVOS UPS")
    print("="*60)
    
    while True:
        print("\nOpciones:")
        print("  1. Agregar nuevo UPS (192.168.0.100)")
        print("  2. Listar UPS configurados")
        print("  3. Salir")
        
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            agregar_ups_nuevo()
        elif opcion == "2":
            listar_ups_configurados()
        elif opcion == "3":
            print("\n👋 Saliendo...\n")
            break
        else:
            print("\n❌ Opción inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
