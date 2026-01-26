from flask import Blueprint, render_template, request, redirect, url_for
from app.base_datos import GestorDB
import os
from . import dashboard_bp

db = GestorDB()

@dashboard_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    pedido_data = None
    estado_pedido = None
    pedido_buscado = None
    clientes = db.obtener_clientes_unicos()

    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'buscar_pedido':
            # Buscar pedido específico
            pedido_num = request.form.get('pedido_buscar', '').strip()
            pedido_buscado = pedido_num

            if pedido_num:
                # Buscar en base de datos
                pedido_data = db.obtener_proyecto_por_pedido(pedido_num)

                if pedido_data:
                    # Determinar el estado del pedido
                    estado_pedido = {
                        'tiene_ups': False,
                        'tiene_calculos': False,
                        'tiene_aviso': False,
                        'modelo_ups': None
                    }

                    # Verificar si tiene UPS asignado (modelo_snap guardado)
                    if pedido_data.get('modelo_snap'):
                        estado_pedido['tiene_ups'] = True
                        estado_pedido['modelo_ups'] = pedido_data['modelo_snap']

                    # Verificar si tiene cálculos publicados
                    if pedido_data.get('fecha_publicacion'):
                        estado_pedido['tiene_calculos'] = True

                    # Verificar si tiene checklist/aviso generado
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # subir un nivel desde app/routes
                    temp_dir = os.path.join(base_dir, 'static', 'temp')
                    if os.path.exists(temp_dir):
                        checklist_files = [f for f in os.listdir(temp_dir)
                                         if f.endswith('.pdf') and 'Checklist' in f and pedido_num in f]
                        if checklist_files:
                            estado_pedido['tiene_aviso'] = True
        
        elif accion == 'crear_proyecto':
            # Crear nuevo proyecto
            pedido = request.form.get('pedido')
            cliente_nombre = request.form.get('cliente_nombre')
            sucursal_nombre = request.form.get('sucursal_nombre')
            
            # Nuevos campos del dashboard
            potencia_kva = request.form.get('potencia_kva')
            voltaje_entrada = request.form.get('voltaje_entrada')
            voltaje_salida = request.form.get('voltaje_salida')

            # Insertar proyecto en BD
            try:
                # Nota: GestorDB maneja su propia conexión, pero aquí necesitamos raw cursor o un método específico.
                # db._conectar() es interno. Deberíamos mover esto a un método de db o usarlo así.
                # Para limpieza, usaremos db._conectar() aquí igual que antes.
                conn = db._conectar()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO proyectos_publicados (pedido, cliente_snap, sucursal_snap, potencia_kva, voltaje_entrada, voltaje_salida)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (pedido, cliente_nombre, sucursal_nombre, potencia_kva, voltaje_entrada, voltaje_salida))
                conn.commit()
                conn.close()

                # Redirigir a calculadora
                # IMPORTANTE: url_for necesita el nombre del blueprint. 'calculator.calculadora'
                return redirect(url_for('calculator.calculadora') + f'?pedido={pedido}')
            except Exception as e:
                print(f"Error al crear proyecto: {e}")
                return redirect(url_for('dashboard.dashboard'))

    return render_template('dashboard.html',
                         pedido=pedido_data,
                         estado=estado_pedido,
                         pedido_buscado=pedido_buscado,
                         clientes=clientes)
