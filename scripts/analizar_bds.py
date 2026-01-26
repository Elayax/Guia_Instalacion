# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

# Forzar salida UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def analizar_base_datos(db_path, nombre_db):
    print(f"\n{'='*60}")
    print(f"ANALISIS DE: {nombre_db}")
    print(f"Ruta: {db_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(db_path):
        print(f"X Base de datos NO ENCONTRADA: {db_path}\n")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Listar tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [row['name'] for row in cursor.fetchall()]
    print(f"TABLAS ENCONTRADAS ({len(tablas)}):")
    for tabla in tablas:
        print(f"   - {tabla}")
    
    # 2. Analizar tabla proyectos_publicados
    if 'proyectos_publicados' in tablas:
        print(f"\nTABLA proyectos_publicados:")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) as total FROM proyectos_publicados")
        total = cursor.fetchone()['total']
        print(f"   Total de proyectos: {total}")
        
        # Mostrar columnas
        cursor.execute("PRAGMA table_info(proyectos_publicados)")
        columnas = cursor.fetchall()
        print(f"\n   Columnas ({len(columnas)}):")
        for col in columnas:
            print(f"      {col['name']} ({col['type']})")
        
        # Mostrar primeros 3 registros
        if total > 0:
            print(f"\n   Primeros 3 proyectos:")
            cursor.execute("""
                SELECT pedido, cliente_snap, sucursal_snap, modelo_snap, 
                       voltaje, fases, longitud, id_ups, id_bateria
                FROM proyectos_publicados 
                LIMIT 3
            """)
            for i, row in enumerate(cursor.fetchall(), 1):
                print(f"\n   Proyecto {i}:")
                print(f"      Pedido: {row['pedido']}")
                print(f"      Cliente: {row['cliente_snap']}")
                print(f"      Sucursal: {row['sucursal_snap']}")
                print(f"      UPS: {row['modelo_snap']}")
                print(f"      Config: {row['voltaje']}V, {row['fases']}F, {row['longitud']}m")
                print(f"      IDs: UPS={row['id_ups']}, Bateria={row['id_bateria']}")
    else:
        print(f"\nX TABLA proyectos_publicados NO EXISTE")
    
    # 3. Analizar tabla clientes
    if '  clientes' in tablas:
        cursor.execute("SELECT COUNT(*) as total FROM clientes")
        total_clientes = cursor.fetchone()['total']
        print(f"\nTABLA clientes: {total_clientes} registros")
        
        if total_clientes > 0:
            cursor.execute("SELECT cliente, COUNT(*) as sucursales FROM clientes GROUP BY cliente LIMIT 3")
            print("   Primeros 3 clientes:")
            for row in cursor.fetchall():
                print(f"      - {row['cliente']}: {row['sucursales']} sucursales")
    
    # 4. Analizar tabla ups_specs
    if 'ups_specs' in tablas:
        cursor.execute("SELECT COUNT(*) as total FROM ups_specs")
        total_ups = cursor.fetchone()['total']
        print(f"\nTABLA ups_specs: {total_ups} equipos")
        
        if total_ups > 0:
            cursor.execute("""
                SELECT id, Nombre_del_Producto, Capacidad_kVA 
                FROM ups_specs 
                ORDER BY Capacidad_kVA 
                LIMIT 3
            """)
            print("   Primeros 3 UPS:")
            for row in cursor.fetchall():
                print(f"      - ID:{row['id']} | {row['Nombre_del_Producto']} ({row['Capacidad_kVA']} kVA)")
    
    # 5. Analizar tabla baterias_modelos
    if 'baterias_modelos' in tablas:
        cursor.execute("SELECT COUNT(*) as total FROM baterias_modelos")
        total_bat = cursor.fetchone()['total']
        print(f"\nTABLA baterias_modelos: {total_bat} modelos")
        
        if total_bat > 0:
            cursor.execute("SELECT modelo, capacidad_nominal_ah FROM baterias_modelos LIMIT 3")
            print("   Primeros 3 modelos:")
            for row in cursor.fetchall():
                print(f"      - {row['modelo']} ({row['capacidad_nominal_ah']} Ah)")
    
    conn.close()
    print()

# Ejecutar analisis
print("\n" + "="*60)
print("DIAGNOSTICO COMPLETO DE BASES DE DATOS")
print("="*60)

analizar_base_datos('app/Equipos.db', 'EQUIPOS.DB (Base Principal)')
analizar_base_datos('app/sistema_ups_master.db', 'SISTEMA_UPS_MASTER.DB (Base Secundaria?)')

print("\n" + "="*60)
print("ANALISIS COMPLETADO")
print("="*60)
