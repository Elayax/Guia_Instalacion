from flask import Blueprint, render_template, request, make_response, redirect, url_for
from datetime import datetime
from app.calculos import CalculadoraUPS
from app.reporte import ReportePDF
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
    lista_baterias = db.obtener_baterias_modelos(solo_con_curvas=True)
    
    resultado = None
    mensaje = None
    
    if request.method == 'POST':
        resultado, mensaje = procesar_calculo_ups(db, request.form)

    return render_template('index.html', clientes=lista_clientes_unicos, ups=lista_ups, baterias=lista_baterias, res=resultado, msg=mensaje)

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
                filepath = guardar_archivo_temporal(file)
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
    # Estado inicial de la vista (Diccionario de contexto)
    state = {
        'mensaje': None,
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
                           msg=state['mensaje'],
                           ups_seleccionado=state['ups_seleccionado'],
                           agregando_ups=state['agregando_ups'],
                           bateria_seleccionada=state['bateria_seleccionada'],
                           agregando_bateria=state['agregando_bateria'],
                           unidad_curva=state['unidad_curva'],
                           pivot_data=state['pivot_data'],
                           active_tab=state['active_tab'])

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