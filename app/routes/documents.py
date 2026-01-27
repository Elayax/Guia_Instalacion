from flask import Blueprint, render_template, request, make_response, send_file
from app.checklist import ChecklistPDF
from app.base_datos import GestorDB
from app.auxiliares import guardar_pdf_proyecto
import os
from . import documents_bp

db = GestorDB()

@documents_bp.route('/reimprimir-guia/<pedido>')
def reimprimir_guia(pedido):
    """Reimprime la guía de instalación de un pedido ya publicado"""
    proyecto = db.obtener_proyecto_por_pedido(pedido)

    if not proyecto:
        return "Pedido no encontrado", 404

    if not proyecto.get('pdf_guia_url'):
        return "No hay guía generada para este pedido", 404

    # Verificar que el archivo existe
    # Ruta base: subir desde app/routes
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(base_dir, 'static', proyecto['pdf_guia_url'])

    if not os.path.exists(pdf_path):
        return "El archivo PDF no se encuentra disponible", 404

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'Guia_Instalacion_{pedido}.pdf',
        mimetype='application/pdf'
    )

@documents_bp.route('/generar-checklist/<pedido>', methods=['GET', 'POST'])
def generar_checklist(pedido):
    """Genera el checklist para un pedido"""
    proyecto = db.obtener_proyecto_por_pedido(pedido)

    if not proyecto:
        return "Pedido no encontrado", 404

    if request.method == 'GET':
        # Mostrar formulario con datos para generar checklist
        return render_template('generar_checklist.html', proyecto=proyecto, pedido=pedido)

    # POST: Generar el checklist
    datos_checklist = {
        'pedido': pedido,
        'cliente_nombre': proyecto.get('cliente_snap', ''),
        'sucursal_nombre': proyecto.get('sucursal_snap', ''),
        'modelo_ups': proyecto.get('modelo_snap', ''),
        'capacidad': f"{proyecto.get('potencia_snap', '')} kVA" if proyecto.get('potencia_snap') else '',
        'area_frente': request.form.get('area_frente', ''),
        'nombre_jefe': request.form.get('nombre_jefe', ''),
        'observaciones_conexion': request.form.get('observaciones_conexion', ''),
        'comentarios': request.form.get('comentarios', ''),
        'direccion_instalacion': request.form.get('direccion_instalacion', ''),
        'nombre_contacto': request.form.get('nombre_contacto', ''),
        'telefono_contacto': request.form.get('telefono_contacto', ''),
        'email_contacto': request.form.get('email_contacto', '')
    }

    # Generar el checklist PDF
    checklist_pdf = ChecklistPDF()
    pdf_bytes = checklist_pdf.generar_checklist(datos_checklist)

    # Guardar permanentemente
    pdf_url = guardar_pdf_proyecto(bytes(pdf_bytes), pedido, tipo='checklist')
    db.actualizar_pdf_checklist(pedido, pdf_url)

    # Devolver el PDF para descarga
    response = make_response(bytes(pdf_bytes))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Checklist_{pedido}.pdf'
    return response

@documents_bp.route('/reimprimir-checklist/<pedido>')
def reimprimir_checklist(pedido):
    """Reimprime el checklist de un pedido ya publicado"""
    proyecto = db.obtener_proyecto_por_pedido(pedido)

    if not proyecto:
        return "Pedido no encontrado", 404

    if not proyecto.get('pdf_checklist_url'):
        return "No hay checklist generado para este pedido", 404

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(base_dir, 'static', proyecto['pdf_checklist_url'])

    if not os.path.exists(pdf_path):
        return "El archivo PDF no se encuentra disponible", 404

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'Checklist_{pedido}.pdf',
        mimetype='application/pdf'
    )
