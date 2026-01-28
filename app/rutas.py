from flask import Blueprint, render_template, request, make_response, redirect, url_for
from datetime import datetime
from app.calculos import CalculadoraUPS, CalculadoraBaterias
from app.reporte import ReportePDF
from app.checklist import ChecklistPDF
from app.base_datos import GestorDB
from app.auxiliares import (
    obtener_datos_plantilla,
    procesar_post_gestion,
    procesar_calculo_ups,
    guardar_archivo_temporal
)
import json
import os
import csv
import io
import tempfile

main = Blueprint('main', __name__)
db = GestorDB() 

# --- API: BUSCAR PEDIDO (Para el botón de la lupa) ---
@main.route('/api/buscar-pedido/<pedido>')
def buscar_pedido(pedido):
    proyecto = db.obtener_proyecto_por_pedido(pedido)
    if proyecto:
        # Convertimos a diccionario y devolvemos JSON
        return json.dumps(dict(proyecto))
    return json.dumps({}), 404

# ... (imports y configuraciones igual) ...

# --- API: OBTENER SUCURSALES (Para el segundo select) ---
@main.route('/api/sucursales/<cliente>')
def get_sucursales(cliente):
    sucursales = db.obtener_sucursales_por_cliente(cliente)
    return json.dumps(sucursales)

# --- API: DETALLES UPS (Para ficha técnica y edición) ---
@main.route('/api/ups/<int:id_ups>')
def get_ups_details(id_ups):
    ups = db.obtener_ups_id(id_ups)
    if ups:
        return json.dumps(dict(ups))
    return json.dumps({}), 404

# --- API: DETALLES BATERIAS ---
@main.route('/api/bateria/<int:id_bat>')
def get_bateria_details(id_bat):
    bat = db.obtener_bateria_id(id_bat)
    if bat:
        return json.dumps(bat)
    return json.dumps({}), 404

@main.route('/api/bateria/<int:id_bat>/curvas')
def get_bateria_curvas(id_bat):
    curvas = db.obtener_curvas_por_bateria(id_bat)
    return json.dumps(curvas)

# --- API: TIPOS DE VENTILACION ---
@main.route('/api/tipos-ventilacion')
def get_tipos_ventilacion():
    tipos = db.obtener_tipos_ventilacion()
    return json.dumps(tipos)

# --- DASHBOARD PRINCIPAL (POR PEDIDO) ---
@main.route('/', methods=['GET', 'POST'])
def dashboard():
    pedido_data = None
    estado_pedido = None
    pedido_buscado = None
    clientes = db.obtener_clientes_unicos()

    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'buscar_pedido':
            # Buscar pedido específico
            pedido_num = request.form.get('pedido_buscar', '').strip()
            pedido_buscado = pedido_num

            if pedido_num:
                # Buscar en base de datos
                pedido_data = db.obtener_proyecto_por_pedido(pedido_num)

                if pedido_data:
                    # Determinar el estado del pedido
                    estado_pedido = {
                        'tiene_ups': False,
                        'tiene_calculos': False,
                        'tiene_aviso': False,
                        'modelo_ups': None
                    }

                    # Verificar si tiene UPS asignado (modelo_snap guardado)
                    if pedido_data.get('modelo_snap'):
                        estado_pedido['tiene_ups'] = True
                        estado_pedido['modelo_ups'] = pedido_data['modelo_snap']

                    # Verificar si tiene cálculos publicados
                    # Si el proyecto existe en proyectos_publicados, significa que fue publicado
                    if pedido_data.get('fecha_publicacion'):
                        estado_pedido['tiene_calculos'] = True

                    # Verificar si tiene checklist/aviso generado
                    # Buscar archivos PDF de checklist en /static/temp
                    temp_dir = os.path.join(os.path.dirname(__file__), 'static', 'temp')
                    if os.path.exists(temp_dir):
                        checklist_files = [f for f in os.listdir(temp_dir)
                                         if f.endswith('.pdf') and 'Checklist' in f and pedido_num in f]
                        if checklist_files:
                            estado_pedido['tiene_aviso'] = True

        elif accion == 'crear_proyecto':
            # Crear nuevo proyecto
            pedido = request.form.get('pedido')
            cliente_nombre = request.form.get('cliente_nombre')
            sucursal_nombre = request.form.get('sucursal_nombre')

            # Insertar proyecto en BD
            try:
                conn = db._conectar()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO proyectos_publicados (pedido, cliente_snap, sucursal_snap)
                    VALUES (?, ?, ?)
                ''', (pedido, cliente_nombre, sucursal_nombre))
                conn.commit()
                conn.close()

                # Redirigir a calculadora para generar la guía directamente
                return redirect(url_for('main.calculadora') + f'?pedido={pedido}')
            except Exception as e:
                print(f"Error al crear proyecto: {e}")
                # Si hay error (ej: pedido duplicado), mostrar el proyecto existente
                return redirect(url_for('main.dashboard'))

    return render_template('dashboard.html',
                         pedido=pedido_data,
                         estado=estado_pedido,
                         pedido_buscado=pedido_buscado,
                         clientes=clientes)

@main.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    # 1. Cargar listas iniciales
    lista_clientes_unicos = db.obtener_clientes_unicos() # Solo nombres
    lista_ups = db.obtener_ups_todos()
    lista_baterias = db.obtener_baterias_modelos(solo_con_curvas=True)

    # Preservar el pedido si existe en GET o POST para no perder el contexto
    pedido_actual = request.args.get('pedido') or request.form.get('pedido')

    resultado = None
    mensaje = None
    pdf_trigger = None  # Para activar descarga automática del PDF

    if request.method == 'POST':
        # Verificar si es una solicitud para generar PDF
        accion = request.form.get('accion')

        if accion in ['preview', 'publicar']:
            # GENERAR PDF + MOSTRAR RESULTADOS
            resultado, mensaje = procesar_calculo_ups(db, request.form)

            # Generar el PDF
            datos = request.form.to_dict()

            if resultado and datos.get('id_ups'):
                ups_data = db.obtener_ups_id(datos['id_ups'])
                if ups_data:
                    es_publicar = (accion == 'publicar')
                    pedido = datos.get('pedido', 'temporal')

                    # Manejo de imágenes
                    imagenes_temp = {}
                    from app.auxiliares import guardar_archivo_temporal, guardar_imagen_proyecto

                    if es_publicar:
                        if 'imagen_unifilar_ac' in request.files:
                            file = request.files['imagen_unifilar_ac']
                            if file and file.filename:
                                nombre = guardar_imagen_proyecto(file, pedido)
                                imagenes_temp['unifilar_ac'] = os.path.join(os.path.dirname(__file__), 'static', 'img', 'proyectos', pedido, nombre)

                        if 'imagen_baterias_dc' in request.files:
                            file = request.files['imagen_baterias_dc']
                            if file and file.filename:
                                nombre = guardar_imagen_proyecto(file, pedido)
                                imagenes_temp['baterias_dc'] = os.path.join(os.path.dirname(__file__), 'static', 'img', 'proyectos', pedido, nombre)

                        if 'imagen_layout_equipos' in request.files:
                            file = request.files['imagen_layout_equipos']
                            if file and file.filename:
                                nombre = guardar_imagen_proyecto(file, pedido)
                                imagenes_temp['layout_equipos'] = os.path.join(os.path.dirname(__file__), 'static', 'img', 'proyectos', pedido, nombre)
                    else:
                        if 'imagen_unifilar_ac' in request.files:
                            file = request.files['imagen_unifilar_ac']
                            if file and file.filename:
                                imagenes_temp['unifilar_ac'] = guardar_archivo_temporal(file)

                        if 'imagen_baterias_dc' in request.files:
                            file = request.files['imagen_baterias_dc']
                            if file and file.filename:
                                imagenes_temp['baterias_dc'] = guardar_archivo_temporal(file)

                        if 'imagen_layout_equipos' in request.files:
                            file = request.files['imagen_layout_equipos']
                            if file and file.filename:
                                imagenes_temp['layout_equipos'] = guardar_archivo_temporal(file)

                    # Obtener info adicional
                    tipo_ventilacion_data = None
                    if ups_data.get('tipo_ventilacion_id'):
                        tipo_ventilacion_data = db.obtener_tipo_ventilacion_id(ups_data['tipo_ventilacion_id'])

                    # Agregar cálculos de batería si existen
                    bateria_info = {}
                    id_bateria = datos.get('id_bateria')
                    if id_bateria and datos.get('tiempo_respaldo'):
                        try:
                            bateria_info = db.obtener_bateria_id(id_bateria) or {}
                            curvas = db.obtener_curvas_por_bateria(id_bateria)
                            if curvas:
                                from app.calculos import CalculadoraBaterias
                                calc_bat = CalculadoraBaterias()
                                res_bat = calc_bat.calcular(
                                    kva=ups_data.get('Capacidad_kVA'),
                                    kw=ups_data.get('Capacidad_kW'),
                                    eficiencia=ups_data.get('Eficiencia_Modo_Bateria_pct'),
                                    v_dc=ups_data.get('Bateria_Vdc'),
                                    tiempo_min=float(datos['tiempo_respaldo'] or 0),
                                    curvas=curvas,
                                    bat_voltaje_nominal=bateria_info.get('voltaje_nominal', 12)
                                )
                                resultado.update(res_bat)
                        except Exception as e:
                            resultado['bat_error'] = str(e)

                    resultado['tipo_ventilacion'] = tipo_ventilacion_data.get('nombre') if tipo_ventilacion_data else None
                    resultado['tipo_ventilacion_data'] = tipo_ventilacion_data

                    # Si es publicar, guardar en BD
                    if es_publicar:
                        save_data = {
                            'pedido': pedido,
                            'cliente_nombre': datos.get('cliente_texto'),
                            'sucursal_nombre': datos.get('sucursal_texto'),
                            'fases': datos.get('fases'),
                            'voltaje': datos.get('voltaje'),
                            'longitud': datos.get('longitud'),
                            'id_ups': datos.get('id_ups'),
                            'id_bateria': datos.get('id_bateria'),
                            'tiempo_respaldo': datos.get('tiempo_respaldo')
                        }
                        if db.publicar_proyecto(resultado, save_data):
                            resultado['es_publicado'] = True
                            mensaje = "✅ Proyecto publicado correctamente"
                        else:
                            es_publicar = False
                            mensaje = "⚠️ El proyecto fue actualizado"

                    # Generar PDF
                    pdf = ReportePDF()
                    pdf_bytes = pdf.generar_cuerpo(datos, resultado, ups=ups_data, bateria=bateria_info, es_publicado=es_publicar, imagenes_temp=imagenes_temp)

                    # Crear directorio temp si no existe
                    import tempfile
                    temp_dir = os.path.join(os.path.dirname(__file__), 'static', 'temp')
                    os.makedirs(temp_dir, exist_ok=True)

                    # Guardar PDF temporalmente
                    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
                    temp_pdf.write(bytes(pdf_bytes))
                    temp_pdf.close()

                    # Nombre para descarga
                    nombre_seguro = str(pedido).replace(" ", "_")
                    prefijo = "Publicado" if es_publicar else "Preview"
                    pdf_filename = f'{prefijo}_Memoria_{nombre_seguro}.pdf'

                    # Activar descarga automática
                    pdf_trigger = {
                        'path': f'/static/temp/{os.path.basename(temp_pdf.name)}',
                        'filename': pdf_filename
                    }
        else:
            # Cálculo normal sin PDF
            resultado, mensaje = procesar_calculo_ups(db, request.form)

    return render_template('index.html',
                         clientes=lista_clientes_unicos,
                         ups=lista_ups,
                         baterias=lista_baterias,
                         res=resultado,
                         msg=mensaje,
                         pedido=pedido_actual,
                         pdf_trigger=pdf_trigger)

@main.route('/descargar-plantilla/<tipo>')
def descargar_plantilla(tipo):
    si = io.StringIO()
    writer = csv.writer(si)
    
    headers, rows = obtener_datos_plantilla(tipo)
    
    if tipo == 'ups':
        writer.writerow(headers)
        writer.writerows(rows)
    elif tipo == 'clientes':
        writer.writerow(headers)
        writer.writerows(rows)
    elif tipo == 'baterias_modelos':
        writer.writerow(headers)
        writer.writerows(rows)
    elif tipo == 'baterias_curvas':
        writer.writerow(headers)
        writer.writerows(rows)
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=plantilla_{tipo}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main.route('/exportar/<tabla>')
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

# --- EDICIÓN DE EQUIPOS (RESTAURADO) ---
@main.route('/equipos', methods=['GET', 'POST'])
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

# --- GESTIÓN DE BATERÍAS (RESTAURADO) ---
@main.route('/baterias', methods=['GET', 'POST'])
def baterias():
    bateria_seleccionada = None
    mensaje = None
    lista_baterias = db.obtener_baterias_modelos()
    pivot_data = None
    error_logs = None # <--- Nueva variable para logs de error
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        # Recargar datos de la batería seleccionada si se está trabajando en una
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
                bateria_seleccionada = db.obtener_bateria_id(id_bat) # Recargar
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
                        # Si hay logs incluso con 'ok', son advertencias
                        error_logs = res.get('logs')
                else:
                    mensaje = f"❌ Error al cargar el archivo: {res.get('msg', 'Revisa los detalles abajo.')}"
                    error_logs = res.get('logs')
                
                # Siempre recargar los datos para mostrar el estado actual
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

# --- GESTIÓN DE BD ---
@main.route('/gestion', methods=['GET', 'POST'])
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
        'pivot_data': None,
        'unidad_curva': 'W'
    }

    if request.method == 'POST':
        procesar_post_gestion(db, request, state)
    
    return render_template('gestion.html',
                           clientes=db.obtener_clientes(),
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
                           unidad_curva=state['unidad_curva'],
                           pivot_data=state['pivot_data'],
                           active_tab=state['active_tab'],
                           tipo_vent_seleccionado=state.get('tipo_vent_seleccionado'))

# --- GENERAR PDF ---
@main.route('/descargar-pdf', methods=['POST'])
def descargar_pdf():
    datos = request.form.to_dict()

    if not datos.get('id_ups'):
        return "Error: ID de UPS no proporcionado.", 400

    ups_data = db.obtener_ups_id(datos['id_ups'])
    if not ups_data:
        return "Error: UPS no encontrado.", 404

    # Determinar si es publicar o preview
    accion = datos.get('accion', 'preview')
    es_publicar = (accion == 'publicar')
    pedido = datos.get('pedido', 'temporal')

    # Manejo de imágenes: TEMPORAL (preview) o PERMANENTE (publicar)
    imagenes_temp = {}

    if es_publicar:
        # PUBLICAR: Guardar imágenes permanentemente
        from app.auxiliares import guardar_imagen_proyecto

        if 'imagen_unifilar_ac' in request.files:
            file_unifilar = request.files['imagen_unifilar_ac']
            if file_unifilar and file_unifilar.filename != '':
                nombre_archivo = guardar_imagen_proyecto(file_unifilar, pedido)
                imagenes_temp['unifilar_ac'] = os.path.join(os.path.dirname(__file__), 'static', 'img', 'proyectos', pedido, nombre_archivo)

        if 'imagen_baterias_dc' in request.files:
            file_baterias = request.files['imagen_baterias_dc']
            if file_baterias and file_baterias.filename != '':
                nombre_archivo = guardar_imagen_proyecto(file_baterias, pedido)
                imagenes_temp['baterias_dc'] = os.path.join(os.path.dirname(__file__), 'static', 'img', 'proyectos', pedido, nombre_archivo)

        if 'imagen_layout_equipos' in request.files:
            file_layout = request.files['imagen_layout_equipos']
            if file_layout and file_layout.filename != '':
                nombre_archivo = guardar_imagen_proyecto(file_layout, pedido)
                imagenes_temp['layout_equipos'] = os.path.join(os.path.dirname(__file__), 'static', 'img', 'proyectos', pedido, nombre_archivo)
    else:
        # PREVIEW: Guardar imágenes temporalmente
        from app.auxiliares import guardar_archivo_temporal

        if 'imagen_unifilar_ac' in request.files:
            file_unifilar = request.files['imagen_unifilar_ac']
            if file_unifilar and file_unifilar.filename != '':
                imagenes_temp['unifilar_ac'] = guardar_archivo_temporal(file_unifilar)

        if 'imagen_baterias_dc' in request.files:
            file_baterias = request.files['imagen_baterias_dc']
            if file_baterias and file_baterias.filename != '':
                imagenes_temp['baterias_dc'] = guardar_archivo_temporal(file_baterias)

        if 'imagen_layout_equipos' in request.files:
            file_layout = request.files['imagen_layout_equipos']
            if file_layout and file_layout.filename != '':
                imagenes_temp['layout_equipos'] = guardar_archivo_temporal(file_layout)

    # Obtener tipo de ventilación si existe
    tipo_ventilacion_data = None
    if ups_data.get('tipo_ventilacion_id'):
        tipo_ventilacion_data = db.obtener_tipo_ventilacion_id(ups_data['tipo_ventilacion_id'])

    # Recalculamos para el PDF
    calc = CalculadoraUPS()
    res = calc.calcular(datos)

    # Añadir cálculo de baterías
    id_bateria = datos.get('id_bateria')
    bateria_info = {}
    if id_bateria and datos.get('tiempo_respaldo'):
        try:
            bateria_info = db.obtener_bateria_id(id_bateria) or {}
            curvas = db.obtener_curvas_por_bateria(id_bateria)
            if curvas:
                calc_bat = CalculadoraBaterias()
                res_bat = calc_bat.calcular(
                    kva=ups_data.get('Capacidad_kVA'),
                    kw=ups_data.get('Capacidad_kW'),
                    eficiencia=ups_data.get('Eficiencia_Modo_Bateria_pct'),
                    v_dc=ups_data.get('Bateria_Vdc'),
                    tiempo_min=float(datos['tiempo_respaldo'] or 0),
                    curvas=curvas,
                    bat_voltaje_nominal=bateria_info.get('voltaje_nominal', 12)
                )
                res.update(res_bat)
        except Exception as e:
            res['bat_error'] = str(e)

    # Pasamos datos visuales extra
    res['modelo_nombre'] = datos.get('modelo_nombre')
    res['tipo_ventilacion'] = tipo_ventilacion_data.get('nombre') if tipo_ventilacion_data else None
    res['tipo_ventilacion_data'] = tipo_ventilacion_data

    # Si es publicar, guardar en la base de datos
    if es_publicar:
        save_data = {
            'pedido': pedido,
            'cliente_nombre': datos.get('cliente_texto'),
            'sucursal_nombre': datos.get('sucursal_texto'),
            'fases': datos.get('fases')
        }
        if db.publicar_proyecto(res, save_data):
            res['es_publicado'] = True
        else:
            # Si falla la publicación (pedido duplicado), aún generar el PDF pero como preview
            es_publicar = False

    pdf = ReportePDF()
    pdf_bytes = pdf.generar_cuerpo(datos, res, ups=ups_data, bateria=bateria_info, es_publicado=es_publicar, imagenes_temp=imagenes_temp)

    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    nombre_seguro = str(pedido).replace(" ", "_")
    prefijo = "Publicado" if es_publicar else "Preview"
    response.headers['Content-Disposition'] = f'attachment; filename={prefijo}_Memoria_{nombre_seguro}.pdf'
    return response
