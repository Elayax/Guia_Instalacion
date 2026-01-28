"""
Script rápido para probar conexión SNMP con UPS.
Basado en el código del usuario con integración al SNMPClient existente.

Uso:
    python tests/test_snmp_quick.py --ip 192.168.1.100
    python tests/test_snmp_quick.py --ip 10.147.17.2 --port 8161

Autor: Sistema de Monitoreo UPS
Fecha: 2026-01-27
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pysnmp.hlapi.asyncio import *
from app.services.protocols.snmp_client import SNMPClient, SNMPClientError


async def consultar_ups(ip_address, port=161, community='public'):
    """
    Consulta UPS usando SNMP de forma asíncrona.
    Versión adaptada del código del usuario.
    """
    print(f"\n{'='*70}")
    print(f"📡 PROBANDO CONEXIÓN SNMP")
    print(f"{'='*70}")
    print(f"  IP: {ip_address}")
    print(f"  Puerto: {port}")
    print(f"  Community: {community}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # OIDs sacados del archivo INVT_MIB.csv (del usuario)
    oids = {
        "Modelo": "1.3.6.1.4.1.56788.1.1.1.1.3.0",  # upsInfoModel
        "Voltaje Batería": "1.3.6.1.4.1.56788.1.1.1.3.5.1.0",  # Voltaje batería (con escala x0.1)
        "Carga Batería": "1.3.6.1.4.1.56788.1.1.1.3.5.3.0",  # % Carga batería
        "Temperatura": "1.3.6.1.4.1.56788.1.1.1.3.5.5.0",  # Temperatura batería
        "Voltaje Entrada": "1.3.6.1.4.1.56788.1.1.1.3.2.1.0",  # Voltaje entrada fase A
        "Voltaje Salida": "1.3.6.1.4.1.56788.1.1.1.3.3.1.0",  # Voltaje salida fase A
    }

    resultados = {}
    
    for nombre, oid in oids.items():
        try:
            errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=1),  # SNMPv2c
                await UdpTransportTarget.create((ip_address, port), timeout=5, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )

            if errorIndication:
                print(f"❌ {nombre}: Error de conexión - {errorIndication}")
                resultados[nombre] = None
            elif errorStatus:
                print(f"❌ {nombre}: Error SNMP - {errorStatus.prettyPrint()}")
                resultados[nombre] = None
            else:
                for varBind in varBinds:
                    valor = varBind[1]
                    valor_str = str(valor)
                    
                    # Aplicar factor de escala para voltaje batería
                    if nombre == "Voltaje Batería":
                        try:
                            valor_num = float(valor_str) * 0.1
                            valor_str = f"{valor_num:.1f} V"
                        except:
                            valor_str = f"{valor_str} (raw)"
                    elif nombre in ["Carga Batería"]:
                        valor_str = f"{valor_str} %"
                    elif nombre == "Temperatura":
                        valor_str = f"{valor_str} °C"
                    elif "Voltaje" in nombre:
                        valor_str = f"{valor_str} V"
                    
                    print(f"✅ {nombre}: {valor_str}")
                    resultados[nombre] = valor_str
                    
        except Exception as e:
            print(f"❌ {nombre}: Excepción - {e}")
            resultados[nombre] = None
    
    return resultados


def consultar_ups_sync(ip_address, port=161, community='public'):
    """Wrapper síncrono para llamar desde CLI."""
    return asyncio.run(consultar_ups(ip_address, port, community))


def test_con_snmp_client(ip_address, port=161, community='public'):
    """
    Prueba usando la clase SNMPClient del proyecto.
    Método alternativo más robusto.
    """
    print(f"\n{'='*70}")
    print(f"🔍 PRUEBA CON SNMPClient (Método Alternativo)")
    print(f"{'='*70}\n")
    
    try:
        client = SNMPClient(ip_address, port, community, timeout=5, retries=2)
        
        # Test de conectividad básica
        success, message = client.test_connection()
        print(f"  Conectividad: {message}")
        
        if success:
            # Leer algunos OIDs críticos
            print(f"\n  📊 Leyendo parámetros críticos...\n")
            
            critical_oids = {
                'Modelo': '.1.3.6.1.4.1.56788.1.1.1.1.3.0',
                'Voltaje Batería': '.1.3.6.1.4.1.56788.1.1.1.3.5.1.0',
                'Carga Batería': '.1.3.6.1.4.1.56788.1.1.1.3.5.3.0',
            }
            
            for nombre, oid in critical_oids.items():
                try:
                    valor = client.get_oid(oid)
                    if valor:
                        if nombre == "Voltaje Batería":
                            valor_num = float(valor) * 0.1
                            print(f"  ✅ {nombre}: {valor_num:.1f} V")
                        elif nombre == "Carga Batería":
                            print(f"  ✅ {nombre}: {valor} %")
                        else:
                            print(f"  ✅ {nombre}: {valor}")
                    else:
                        print(f"  ⚠️ {nombre}: Sin respuesta")
                except SNMPClientError as e:
                    print(f"  ❌ {nombre}: {e}")
        
        return success
        
    except Exception as e:
        print(f"  ❌ Error inicializando cliente: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Prueba rápida de conexión SNMP con UPS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python tests/test_snmp_quick.py --ip 192.168.1.100
  python tests/test_snmp_quick.py --ip 10.147.17.2 --port 8161
  python tests/test_snmp_quick.py --ip 10.147.17.2 --port 8161 --community private
        """
    )
    
    parser.add_argument('--ip', required=True, help='Dirección IP del UPS')
    parser.add_argument('--port', type=int, default=161, help='Puerto SNMP (default: 161)')
    parser.add_argument('--community', default='public', help='Community string (default: public)')
    parser.add_argument('--method', choices=['async', 'client', 'both'], default='both',
                       help='Método de prueba (default: both)')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  🔧 SCRIPT DE PRUEBA SNMP - SISTEMA UPS")
    print("="*70)
    
    success_async = True
    success_client = True
    
    # Método 1: Async directo (código del usuario)
    if args.method in ['async', 'both']:
        try:
            resultados = consultar_ups_sync(args.ip, args.port, args.community)
            # Verificar si al menos un valor fue leído
            success_async = any(v is not None for v in resultados.values())
        except Exception as e:
            print(f"\n❌ Error en prueba async: {e}")
            success_async = False
    
    # Método 2: SNMPClient (método del proyecto)
    if args.method in ['client', 'both']:
        try:
            success_client = test_con_snmp_client(args.ip, args.port, args.community)
        except Exception as e:
            print(f"\n❌ Error en prueba con SNMPClient: {e}")
            success_client = False
    
    # Resumen final
    print(f"\n{'='*70}")
    print(f"  📋 RESUMEN")
    print(f"{'='*70}")
    if args.method == 'both':
        print(f"  Método Async: {'✅ EXITOSO' if success_async else '❌ FALLIDO'}")
        print(f"  Método SNMPClient: {'✅ EXITOSO' if success_client else '❌ FALLIDO'}")
        overall_success = success_async or success_client
    elif args.method == 'async':
        overall_success = success_async
    else:
        overall_success = success_client
    
    print(f"\n  Estado General: {'✅ CONEXIÓN EXITOSA' if overall_success else '❌ CONEXIÓN FALLIDA'}")
    print(f"{'='*70}\n")
    
    sys.exit(0 if overall_success else 1)


if __name__ == '__main__':
    main()
