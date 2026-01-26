"""
Script para eliminar proyectos problemáticos sin datos
"""
import sqlite3

# Proyectos a eliminar (según usuario: "si hay proyectos que están causando problemas o datos, solo elimínalos")
PEDIDOS_A_ELIMINAR = ['123', '2023', '11']  # Sin modelo_snap, sin datos útiles

db_path = 'app/Equipos.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("="*80)
print("ELIMINANDO PROYECTOS SIN DATOS")
print("="*80)

for pedido in PEDIDOS_A_ELIMINAR:
    # Verificar información antes de eliminar
    cursor = conn.execute("""
        SELECT pedido, cliente_snap, sucursal_snap, modelo_snap, id_ups, voltaje
        FROM proyectos_publicados
        WHERE pedido = ?
    """, (pedido,))
    proyecto = cursor.fetchone()
    
    if proyecto:
        print(f"\nEliminando Pedido {pedido}:")
        print(f"  Cliente: {proyecto['cliente_snap']}")
        print(f"  Sucursal: {proyecto['sucursal_snap']}")
        print(f"  Modelo: {proyecto['modelo_snap']} (None = sin datos)")
        print(f"  id_ups: {proyecto['id_ups']}")
        print(f"  voltaje: {proyecto['voltaje']}")
        
        conn.execute("DELETE FROM proyectos_publicados WHERE pedido = ?", (pedido,))
        print(f"  -> ELIMINADO")
    else:
        print(f"\nPedido {pedido} no encontrado")

conn.commit()

# Report final status
cursor = conn.execute("SELECT COUNT(*) as total FROM proyectos_publicados")
total_final = cursor.fetchone()['total']

cursor = conn.execute("""
    SELECT COUNT(*) as completos 
    FROM proyectos_publicados 
    WHERE id_ups IS NOT NULL
""")
completos = cursor.fetchone()['completos']

cursor = conn.execute("""
    SELECT COUNT(*) as incompletos 
    FROM proyectos_publicados 
    WHERE id_ups IS NULL OR voltaje IS NULL OR fases IS NULL
""")
incompletos = cursor.fetchone()['incompletos']

print("\n" + "="*80)
print("ESTADO FINAL DE LA BASE DE DATOS")
print("="*80)
print(f"Total de proyectos: {total_final}")
print(f"Proyectos con UPS asignado: {completos}")
print(f"Proyectos con datos incompletos: {incompletos}")

if incompletos > 0:
    print("\nProyectos que aún requieren completar voltaje/fases/longitud:")
    cursor = conn.execute("""
        SELECT pedido, cliente_snap, modelo_snap
        FROM proyectos_publicados
        WHERE id_ups IS NOT NULL AND (voltaje IS NULL OR fases IS NULL)
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  - {row['pedido']}: {row['cliente_snap']} - {row['modelo_snap']}")

conn.close()

print("\n" + "="*80)
print("LIMPIEZA COMPLETADA")
print("="*80)
