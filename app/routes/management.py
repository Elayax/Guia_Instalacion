import logging
from flask import render_template, request, redirect, url_for, make_response, current_app
from flask_login import login_required
from app.auxiliares import procesar_post_gestion, obtener_datos_plantilla
from . import management_bp

logger = logging.getLogger(__name__)


@management_bp.route('/equipos')
@login_required
def equipos():
    return redirect(url_for('management.gestion', tab='ups'))


@management_bp.route('/baterias')
@login_required
def baterias():
    return redirect(url_for('management.gestion', tab='baterias'))


@management_bp.route('/gestion', methods=['GET', 'POST'])
@login_required
def gestion():
    db = current_app.db
    state = {
        'active_tab': request.args.get('tab', 'ups'),
        'ups_seleccionado': None,
        'bateria_seleccionada': None,
        'agregando_ups': False,
        'agregando_bateria': False,
        'agregando_personal': False,
        'personal_seleccionado': None,
        'unidad_curva': 'W',
        'mensaje': None,
        'error_logs': None,
        'pivot_data': None,
        'tipo_vent_seleccionado': None,
    }

    if request.method == 'POST':
        procesar_post_gestion(db, request, state)

    return render_template('gestion.html',
        ups=db.obtener_ups_todos(),
        clientes=db.obtener_clientes(),
        baterias=db.obtener_baterias_modelos(),
        personal=db.obtener_personal(),
        proyectos=db.obtener_proyectos(),
        tipos_ventilacion=db.obtener_tipos_ventilacion(),
        **state)


@management_bp.route('/carga-masiva')
@login_required
def carga_masiva():
    return render_template('carga_masiva.html')


@management_bp.route('/descargar-plantilla/<tipo>')
@login_required
def descargar_plantilla(tipo):
    headers, rows = obtener_datos_plantilla(tipo)
    if not headers:
        return "Tipo de plantilla no reconocido", 404

    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=plantilla_{tipo}.csv'
    return response


@management_bp.route('/exportar-tabla/<tabla>')
@login_required
def exportar_tabla(tabla):
    db = current_app.db
    headers, rows = db.obtener_datos_tabla(tabla)
    if not headers:
        return "Tabla no encontrada", 404

    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={tabla}.csv'
    return response


@management_bp.route('/recuperacion-proyectos', methods=['GET', 'POST'])
@login_required
def recuperacion_proyectos():
    db = current_app.db
    mensaje = None
    errores = None
    proyectos_incompletos = db.obtener_proyectos_incompletos()

    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'completar':
            pedido = request.form.get('pedido')
            datos = {
                'id_ups': request.form.get('id_ups') or None,
                'voltaje': request.form.get('voltaje') or None,
                'fases': request.form.get('fases') or None,
                'longitud': request.form.get('longitud') or None,
                'tiempo_respaldo': request.form.get('tiempo_respaldo') or None,
                'id_bateria': request.form.get('id_bateria') or None,
            }
            exito, errores = db.completar_datos_proyecto(pedido, datos)
            if exito:
                mensaje = f"Proyecto {pedido} actualizado correctamente"
            else:
                mensaje = f"Error actualizando proyecto {pedido}"
            proyectos_incompletos = db.obtener_proyectos_incompletos()

        elif accion == 'eliminar':
            pedido = request.form.get('pedido')
            if db.eliminar_proyecto(pedido):
                mensaje = f"Proyecto {pedido} eliminado correctamente"
            else:
                mensaje = f"Error eliminando proyecto {pedido}"
            proyectos_incompletos = db.obtener_proyectos_incompletos()

    return render_template('recuperacion_proyectos.html',
        proyectos=proyectos_incompletos,
        ups_list=db.obtener_ups_todos(),
        baterias_list=db.obtener_baterias_modelos(),
        mensaje=mensaje,
        errores=errores)
