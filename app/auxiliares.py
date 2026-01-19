import os
from app.calculos import CalculadoraUPS, CalculadoraBaterias

def procesar_post_gestion(db, request, state):
    """Despachador principal de lógica POST para gestión"""
    tipo = request.form.get('tipo')
    accion = request.form.get('accion')
    
    # Actualizar estado base desde el form
    if request.form.get('active_tab'): state['active_tab'] = request.form.get('active_tab')
    if request.form.get('unidad_curva'): state['unidad_curva'] = request.form.get('unidad_curva')

    # 1. Carga Masiva
    if request.files.get('archivo_csv'):
        state['mensaje'] = _procesar_carga_masiva(db, request.files['archivo_csv'], request.form.get('tipo_carga'))
        state['active_tab'] = 'carga'
        return

    # 2. Acciones por Tipo (Clientes y Eliminaciones)
    if tipo:
        if _procesar_acciones_tipo(db, request, state, tipo):
            return

    # 3. Acciones por 'accion' (UPS y Baterías)
    if accion:
        if 'ups' in accion:
            _procesar_acciones_ups(db, request, state, accion)
        elif 'bateria' in accion or accion in ['subir_curvas', 'cambiar_unidad_curva']:
            _procesar_acciones_bateria(db, request, state, accion)

def _procesar_acciones_tipo(db, request, state, tipo):
    """Maneja add_cliente, del_cliente, del_ups, del_bateria"""
    if tipo == 'add_cliente':
        db.agregar_cliente(request.form)
        state['active_tab'] = 'clientes'
        return True
    elif tipo == 'del_cliente':
        db.eliminar_cliente(request.form.get('id'))
        state['active_tab'] = 'clientes'
        return True
    elif tipo == 'del_ups':
        db.eliminar_ups(request.form.get('id'))
        state['active_tab'] = 'ups'
        return True
    elif tipo == 'del_bateria':
        db.eliminar_bateria(request.form.get('id'))
        state['active_tab'] = 'baterias'
        return True
    return False

def _procesar_acciones_ups(db, request, state, accion):
    """Lógica de estado para UPS"""
    state['active_tab'] = 'ups'
    
    if accion == 'iniciar_agregar_ups':
        state['agregando_ups'] = True
        
    elif accion == 'editar_ups':
        id_ups = request.form.get('id_ups')
        state['ups_seleccionado'] = db.obtener_ups_id(id_ups)
        
    elif accion == 'guardar_ups':
        id_ups = request.form.get('id')
        exito = False
        if id_ups:
            exito = db.actualizar_ups(id_ups, request.form)
            state['mensaje'] = "✅ Equipo actualizado correctamente." if exito else "❌ Error al actualizar."
        else:
            exito = db.insertar_ups_manual(request.form)
            state['mensaje'] = "✅ Nuevo equipo agregado." if exito else "❌ Error al agregar."
            
    elif accion == 'cancelar_edicion_ups':
        state['ups_seleccionado'] = None
        state['agregando_ups'] = False

def _procesar_acciones_bateria(db, request, state, accion):
    """Lógica de estado para Baterías"""
    state['active_tab'] = 'baterias'
    
    if accion == 'iniciar_agregar_bateria':
        state['agregando_bateria'] = True
        
    elif accion == 'editar_bateria':
        id_bat = request.form.get('id_bateria')
        state['bateria_seleccionada'] = db.obtener_bateria_id(id_bat)
        if state['bateria_seleccionada']:
            state['pivot_data'] = db.obtener_curvas_pivot(state['bateria_seleccionada']['id'], unidad=state['unidad_curva'])
            
    elif accion == 'cambiar_unidad_curva':
        id_bat = request.form.get('id')
        state['bateria_seleccionada'] = db.obtener_bateria_id(id_bat)
        if state['bateria_seleccionada']:
            state['pivot_data'] = db.obtener_curvas_pivot(state['bateria_seleccionada']['id'], unidad=state['unidad_curva'])
            
    elif accion == 'guardar_bateria':
        id_bat = request.form.get('id')
        if id_bat:
            if db.actualizar_bateria(id_bat, request.form):
                state['mensaje'] = "✅ Batería actualizada."
                state['bateria_seleccionada'] = db.obtener_bateria_id(id_bat)
                state['pivot_data'] = db.obtener_curvas_pivot(id_bat, unidad=state['unidad_curva'])
            else:
                state['mensaje'] = "❌ Error al actualizar."
        else:
            if db.agregar_modelo_bateria(request.form):
                state['mensaje'] = "✅ Nueva batería agregada."
            else:
                state['mensaje'] = "❌ Error al agregar."
                
    elif accion == 'subir_curvas':
        id_bat = request.form.get('id')
        file = request.files.get('archivo_csv')
        filepath = guardar_archivo_temporal(file)
        
        if filepath:
            res = db.cargar_curvas_por_id_csv(id_bat, filepath)
            state['mensaje'] = f"✅ Curvas: {res.get('insertados',0)} registros." if res['status'] == 'ok' else f"❌ Error: {res.get('msg')}"
            
            state['bateria_seleccionada'] = db.obtener_bateria_id(id_bat)
            state['pivot_data'] = db.obtener_curvas_pivot(id_bat, unidad=state['unidad_curva'])
            
    elif accion == 'cancelar_edicion_bateria':
        state['bateria_seleccionada'] = None
        state['agregando_bateria'] = False

def guardar_archivo_temporal(file):
    """Guarda un archivo subido en la carpeta uploads y retorna su ruta"""
    if not file or file.filename == '': return None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(base_dir, 'static', 'uploads')
    if not os.path.exists(upload_dir): os.makedirs(upload_dir)
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)
    return filepath

def procesar_calculo_ups(db, form):
    """Maneja la lógica de cálculo y publicación del index"""
    accion = form.get('accion')
    id_ups = form.get('id_ups')
    
    if not id_ups:
        return None, None
        
    ups_data = db.obtener_ups_id(id_ups)
    if not ups_data:
        return None, "❌ Error: Equipo no encontrado en la base de datos."

    # Preparar datos para cálculo
    voltaje_sel = form.get('voltaje')
    if not voltaje_sel:
        voltaje_sel = ups_data.get('Voltaje_Entrada_1_V')
    
    datos_calc = {
        'kva': ups_data.get('Capacidad_kVA') or 0,
        'voltaje': voltaje_sel or 0,
        'fases': form.get('fases') or 0,
        'longitud': form.get('longitud') or 0,
        'lat': form.get('lat_oculta'),
        'lon': form.get('lon_oculta'),
        'tiempo_respaldo': form.get('tiempo_respaldo')
    }
    
    calc = CalculadoraUPS()
    resultado = calc.calcular(datos_calc)
    
    # --- CÁLCULO BATERÍAS ---
    id_bateria = form.get('id_bateria')
    if id_bateria:
        try:
            bat_data = db.obtener_bateria_id(id_bateria)
            curvas = db.obtener_curvas_por_bateria(id_bateria)
            calc_bat = CalculadoraBaterias()
            
            res_bat = calc_bat.calcular(
                kva=datos_calc['kva'],
                kw=ups_data.get('Capacidad_kW'),
                eficiencia=ups_data.get('Eficiencia_Modo_Bateria_pct'),
                v_dc=ups_data.get('Bateria_Vdc'),
                tiempo_min=float(datos_calc['tiempo_respaldo'] or 0),
                curvas=curvas,
                bat_voltaje_nominal=bat_data.get('voltaje_nominal', 12)
            )
            resultado.update(res_bat)
            resultado['bateria_modelo'] = bat_data.get('modelo')
        except Exception as e:
            resultado['bat_error'] = str(e)
    
    # Enriquecer resultado
    resultado.update({
        'Nombre_del_Producto': ups_data.get('Nombre_del_Producto'),
        'modelo_nombre': ups_data.get('Nombre_del_Producto'),
        'fabricante': ups_data.get('Serie'),
        'cliente_nom': form.get('cliente_texto'),
        'sucursal_nom': form.get('sucursal_texto'),
        'pedido': form.get('pedido'),
        'kva': ups_data.get('Capacidad_kVA'),
        'Capacidad_kVA': ups_data.get('Capacidad_kVA'),
        'voltaje': datos_calc['voltaje'],
        'fases': datos_calc['fases'],
        'longitud': datos_calc['longitud'],
        'tiempo_respaldo': datos_calc['tiempo_respaldo'],
        'lat': datos_calc['lat'],
        'lon': datos_calc['lon'],
        'kw': ups_data.get('Capacidad_kW'),
        'eficiencia': ups_data.get('Eficiencia_Modo_AC_pct'),
        'baterias_v': ups_data.get('Bateria_Vdc'),
        'peso': ups_data.get('Peso_Gabinete_kg'),
        'dimensiones': f"{ups_data.get('Dim_Largo_mm')} x {ups_data.get('Dim_Ancho_mm')} x {ups_data.get('Dim_Alto_mm')} mm",
        'dim_largo': ups_data.get('Dim_Largo_mm'),
        'dim_ancho': ups_data.get('Dim_Ancho_mm'),
        'dim_alto': ups_data.get('Dim_Alto_mm'),
        'ruido': ups_data.get('Nivel_Ruido_dB')
    })
    
    mensaje = "👁️ VISTA PREVIA GENERADA"
    if accion == 'publicar':
        if not form.get('pedido'):
            mensaje = "⚠️ Falta el número de Pedido"
        else:
            save_data = {'pedido': form.get('pedido'), 'cliente_nombre': form.get('cliente_texto'), 'sucursal_nombre': form.get('sucursal_texto'), 'fases': form.get('fases')}
            if db.publicar_proyecto(resultado, save_data):
                mensaje = "✅ PROYECTO PUBLICADO CORRECTAMENTE"
                resultado['es_publicado'] = True
            else:
                mensaje = "⚠️ ERROR: El número de pedido ya existe."
                
    return resultado, mensaje

def _procesar_carga_masiva(db, file, tipo_carga):
    filepath = guardar_archivo_temporal(file)
    if filepath:
        if tipo_carga == 'ups': db.cargar_ups_desde_csv(filepath)
        elif tipo_carga == 'clientes': db.cargar_clientes_desde_csv(filepath)
        elif tipo_carga == 'baterias_modelos': db.cargar_baterias_modelos_desde_csv(filepath)
        elif tipo_carga == 'baterias_curvas': db.cargar_curvas_baterias_masiva(filepath)
        return "✅ Carga masiva procesada."
    return "⚠️ Error en archivo."

def obtener_datos_plantilla(tipo):
    """Retorna headers y filas de ejemplo para las plantillas CSV"""
    if tipo == 'ups':
        headers = ['Nombre del Producto', 'Serie', 'Capacidad_kVA', 'Capacidad_kW', 'Eficiencia_Modo_AC_pct', 'Eficiencia_Modo_Bateria_pct', 'Eficiencia_Modo_ECO_pct', 'FP_Salida', 'Voltaje_Entrada_1_V', 'Voltaje_Entrada_2_V', 'Voltaje_Entrada_3_V', 'Conexion_Entrada', 'Voltaje_Salida_1_V', 'Voltaje_Salida_2_V', 'Voltaje_Salida_3_V', 'Conexion_Salida', 'Frecuencia_1_Hz', 'Frecuencia_2_Hz', 'Frecuencia_Precision_pct', 'THDu_Lineal_pct', 'THDu_NoLineal_pct', 'Sobrecarga_110_pct_min', 'Sobrecarga_125_pct_min', 'Sobrecarga_150_pct_min', 'Bateria_Vdc', 'Bateria_Piezas_min', 'Bateria_Piezas_max', 'Bateria_Piezas_defecto', 'Precision_Voltaje_pct', 'TempTrabajo_min_C', 'TempTrabajo_max_C', 'Humedad_min_pct', 'Humedad_max_pct', 'Peso_Gabinete_kg', 'Dim_Largo_mm', 'Dim_Ancho_mm', 'Dim_Alto_mm', 'Nivel_Ruido_dB', 'Cable_Entrada_mm2', 'Cable_Entrada_conductores', 'Cable_Salida_mm2', 'Cable_Salida_conductores', 'Cable_Bateria_mm2', 'Cable_Bateria_conductores', 'Cable_PE_mm2']
        rows = [
            ['Dragon Power Plus 60', 'Modular', '60', '60', '96', '96', 'S/D', '1', 'S/D', 'S/D', 'S/D', 'S/D', '480', 'S/D', 'S/D', '(3P + N + PE)', '50', '60', 'S/D', '1', '5', '60', '10', '1', '240', '30', '50', 'S/D', '1', '0', '40', '0', '95', 'S/D', '442', '659', '174', '72', '240', '3', 'S/D', 'S/D', '240', '3', 'S/D'],
            ['Dragon Power Plus 50', 'Modular', '50', '50', '96', 'S/D', 'S/D', '1', 'S/D', 'S/D', 'S/D', 'S/D', '440', '460', '480', '(3P + N + PE)', '50', '60', 'S/D', '2', '4', '60', '10', '1', '240', '40', '50', 'S/D', '1', '0', '40', '0', '95', '180', '440', '620', '131', '65', '150', 'S/D', '150', 'S/D', '150', '2', 'S/D'],
            ['Dragon Power Plus 40', 'Modular', '40', '40', '96', '95', 'S/D', '1', 'S/D', 'S/D', 'S/D', 'S/D', '480', 'S/D', 'S/D', '(L-L)', '50', '60', 'S/D', '1', '5.5', '60', '10', '1', '240', 'S/D', 'S/D', 'S/D', '1', '0', '40', '0', '95', '120', '510', '700', '178', '72', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D'],
            ['Dragon Power Plus 40', 'Modular', '40', '36', '96', '96', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '480', 'S/D', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '240', '32', '44', '40', '1.5', '0', '40', '0', '95', '120', '510', '700', '178', '65', '50', 'S/D', '35', 'S/D', '50', 'S/D', 'S/D'],
            ['Dragon Power Plus 40', 'Modular', '400', '360', '96', '96', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '480', 'S/D', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '240', '32', '44', 'S/D', '1.5', '0', '40', '0', '95', '450', '510', '700', '178', '65', '2', 'S/D', '2', 'S/D', '2', '240', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '30', '30', 'S/D', '93', 'S/D', '1', 'S/D', 'S/D', 'S/D', 'S/D', '208', '220', 'S/D', '(3P + N + PE)', '50', '60', 'S/D', '1.5', '6', '60', '10', '1', '120', 'S/D', 'S/D', 'S/D', '1', '0', '40', '0', '95', '210', '510', '700', '178', '68', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '30', '27', '94', '93', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', '36', '44', '40', '1.5', '0', '40', '0', '95', '165', '510', '700', '178', '65', '70', 'S/D', '70', 'S/D', '2', '50', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '60', '54', '94', '93', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', '36', '44', 'S/D', '1.5', '0', '40', '0', '95', '210', '510', '700', '178', '65', '70', 'S/D', '70', 'S/D', '2', '50', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '90', '81', '94', '93', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', '36', '44', 'S/D', '1.5', '0', '40', '0', '95', '305', '510', '700', '178', '65', '2', 'S/D', '2', 'S/D', '2', '120', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '120', '108', '94', '93', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', '36', '44', 'S/D', '1.5', '0', '40', '0', '95', '350', '510', '700', '178', '65', '2', 'S/D', '2', 'S/D', '2', '120', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '150', '135', '94', '93', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', '36', '44', 'S/D', '1.5', '0', '40', '0', '95', '445', '510', '700', '178', '65', '2', 'S/D', '2', 'S/D', '2', '185', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '180', '162', '94', '93', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', '36', '44', 'S/D', '1.5', '0', '40', '0', '95', '490', '510', '700', '178', '65', '2', 'S/D', '2', 'S/D', '2', '185', 'S/D'],
            ['Dragon Power Plus 30', 'Modular', '300', '270', '94', '93', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', '36', '44', 'S/D', '1.5', '0', '40', '0', '95', '900', '510', '700', '178', '65', '2', 'S/D', '2', 'S/D', '2', '240', 'S/D'],
            ['Dragon Power Plus 15', 'Modular/Rack', '15', '13.5', '95.5', '95', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '220', 'S/D', '(3P + N + PE)', '50', '60', 'S/D', '1.5', '6', '60', '10', '1', '120', '24', '40', 'S/D', '1', '0', '40', '0', '95', '30', '500', '800', '650', '65', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D', 'S/D'],
            ['Dragon Power Plus 15', 'Modular/Rack', '15', '13.5', '95.5', '95.5', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', 'S/D', 'S/D', 'S/D', '1.5', '0', '40', '0', '95', '30', '488', '945', '130', '65', '10', 'S/D', '10', 'S/D', '16', 'S/D', 'S/D'],
            ['Dragon Power Plus 15', 'Modular/Rack', '10', '9', '95', '94.5', 'S/D', '0.9', 'S/D', 'S/D', 'S/D', 'S/D', '208', '120', 'S/D', 'S/D', '50', '60', 'S/D', '1', '6', '60', '10', '1', '120', 'S/D', 'S/D', 'S/D', '1.5', '0', '40', '0', '95', '25', '488', '945', '130', '65', '10', 'S/D', '6', 'S/D', '10', 'S/D', 'S/D']
        ]
        return headers, rows
    elif tipo == 'clientes':
        headers = ['Cliente', 'Sucursal', 'Direccion', 'Link Maps', 'Coordenadas']
        rows = [['Empresa Demo', 'Matriz', 'Av. Reforma 123', 'https://maps.google.com/...', '19.4326, -99.1332']]
        return headers, rows
    elif tipo == 'baterias_modelos':
        headers = ['modelo','serie','voltaje_nominal','capacidad_nominal_ah','resistencia_interna_mohm','max_corriente_descarga_5s_a','largo_mm','ancho_mm','alto_contenedor_mm','alto_total_mm','peso_kg','tipo_terminal','material_contenedor','carga_flotacion_v_min','carga_flotacion_v_max','coef_temp_flotacion_mv_c','carga_ciclica_v_min','carga_ciclica_v_max','corriente_inicial_max_a','coef_temp_ciclica_mv_c','temp_descarga_min_c','temp_descarga_max_c','temp_carga_min_c','temp_carga_max_c','temp_almacenaje_min_c','temp_almacenaje_max_c','temp_nominal_c','capacidad_40c_pct','capacidad_25c_pct','capacidad_0c_pct','autodescarga_meses_max']
        rows = [['LBS12-100','General Purpose','12','100.0','4.9','1200.0','330','173','212','220','30.6','T11','ABS','13.5','13.8','-20','14.4','15.0','30.0','-30','-15','50','0','40','-15','40','25','103','100','86','6']]
        return headers, rows
    elif tipo == 'baterias_curvas':
        headers = ['Modelo', 'Unidad', 'Tiempo_Min', 'FV_1.60', 'FV_1.65', 'FV_1.70', 'FV_1.75', 'FV_1.80']
        rows = [
            ['LBS12-100', 'W', '15', '300', '290', '280', '270', '260'],
            ['LBS12-100', 'A', '15', '28', '27', '26', '25', '24']
        ]
        return headers, rows
    return [], []