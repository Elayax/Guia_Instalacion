from flask import Blueprint, render_template, request, make_response, redirect, url_for
from app.base_datos import GestorDB
from app.reporte import ReportePDF
from app.auxiliares import (
    procesar_calculo_ups,
    guardar_archivo_temporal,
    guardar_pdf_proyecto,
    guardar_imagen_proyecto
)
import os
import tempfile
from werkzeug.datastructures import ImmutableMultiDict
from app.routes import calculator_bp

db = GestorDB()

@calculator_bp.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    # 1. Cargar listas iniciales
    lista_clientes_unicos = db.obtener_clientes_unicos()
    lista_ups = db.obtener_ups_todos()
    lista_baterias = db.obtener_baterias_modelos(solo_con_curvas=True)

    pedido_actual = request.args.get('pedido') or request.form.get('pedido')

    resultado = None
    mensaje = None
    pdf_trigger = None
    datos_guardados = None
    es_recalculo = False

    if request.method == 'GET' and pedido_actual:
        datos_guardados = db.obtener_proyecto_por_pedido(pedido_actual)
        if datos_guardados:
            es_recalculo = True
            try:
                # Mapeo de campos nuevos
                voltaje_inicial = str(datos_guardados.get('voltaje') or datos_guardados.get('voltaje_salida') or '')
                kva_inicial = str(datos_guardados.get('kva') or datos_guardados.get('potencia_kva') or '')
                
                form_data = {
                    'voltaje': voltaje_inicial,
                    'kva': kva_inicial,
                    'fases': str(datos_guardados.get('fases') or ''),
                    'longitud': str(datos_guardados.get('longitud') or ''),
                    'id_ups': str(datos_guardados.get('id_ups') or ''),
                    'id_bateria': str(datos_guardados.get('id_bateria') or ''),
                    'tiempo_respaldo': str(datos_guardados.get('tiempo_respaldo') or ''),
                    'pedido': pedido_actual
                }
                simulated_form = ImmutableMultiDict(form_data)
                resultado, _ = procesar_calculo_ups(db, simulated_form)
                
                # Calcular baterías si existen
                if resultado and datos_guardados.get('id_bateria') and datos_guardados.get('tiempo_respaldo'):
                    try:
                        ups_data = db.obtener_ups_id(datos_guardados['id_ups'])
                        bateria_info = db.obtener_bateria_id(datos_guardados['id_bateria']) or {}
                        curvas = db.obtener_curvas_por_bateria(datos_guardados['id_bateria'])
                        if curvas and ups_data:
                            from app.calculos import CalculadoraBaterias
                            calc_bat = CalculadoraBaterias()
                            res_bat = calc_bat.calcular(
                                kva=ups_data.get('Capacidad_kVA'),
                                kw=ups_data.get('Capacidad_kW'),
                                eficiencia=ups_data.get('Eficiencia_Modo_Bateria_pct'),
                                v_dc=ups_data.get('Bateria_Vdc'),
                                tiempo_min=float(datos_guardados['tiempo_respaldo'] or 0),
                                curvas=curvas,
                                bat_voltaje_nominal=bateria_info.get('voltaje_nominal', 12)
                            )
                            resultado.update(res_bat)
                    except Exception as e:
                        print(f"Error calculando baterías en pre-carga: {e}")
                        
            except Exception as e:
                print(f"Error pre-cargando cálculo: {e}")
                import traceback
                traceback.print_exc()

    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'calcular':
            resultado, mensaje = procesar_calculo_ups(db, request.form)
            
            if resultado and pedido_actual:
                datos_form = request.form.to_dict()
                ups_data = None
                if datos_form.get('id_ups'):
                    ups_data = db.obtener_ups_id(datos_form['id_ups'])
                
                datos_guardar = {
                    'voltaje': datos_form.get('voltaje'),
                    'fases': datos_form.get('fases'),
                    'longitud': datos_form.get('longitud'),
                    'tiempo_respaldo': datos_form.get('tiempo_respaldo'),
                    'id_ups': datos_form.get('id_ups'),
                    'id_bateria': datos_form.get('id_bateria'),
                    'modelo_snap': ups_data.get('Nombre_del_Producto') if ups_data else None,
                    'potencia_snap': ups_data.get('Capacidad_kVA') if ups_data else None,
                    'cliente_snap': datos_form.get('cliente_texto'),
                    'sucursal_snap': datos_form.get('sucursal_texto'),
                    'calibre_fases': resultado.get('calibre_fases'),
                    'config_salida': resultado.get('config_salida'),
                    'calibre_tierra': resultado.get('calibre_tierra')
                }
                
                # Se usa publicar_proyecto para guardar los datos del cálculo
                if db.publicar_proyecto(resultado, request.form): # Pasar resultado y request.form
                    es_recalculo = True
                    datos_guardados = db.obtener_proyecto_por_pedido(pedido_actual)
            
            if resultado:
                datos = request.form.to_dict()
                id_bateria = datos.get('id_bateria')
                if id_bateria and datos.get('tiempo_respaldo') and datos.get('id_ups'):
                    try:
                        ups_data = db.obtener_ups_id(datos['id_ups'])
                        bateria_info = db.obtener_bateria_id(id_bateria) or {}
                        curvas = db.obtener_curvas_por_bateria(id_bateria)
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
        
        elif accion in ['preview', 'publicar']:
            resultado, mensaje = procesar_calculo_ups(db, request.form)
            datos = request.form.to_dict()

            if resultado and datos.get('id_ups'):
                ups_data = db.obtener_ups_id(datos['id_ups'])
                if ups_data:
                    es_publicar = (accion == 'publicar')
                    pedido = datos.get('pedido', 'temporal')

                    imagenes_temp = {}
                    # Ajustar ruta base para imágenes: subir un nivel desde routes/
                    base_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                    if es_publicar:
                        if 'imagen_unifilar_ac' in request.files:
                            file = request.files['imagen_unifilar_ac']
                            if file and file.filename:
                                nombre = guardar_imagen_proyecto(file, pedido)
                                imagenes_temp['unifilar_ac'] = os.path.join(base_app_dir, 'static', 'img', 'proyectos', pedido, nombre)

                        if 'imagen_baterias_dc' in request.files:
                            file = request.files['imagen_baterias_dc']
                            if file and file.filename:
                                nombre = guardar_imagen_proyecto(file, pedido)
                                imagenes_temp['baterias_dc'] = os.path.join(base_app_dir, 'static', 'img', 'proyectos', pedido, nombre)

                        if 'imagen_layout_equipos' in request.files:
                            file = request.files['imagen_layout_equipos']
                            if file and file.filename:
                                nombre = guardar_imagen_proyecto(file, pedido)
                                imagenes_temp['layout_equipos'] = os.path.join(base_app_dir, 'static', 'img', 'proyectos', pedido, nombre)
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

                    tipo_ventilacion_data = None
                    if ups_data.get('tipo_ventilacion_id'):
                        tipo_ventilacion_data = db.obtener_tipo_ventilacion_id(ups_data['tipo_ventilacion_id'])

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

                    pdf = ReportePDF()
                    pdf_bytes = pdf.generar_cuerpo(datos, resultado, ups=ups_data, bateria=bateria_info, es_publicado=es_publicar, imagenes_temp=imagenes_temp)

                    if es_publicar:
                        pdf_url = guardar_pdf_proyecto(bytes(pdf_bytes), pedido, tipo='guia')
                        db.actualizar_pdf_guia(pedido, pdf_url)
                        pdf_trigger = {
                            'path': f'/static/{pdf_url}',
                            'filename': f'Guia_Instalacion_{pedido}.pdf'
                        }
                    else:
                        temp_dir = os.path.join(base_app_dir, 'static', 'temp')
                        os.makedirs(temp_dir, exist_ok=True)

                        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
                        temp_pdf.write(bytes(pdf_bytes))
                        temp_pdf.close()

                        nombre_seguro = str(pedido).replace(" ", "_")
                        pdf_filename = f'Preview_Memoria_{nombre_seguro}.pdf'

                        pdf_trigger = {
                            'path': f'/static/temp/{os.path.basename(temp_pdf.name)}',
                            'filename': pdf_filename
                        }
        else:
            resultado, mensaje = procesar_calculo_ups(db, request.form)

    return render_template('index.html',
                         clientes=lista_clientes_unicos,
                         ups=lista_ups,
                         baterias=lista_baterias,
                         res=resultado,
                         msg=mensaje,
                         pedido=pedido_actual,
                         pdf_trigger=pdf_trigger,
                         datos_guardados=datos_guardados,
                         es_recalculo=es_recalculo)

@calculator_bp.route('/generar-pdf-calculadora', methods=['POST'])
def generar_pdf_calculadora():
    datos = request.form.to_dict()
    
    if not datos.get('id_ups'):
        return "Error: ID de UPS no proporcionado.", 400
    
    ups_data = db.obtener_ups_id(datos['id_ups'])
    if not ups_data:
        return "Error: UPS no encontrado.", 404
    
    accion = datos.get('accion', 'preview')
    es_publicar = (accion == 'publicar')
    pedido = datos.get('pedido', 'temporal')
    
    def to_float(val, default=0.0):
        try:
            return float(val) if val and str(val).strip() else default
        except:
            return default

    resultado = {
        'pedido': pedido,
        'cliente_nom': datos.get('cliente_texto', ''),
        'sucursal_nom': datos.get('sucursal_texto', ''),
        'modelo_nombre': datos.get('modelo_nombre', ''),
        'kva': datos.get('kva', ''),
        'voltaje': datos.get('voltaje', ''),
        'i_nom': to_float(datos.get('i_nom')),
        'i_diseno': to_float(datos.get('i_diseno')),
        'dv_pct': to_float(datos.get('dv_pct')),
        'fase_sel': datos.get('fase_sel', ''),
        'breaker_sel': to_float(datos.get('breaker_sel')),
        'gnd_sel': datos.get('gnd_sel', 'S/D'),
        'i_real_cable': to_float(datos.get('i_real_cable')),
        'nota_altitud': datos.get('nota_altitud', ''),
        'bat_series': to_float(datos.get('bat_series')),
        'bat_strings': to_float(datos.get('bat_strings')),
        'bat_total': to_float(datos.get('bat_total')),
        'baterias_total': to_float(datos.get('bat_total')), 
        'baterias_por_string': to_float(datos.get('baterias_por_string')),
        'numero_strings': to_float(datos.get('numero_strings')),
        'autonomia_calculada_min': to_float(datos.get('autonomia_calculada_min')),
        'autonomia_deseada_min': to_float(datos.get('autonomia_deseada_min')),
        'bateria_modelo': datos.get('bateria_modelo', ''),
        'tiempo_respaldo': datos.get('tiempo_respaldo', ''),
        'bat_justificacion': datos.get('bat_justificacion', ''),
        'dim_largo': datos.get('dim_largo', ''),
        'dim_ancho': datos.get('dim_ancho', ''),
        'dim_alto': datos.get('dim_alto', ''),
        'peso': datos.get('peso', ''),
        'es_publicado': es_publicar
    }
    
    imagenes_temp = {}
    base_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if es_publicar:
        if 'imagen_unifilar_ac' in request.files:
            file = request.files['imagen_unifilar_ac']
            if file and file.filename:
                nombre = guardar_imagen_proyecto(file, pedido)
                imagenes_temp['unifilar_ac'] = os.path.join(base_app_dir, 'static', 'img', 'proyectos', pedido, nombre)
        
        if 'imagen_baterias_dc' in request.files:
            file = request.files['imagen_baterias_dc']
            if file and file.filename:
                nombre = guardar_imagen_proyecto(file, pedido)
                imagenes_temp['baterias_dc'] = os.path.join(base_app_dir, 'static', 'img', 'proyectos', pedido, nombre)
        
        if 'imagen_layout_equipos' in request.files:
            file = request.files['imagen_layout_equipos']
            if file and file.filename:
                nombre = guardar_imagen_proyecto(file, pedido)
                imagenes_temp['layout_equipos'] = os.path.join(base_app_dir, 'static', 'img', 'proyectos', pedido, nombre)
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
    
    tipo_ventilacion_data = None
    if ups_data.get('tipo_ventilacion_id'):
        tipo_ventilacion_data = db.obtener_tipo_ventilacion_id(ups_data['tipo_ventilacion_id'])
    
    resultado['tipo_ventilacion'] = tipo_ventilacion_data.get('nombre') if tipo_ventilacion_data else None
    resultado['tipo_ventilacion_data'] = tipo_ventilacion_data
    
    bateria_info = {}
    id_bateria = datos.get('id_bateria')
    if id_bateria:
        bateria_info = db.obtener_bateria_id(id_bateria) or {}
    
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
        else:
            es_publicar = False
    
    pdf = ReportePDF()
    pdf_bytes = pdf.generar_cuerpo(datos, resultado, ups=ups_data, bateria=bateria_info, es_publicado=es_publicar, imagenes_temp=imagenes_temp)
    
    if es_publicar:
        pdf_url = guardar_pdf_proyecto(bytes(pdf_bytes), pedido, tipo='guia')
        db.actualizar_pdf_guia(pedido, pdf_url)
    
    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    nombre_seguro = str(pedido).replace(" ", "_")
    prefijo = "Guia" if es_publicar else "Preview"
    response.headers['Content-Disposition'] = f'attachment; filename={prefijo}_Instalacion_{nombre_seguro}.pdf'
    return response
