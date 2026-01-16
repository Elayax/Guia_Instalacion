from flask import Blueprint, render_template, request, make_response, redirect, url_for
from datetime import datetime
from app.calculos import CalculadoraUPS
from app.reporte import ReportePDF
from app.base_datos import GestorDB
import json
import os
import csv
import io

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

@main.route('/', methods=['GET', 'POST'])
def index():
    # 1. Cargar listas iniciales
    lista_clientes_unicos = db.obtener_clientes_unicos() # Solo nombres
    lista_ups = db.obtener_ups_todos()
    lista_baterias = db.obtener_baterias_modelos()
    
    resultado = None
    mensaje = None
    
    # ... (El resto de la lógica POST se mantiene casi igual, 
    # solo asegúrate de recibir 'lat_oculta' y 'lon_oculta' del formulario) ...
    
    if request.method == 'POST':
        f = request.form
        accion = f.get('accion')
        id_ups = f.get('id_ups')
        
        if id_ups:
            ups_data = db.obtener_ups_id(id_ups)
            
            if ups_data:
                # Preparar datos para cálculo
                # Si el usuario no selecciona voltaje (ej. auto), usar el de la BD
                voltaje_sel = f.get('voltaje')
                if not voltaje_sel:
                    voltaje_sel = ups_data.get('Voltaje_Entrada_1_V')
                
                datos_calc = {
                    'kva': ups_data.get('Capacidad_kVA') or 0,
                    'voltaje': voltaje_sel or 0,
                    'fases': f.get('fases') or 0,
                    'longitud': f.get('longitud') or 0,
                    'lat': f.get('lat_oculta'),
                    'lon': f.get('lon_oculta'),
                    'tiempo_respaldo': f.get('tiempo_respaldo')
                }
                
                calc = CalculadoraUPS()
                resultado = calc.calcular(datos_calc)
                
                # Enriquecer resultado con datos del equipo y cliente para el reporte
                resultado.update({
                    'Nombre_del_Producto': ups_data.get('Nombre_del_Producto'),
                    'modelo_nombre': ups_data.get('Nombre_del_Producto'),
                    'fabricante': ups_data.get('Serie'),
                    'cliente_nom': f.get('cliente_texto'),
                    'sucursal_nom': f.get('sucursal_texto'),
                    'pedido': f.get('pedido'),
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
                
                if accion == 'publicar':
                    if not f.get('pedido'):
                        mensaje = "⚠️ Falta el número de Pedido"
                    else:
                        save_data = {
                            'pedido': f.get('pedido'),
                            'cliente_nombre': f.get('cliente_texto'),
                            'sucursal_nombre': f.get('sucursal_texto'),
                            'fases': f.get('fases')
                        }
                        if db.publicar_proyecto(resultado, save_data):
                            mensaje = "✅ PROYECTO PUBLICADO CORRECTAMENTE"
                            resultado['es_publicado'] = True
                        else:
                            mensaje = "⚠️ ERROR: El número de pedido ya existe."
                else:
                    mensaje = "👁️ VISTA PREVIA GENERADA"
            else:
                mensaje = "❌ Error: Equipo no encontrado en la base de datos."

    return render_template('index.html', clientes=lista_clientes_unicos, ups=lista_ups, baterias=lista_baterias, res=resultado, msg=mensaje)

# --- CARGA MASIVA ---
@main.route('/carga-masiva', methods=['GET', 'POST'])
def carga_masiva():
    if request.method == 'POST':
        file = request.files.get('archivo_csv')
        tipo = request.form.get('tipo_carga') # 'ups' o 'clientes'
        
        if file and file.filename != '':
            # Guardar archivo temporalmente
            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.path.join(base_dir, 'static', 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            filepath = os.path.join(upload_dir, file.filename)
            file.save(filepath)
            
            # Procesar según selección
            if tipo == 'ups':
                db.cargar_ups_desde_csv(filepath)
            elif tipo == 'clientes':
                db.cargar_clientes_desde_csv(filepath)
            elif tipo == 'baterias_modelos':
                db.cargar_baterias_modelos_desde_csv(filepath)
            elif tipo == 'baterias_curvas':
                db.cargar_curvas_baterias_masiva(filepath)
                
            return redirect(url_for('main.gestion'))
            
    return render_template('carga_masiva.html')

@main.route('/descargar-plantilla/<tipo>')
def descargar_plantilla(tipo):
    si = io.StringIO()
    writer = csv.writer(si)
    
    if tipo == 'ups':
        headers = ['Nombre del Producto', 'Serie', 'Capacidad_kVA', 'Capacidad_kW', 'Eficiencia_Modo_AC_pct', 'Eficiencia_Modo_Bateria_pct', 'Eficiencia_Modo_ECO_pct', 'FP_Salida', 'Voltaje_Entrada_1_V', 'Voltaje_Entrada_2_V', 'Voltaje_Entrada_3_V', 'Conexion_Entrada', 'Voltaje_Salida_1_V', 'Voltaje_Salida_2_V', 'Voltaje_Salida_3_V', 'Conexion_Salida', 'Frecuencia_1_Hz', 'Frecuencia_2_Hz', 'Frecuencia_Precision_pct', 'THDu_Lineal_pct', 'THDu_NoLineal_pct', 'Sobrecarga_110_pct_min', 'Sobrecarga_125_pct_min', 'Sobrecarga_150_pct_min', 'Bateria_Vdc', 'Bateria_Piezas_min', 'Bateria_Piezas_max', 'Bateria_Piezas_defecto', 'Precision_Voltaje_pct', 'TempTrabajo_min_C', 'TempTrabajo_max_C', 'Humedad_min_pct', 'Humedad_max_pct', 'Peso_Gabinete_kg', 'Dim_Largo_mm', 'Dim_Ancho_mm', 'Dim_Alto_mm', 'Nivel_Ruido_dB', 'Cable_Entrada_mm2', 'Cable_Entrada_conductores', 'Cable_Salida_mm2', 'Cable_Salida_conductores', 'Cable_Bateria_mm2', 'Cable_Bateria_conductores', 'Cable_PE_mm2']
        writer.writerow(headers)
        
        # Datos completos proporcionados
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
        writer.writerows(rows)
    elif tipo == 'clientes':
        headers = ['Cliente', 'Sucursal', 'Direccion', 'Link Maps', 'Coordenadas']
        writer.writerow(headers)
        writer.writerow(['Empresa Demo', 'Matriz', 'Av. Reforma 123', 'https://maps.google.com/...', '19.4326, -99.1332'])
    elif tipo == 'baterias_modelos':
        headers = ['modelo','serie','voltaje_nominal','capacidad_nominal_ah','resistencia_interna_mohm','max_corriente_descarga_5s_a','largo_mm','ancho_mm','alto_contenedor_mm','alto_total_mm','peso_kg','tipo_terminal','material_contenedor','carga_flotacion_v_min','carga_flotacion_v_max','coef_temp_flotacion_mv_c','carga_ciclica_v_min','carga_ciclica_v_max','corriente_inicial_max_a','coef_temp_ciclica_mv_c','temp_descarga_min_c','temp_descarga_max_c','temp_carga_min_c','temp_carga_max_c','temp_almacenaje_min_c','temp_almacenaje_max_c','temp_nominal_c','capacidad_40c_pct','capacidad_25c_pct','capacidad_0c_pct','autodescarga_meses_max']
        writer.writerow(headers)
        writer.writerow(['LBS12-100','General Purpose','12','100.0','4.9','1200.0','330','173','212','220','30.6','T11','ABS','13.5','13.8','-20','14.4','15.0','30.0','-30','-15','50','0','40','-15','40','25','103','100','86','6'])
    elif tipo == 'baterias_curvas':
        headers = ['Modelo', 'Unidad', 'Tiempo_Min', 'FV_1.60', 'FV_1.65', 'FV_1.70', 'FV_1.75', 'FV_1.80']
        writer.writerow(headers)
        writer.writerow(['LBS12-100', 'W', '15', '300', '290', '280', '270', '260'])
        writer.writerow(['LBS12-100', 'A', '15', '28', '27', '26', '25', '24'])
        
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

# --- EDICIÓN DE EQUIPOS ---
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
            # Actualizamos en BD
            if db.actualizar_ups(id_ups, request.form):
                mensaje = "✅ Equipo actualizado correctamente."
                # Recargamos los datos actualizados
                ups_seleccionado = db.obtener_ups_id(id_ups)
            else:
                mensaje = "❌ Error al actualizar el equipo."
                
    return render_template('equipos.html', ups_lista=lista_ups, ups=ups_seleccionado, msg=mensaje)

# --- GESTIÓN DE BATERÍAS (NUEVA RUTA) ---
@main.route('/baterias', methods=['GET', 'POST'])
def baterias():
    bateria_seleccionada = None
    mensaje = None
    lista_baterias = db.obtener_baterias_modelos()
    curvas = []
    pivot_data = None
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'buscar':
            id_busqueda = request.form.get('id_bateria_buscar')
            if id_busqueda:
                bateria_seleccionada = db.obtener_bateria_id(id_busqueda)
                if bateria_seleccionada:
                    pivot_data = db.obtener_curvas_pivot(bateria_seleccionada['id'])
                
        elif accion == 'guardar':
            id_bat = request.form.get('id')
            if db.actualizar_bateria(id_bat, request.form):
                mensaje = "✅ Batería actualizada correctamente."
                bateria_seleccionada = db.obtener_bateria_id(id_bat)
                if bateria_seleccionada:
                    pivot_data = db.obtener_curvas_pivot(bateria_seleccionada['id'])
            else:
                mensaje = "❌ Error al actualizar la batería."
        
        elif accion == 'subir_curvas':
            id_bat = request.form.get('id')
            file = request.files.get('archivo_csv')
            if id_bat and file and file.filename != '':
                base_dir = os.path.dirname(os.path.abspath(__file__))
                upload_dir = os.path.join(base_dir, 'static', 'uploads')
                if not os.path.exists(upload_dir): os.makedirs(upload_dir)
                filepath = os.path.join(upload_dir, file.filename)
                file.save(filepath)
                
                res = db.cargar_curvas_por_id_csv(id_bat, filepath)
                if res['status'] == 'ok':
                    mensaje = f"✅ Curvas actualizadas. {res['insertados']} registros insertados."
                else:
                    mensaje = f"❌ Error: {res['msg']}"
                
                bateria_seleccionada = db.obtener_bateria_id(id_bat)
                pivot_data = db.obtener_curvas_pivot(id_bat)
                
    return render_template('baterias.html', baterias_lista=lista_baterias, bateria=bateria_seleccionada, pivot_data=pivot_data, msg=mensaje)

# --- GESTIÓN DE BD ---
@main.route('/gestion', methods=['GET', 'POST'])
def gestion():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        if tipo == 'add_cliente':
            db.agregar_cliente(request.form)
        elif tipo == 'del_cliente':
            db.eliminar_cliente(request.form.get('id'))
        elif tipo == 'add_ups':
            # db.agregar_ups(request.form) # Deshabilitado temporalmente por cambio de esquema
            pass
        elif tipo == 'del_ups':
            db.eliminar_ups(request.form.get('id'))
        elif tipo == 'del_bateria':
            db.eliminar_bateria(request.form.get('id'))
        return redirect(url_for('main.gestion'))

    clientes = db.obtener_clientes()
    ups_lista = db.obtener_ups_todos()
    proyectos = db.obtener_proyectos()
    baterias = db.obtener_baterias_modelos()
    return render_template('gestion.html', clientes=clientes, ups=ups_lista, proyectos=proyectos, baterias=baterias)

# --- GENERAR PDF ---
@main.route('/descargar-pdf', methods=['POST'])
def descargar_pdf():
    datos = request.form.to_dict()
    
    if not datos.get('kva') or not datos.get('voltaje'):
         return "Error: Faltan datos técnicos.", 400

    # Obtener datos de batería si se seleccionó alguna
    id_bateria = datos.get('id_bateria')
    bateria_info = {}
    if id_bateria:
        bateria_info = db.obtener_bateria_id(id_bateria) or {}

    # Recalculamos para el PDF
    calc = CalculadoraUPS()
    res = calc.calcular(datos)
    
    # Pasamos datos visuales extra
    res['modelo_nombre'] = datos.get('modelo_nombre')
    es_publicado = datos.get('es_publicado') == 'True'
    
    pdf = ReportePDF()
    pdf_bytes = pdf.generar_cuerpo(datos, res, bateria=bateria_info, es_publicado=es_publicado)
    
    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    nombre_seguro = str(datos.get("pedido", "reporte")).replace(" ", "_")
    response.headers['Content-Disposition'] = f'attachment; filename=Memoria_{nombre_seguro}.pdf'
    return response