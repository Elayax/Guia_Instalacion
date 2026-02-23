import asyncio
import sys
import os

# Aseguramos que Python encuentre la librería app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from pysnmp.hlapi.asyncio import (
        SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
        ObjectType, ObjectIdentity, next_cmd
    )
except ImportError:
    from pysnmp.hlapi.asyncio import *

async def escaneo_universal(ip):
    print(f"\n📡 --- ESCANEO UNIVERSAL (Modo Compatibilidad v1) ---")
    print(f"🎯 Objetivo: {ip}")
    print("⏳ Buscando CUALQUIER dato disponible...")

    # TRUCO 1: Usamos 'mpModel=0' que significa SNMP v1 (El más compatible)
    community = CommunityData('public', mpModel=0) 
    
    # TRUCO 2: Empezamos desde 'internet', la raíz de todo.
    # Si el UPS tiene datos, aparecerán aquí.
    oid_inicial = "1.3.6.1.2.1" 

    try:
        transport = await UdpTransportTarget.create((ip, 161), timeout=2.0, retries=2)
        engine = SnmpEngine()
        
        current_oid = ObjectType(ObjectIdentity(oid_inicial))
        
        count = 0
        errores_consecutivos = 0

        while True:
            errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
                engine,
                community,
                transport,
                ContextData(),
                current_oid
            )

            if errorIndication:
                print(f"❌ Error de red: {errorIndication}")
                break
            
            # Si el dispositivo dice "No tengo más", terminamos
            if errorStatus:
                # El error 2 (noSuchName) en v1 significa fin de la tabla
                print(f"🏁 Fin del escaneo (Status: {errorStatus.prettyPrint()})")
                break
            
            if not varBinds:
                break

            for varBind in varBinds:
                oid_res = str(varBind[0])
                val_res = varBind[1].prettyPrint()
                
                # Imprimimos todo para ver qué diablos devuelve
                print(f"🔹 {oid_res} = {val_res}")
                
                # Actualizamos para pedir el siguiente
                current_oid = ObjectType(ObjectIdentity(oid_res))
                count += 1

            # Límite de seguridad para que no se cicle infinito si hay miles de datos
            if count >= 50: 
                print("\n🛑 Pausa: Se encontraron los primeros 50 datos.")
                print("   Revisa arriba si ves algo como 'Dragon', 'UPS', o números de voltaje (120, 220, etc).")
                break

        if count == 0:
            print("\n💀 El UPS responde, pero está vacío. Posibles causas:")
            print("   1. La 'Community String' no es 'public'. (¿Tienes el manual de la tarjeta de red?)")
            print("   2. El puerto 161 UDP está bloqueado en el router (Revisar Firewall).")

    except Exception as e:
        print(f"❌ Excepción crítica: {e}")

if __name__ == "__main__":
    IP_UPS = "10.138.22.243" 
    if len(sys.argv) > 1:
        IP_UPS = sys.argv[1].strip()

    asyncio.run(escaneo_universal(IP_UPS))