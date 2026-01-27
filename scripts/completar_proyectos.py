# -*- coding: utf-8 -*-
"""
Script para completar datos faltantes en proyectos recuperados.
Permite rellenar voltaje, fases y longitud de forma interactiva.
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

sys.path.insert(0, os.path.dirname(__file__))

from app.base_datos import GestorDB
from app.migration_tools import MigradorProyectos


def mostrar_proyecto(proyecto):
    """Muestra información del proyecto de forma legible"""
    print(f"\n{'='*70}")
    print(f"PEDIDO: {proyecto['pedido']}")
    print(f"{'='*70}")
    print(f"Cliente: {proyecto['cliente_snap']}")
    print(f"Sucursal: {proyecto['sucursal_snap']}")
    print(f"UPS: {proyecto['modelo_snap']} ({proyecto['potencia_snap']} kVA)")
    print(f"\nDatos actuales:")
    print(f"  - Voltaje: {proyecto['voltaje'] or 'NO DEFINIDO'}")
    print(f"  - Fases: {proyecto['fases'] or 'NO DEFINIDO'}")
    print(f"  - Longitud: {proyecto['longitud'] or 'NO DEFINIDO'}")
    print(f"  - ID UPS: {proyecto['id_ups'] or 'NO DEFINIDO'}")
    print(f"  - ID Batería: {proyecto['id_bateria'] or 'NO DEFINIDO'}")
    print(f"{'='*70}\n")

def solicitar_voltaje():
    """Solicita voltaje al usuario con validación"""
    while True:
        voltaje = input("Voltaje (V) [220, 380, 440, etc.]: ").strip()
        if not voltaje:
            print("❌ El voltaje es obligatorio")
            continue
        try:
            voltaje_num = float(voltaje)
            if voltaje_num <= 0:
                print("❌ El voltaje debe ser positivo")
                continue
            if voltaje_num > 1000:
                resp = input(f"⚠️  {voltaje_num}V parece muy alto. ¿Confirmar? (s/n): ")
                if resp.lower() != 's':
                    continue
            return voltaje_num
        except ValueError:
            print("❌ Debe ser un número válido")

def solicitar_fases():
    """Solicita número de fases con validación"""
    while True:
        fases = input("Fases [1 o 3]: ").strip()
        if not fases:
            print("❌ Las fases son obligatorias")
            continue
        if fases in ['1', '3']:
            return int(fases)
        print("❌ Debe ser 1 o 3")

def solicitar_longitud():
    """Solicita longitud de cable con validación"""
    while True:
        longitud = input("Longitud del cable (metros) [ej: 15, 25.5]: ").strip()
        if not longitud:
            print("❌ La longitud es obligatoria")
            continue
        try:
            longitud_num = float(longitud)
            if longitud_num <= 0:
                print("❌ La longitud debe ser positiva")
                continue
            if longitud_num > 200:
                resp = input(f"⚠️  {longitud_num}m parece muy largo. ¿Confirmar? (s/n): ")
                if resp.lower() != 's':
                    continue
            return longitud_num
        except ValueError:
            print("❌ Debe ser un número válido")

def confirmar_datos(datos):
    """Muestra resumen y pide confirmación"""
    print(f"\n{'─'*50}")
    print("RESUMEN DE DATOS A GUARDAR:")
    print(f"{'─'*50}")
    for key, value in datos.items():
        if value is not None:
            print(f"  {key}: {value}")
    print(f"{'─'*50}")
    resp = input("\n¿Guardar estos datos? (s/n): ")
    return resp.lower() == 's'

def completar_proyecto_interactivo(proyecto, migrador, db):
    """Completa datos de un proyecto de forma interactiva"""
    mostrar_proyecto(proyecto)
    
    # Intentar recuperar id_ups automáticamente
    if not proyecto.get('id_ups'):
        print("🔍 Intentando recuperar UPS automáticamente...")
        recuperacion = migrador.recuperar_id_ups_automatico(proyecto)
        
        if recuperacion:
            ups = recuperacion['ups_encontrado']
            print(f"✅ UPS encontrado: {ups['Nombre_del_Producto']} ({ups['Capacidad_kVA']} kVA)")
            print(f"   Confianza: {recuperacion['confianza'].upper()}")
            
            if recuperacion['confianza'] == 'alta':
                resp = input("\n¿Usar este UPS? (s/n): ")
                if resp.lower() == 's':
                    proyecto['id_ups'] = recuperacion['id_ups']
                    print("✅ UPS asignado automáticamente")
            elif recuperacion.get('alternativas'):
                print(f"\n⚠️  Múltiples opciones encontradas ({len(recuperacion['alternativas'])})")
                for i, alt in enumerate(recuperacion['alternativas'][:5], 1):
                    print(f"  {i}. {alt['Nombre_del_Producto']} ({alt['Capacidad_kVA']} kVA) - ID: {alt['id']}")
                
                seleccion = input("\nSeleccionar opción (número) o 's' para saltar: ").strip()
                if seleccion.isdigit():
                    idx = int(seleccion) - 1
                    if 0 <= idx < len(recuperacion['alternativas']):
                        proyecto['id_ups'] = recuperacion['alternativas'][idx]['id']
                        print(f"✅ UPS asignado: {recuperacion['alternativas'][idx]['Nombre_del_Producto']}")
        else:
            print("❌ No se pudo recuperar UPS automáticamente")
            print("   Deberás asignarlo manualmente desde la interfaz web")
    
    # Recopilar datos faltantes
    datos_nuevos = {}
    
    if proyecto.get('id_ups'):
        datos_nuevos['id_ups'] = proyecto['id_ups']
    
    if not proyecto.get('voltaje'):
        print("\n📋 VOLTAJE")
        datos_nuevos['voltaje'] = solicitar_voltaje()
    
    if not proyecto.get('fases'):
        print("\n📋 FASES")
        datos_nuevos['fases'] = solicitar_fases()
    
    if not proyecto.get('longitud'):
        print("\n📋 LONGITUD DE CABLE")
        datos_nuevos['longitud'] = solicitar_longitud()
    
    # Preguntar por tiempo de respaldo (opcional)
    if not proyecto.get('tiempo_respaldo'):
        print("\n📋 TIEMPO DE RESPALDO (Opcional)")
        tiempo = input("Tiempo de respaldo en minutos (Enter para saltar): ").strip()
        if tiempo:
            try:
                datos_nuevos['tiempo_respaldo'] = float(tiempo)
            except ValueError:
                print("⚠️  Valor inválido, se omitirá tiempo de respaldo")
    
    # Confirmar y guardar
    if confirmar_datos(datos_nuevos):
        if migrador.actualizar_proyecto(proyecto['pedido'], datos_nuevos):
            print("\n✅ ¡Proyecto actualizado exitosamente!")
            return True
        else:
            print("\n❌ Error al actualizar el proyecto")
            return False
    else:
        print("\n⚠️  Cambios descartados")
        return False

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("COMPLETAR DATOS DE PROYECTOS RECUPERADOS")
    print("="*70)
    
    db = GestorDB()
    migrador = MigradorProyectos()
    
    # Obtener proyectos incompletos
    proyectos = migrador.obtener_proyectos_incompletos()
    
    if not proyectos:
        print("\n✅ No hay proyectos incompletos. ¡Todo está en orden!")
        return
    
    print(f"\n📊 Se encontraron {len(proyectos)} proyectos con datos incompletos:\n")
    
    for i, p in enumerate(proyectos, 1):
        faltantes = []
        if not p.get('id_ups'):
            faltantes.append('UPS')
        if not p.get('voltaje'):
            faltantes.append('Voltaje')
        if not p.get('fases'):
            faltantes.append('Fases')
        if not p.get('longitud'):
            faltantes.append('Longitud')
        
        print(f"  {i}. {p['pedido']} - {p['cliente_snap']} ({', '.join(faltantes)})")
    
    print(f"\n{'='*70}\n")
    
    # Modo de operación
    print("Opciones:")
    print("  1. Completar todos los proyectos (uno por uno)")
    print("  2. Completar un proyecto específico")
    print("  3. Solo mostrar reporte (sin modificar)")
    
    opcion = input("\nSeleccionar opción: ").strip()
    
    if opcion == '1':
        # Completar todos
        actualizados = 0
        for proyecto in proyectos:
            if completar_proyecto_interactivo(proyecto, migrador, db):
                actualizados += 1
            
            if proyecto != proyectos[-1]:
                continuar = input("\n¿Continuar con el siguiente proyecto? (s/n): ")
                if continuar.lower() != 's':
                    break
        
        print(f"\n{'='*70}")
        print(f"RESUMEN: {actualizados} de {len(proyectos)} proyectos actualizados")
        print(f"{'='*70}\n")
    
    elif opcion == '2':
        # Completar uno específico
        pedido = input("\nIngresa el número de pedido: ").strip()
        proyecto_encontrado = None
        
        for p in proyectos:
            if str(p['pedido']) == pedido:
                proyecto_encontrado = p
                break
        
        if proyecto_encontrado:
            completar_proyecto_interactivo(proyecto_encontrado, migrador, db)
        else:
            print(f"\n❌ Pedido '{pedido}' no encontrado en proyectos incompletos")
    
    elif opcion == '3':
        # Solo reporte
        print("\n📋 REPORTE DETALLADO\n")
        plan = migrador.ejecutar_migracion_automatica(auto_aplicar=False)
        migrador.generar_reporte_migracion(plan)
    
    else:
        print("\n❌ Opción inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
