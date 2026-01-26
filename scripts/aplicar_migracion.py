"""
Script para aplicar migración automática de proyectos con confianza alta
"""
from app.migration_tools import MigradorProyectos

migrador = MigradorProyectos()

print("="*80)
print("APLICANDO MIGRACIÓN AUTOMÁTICA")
print("="*80)
print("\nObteniendo plan de migración...")

plan = migrador.ejecutar_migracion_automatica(auto_aplicar=False)

# Filtrar solo proyectos con confianza alta
proyectos_alta_confianza = [
    item for item in plan 
    if item['confianza'] == 'alta' and item['id_ups_recuperado']
]

print(f"\nProyectos con confianza alta: {len(proyectos_alta_confianza)}")
print(f"Proyectos que requieren atención manual: {len(plan) - len(proyectos_alta_confianza)}\n")

actualizados = 0
errores = 0

for item in proyectos_alta_confianza:
    proyecto = item['proyecto']
    pedido = proyecto['pedido']
    id_ups = item['id_ups_recuperado']
    ups_nombre = item['ups_sugerido']['Nombre_del_Producto']
    
    print(f"Actualizando Pedido {pedido}...")
    print(f"  Cliente: {proyecto['cliente_snap']} - {proyecto['sucursal_snap']}")
    print(f"  UPS: {ups_nombre} (ID: {id_ups})")
    
    datos_update = {'id_ups': id_ups}
    
    if migrador.actualizar_proyecto(pedido, datos_update):
        print(f"  OK ACTUALIZADO\n")
        actualizados += 1
    else:
        print(f"  X ERROR al actualizar\n")
        errores += 1

print("="*80)
print("RESULTADO DE LA MIGRACIÓN")
print("="*80)
print(f"Proyectos actualizados: {actualizados}/{len(proyectos_alta_confianza)}")
print(f"Errores: {errores}")

if actualizados > 0:
    print(f"\nOK Se recuperaron {actualizados} proyectos exitosamente")
    print("Los siguientes campos aún requieren completarse manualmente:")
    print("  - voltaje")
    print("  - fases")
    print("  - longitud")
    print("  - tiempo_respaldo (opcional)")
    print("  - id_bateria (opcional)")

print("\nProyectos pendientes de migración manual:")
for item in plan:
    if item['confianza'] != 'alta' or not item['id_ups_recuperado']:
        proyecto = item['proyecto']
        print(f"  - Pedido {proyecto['pedido']}: {proyecto['cliente_snap']}")

print("\n" + "="*80)
