import logging
import os
from flask import render_template, request, make_response, current_app
from flask_login import login_required, current_user
from app.reporte import ReportePDF
from app.permisos import permiso_requerido
from app.auxiliares import (
    normalizar_imagen,
    guardar_pdf_proyecto,
    guardar_imagen_proyecto
)
from . import guia_rapida_bp

logger = logging.getLogger(__name__)


def _to_float(val, default=0.0):
    """Convierte un valor a float de forma segura."""
    try:
        return float(val) if val and str(val).strip() else default
    except (ValueError, TypeError):
        return default


@guia_rapida_bp.route('/guia-rapida')
@login_required
@permiso_requerido('guia_rapida')
def guia_rapida():
    """Renderiza el formulario de Guía Rápida con datos de BD para autocomplete."""
    db = current_app.db
    return render_template('guia_rapida.html',
        clientes=db.obtener_clientes_unicos(),
        ups=db.obtener_ups_todos(),
        baterias=db.obtener_baterias_modelos(),
        tipos_ventilacion=db.obtener_tipos_ventilacion()
    )


@guia_rapida_bp.route('/generar-pdf-guia-rapida', methods=['POST'])
@login_required
@permiso_requerido('guia_rapida')
def generar_pdf_guia_rapida():
    """Genera PDF de instalación desde datos manuales del formulario Guía Rápida."""
    db = current_app.db
    datos = request.form.to_dict()

    if not datos.get('id_ups'):
        return "Error: Debe seleccionar un modelo de UPS.", 400

    ups_data = db.obtener_ups_id(datos['id_ups'])
    if not ups_data:
        return "Error: UPS no encontrado en la base de datos.", 404

    accion = datos.get('accion', 'preview')
    es_publicar = (accion == 'publicar')
    pedido = datos.get('pedido', 'temporal')

    # Construir resultado manualmente desde el formulario (sin cálculos)
    resultado = {
        'pedido': pedido,
        'cliente_nom': datos.get('cliente_texto', ''),
        'sucursal_nom': datos.get('sucursal_texto', ''),
        'modelo_nombre': datos.get('modelo_nombre', ''),
        'kva': datos.get('kva', ''),
        'voltaje': datos.get('voltaje', ''),
        'fases': datos.get('fases', ''),
        'longitud': datos.get('longitud', ''),
        'i_nom': _to_float(datos.get('i_nom')),
        'i_diseno': _to_float(datos.get('i_diseno')),
        'dv_pct': _to_float(datos.get('dv_pct')),
        'fase_sel': datos.get('fase_sel', ''),
        'breaker_sel': _to_float(datos.get('breaker_sel')),
        'gnd_sel': datos.get('gnd_sel', 'S/D'),
        'i_real_cable': _to_float(datos.get('i_real_cable')),
        'nota_altitud': datos.get('nota_altitud', ''),
        'baterias_total': _to_float(datos.get('baterias_total')),
        'baterias_por_string': _to_float(datos.get('baterias_por_string')),
        'numero_strings': _to_float(datos.get('numero_strings')),
        'autonomia_calculada_min': _to_float(datos.get('autonomia_calculada_min')),
        'autonomia_deseada_min': _to_float(datos.get('autonomia_deseada_min')),
        'bateria_modelo': datos.get('bateria_modelo', ''),
        'tiempo_respaldo': datos.get('tiempo_respaldo', ''),
        'dim_largo': datos.get('dim_largo', ''),
        'dim_ancho': datos.get('dim_ancho', ''),
        'dim_alto': datos.get('dim_alto', ''),
        'peso': datos.get('peso', ''),
        'es_publicado': es_publicar
    }

    # Manejo de imágenes con normalización
    imagenes_temp = {}
    base_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    image_fields = [
        ('imagen_portada', 'portada'),
        ('imagen_unifilar_ac', 'unifilar_ac'),
        ('imagen_baterias_dc', 'baterias_dc'),
        ('imagen_layout_equipos', 'layout_equipos')
    ]

    if es_publicar:
        for field_name, key in image_fields:
            if field_name in request.files:
                file = request.files[field_name]
                if file and file.filename:
                    nombre = guardar_imagen_proyecto(file, pedido)
                    if nombre:
                        imagenes_temp[key] = os.path.join(
                            base_app_dir, 'static', 'img', 'proyectos', pedido, nombre
                        )
    else:
        for field_name, key in image_fields:
            if field_name in request.files:
                file = request.files[field_name]
                if file and file.filename:
                    ruta_normalizada = normalizar_imagen(file)
                    if ruta_normalizada:
                        imagenes_temp[key] = ruta_normalizada

    # Obtener tipo de ventilación desde el UPS
    tipo_ventilacion_data = None
    if ups_data.get('tipo_ventilacion_id'):
        tipo_ventilacion_data = db.obtener_tipo_ventilacion_id(ups_data['tipo_ventilacion_id'])

    resultado['tipo_ventilacion'] = tipo_ventilacion_data.get('nombre') if tipo_ventilacion_data else None
    resultado['tipo_ventilacion_data'] = tipo_ventilacion_data

    # Obtener datos de batería si se seleccionó
    bateria_info = {}
    id_bateria = datos.get('id_bateria')
    if id_bateria:
        bateria_info = db.obtener_bateria_id(id_bateria) or {}

    # Publicar proyecto si corresponde
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

    # Generar PDF usando el mismo ReportePDF
    pdf = ReportePDF()
    pdf_bytes = pdf.generar_cuerpo(
        datos, resultado,
        ups=ups_data,
        bateria=bateria_info,
        es_publicado=es_publicar,
        imagenes_temp=imagenes_temp
    )

    # Guardar PDF permanente si es publicación
    if es_publicar:
        pdf_url = guardar_pdf_proyecto(bytes(pdf_bytes), pedido, tipo='guia')
        db.actualizar_pdf_guia(pedido, pdf_url)

    # Retornar PDF como descarga
    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    nombre_seguro = str(pedido).replace(" ", "_")
    prefijo = "Guia" if es_publicar else "Preview"
    response.headers['Content-Disposition'] = f'attachment; filename={prefijo}_Instalacion_{nombre_seguro}.pdf'
    return response


@guia_rapida_bp.route('/generar-ejemplo-pdf')
@login_required
@permiso_requerido('guia_rapida')
def generar_ejemplo_pdf():
    """Genera un PDF de ejemplo con datos ficticios."""

    db = current_app.db

    datos_ejemplo = {
        'pedido': 'EJEMPLO-001',
        'cliente_texto': 'CLIENTE EJEMPLO S.A. DE C.V.',
        'sucursal_texto': 'SUCURSAL DEMO - CDMX',
        'modelo_nombre': 'Dragon Power Plus 60',
        'kva': '60',
        'voltaje': '220',
        'fases': '3',
        'longitud': '15',
    }

    resultado_ejemplo = {
        'pedido': 'EJEMPLO-001',
        'cliente_nom': 'CLIENTE EJEMPLO S.A. DE C.V.',
        'sucursal_nom': 'SUCURSAL DEMO - CDMX',
        'modelo_nombre': 'Dragon Power Plus 60',
        'kva': '60',
        'voltaje': '220',
        'fases': '3',
        'longitud': '15',
        'i_nom': 157.5,
        'i_diseno': 196.9,
        'dv_pct': 1.85,
        'fase_sel': '1/0',
        'breaker_sel': 200.0,
        'gnd_sel': '6',
        'i_real_cable': 230.0,
        'nota_altitud': '',
        'baterias_total': 40.0,
        'baterias_por_string': 20.0,
        'numero_strings': 2.0,
        'autonomia_calculada_min': 12.5,
        'autonomia_deseada_min': 10.0,
        'bateria_modelo': 'LBS12-100 (100Ah)',
        'tiempo_respaldo': '10',
        'dim_largo': '442',
        'dim_ancho': '659',
        'dim_alto': '174',
        'peso': '180',
        'es_publicado': False,
        'tipo_ventilacion': None,
        'tipo_ventilacion_data': None,
    }

    # Intentar obtener un UPS real de la BD para la portada
    ups_data = None
    try:
        todos_ups = db.obtener_ups_todos()
        if todos_ups:
            ups_data = db.obtener_ups_id(todos_ups[0].get('id') or todos_ups[0].get('Id'))
    except Exception:
        pass

    bateria_ejemplo = {
        'modelo': 'LBS12-100',
        'fabricante': 'LBS Energy',
        'voltaje_nominal': 12,
        'capacidad_ah': 100,
    }

    pdf = ReportePDF()
    pdf_bytes = pdf.generar_cuerpo(
        datos_ejemplo, resultado_ejemplo,
        ups=ups_data,
        bateria=bateria_ejemplo,
        es_publicado=False,
        imagenes_temp={}
    )

    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=Ejemplo_Guia_Instalacion.pdf'
    return response
