import os
from app.calculos import CalculadoraUPS, CalculadoraBaterias

def procesar_post_gestion(db, request, state):
    """Despachador principal de lógica POST para gestión"""
    tipo = request.form.get('tipo')
    accion = request.form.get('accion')
    
    # Actualizar estado base desde el form
    if request.form.get('active_tab'): state['active_tab'] = request.form.get('active_tab')
    if request.form.get('unidad_curva'): state['unidad_curva'] = request.form.get('unidad_curva')
    state['error_logs'] = None # Limpiar logs en cada POST

    # 1. Carga Masiva
    if request.files.get('archivo_csv'):
        mensaje, logs = _procesar_carga_masiva(db, request.files['archivo_csv'], request.form.get('tipo_carga'))
        state['mensaje'] = mensaje
        state['error_logs'] = logs
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
        elif 'bateria' in accion or accion in ['subir_curvas', 'guardar_curvas', 'cambiar_unidad_curva_W', 'cambiar_unidad_curva_A']:
            _procesar_acciones_bateria(db, request, state, accion)
        elif 'personal' in accion:
            _procesar_acciones_personal(db, request, state, accion)

def _procesar_acciones_tipo(db, request, state, tipo):
    """Maneja add_cliente, del_cliente, del_ups, del_bateria, add_tipo_vent, del_tipo_vent"""
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
    elif tipo == 'add_personal':
        db.agregar_personal(request.form)
        state['active_tab'] = 'personal'
        return True
    elif tipo == 'edit_personal':
        id_personal = request.form.get('id_personal')
        state['personal_seleccionado'] = db.obtener_personal_id(id_personal)
        state['active_tab'] = 'personal'
        return True
    elif tipo == 'update_personal':
        db.actualizar_personal(request.form.get('id'), request.form)
        state['active_tab'] = 'personal'
        state['personal_seleccionado'] = None
        state['mensaje'] = "Personal actualizado correctamente"
        return True
    elif tipo == 'cancelar_edit_personal':
        state['personal_seleccionado'] = None
        state['active_tab'] = 'personal'
        return True
    elif tipo == 'del_personal':
        db.eliminar_personal(request.form.get('id'))
        state['active_tab'] = 'personal'
        return True
    elif tipo == 'add_tipo_vent':
        print(f"➕ Agregando nuevo tipo de ventilación")

        # Manejar imagen si existe
        imagen_url = None
        if 'imagen_ventilacion' in request.files:
            file = request.files['imagen_ventilacion']
            print(f"📁 Archivo recibido: {file.filename if file else 'None'}")
            if file and file.filename != '':
                print(f"💾 Intentando guardar imagen...")
                imagen_url = guardar_imagen_ups(file)
                if imagen_url:
                    print(f"✅ Imagen guardada como: {imagen_url}")
                else:
                    print(f"❌ Error: guardar_imagen_ups retornó None")

        success = db.agregar_tipo_ventilacion(request.form, imagen_url)
        state['active_tab'] = 'ventilacion'

        if success:
            if imagen_url:
                state['mensaje'] = '✅ Tipo de ventilación agregado con imagen correctamente'
            else:
                state['mensaje'] = '✅ Tipo de ventilación agregado (sin imagen)'
        else:
            state['mensaje'] = '❌ Error al agregar. Puede que el nombre ya exista. Revise la consola del servidor.'

        return True
    elif tipo == 'del_tipo_vent':
        success = db.eliminar_tipo_ventilacion(request.form.get('id'))
        state['active_tab'] = 'ventilacion'
        state['mensaje'] = 'Tipo de ventilación eliminado' if success else 'Error al eliminar (puede estar en uso)'
        return True
    elif tipo == 'edit_tipo_vent':
        id_tipo = request.form.get('id_tipo_vent')
        state['tipo_vent_seleccionado'] = db.obtener_tipo_ventilacion_id(id_tipo)
        state['active_tab'] = 'ventilacion'
        return True
    elif tipo == 'update_tipo_vent':
        id_tipo = request.form.get('id')
        print(f"🔄 Procesando actualización de tipo ventilación ID: {id_tipo}")

        # Manejar imagen si existe
        imagen_url = None
        if 'imagen_ventilacion' in request.files:
            file = request.files['imagen_ventilacion']
            print(f"📁 Archivo recibido: {file.filename if file else 'None'}")
            if file and file.filename != '':
                print(f"💾 Intentando guardar imagen...")
                imagen_url = guardar_imagen_ups(file)
                if imagen_url:
                    print(f"✅ Imagen guardada como: {imagen_url}")
                else:
                    print(f"❌ Error: guardar_imagen_ups retornó None")
        else:
            print(f"ℹ️ No se envió archivo de imagen")

        success = db.actualizar_tipo_ventilacion(id_tipo, request.form, imagen_url)
        state['active_tab'] = 'ventilacion'

        if success:
            if imagen_url:
                state['mensaje'] = '✅ Tipo de ventilación e imagen actualizados correctamente'
            else:
                state['mensaje'] = '✅ Tipo de ventilación actualizado (sin cambio de imagen)'
        else:
            state['mensaje'] = '❌ Error al actualizar. Revise la consola del servidor para más detalles.'

        return True
    elif tipo == 'cancelar_edit_tipo_vent':
        state['tipo_vent_seleccionado'] = None
        state['active_tab'] = 'ventilacion'
        return True
    return False

def guardar_imagen_ups(file):
    """Guarda una imagen de UPS en la carpeta static/img/ups y retorna su nombre."""
    if not file or file.filename == '': return None

    try:
        # Asegurar que el nombre de archivo es seguro
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)

        # Si el nombre quedó vacío después de secure_filename, usar timestamp
        if not filename:
            import time
            ext = '.png'  # extensión por defecto
            if '.' in file.filename:
                ext = '.' + file.filename.rsplit('.', 1)[1].lower()
            filename = f'imagen_{int(time.time())}{ext}'

        # Crear ruta de guardado
        base_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(base_dir, 'static', 'img', 'ups')
        if not os.path.exists(upload_dir): os.makedirs(upload_dir)

        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        print(f"✅ Imagen guardada exitosamente: {filename}")
        return filename # Guardar solo el nombre del archivo en la BD
    except Exception as e:
        print(f"❌ Error guardando imagen: {e}")
        return None

def _procesar_acciones_ups(db, request, state, accion):
    """Lógica de estado para UPS"""
    state['active_tab'] = 'ups'
    
    if accion == 'iniciar_agregar_ups':
        state['agregando_ups'] = True
        
    elif accion == 'editar_ups':
        id_ups = request.form.get('id_ups')
        state['ups_seleccionado'] = db.obtener_ups_id(id_ups)
        
    elif accion == 'guardar_ups':
        datos_form = request.form.to_dict()
        id_ups = datos_form.get('id')

        # VALIDACIÓN 1: Número de modelo no vacío
        numero_modelo = datos_form.get('Nombre_del_Producto', '').strip()
        if not numero_modelo:
            state['mensaje'] = "❌ ERROR: El número de modelo es obligatorio. Por favor ingrese un nombre de producto."
            if id_ups:
                state['ups_seleccionado'] = db.obtener_ups_id(id_ups)
            else:
                state['agregando_ups'] = True
            return

        # VALIDACIÓN 2: Número de modelo no duplicado
        if db.verificar_modelo_ups_existe(numero_modelo, excluir_id=id_ups):
            state['mensaje'] = f"❌ ERROR: Ya existe un equipo con el modelo '{numero_modelo}'. Por favor use un nombre diferente."
            if id_ups:
                state['ups_seleccionado'] = db.obtener_ups_id(id_ups)
            else:
                state['agregando_ups'] = True
            return

        # --- Lógica de subida de imagen ---
        file = request.files.get('imagen_ups')
        if file and file.filename:
            nombre_archivo = guardar_imagen_ups(file)
            if nombre_archivo:
                datos_form['imagen_url'] = nombre_archivo

        # --- Nuevas imagenes de reporte ---
        file_instalacion = request.files.get('imagen_instalacion')
        if file_instalacion and file_instalacion.filename:
            nombre_archivo_inst = guardar_imagen_ups(file_instalacion)
            if nombre_archivo_inst:
                datos_form['imagen_instalacion_url'] = nombre_archivo_inst
        
        file_baterias = request.files.get('imagen_baterias')
        if file_baterias and file_baterias.filename:
            nombre_archivo_bat = guardar_imagen_ups(file_baterias)
            if nombre_archivo_bat:
                datos_form['imagen_baterias_url'] = nombre_archivo_bat

        exito = False
        if id_ups:
            exito = db.actualizar_ups(id_ups, datos_form)
            state['mensaje'] = "✅ Equipo actualizado correctamente." if exito else "❌ Error al actualizar."
            if exito: # Recargar datos si la actualización fue exitosa
                state['ups_seleccionado'] = db.obtener_ups_id(id_ups)
        else:
            exito = db.insertar_ups_manual(datos_form)
            state['mensaje'] = "✅ Nuevo equipo agregado." if exito else "❌ Error al agregar."
            if exito: # Limpiar para permitir agregar otro
                 state['agregando_ups'] = False
            
    elif accion == 'cancelar_edicion_ups':
        state['ups_seleccionado'] = None
        state['agregando_ups'] = False

def _procesar_acciones_bateria(db, request, state, accion):
    """Lógica de estado para Baterías"""
    state['active_tab'] = 'baterias'
    id_bat = request.form.get('id') or request.form.get('id_bateria')

    # --- Acciones que cambian la unidad de la curva y recargan ---
    if accion.startswith('cambiar_unidad_curva'):
        state['unidad_curva'] = 'A' if accion.endswith('_A') else 'W'
    
    # --- Acción para guardar curvas editadas desde la tabla ---
    elif accion == 'guardar_curvas':
        if id_bat:
            res = db.actualizar_curvas_desde_form(id_bat, request.form)
            state['mensaje'] = f"✅ Curvas guardadas: {res.get('insertados', 0)} puntos actualizados." if res.get('status') == 'ok' else f"❌ Error: {res.get('msg')}"
            state['error_logs'] = res.get('logs')

    # --- Acción para iniciar la adición de una nueva batería ---
    elif accion == 'iniciar_agregar_bateria':
        state['agregando_bateria'] = True
        
    # --- Acción para guardar el modelo de batería (la ficha técnica) ---
    elif accion == 'guardar_bateria':
        if id_bat:
            if db.actualizar_bateria(id_bat, request.form):
                state['mensaje'] = "✅ Batería actualizada."
            else:
                state['mensaje'] = "❌ Error al actualizar."
        else:
            if db.agregar_modelo_bateria(request.form):
                state['mensaje'] = "✅ Nueva batería agregada."
            else:
                state['mensaje'] = "❌ Error al agregar."
                
    # --- Acción para subir un nuevo archivo CSV de curvas ---
    elif accion == 'subir_curvas':
        file = request.files.get('archivo_csv')
        if id_bat and file and file.filename:
            filepath = guardar_archivo_temporal(file)
            if filepath:
                res = db.cargar_curvas_por_id_csv(id_bat, filepath)
                state['mensaje'] = f"✅ Archivo procesado. {res.get('insertados', 0)} registros insertados." if res['status'] == 'ok' else f"❌ Error: {res.get('msg')}"
                state['error_logs'] = res.get('logs')
        else:
            state['mensaje'] = "⚠️ No se seleccionó un archivo CSV para subir."

    # --- Cancelar edición/adición ---
    elif accion == 'cancelar_edicion_bateria':
        state['bateria_seleccionada'] = None
        state['agregando_bateria'] = False
        return # Evitar recarga de datos innecesaria

    # --- Recargar siempre los datos de la batería y las curvas al final ---
    if id_bat and not state.get('agregando_bateria'):
        state['bateria_seleccionada'] = db.obtener_bateria_id(id_bat)
        if state['bateria_seleccionada']:
            state['pivot_data'] = db.obtener_curvas_pivot(id_bat, unidad=state['unidad_curva'])
        pass

def _procesar_acciones_personal(db, request, state, accion):
    """Lógica de estado para Personal"""
    state['active_tab'] = 'personal'
    
    if accion == 'iniciar_agregar_personal':
        state['agregando_personal'] = True
        
    elif accion == 'cancelar_edicion_personal':
        state['personal_seleccionado'] = None
        state['agregando_personal'] = False
        
    elif accion == 'editar_personal':
        id_personal = request.form.get('id_personal')
        # Buscamos en la lista de personal (no hay método específico obtener_personal_id en DB todavía, usamos filtro)
        todos = db.obtener_personal()
        found = next((p for p in todos if str(p['id']) == str(id_personal)), None)
        state['personal_seleccionado'] = found
        
    elif accion == 'guardar_personal':
        nombre = request.form.get('nombre')
        puesto = request.form.get('puesto')
        id_personal = request.form.get('id')
        
        if id_personal:
            if db.actualizar_personal(id_personal, nombre, puesto):
                state['mensaje'] = "✅ Personal actualizado."
                state['personal_seleccionado'] = None
            else:
                 state['mensaje'] = "❌ Error al actualizar personal."
        else:
            if db.agregar_personal(nombre, puesto):
                state['mensaje'] = "✅ Personal agregado."
                state['agregando_personal'] = False
            else:
                state['mensaje'] = "❌ Error al agregar personal."

def guardar_archivo_temporal(file):
    """Guarda un archivo subido en la carpeta uploads y retorna su ruta"""
    if not file or file.filename == '': return None
    from werkzeug.utils import secure_filename
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(base_dir, 'static', 'uploads')
    if not os.path.exists(upload_dir): os.makedirs(upload_dir)
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    return filepath

def guardar_imagen_proyecto(file, pedido):
    """Guarda una imagen permanente en la carpeta del proyecto"""
    if not file or file.filename == '': return None
    from werkzeug.utils import secure_filename
    import time

    # Crear nombre único con timestamp
    filename = secure_filename(file.filename)
    nombre_base, extension = os.path.splitext(filename)
    timestamp = int(time.time())
    filename_unico = f"{nombre_base}_{timestamp}{extension}"

    # Crear carpeta del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    proyecto_dir = os.path.join(base_dir, 'static', 'img', 'proyectos', pedido)
    if not os.path.exists(proyecto_dir): os.makedirs(proyecto_dir)

    filepath = os.path.join(proyecto_dir, filename_unico)
    file.save(filepath)
    return filename_unico  # Retorna solo el nombre del archivo

def guardar_pdf_proyecto(pdf_bytes, pedido, tipo='guia'):
    """
    Guarda un PDF permanentemente en la carpeta del proyecto

    Args:
        pdf_bytes: bytes del PDF a guardar
        pedido: número de pedido
        tipo: 'guia' o 'checklist'

    Returns:
        ruta relativa del PDF guardado (para almacenar en BD)
    """
    from datetime import datetime

    # Crear carpeta del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    proyecto_dir = os.path.join(base_dir, 'static', 'pdf', 'proyectos', str(pedido))
    if not os.path.exists(proyecto_dir):
        os.makedirs(proyecto_dir)

    # Nombre del archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if tipo == 'guia':
        filename = f"Guia_Instalacion_{pedido}_{timestamp}.pdf"
    else:
        filename = f"Checklist_{pedido}_{timestamp}.pdf"

    filepath = os.path.join(proyecto_dir, filename)

    # Guardar PDF
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)

    # Retornar ruta relativa desde static
    return f"pdf/proyectos/{pedido}/{filename}"

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
    
    # Mensaje inicial (la publicación se hace en rutas.py con todos los datos)
    mensaje = "👁️ VISTA PREVIA GENERADA" if accion != 'publicar' else "📊 Cálculos realizados"

    return resultado, mensaje

def _procesar_carga_masiva(db, file, tipo_carga):
    filepath = guardar_archivo_temporal(file)
    if not filepath:
        return "⚠️ Error en archivo. No se pudo guardar.", None

    res = {}
    if tipo_carga == 'ups': 
        res = db.cargar_ups_desde_csv(filepath)
    elif tipo_carga == 'clientes': 
        res = db.cargar_clientes_desde_csv(filepath)
    elif tipo_carga == 'baterias_modelos': 
        res = db.cargar_baterias_modelos_desde_csv(filepath)
    elif tipo_carga == 'baterias_curvas': 
        res = db.cargar_curvas_baterias_masiva(filepath)
    else:
        return "⚠️ Tipo de carga masiva no reconocido.", None

    # Formatear mensaje de respuesta
    insertados = res.get('insertados', 0)
    errores = res.get('errores', 0)
    
    if res.get('status') == 'ok':
        if errores > 0:
            mensaje = f"🟡 Carga parcial: {insertados} registros insertados, {errores} filas con errores. Revise los detalles."
        else:
            mensaje = f"✅ Carga masiva procesada: {insertados} registros insertados."
    else:
        mensaje = f"❌ Error en carga masiva: {res.get('msg', 'Error desconocido.')}"

    return mensaje, res.get('logs')

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