from flask import Blueprint, render_template, request, make_response, redirect, url_for
from app.calculos import CalculadoraUPS
from app.reporte import ReportePDF
from app.base_datos import GestorDB
import json
import os
from werkzeug.utils import secure_filename

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
                'kva': ups_data['kva'],
                'voltaje': f.get('voltaje') or ups_data['v_entrada'],
                'fases': f.get('fases'),
                'longitud': f.get('longitud') or 0,
                'lat': f.get('lat_oculta'),
                'lon': f.get('lon_oculta')
            }
            calc = CalculadoraUPS()
            resultado = calc.calcular(datos_calc)
            
            # Datos extra para el template
            resultado['modelo_nombre'] = ups_data['modelo']
            resultado['fabricante'] = ups_data['fabricante']
            resultado['cliente_nom'] = f.get('cliente_texto') # Ojo aquí
            resultado['sucursal_nom'] = f.get('sucursal_texto')
            resultado['pedido'] = f.get('pedido')
            resultado['kva'] = ups_data['kva']
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
            db.agregar_ups(request.form)
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

    if not datos.get('longitud'):
        datos['longitud'] = 0

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

# --- CARGA MASIVA ---
@main.route('/carga-masiva', methods=['GET', 'POST'])
def carga_masiva():
    resultado = None
    
    if request.method == 'POST':
        if 'archivo_csv' not in request.files:
            resultado = {'status': 'error', 'msg': 'No se seleccionó ningún archivo'}
        else:
            tipo_carga = request.form.get('tipo_carga', 'clientes') # Default a clientes
            archivo = request.files['archivo_csv']
            if archivo.filename == '':
                resultado = {'status': 'error', 'msg': 'Nombre de archivo vacío'}
            elif archivo and archivo.filename.endswith('.csv'):
                filename = secure_filename(archivo.filename)
                ruta_temp = os.path.join(os.path.dirname(__file__), 'static', filename)
                archivo.save(ruta_temp)
                
                # Procesar
                if tipo_carga == 'equipos':
                    resultado = db.cargar_ups_desde_csv(ruta_temp)
                else:
                    resultado = db.cargar_clientes_desde_csv(ruta_temp)
                
                # Limpiar
                if os.path.exists(ruta_temp):
                    os.remove(ruta_temp)
            else:
                resultado = {'status': 'error', 'msg': 'Formato inválido. Solo se permite .CSV'}
                
    return render_template('carga_masiva.html', res=resultado)

@main.route('/descargar-plantilla')
def descargar_plantilla():
    tipo = request.args.get('tipo', 'clientes')
    
    if tipo == 'equipos':
        csv_content = "\ufeffMarca,Modelo,Capacidad\nAPC,Smart-UPS 3000,3.0\nEaton,9PX 6000,6.0"
        nombre_archivo = "plantilla_equipos_ups.csv"
    else:
        csv_content = "\ufeffCliente,Sucursal,Direccion,LinkMaps,LatLon\nEmpresa Demo,Planta 1,Av. Reforma 123,https://maps.google.com/?q=...,\"19.43, -99.13\""
        nombre_archivo = "plantilla_clientes.csv"
        
    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = f"attachment; filename={nombre_archivo}"
    return response