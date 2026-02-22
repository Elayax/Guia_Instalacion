from flask import Blueprint, render_template, request, make_response, redirect, url_for
from app.base_datos import GestorDB
from app.auxiliares import (
    procesar_post_gestion,
    obtener_datos_plantilla,
    guardar_archivo_temporal,
    _procesar_carga_masiva
)
from datetime import datetime
import io
import csv
from . import management_bp

db = GestorDB()

@management_bp.route('/gestion', methods=['GET', 'POST'])
def gestion():
    # Estado inicial de la vista (Diccionario de contexto)
    state = {
        'mensaje': None,
        'error_logs': None,
        'active_tab': 'ups',
        'ups_seleccionado': None,
        'agregando_ups': False,
        'bateria_seleccionada': None,
        'agregando_bateria': False,
        'personal_seleccionado': None,
        'pivot_data': None,
        'unidad_curva': 'W'
    }

    if request.method == 'POST':
        procesar_post_gestion(db, request, state)
    
    return render_template('gestion.html',
                           clientes=db.obtener_clientes(),
                           personal=db.obtener_personal(),
                           ups=db.obtener_ups_todos(),
                           proyectos=db.obtener_proyectos(),
                           baterias=db.obtener_baterias_modelos(),
                           tipos_ventilacion=db.obtener_tipos_ventilacion(),
                           msg=state['mensaje'],
                           error_logs=state['error_logs'],
                           ups_seleccionado=state['ups_seleccionado'],
                           agregando_ups=state['agregando_ups'],
                           bateria_seleccionada=state['bateria_seleccionada'],
                           agregando_bateria=state['agregando_bateria'],
                           personal_seleccionado=state.get('personal_seleccionado'),
                           unidad_curva=state['unidad_curva'],
                           pivot_data=state['pivot_data'],
                           active_tab=state['active_tab'],
                           tipo_vent_seleccionado=state.get('tipo_vent_seleccionado'))

@management_bp.route('/equipos', methods=['GET', 'POST'])
def equipos():
    ups_seleccionado = None
    mensaje = None
    lista_ups = db.obtener_ups_todos() # Para el buscador
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'buscar':
            id_busqueda = request.form.get('id_ups_buscar')
            if id_busqueda:
                ups_seleccionado = db.obtener_ups_id(id_busqueda)
                
        elif accion == 'guardar':
            id_ups = request.form.get('id')
            if db.actualizar_ups(id_ups, request.form):
                mensaje = "✅ Equipo actualizado correctamente."
                ups_seleccionado = db.obtener_ups_id(id_ups)
            else:
                mensaje = "❌ Error al actualizar el equipo."
                
    return render_template('equipos.html', ups_lista=lista_ups, ups=ups_seleccionado, msg=mensaje)

@management_bp.route('/baterias', methods=['GET', 'POST'])
def baterias():
    bateria_seleccionada = None
    mensaje = None
    lista_baterias = db.obtener_baterias_modelos()
    pivot_data = None
    error_logs = None
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        id_bat_actual = request.form.get('id_bateria_buscar') or request.form.get('id')
        if id_bat_actual:
            bateria_seleccionada = db.obtener_bateria_id(id_bat_actual)

        if accion == 'buscar':
            if bateria_seleccionada:
                pivot_data = db.obtener_curvas_pivot(bateria_seleccionada['id'])
                
        elif accion == 'guardar':
            id_bat = request.form.get('id')
            if db.actualizar_bateria(id_bat, request.form):
                mensaje = "✅ Batería actualizada correctamente."
                bateria_seleccionada = db.obtener_bateria_id(id_bat)
            else:
                mensaje = "❌ Error al actualizar la batería."
            
            if bateria_seleccionada:
                pivot_data = db.obtener_curvas_pivot(bateria_seleccionada['id'])

        elif accion == 'subir_curvas':
            id_bat = request.form.get('id')
            file = request.files.get('archivo_csv')
            
            if id_bat and file and file.filename != '':
                filepath = guardar_archivo_temporal(file)
                res = db.cargar_curvas_por_id_csv(id_bat, filepath)
                
                if res['status'] == 'ok':
                    mensaje = f"✅ Curvas actualizadas. {res.get('insertados', 0)} registros procesados."
                    if res.get('logs'):
                        error_logs = res.get('logs')
                else:
                    mensaje = f"❌ Error al cargar el archivo: {res.get('msg', 'Revisa los detalles abajo.')}"
                    error_logs = res.get('logs')
                
                bateria_seleccionada = db.obtener_bateria_id(id_bat)
                pivot_data = db.obtener_curvas_pivot(id_bat)
            else:
                mensaje = "❌ No se seleccionó ningún archivo para subir."

    return render_template('baterias.html', 
                           baterias_lista=lista_baterias, 
                           bateria=bateria_seleccionada, 
                           pivot_data=pivot_data, 
                           msg=mensaje,
                           error_logs=error_logs)

@management_bp.route('/eliminar-proyecto', methods=['POST'])
def eliminar_proyecto():
    """Elimina un proyecto publicado desde la gestión BD"""
    pedido = request.form.get('pedido')
    
    if not pedido:
        return redirect(url_for('management.gestion', msg="Error: No se proporcionó número de pedido"))
    
    if db.eliminar_proyecto(pedido):
        return redirect(url_for('management.gestion', msg=f"Proyecto {pedido} eliminado correctamente", active_tab='proyectos'))
    else:
        return redirect(url_for('management.gestion', msg=f"Error al eliminar proyecto {pedido}", active_tab='proyectos'))

@management_bp.route('/descargar-plantilla/<tipo>')
def descargar_plantilla(tipo):
    si = io.StringIO()
    writer = csv.writer(si)
    
    headers, rows = obtener_datos_plantilla(tipo)
    
    if tipo in ['ups', 'clientes', 'baterias_modelos', 'baterias_curvas']:
        writer.writerow(headers)
        writer.writerows(rows)
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=plantilla_{tipo}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@management_bp.route('/exportar/<tabla>')
def exportar_bd(tabla):
    headers, rows = db.obtener_datos_tabla(tabla)
    
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(headers)
    writer.writerows(rows)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=backup_{tabla}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@management_bp.route('/recuperacion-proyectos', methods=['GET', 'POST'])
def recuperacion_proyectos():
    """Interfaz para completar datos faltantes de proyectos recuperados"""
    msg = None
    msg_type = None
    
    if request.method == 'POST':
        pedido = request.form.get('pedido')
        datos = {
            'voltaje': request.form.get('voltaje'),
            'fases': request.form.get('fases'),
            'longitud': request.form.get('longitud'),
            'tiempo_respaldo': request.form.get('tiempo_respaldo')  
        }
        
        datos = {k: v for k, v in datos.items() if v and v.strip()}
        
        exito, errores = db.completar_datos_proyecto(pedido, datos)
        
        if exito:
            msg = f"✓ Proyecto {pedido} actualizado correctamente"
            msg_type = "success"
        else:
            msg = "Error al actualizar: " + "; ".join(errores)
            msg_type = "danger"
    
    proyectos_incompletos = db.obtener_proyectos_incompletos()
    
    return render_template('recuperacion_proyectos.html',
                         proyectos_incompletos=proyectos_incompletos,
                         msg=msg,
                         msg_type=msg_type)

@management_bp.route('/carga-masiva', methods=['GET', 'POST'])
def carga_masiva():
    mensaje = None
    if request.method == 'POST':
        file = request.files.get('archivo_csv')
        tipo = request.form.get('tipo_carga')
        # Logs ignored for simple msg
        mensaje, logs = _procesar_carga_masiva(db, file, tipo)
       
    return render_template('carga_masiva.html', msg=mensaje)
