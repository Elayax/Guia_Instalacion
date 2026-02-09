import logging
import os
from flask import render_template, request, redirect, url_for, current_app
from flask_login import login_required
from . import dashboard_bp

logger = logging.getLogger(__name__)


@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    db = current_app.db
    pedido_data = None
    estado_pedido = None
    pedido_buscado = None
    clientes = db.obtener_clientes_unicos()

    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'buscar_pedido':
            pedido_num = request.form.get('pedido_buscar', '').strip()
            pedido_buscado = pedido_num

            if pedido_num:
                pedido_data = db.obtener_proyecto_por_pedido(pedido_num)

                if pedido_data:
                    estado_pedido = {
                        'tiene_ups': False,
                        'tiene_calculos': False,
                        'tiene_aviso': False,
                        'modelo_ups': None
                    }

                    if pedido_data.get('modelo_snap'):
                        estado_pedido['tiene_ups'] = True
                        estado_pedido['modelo_ups'] = pedido_data['modelo_snap']

                    if pedido_data.get('fecha_publicacion'):
                        estado_pedido['tiene_calculos'] = True

                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    temp_dir = os.path.join(base_dir, 'static', 'temp')
                    if os.path.exists(temp_dir):
                        checklist_files = [f for f in os.listdir(temp_dir)
                                         if f.endswith('.pdf') and 'Checklist' in f and pedido_num in f]
                        if checklist_files:
                            estado_pedido['tiene_aviso'] = True

        elif accion == 'crear_proyecto':
            pedido = request.form.get('pedido')
            cliente_nombre = request.form.get('cliente_nombre')
            sucursal_nombre = request.form.get('sucursal_nombre')
            potencia_kva = request.form.get('potencia_kva')
            voltaje_entrada = request.form.get('voltaje_entrada')
            voltaje_salida = request.form.get('voltaje_salida')

            try:
                datos_guardar = {
                    'cliente_snap': cliente_nombre,
                    'sucursal_snap': sucursal_nombre,
                    'potencia_snap': potencia_kva,
                    'voltaje_entrada': voltaje_entrada,
                    'voltaje_salida': voltaje_salida,
                }
                # Filtrar None values
                datos_guardar = {k: v for k, v in datos_guardar.items() if v is not None}

                if db.guardar_calculo(pedido, datos_guardar):
                    return redirect(url_for('calculator.calculadora') + f'?pedido={pedido}')
                else:
                    logger.error("Error al crear proyecto %s", pedido)
            except Exception as e:
                logger.error("Error al crear proyecto: %s", e)
                return redirect(url_for('dashboard.dashboard'))

    return render_template('dashboard.html',
                         pedido=pedido_data,
                         estado=estado_pedido,
                         pedido_buscado=pedido_buscado,
                         clientes=clientes)
