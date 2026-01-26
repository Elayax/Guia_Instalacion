with open('app/rutas.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Código de las nuevas rutas
new_routes = '''
# --- RECUPERACION DE PROYECTOS ---
@main.route('/recuperacion-proyectos')
def recuperacion_proyectos():
    """Interfaz para completar datos faltantes en proyectos antiguos"""
    from app.migration_tools import MigradorProyectos
    migrador = MigradorProyectos()
    plan = migrador.ejecutar_migracion_automatica(auto_aplicar=False)
    
    lista_ups = db.obtener_ups_todos()
    lista_baterias = db.obtener_baterias_modelos()
    
    return render_template('recuperacion_proyectos.html',
                         plan_migracion=plan,
                         ups_list=lista_ups,
                         baterias_list=lista_baterias)

@main.route('/api/completar-proyecto', methods=['POST'])
def completar_proyecto():
    """API para actualizar proyecto con datos completos"""
    from app.migration_tools import MigradorProyectos
    migrador = MigradorProyectos()
    
    datos = request.json
    pedido = datos.get('pedido')
    
    if not pedido:
        return {'success': False, 'error': 'Pedido requerido'}, 400
    
    # Extraer solo los datos válidos
    datos_update = {}
    for field in ['id_ups', 'voltaje', 'fases', 'longitud', 'tiempo_respaldo', 'id_bateria']:
        if field in datos and datos[field]:
            datos_update[field] = datos[field]
    
    if migrador.actualizar_proyecto(pedido, datos_update):
        return {'success': True}
    
    return {'success': False, 'error': 'Error al actualizar'}, 500

@main.route('/api/aplicar-migracion-masiva', methods=['POST'])
def aplicar_migracion_masiva():
    """Aplica updates a todos los proyectos con confianza alta"""
    from app.migration_tools import MigradorProyectos
    migrador = MigradorProyectos()
    
    plan = migrador.ejecutar_migracion_automatica(auto_aplicar=False)
    actualizados = 0
    errores = 0
    
    for item in plan:
        if item['confianza'] == 'alta' and item['id_ups_recuperado']:
            datos_update = {'id_ups': item['id_ups_recuperado']}
            if migrador.actualizar_proyecto(item['proyecto']['pedido'], datos_update):
                actualizados += 1
            else:
                errores += 1
    
    return {
        'success': True,
        'actualizados': actualizados,
        'errores': errores
    }

'''

# Agregar import json al inicio si no existe
if 'import json' not in content:
    # Buscar la línea de import tempfile y agregar json después
    content = content.replace('import tempfile', 'import tempfile\nimport json')

# Insertar las nuevas rutas antes de las últimas líneas
# Buscar un marcador apropiado o insertar antes de las últimas funciones
if '# --- RECUPERACION DE PROYECTOS ---' not in content:
    # Insertar antes de las últimas líneas
    lines = content.split('\n')
    insert_pos = len(lines) - 10  # 10 líneas antes del final
    lines.insert(insert_pos, new_routes)
    content = '\n'.join(lines)

with open('app/rutas.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Rutas agregadas exitosamente")
