"""
Script de Diagnóstico para Conexiones UPS
Prueba conectividad y obtiene datos de los UPS configurados
"""

import asyncio
import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.base_datos import GestorDB
from app.services.protocols.snmp_client import SNMPClient

async def test_snmp_connection(ip, community='public', port=161):
    """Prueba conexión SNMP a un UPS"""
    print(f"\n{'='*60}")
    print(f"🔍 Probando conexión SNMP a {ip}:{port}")
    print(f"   Community: {community}")
    print(f"{'='*60}")
    
    client = SNMPClient(community=community, port=port)
    
    try:
        data = await client.get_ups_data(ip)
        
        if data:
            print(f"\n✅ CONEXIÓN EXITOSA!")
            print(f"\n📊 Datos recibidos del UPS:")
            print(f"-" * 60)
            
            # Agrupar datos por categoría
            print(f"\n🔌 ENTRADA:")
            for key in ['input_voltage_l1', 'input_voltage_l2', 'input_voltage_l3', 'input_frequency']:
                if key in data:
                    print(f"   {key:25s}: {data[key]}")
            
            print(f"\n⚡ SALIDA:")
            for key in ['output_voltage_l1', 'output_voltage_l2', 'output_voltage_l3', 
                       'output_current_l1', 'output_current_l2', 'output_current_l3',
                       'output_frequency', 'output_load']:
                if key in data:
                    print(f"   {key:25s}: {data[key]}")
            
            print(f"\n🔋 BATERÍA:")
            for key in ['battery_voltage', 'battery_current', 'battery_capacity', 
                       'battery_runtime', 'battery_status']:
                if key in data:
                    print(f"   {key:25s}: {data[key]}")
            
            print(f"\n📈 POTENCIA:")
            for key in ['active_power', 'apparent_power', 'power_factor']:
                if key in data:
                    print(f"   {key:25s}: {data[key]}")
            
            print(f"\n🌡️ AMBIENTE:")
            for key in ['temperature', 'power_source']:
                if key in data:
                    print(f"   {key:25s}: {data[key]}")
            
            return True
        else:
            print(f"\n❌ Sin respuesta del UPS")
            print(f"   Posibles causas:")
            print(f"   - IP incorrecta o no alcanzable")
            print(f"   - Puerto 161 bloqueado por firewall")
            print(f"   - SNMP no habilitado en el UPS")
            print(f"   - Community string incorrecta")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR DE CONEXIÓN")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        return False

async def test_all_configured_devices():
    """Prueba todos los dispositivos configurados en la BD"""
    print(f"\n{'#'*60}")
    print(f"# TEST DE DISPOSITIVOS CONFIGURADOS EN LA BASE DE DATOS")
    print(f"{'#'*60}")
    
    db = GestorDB()
    devices = db.obtener_monitoreo_ups()
    
    if not devices:
        print(f"\n⚠️  No hay dispositivos configurados en la base de datos")
        print(f"   Agrega dispositivos desde la interfaz web:")
        print(f"   http://localhost:5000/monitoreo")
        return
    
    print(f"\n📋 Encontrados {len(devices)} dispositivo(s):\n")
    
    results = []
    for dev in devices:
        print(f"\n┌─ Dispositivo #{dev['id']}: {dev.get('nombre', 'Sin Nombre')}")
        print(f"│  IP: {dev['ip']}")
        print(f"│  Protocolo: {dev.get('protocolo', 'modbus').upper()}")
        print(f"└─ Puerto: {dev.get('snmp_port' if dev.get('protocolo') == 'snmp' else 'port', 'N/A')}")
        
        if dev.get('protocolo', 'modbus') == 'snmp':
            success = await test_snmp_connection(
                dev['ip'],
                dev.get('snmp_community', 'public'),
                dev.get('snmp_port', 161)
            )
            results.append({
                'name': dev.get('nombre', 'Sin Nombre'),
                'ip': dev['ip'],
                'success': success
            })
        else:
            print(f"\n⚠️  Protocolo Modbus - Test no implementado en este script")
            print(f"   Para probar Modbus, usa las herramientas en tests/")
            results.append({
                'name': dev.get('nombre', 'Sin Nombre'),
                'ip': dev['ip'],
                'success': None
            })
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE RESULTADOS")
    print(f"{'='*60}\n")
    
    for r in results:
        status = "✅ OK" if r['success'] else ("⏭️  N/A" if r['success'] is None else "❌ FALLO")
        print(f"  {status:10s} | {r['name']:30s} | {r['ip']}")
    
    print(f"\n{'='*60}\n")

async def test_specific_ips():
    """Prueba las IPs específicas mencionadas por el usuario"""
    print(f"\n{'#'*60}")
    print(f"# TEST DE IPs ESPECÍFICAS (UPS PRODUCTIVOS)")
    print(f"{'#'*60}")
    
    # UPS actual
    await test_snmp_connection('192.168.10.198', 'public', 161)
    
    # UPS nuevo
    await test_snmp_connection('192.168.0.100', 'public', 161)

async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnóstico de Conexiones UPS')
    parser.add_argument('--all', action='store_true', help='Probar todos los dispositivos de la BD')
    parser.add_argument('--ip', type=str, help='Probar IP específica')
    parser.add_argument('--community', type=str, default='public', help='SNMP Community (default: public)')
    parser.add_argument('--port', type=int, default=161, help='SNMP Port (default: 161)')
    parser.add_argument('--production', action='store_true', help='Probar UPS en producción (192.168.10.198 y 192.168.0.100)')
    
    args = parser.parse_args()
    
    if args.all:
        await test_all_configured_devices()
    elif args.ip:
        await test_snmp_connection(args.ip, args.community, args.port)
    elif args.production:
        await test_specific_ips()
    else:
        # Modo interactivo
        print(f"\n🔧 DIAGNÓSTICO DE CONEXIONES UPS")
        print(f"{'='*60}\n")
        print(f"Opciones:")
        print(f"  1. Probar todos los dispositivos configurados")
        print(f"  2. Probar UPS en producción (192.168.10.198 y 192.168.0.100)")
        print(f"  3. Probar IP específica")
        print(f"  4. Salir\n")
        
        choice = input("Selecciona una opción (1-4): ").strip()
        
        if choice == '1':
            await test_all_configured_devices()
        elif choice == '2':
            await test_specific_ips()
        elif choice == '3':
            ip = input("Ingresa la IP del UPS: ").strip()
            community = input("Community string (Enter para 'public'): ").strip() or 'public'
            port = input("Puerto SNMP (Enter para 161): ").strip()
            port = int(port) if port else 161
            await test_snmp_connection(ip, community, port)
        elif choice == '4':
            print("Saliendo...")
        else:
            print("Opción inválida")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
