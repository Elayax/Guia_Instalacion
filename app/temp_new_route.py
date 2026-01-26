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
    guardar_archivo_temporal,
    guardar_pdf_proyecto,
    guardar_imagen_proyecto
)
import json
import os
import csv
import io
import tempfile

main = Blueprint('main', __name__)
db = GestorDB() 

# NUEVA RUTA: Generar PDF con valores editados
@main.route('/generar-pdf-calculadora', methods=['POST'])
def generar_pdf_calculadora():
    """Genera PDF con valores editados manualmente desde la calculadora"""
    datos = request.form.to_dict()
    
    if not datos.get('id_ups'):
        return "Error: ID de UPS no proporcionado.", 400
    
    ups_data = db.obtener_ups_id(datos['id_ups'])
    if not ups_data:
        return "Error: UPS no encontrado.", 404
    
    # Determinar si es preview o publicar
    accion = datos.get('accion', 'preview')
    es_publicar = (accion == 'publicar')
    pedido = datos.get('pedido', 'temporal')
    
    # Construir resultado desde valores editados del formulario
    resultado = {
        'pedido': pedido,
        'cliente_nom': datos.get('cliente_texto', ''),
        'sucursal_nom': datos.get('sucursal_texto', ''),
        'modelo_nombre': datos.get('modelo_nombre', ''),
        'kva': datos.get('kva', ''),
        'voltaje': datos.get('voltaje', ''),
        'i_diseno': datos.get('i_diseno', ''),
        'dv_pct': datos.get('dv_pct', ''),
        'fase_sel': datos.get('fase_sel', ''),
        'breaker_sel': datos.get('breaker_sel', ''),
        'bat_series': datos.get('bat_series', ''),
        'bat_strings': datos.get('bat_strings', ''),
        'bat_total': datos.get('bat_total', ''),
        'bateria_modelo': datos.get('bateria_modelo', ''),
        'tiempo_respaldo': datos.get('tiempo_respaldo', ''),
        'bat_justificacion': datos.get('bat_justificacion', ''),
        'dim_largo': datos.get('dim_largo', ''),
        'dim_ancho': datos.get('dim_ancho', ''),
        'dim_alto': datos.get('dim_alto', ''),
        'peso': datos.get('peso', ''),
        'es_publicado': es_publicar
    }
    
    # Manejo de imágenes
    imagenes_temp = {}
    
    if es_publicar:
        # Guardar imágenes permanentemente
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
        # Guardar imágenes temporalmente
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
    
    # Obtener tipo de ventilación
    tipo_ventilacion_data = None
    if ups_data.get('tipo_ventilacion_id'):
        tipo_ventilacion_data = db.obtener_tipo_ventilacion_id(ups_data['tipo_ventilacion_id'])
    
    resultado['tipo_ventilacion'] = tipo_ventilacion_data.get('nombre') if tipo_ventilacion_data else None
    resultado['tipo_ventilacion_data'] = tipo_ventilacion_data
    
    # Obtener info de batería
    bateria_info = {}
    id_bateria = datos.get('id_bateria')
    if id_bateria:
        bateria_info = db.obtener_bateria_id(id_bateria) or {}
    
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
        else:
           es_publicar = False
    
    # Generar PDF
    pdf = ReportePDF()
    pdf_bytes = pdf.generar_cuerpo(datos, resultado, ups=ups_data, bateria=bateria_info, es_publicado=es_publicar, imagenes_temp=imagenes_temp)
    
    # Si es publicación, guardar permanentemente
    if es_publicar:
        pdf_url = guardar_pdf_proyecto(bytes(pdf_bytes), pedido, tipo='guia')
        db.actualizar_pdf_guia(pedido, pdf_url)
    
    # Devolver PDF para descarga
    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    nombre_seguro = str(pedido).replace(" ", "_")
    prefijo = "Guia" if es_publicar else "Preview"
    response.headers['Content-Disposition'] = f'attachment; filename={prefijo}_Instalacion_{nombre_seguro}.pdf'
    return response
