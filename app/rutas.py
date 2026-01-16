from flask import Blueprint, render_template, request, make_response, redirect, url_for
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

@main.route('/', methods=['GET', 'POST'])
def index():
    # 1. Cargar listas iniciales
    lista_clientes_unicos = db.obtener_clientes_unicos() # Solo nombres
    lista_ups = db.obtener_ups_todos()
    
    resultado = None
    mensaje = None
    
    # ... (El resto de la lógica POST se mantiene casi igual, 
    # solo asegúrate de recibir 'lat_oculta' y 'lon_oculta' del formulario) ...
    
    if request.method == 'POST':
        f = request.form
        accion = f.get('accion')
        
        # VALIDACIONES Y CÁLCULOS (Tu lógica actual funciona bien aquí)
        # ... [Copia tu lógica de cálculo aquí] ...
        # Solo recuerda usar: f.get('voltaje') y f.get('fases')
        
        # Ejemplo rápido de la parte de cálculo para que no te pierdas:
        id_ups = f.get('id_ups')
        if id_ups:
            ups_data = db.obtener_ups_id(id_ups)
            datos_calc = {
                'kva': ups_data['Capacidad_kVA'],
                'voltaje': f.get('voltaje') or ups_data['Voltaje_Entrada_1_V'],
                'fases': f.get('fases'),
                'longitud': f.get('longitud'),
                'lat': f.get('lat_oculta'),
                'lon': f.get('lon_oculta')
            }
            calc = CalculadoraUPS()
            resultado = calc.calcular(datos_calc)
            
            # Datos extra para el template
            resultado['Nombre_del_Producto'] = ups_data['Nombre_del_Producto']
            resultado['modelo_nombre'] = ups_data['Nombre_del_Producto'] # Alias para compatibilidad PDF
            resultado['fabricante'] = ups_data['Serie']
            resultado['cliente_nom'] = f.get('cliente_texto') # Ojo aquí
            resultado['sucursal_nom'] = f.get('sucursal_texto')
            resultado['pedido'] = f.get('pedido')
            resultado['kva'] = ups_data['Capacidad_kVA']
            resultado['Capacidad_kVA'] = ups_data['Capacidad_kVA'] # Para DB
            resultado['voltaje'] = datos_calc['voltaje']
            
            # Lógica de Publicar vs Preview (Igual que antes)
            if accion == 'publicar':
                if not f.get('pedido'):
                    mensaje = "⚠️ Falta el Pedido"
                else:
                    save_data = {
                        'pedido': f.get('pedido'),
                        'cliente_nombre': f.get('cliente_texto'),
                        'sucursal_nombre': f.get('sucursal_texto'),
                        'fases': f.get('fases')
                    }
                    if db.publicar_proyecto(resultado, save_data):
                        mensaje = "✅ PROYECTO PUBLICADO"
                        resultado['es_publicado'] = True
                    else:
                        mensaje = "⚠️ ERROR: Pedido duplicado"
            else:
                mensaje = "👁️ VISTA PREVIA"

    return render_template('index.html', clientes=lista_clientes_unicos, ups=lista_ups, res=resultado, msg=mensaje)

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
                
            return redirect(url_for('main.gestion'))
            
    return render_template('carga_masiva.html')

@main.route('/descargar-plantilla/<tipo>')
def descargar_plantilla(tipo):
    si = io.StringIO()
    writer = csv.writer(si)
    
    if tipo == 'ups':
        headers = ['Nombre del Producto', 'Serie', 'Fuente', 'Capacidad_kVA', 'Capacidad_kW', 'Eficiencia_Modo_AC_pct', 'Eficiencia_Modo_Bateria_pct', 'Eficiencia_Modo_ECO_pct', 'FP_Salida', 'Voltaje_Entrada_1_V', 'Voltaje_Entrada_2_V', 'Voltaje_Entrada_3_V', 'Conexion_Entrada', 'Voltaje_Salida_1_V', 'Voltaje_Salida_2_V', 'Voltaje_Salida_3_V', 'Conexion_Salida', 'Frecuencia_1_Hz', 'Frecuencia_2_Hz', 'Frecuencia_Precision_pct', 'THDu_Lineal_pct', 'THDu_NoLineal_pct', 'Sobrecarga_110_pct_min', 'Sobrecarga_125_pct_min', 'Sobrecarga_150_pct_min', 'Bateria_Vdc', 'Bateria_Piezas_min', 'Bateria_Piezas_max', 'Bateria_Piezas_defecto', 'Precision_Voltaje_pct', 'TempTrabajo_min_C', 'TempTrabajo_max_C', 'Humedad_min_pct', 'Humedad_max_pct', 'Peso_Gabinete_kg', 'Dim_Largo_mm', 'Dim_Ancho_mm', 'Dim_Alto_mm', 'Nivel_Ruido_dB', 'Torque_M6_Nm', 'Torque_M8_Nm', 'Torque_M10_Nm', 'Torque_M12_Nm', 'Torque_M16_Nm', 'Cable_Entrada_mm2', 'Cable_Entrada_conductores', 'Cable_Salida_mm2', 'Cable_Salida_conductores', 'Cable_Bateria_mm2', 'Cable_Bateria_conductores', 'Cable_PE_mm2']
        writer.writerow(headers)
        
        # Datos completos proporcionados
        rows = [
            ['Dragon Power Plus 60', 'Modular', '1', '60.0', '60.0', '96.0', '96.0', '', '1.0', '', '', '', '', '480.0', '', '', '(3P + N + PE)', '50.0', '60.0', '', '1.0', '5.0', '60.0', '10.0', '1.0', '240.0', '30.0', '50.0', '', '1.0', '0.0', '40.0', '0.0', '95.0', '', '442.0', '659.0', '174.0', '72.0', '', '', '', '', '', '240.0', '3.0', '', '', '240.0', '3.0', ''],
            ['Dragon Power Plus 50', 'Modular', '2, 3', '50.0', '50.0', '96.0', '', '', '1.0', '', '', '', '', '440.0', '460.0', '480.0', '(3P + N + PE)', '50.0', '60.0', '', '2.0', '4.0', '60.0', '10.0', '1.0', '240.0', '40.0', '50.0', '', '1.0', '0.0', '40.0', '0.0', '95.0', '180.0', '440.0', '620.0', '131.0', '65.0', '', '', '26.0', '', '', '150.0', '', '150.0', '', '150.0', '2.0', ''],
            ['Dragon Power Plus 40', 'Modular', '4', '40.0', '40.0', '96.0', '95.0', '', '1.0', '', '', '', '', '480.0', '', '', '(L-L)', '50.0', '60.0', '', '1.0', '5.5', '60.0', '10.0', '1.0', '240.0', '', '', '', '1.0', '0.0', '40.0', '0.0', '95.0', '120.0', '510.0', '700.0', '178.0', '72.0', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['Dragon Power Plus 40', 'Modular', '5', '40.0', '36.0', '96.0', '96.0', '', '0.9', '', '', '', '', '480.0', '', '', '', '50.0', '60.0', '', '1.0', '6.0', '60.0', '10.0', '1.0', '240.0', '32.0', '44.0', '40.0', '1.5', '0.0', '40.0', '0.0', '95.0', '120.0', '510.0', '700.0', '178.0', '65.0', '4.9', '', '', '', '', '50.0', '', '35.0', '', '50.0', '', ''],
            ['Dragon Power Plus 40', 'Modular', '5', '400.0', '360.0', '96.0', '96.0', '', '0.9', '', '', '', '', '480.0', '', '', '', '50.0', '60.0', '', '1.0', '6.0', '60.0', '10.0', '1.0', '240.0', '32.0', '44.0', '', '1.5', '0.0', '40.0', '0.0', '95.0', '450.0', '510.0', '700.0', '178.0', '65.0', '', '', '', '', '', '96.0', '2.0', '', '2.0', '', '2.0', '240.0', ''],
            ['Dragon Power Plus 30', 'Modular', '6', '30.0', '30.0', '', '93.0', '', '1.0', '', '', '', '', '208.0', '220.0', '', '(3P + N + PE)', '50.0', '60.0', '', '1.5', '6.0', '60.0', '10.0', '1.0', '120.0', '', '', '', '1.0', '0.0', '40.0', '0.0', '95.0', '210.0', '510.0', '700.0', '178.0', '68.0', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['Dragon Power Plus 30', 'Modular', '7', '30.0', '27.0', '94.0', '93.0', '', '0.9', '', '', '', '', '208.0', '120.0', '', '', '50.0', '60.0', '', '1.0', '6.0', '60.0', '10.0', '1.0', '120.0', '36.0', '44.0', '40.0', '1.5', '0.0', '40.0', '0.0', '95.0', '165.0', '510.0', '700.0', '178.0', '65.0', '4.9', '13.0', '', '', '', '70.0', '', '70.0', '', '2.0', '50.0', ''],
            ['Dragon Power Plus 30', 'Modular', '7', '60.0', '54.0', '94.0', '93.0', '', '0.9', '', '', '', '', '208.0', '120.0', '', '', '50.0', '60.0', '', '1.0', '6.0', '60.0', '10.0', '1.0', '120.0', '36.0', '44.0', '', '1.5', '0.0', '40.0', '0.0', '95.0', '210.0', '510.0', '700.0', '178.0', '65.0', '4.9', '13.0', '', '', '', '70.0', '', '70.0', '', '2.0', '50.0', ''],
            ['Dragon Power Plus 30', 'Modular', '7', '90.0', '81.0', '94.0', '93.0', '', '0.9', '', '', '', '', '208.0', '120.0', '', '', '50.0', '60.0', '', '1.0', '6.0', '60.0', '10.0', '1.0', '120.0', '36.0', '44.0', '', '1.5', '0.0', '40.0', '0.0', '95.0', '305.0', '510.0', '700.0', '178.0', '65.0', '', '', '15.0', '', '', '2.0', '', '2.0', '', '2.0', '120.0', '']
        ]
        writer.writerows(rows)
    elif tipo == 'clientes':
        headers = ['Cliente', 'Sucursal', 'Direccion', 'Link Maps', 'Coordenadas']
        writer.writerow(headers)
        writer.writerow(['Empresa Demo', 'Matriz', 'Av. Reforma 123', 'https://maps.google.com/...', '19.4326, -99.1332'])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=plantilla_{tipo}.csv"
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
        return redirect(url_for('main.gestion'))

    clientes = db.obtener_clientes()
    ups_lista = db.obtener_ups_todos()
    proyectos = db.obtener_proyectos()
    return render_template('gestion.html', clientes=clientes, ups=ups_lista, proyectos=proyectos)

# --- GENERAR PDF ---
@main.route('/descargar-pdf', methods=['POST'])
def descargar_pdf():
    datos = request.form.to_dict()
    
    if not datos.get('kva') or not datos.get('voltaje'):
         return "Error: Faltan datos técnicos.", 400

    # Recalculamos para el PDF
    calc = CalculadoraUPS()
    res = calc.calcular(datos)
    
    # Pasamos datos visuales extra
    res['modelo_nombre'] = datos.get('modelo_nombre')
    es_publicado = datos.get('es_publicado') == 'True'
    
    pdf = ReportePDF()
    pdf_bytes = pdf.generar_cuerpo(datos, res, es_publicado=es_publicado)
    
    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    nombre_seguro = str(datos.get("pedido", "reporte")).replace(" ", "_")
    response.headers['Content-Disposition'] = f'attachment; filename=Memoria_{nombre_seguro}.pdf'
    return response