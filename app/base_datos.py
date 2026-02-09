import os
import csv
import logging
from datetime import datetime
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class GestorDB:
    """Capa de acceso a datos para PostgreSQL con pool de conexiones thread-safe."""

    def __init__(self, pool=None):
        if pool is None:
            from app.db_connection import ConnectionPool
            self.pool = ConnectionPool.get_instance()
        else:
            self.pool = pool

    # =========================================================================
    # UTILIDADES INTERNAS
    # =========================================================================
    def _get_columnas_validas(self, cursor, tabla):
        """Obtiene las columnas válidas de una tabla desde information_schema."""
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name != 'id'",
            (tabla,)
        )
        return {row['column_name'] for row in cursor.fetchall()}

    def _filtrar_datos(self, cursor, tabla, datos_dict):
        """Filtra un diccionario para incluir solo columnas válidas de la tabla."""
        columnas_validas = self._get_columnas_validas(cursor, tabla)
        return {k: v for k, v in datos_dict.items() if k in columnas_validas}

    # =========================================================================
    # IMPORTACIÓN CSV
    # =========================================================================
    def cargar_clientes_desde_csv(self, ruta_csv):
        """Lee CSV y carga datos en la tabla clientes."""
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        filas_insertadas = 0
        errores = 0
        logs = []

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                    lector = csv.reader(f)
                    for fila in lector:
                        if len(fila) < 5:
                            logs.append(f"Fila ignorada (columnas insuficientes): {fila}")
                            continue
                        try:
                            cliente = fila[0].strip()
                            sucursal = fila[1].strip()
                            direccion = fila[2].strip()
                            cursor.execute(
                                "INSERT INTO clientes (cliente, sucursal, direccion) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                                (cliente, sucursal, direccion)
                            )
                            filas_insertadas += 1
                        except Exception as e:
                            logs.append(f"Error en fila {fila}: {e}")
                            errores += 1
            return {'status': 'ok', 'insertados': filas_insertadas, 'errores': errores, 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}

    def _importar_csv_simple(self, ruta_csv, tabla):
        """Método genérico para importar CSV a una tabla plana."""
        TABLAS_PERMITIDAS = {'ups_specs', 'baterias_modelos'}
        if tabla not in TABLAS_PERMITIDAS:
            return {'status': 'error', 'msg': f'Tabla no permitida: {tabla}', 'logs': []}

        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        filas_insertadas = 0
        errores = 0
        logs = []

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                columnas_validas = self._get_columnas_validas(cursor, tabla)

                with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                    lector = csv.DictReader(f)
                    for i, fila in enumerate(lector, start=1):
                        try:
                            datos_limpios = {}
                            for k, v in fila.items():
                                if k and v and v.strip() and v.strip() != 'S/D':
                                    key_clean = k.strip().replace(' ', '_')
                                    if key_clean in columnas_validas:
                                        datos_limpios[key_clean] = v.strip()

                            if not datos_limpios:
                                continue

                            columnas = ', '.join(f'"{k}"' for k in datos_limpios.keys())
                            placeholders = ', '.join(['%s'] * len(datos_limpios))
                            valores = list(datos_limpios.values())

                            cursor.execute(
                                f'INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})',
                                valores
                            )
                            filas_insertadas += 1
                        except Exception as e:
                            errores += 1
                            logs.append(f"Fila {i} Error: {str(e)}")

            return {'status': 'ok', 'insertados': filas_insertadas, 'errores': errores, 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}

    def cargar_ups_desde_csv(self, ruta_csv):
        return self._importar_csv_simple(ruta_csv, 'ups_specs')

    def cargar_baterias_modelos_desde_csv(self, ruta_csv):
        return self._importar_csv_simple(ruta_csv, 'baterias_modelos')

    # =========================================================================
    # GESTIÓN DE UPS
    # =========================================================================
    def obtener_ups_todos(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM ups_specs ORDER BY "Capacidad_kVA"')
            return [dict(row) for row in cursor.fetchall()]

    def obtener_ups_id(self, id_ups):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM ups_specs WHERE id = %s", (id_ups,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def insertar_ups_manual(self, datos_dict):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                datos_limpios = self._filtrar_datos(cursor, 'ups_specs', datos_dict)
                if not datos_limpios:
                    return False

                columnas = ', '.join(f'"{k}"' for k in datos_limpios.keys())
                placeholders = ', '.join(['%s'] * len(datos_limpios))
                valores = list(datos_limpios.values())

                cursor.execute(
                    f'INSERT INTO ups_specs ({columnas}) VALUES ({placeholders})',
                    valores
                )
                return True
        except Exception as e:
            logger.error("Error insertando UPS: %s", e)
            return False

    def actualizar_ups(self, id_ups, datos):
        """Actualiza un registro existente en ups_specs."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                datos_limpios = self._filtrar_datos(cursor, 'ups_specs', datos)
                if not datos_limpios:
                    return False

                set_clause = ', '.join(f'"{k}" = %s' for k in datos_limpios.keys())
                valores = list(datos_limpios.values())
                valores.append(id_ups)

                cursor.execute(
                    f'UPDATE ups_specs SET {set_clause} WHERE id = %s',
                    valores
                )
                return True
        except Exception as e:
            logger.error("Error actualizando UPS: %s", e)
            return False

    def eliminar_ups(self, id_ups):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ups_specs WHERE id = %s", (id_ups,))

    def verificar_modelo_ups_existe(self, nombre_modelo, excluir_id=None):
        """Verifica si existe un UPS con el nombre de modelo dado."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            if excluir_id:
                cursor.execute(
                    'SELECT id FROM ups_specs WHERE "Nombre_del_Producto" = %s AND id != %s',
                    (nombre_modelo, excluir_id)
                )
            else:
                cursor.execute(
                    'SELECT id FROM ups_specs WHERE "Nombre_del_Producto" = %s',
                    (nombre_modelo,)
                )
            return cursor.fetchone() is not None

    # =========================================================================
    # GESTIÓN DE CLIENTES
    # =========================================================================
    def agregar_cliente(self, datos):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO clientes (cliente, sucursal, direccion) VALUES (%s, %s, %s)",
                    (datos['cliente'], datos['sucursal'], datos['direccion'])
                )
        except Exception as e:
            logger.error("Error agregando cliente: %s", e)

    def obtener_clientes(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM clientes ORDER BY cliente, sucursal")
            return [dict(row) for row in cursor.fetchall()]

    def eliminar_cliente(self, id_cliente):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))

    def obtener_clientes_unicos(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT cliente FROM clientes ORDER BY cliente")
            return [row[0] for row in cursor.fetchall()]

    def obtener_sucursales_por_cliente(self, nombre_cliente):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM clientes WHERE cliente = %s ORDER BY sucursal",
                (nombre_cliente,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # GESTIÓN DE PROYECTOS
    # =========================================================================
    def publicar_proyecto(self, datos_calculados, form_data):
        """Publica un proyecto completo con todas sus relaciones."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                id_ups = int(form_data.get('id_ups', 0)) or None
                id_bateria = int(form_data.get('id_bateria', 0)) if form_data.get('id_bateria') else None
                tiempo_respaldo = float(form_data.get('tiempo_respaldo', 0)) if form_data.get('tiempo_respaldo') else None

                cursor.execute('''
                    INSERT INTO proyectos_publicados
                    (pedido, fecha_publicacion,
                     id_ups, id_bateria,
                     modelo_snap, potencia_snap, cliente_snap, sucursal_snap,
                     voltaje, fases, longitud, tiempo_respaldo,
                     calibre_fases, config_salida, calibre_tierra)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (pedido) DO UPDATE SET
                        fecha_publicacion = EXCLUDED.fecha_publicacion,
                        id_ups = EXCLUDED.id_ups,
                        id_bateria = EXCLUDED.id_bateria,
                        modelo_snap = EXCLUDED.modelo_snap,
                        potencia_snap = EXCLUDED.potencia_snap,
                        voltaje = EXCLUDED.voltaje,
                        fases = EXCLUDED.fases,
                        longitud = EXCLUDED.longitud,
                        tiempo_respaldo = EXCLUDED.tiempo_respaldo,
                        calibre_fases = EXCLUDED.calibre_fases,
                        config_salida = EXCLUDED.config_salida,
                        calibre_tierra = EXCLUDED.calibre_tierra
                ''', (
                    form_data['pedido'],
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    id_ups,
                    id_bateria,
                    datos_calculados.get('Nombre_del_Producto', 'Desconocido'),
                    datos_calculados.get('Capacidad_kVA', 0),
                    form_data.get('cliente_nombre', ''),
                    form_data.get('sucursal_nombre', ''),
                    float(form_data.get('voltaje', 0)),
                    int(form_data.get('fases', 3)),
                    float(form_data.get('longitud', 0)),
                    tiempo_respaldo,
                    datos_calculados.get('fase_sel', ''),
                    f"{form_data['fases']}F + N + GND",
                    datos_calculados.get('gnd_sel', '')
                ))
                return True
        except Exception as e:
            logger.error("Error publicando proyecto: %s", e)
            return False

    def eliminar_proyecto(self, pedido):
        """Elimina un proyecto publicado por su número de pedido."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM proyectos_publicados WHERE pedido = %s", (pedido,))
                return True
        except Exception as e:
            logger.error("Error al eliminar proyecto %s: %s", pedido, e)
            return False

    def obtener_proyectos(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM proyectos_publicados ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def obtener_proyecto_por_pedido(self, pedido):
        """Obtiene un proyecto completo con todas sus relaciones."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT
                    p.*,
                    p.id_ups as modelo_id_real,
                    ups."Nombre_del_Producto" as ups_nombre,
                    ups."Capacidad_kVA" as ups_kva,
                    bat.modelo as bateria_modelo,
                    bat.capacidad_nominal_ah as bateria_ah
                FROM proyectos_publicados p
                LEFT JOIN ups_specs ups ON ups.id = p.id_ups
                LEFT JOIN baterias_modelos bat ON bat.id = p.id_bateria
                WHERE p.pedido = %s
            ''', (pedido,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def actualizar_pdf_guia(self, pedido, pdf_url):
        """Actualiza la ruta del PDF de guía para un pedido."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE proyectos_publicados SET pdf_guia_url = %s WHERE pedido = %s",
                    (pdf_url, pedido)
                )
                return True
        except Exception as e:
            logger.error("Error actualizando PDF guía: %s", e)
            return False

    def actualizar_pdf_checklist(self, pedido, pdf_url):
        """Actualiza la ruta del PDF de checklist para un pedido."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE proyectos_publicados SET pdf_checklist_url = %s WHERE pedido = %s",
                    (pdf_url, pedido)
                )
                return True
        except Exception as e:
            logger.error("Error actualizando PDF checklist: %s", e)
            return False

    # =========================================================================
    # GESTIÓN DE BATERÍAS
    # =========================================================================
    def agregar_modelo_bateria(self, datos_dict):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                campos_validos = [
                    'modelo', 'serie', 'voltaje_nominal', 'capacidad_nominal_ah',
                    'resistencia_interna_mohm', 'max_corriente_descarga_5s_a',
                    'largo_mm', 'ancho_mm', 'alto_contenedor_mm', 'alto_total_mm', 'peso_kg',
                    'tipo_terminal', 'material_contenedor',
                    'carga_flotacion_v_min', 'carga_flotacion_v_max', 'coef_temp_flotacion_mv_c',
                    'carga_ciclica_v_min', 'carga_ciclica_v_max', 'corriente_inicial_max_a',
                    'coef_temp_ciclica_mv_c',
                    'temp_descarga_min_c', 'temp_descarga_max_c', 'temp_carga_min_c', 'temp_carga_max_c',
                    'temp_almacenaje_min_c', 'temp_almacenaje_max_c', 'temp_nominal_c',
                    'capacidad_40c_pct', 'capacidad_25c_pct', 'capacidad_0c_pct',
                    'autodescarga_meses_max'
                ]
                datos_limpios = {k: datos_dict[k] for k in campos_validos if k in datos_dict}

                columnas = ', '.join(datos_limpios.keys())
                placeholders = ', '.join(['%s'] * len(datos_limpios))
                valores = list(datos_limpios.values())

                cursor.execute(
                    f"INSERT INTO baterias_modelos ({columnas}) VALUES ({placeholders})",
                    valores
                )
                return True
        except Exception as e:
            logger.error("Error agregando batería: %s", e)
            return False

    def buscar_bateria_optima(self, watts_requeridos_celda, tiempo_minutos, fv_inversor):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT m.modelo, m.capacidad_nominal_ah, m.voltaje_nominal,
                       c.valor as watts_celda, c.tiempo_minutos, c.voltaje_corte_fv, c.unidad
                FROM baterias_curvas_descarga c
                JOIN baterias_modelos m ON c.bateria_id = m.id
                WHERE c.tiempo_minutos >= %s
                  AND c.voltaje_corte_fv >= %s
                  AND c.valor >= %s
                  AND c.unidad = 'W'
                ORDER BY c.valor ASC
                LIMIT 10
            ''', (tiempo_minutos, fv_inversor, watts_requeridos_celda))
            return [dict(row) for row in cursor.fetchall()]

    def obtener_baterias_modelos(self, solo_con_curvas=False):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            if solo_con_curvas:
                cursor.execute("""
                    SELECT DISTINCT m.*
                    FROM baterias_modelos m
                    JOIN baterias_curvas_descarga c ON m.id = c.bateria_id
                    ORDER BY m.modelo
                """)
            else:
                cursor.execute("SELECT * FROM baterias_modelos ORDER BY modelo")
            return [dict(row) for row in cursor.fetchall()]

    def obtener_bateria_id(self, id_bateria):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM baterias_modelos WHERE id = %s", (id_bateria,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def actualizar_bateria(self, id_bateria, datos):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                datos_limpios = self._filtrar_datos(cursor, 'baterias_modelos', datos)
                if not datos_limpios:
                    return False

                set_clause = ', '.join(f'{k} = %s' for k in datos_limpios.keys())
                valores = list(datos_limpios.values())
                valores.append(id_bateria)

                cursor.execute(
                    f"UPDATE baterias_modelos SET {set_clause} WHERE id = %s",
                    valores
                )
                return True
        except Exception as e:
            logger.error("Error actualizando batería: %s", e)
            return False

    def eliminar_bateria(self, id_bateria):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM baterias_modelos WHERE id = %s", (id_bateria,))

    # =========================================================================
    # CURVAS DE DESCARGA
    # =========================================================================
    def obtener_curvas_por_bateria(self, id_bateria):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM baterias_curvas_descarga WHERE bateria_id = %s ORDER BY unidad, tiempo_minutos, voltaje_corte_fv",
                (id_bateria,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def obtener_curvas_pivot(self, bateria_id, unidad='W'):
        """Retorna curvas como matriz para visualización."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT tiempo_minutos, voltaje_corte_fv, valor FROM baterias_curvas_descarga WHERE bateria_id = %s AND unidad = %s ORDER BY tiempo_minutos, voltaje_corte_fv",
                (bateria_id, unidad)
            )
            rows = cursor.fetchall()

        if not rows:
            return None

        voltajes = sorted(list(set(r['voltaje_corte_fv'] for r in rows)))
        datos_por_tiempo = {}
        for r in rows:
            t = r['tiempo_minutos']
            if t not in datos_por_tiempo:
                datos_por_tiempo[t] = {'tiempo': t}
            datos_por_tiempo[t][str(r['voltaje_corte_fv'])] = r['valor']

        data_list = sorted(datos_por_tiempo.values(), key=lambda x: x['tiempo'])
        return {'headers': [str(v) for v in voltajes], 'data': data_list}

    def cargar_curvas_por_id_csv(self, bateria_id, ruta_csv):
        """Carga curvas para una batería específica, limpiando las anteriores."""
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        insertados = 0
        logs = []
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM baterias_curvas_descarga WHERE bateria_id = %s", (bateria_id,))

                with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                    lector = csv.DictReader(f)
                    if not lector.fieldnames:
                        conn.rollback()
                        return {'status': 'error', 'msg': 'El archivo CSV está vacío o no tiene cabecera.', 'logs': []}

                    cols_fv = [c for c in lector.fieldnames if c and c.upper().strip().startswith('FV_')]

                    if 'Tiempo_Min' not in lector.fieldnames:
                        logs.append("La cabecera del CSV debe contener la columna 'Tiempo_Min'.")
                    if not cols_fv:
                        logs.append("El CSV debe contener al menos una columna de voltaje con formato 'FV_x.xx'.")

                    if logs:
                        conn.rollback()
                        return {'status': 'error', 'msg': 'Error de formato en la cabecera del CSV.', 'logs': logs}

                    for i, fila in enumerate(lector, start=2):
                        try:
                            tiempo_str = fila.get('Tiempo_Min', '0').strip()
                            tiempo = int(tiempo_str)
                            unidad = fila.get('Unidad', 'W').strip().upper()
                            if unidad not in ['W', 'A']:
                                unidad = 'W'
                            if tiempo <= 0:
                                logs.append(f"Fila {i}: 'Tiempo_Min' ({tiempo_str}) debe ser positivo.")
                                continue

                            for col in cols_fv:
                                try:
                                    v_corte = float(col.upper().strip().replace('FV_', ''))
                                    valor_str = fila.get(col, '').strip()
                                    if not valor_str:
                                        continue
                                    valor = float(valor_str)
                                    cursor.execute(
                                        "INSERT INTO baterias_curvas_descarga (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad) VALUES (%s, %s, %s, %s, %s)",
                                        (bateria_id, tiempo, v_corte, valor, unidad)
                                    )
                                    insertados += 1
                                except (ValueError, TypeError):
                                    logs.append(f"Fila {i}, Columna {col}: Valor '{fila.get(col, '')}' no es numérico.")
                        except (ValueError, TypeError):
                            logs.append(f"Fila {i}: 'Tiempo_Min' no es un entero válido.")

                if insertados > 0:
                    return {'status': 'ok', 'insertados': insertados, 'logs': logs}
                else:
                    conn.rollback()
                    if not logs:
                        logs.append("El archivo CSV no contenía filas válidas.")
                    return {'status': 'error', 'msg': 'No se insertaron datos.', 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}

    def cargar_curvas_baterias_masiva(self, ruta_csv):
        """Carga curvas para múltiples baterías desde un CSV."""
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo CSV no encontrado', 'logs': []}

        insertados = 0
        errores = 0
        logs = []
        modelos_a_limpiar = set()

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # PRIMERA PASADA: Validación
                with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                    lector_validacion = csv.DictReader(f)
                    if not lector_validacion.fieldnames:
                        return {'status': 'error', 'msg': 'CSV vacío o sin cabecera.', 'logs': []}

                    headers = [h.strip() for h in lector_validacion.fieldnames if h]
                    if 'Modelo' not in headers:
                        logs.append("La cabecera debe contener 'Modelo'.")
                    if 'Tiempo_Min' not in headers:
                        logs.append("La cabecera debe contener 'Tiempo_Min'.")
                    cols_fv = [h for h in headers if h.upper().startswith('FV_')]
                    if not cols_fv:
                        logs.append("Debe haber al menos una columna 'FV_x.xx'.")

                    if logs:
                        return {'status': 'error', 'msg': 'Error de formato.', 'logs': logs, 'insertados': 0, 'errores': 1}

                    for i, fila in enumerate(lector_validacion, start=2):
                        modelo = fila.get('Modelo', '').strip()
                        if not modelo:
                            logs.append(f"Fila {i}: Falta el 'Modelo'.")
                            errores += 1
                            continue
                        cursor.execute("SELECT id FROM baterias_modelos WHERE modelo = %s", (modelo,))
                        row_bat = cursor.fetchone()
                        if not row_bat:
                            logs.append(f"Fila {i}: Modelo '{modelo}' no existe.")
                            errores += 1
                            continue
                        modelos_a_limpiar.add(row_bat['id'])

                if errores > 0:
                    return {'status': 'error', 'msg': 'Errores de validación.', 'logs': logs, 'insertados': 0, 'errores': errores}

                # LIMPIEZA
                if modelos_a_limpiar:
                    placeholders = ','.join('%s' for _ in modelos_a_limpiar)
                    cursor.execute(
                        f"DELETE FROM baterias_curvas_descarga WHERE bateria_id IN ({placeholders})",
                        list(modelos_a_limpiar)
                    )

                # SEGUNDA PASADA: Inserción
                with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                    lector = csv.DictReader(f)
                    cols_fv = [h.strip() for h in lector.fieldnames if h and h.strip().upper().startswith('FV_')]

                    for i, fila in enumerate(lector, start=2):
                        modelo = fila.get('Modelo', '').strip()
                        cursor.execute("SELECT id FROM baterias_modelos WHERE modelo = %s", (modelo,))
                        row_bat = cursor.fetchone()
                        if not row_bat:
                            continue
                        bateria_id = row_bat['id']

                        try:
                            unidad = fila.get('Unidad', 'W').strip().upper()
                            if unidad not in ['W', 'A']:
                                unidad = 'W'
                            tiempo = int(fila.get('Tiempo_Min', 0))
                            if tiempo <= 0:
                                logs.append(f"Fila {i}: 'Tiempo_Min' debe ser positivo.")
                                errores += 1
                                continue

                            for col in cols_fv:
                                try:
                                    voltaje_corte = float(col.upper().replace('FV_', ''))
                                    valor_str = fila.get(col, '').strip()
                                    if not valor_str:
                                        continue
                                    valor = float(valor_str)
                                    cursor.execute(
                                        "INSERT INTO baterias_curvas_descarga (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad) VALUES (%s, %s, %s, %s, %s)",
                                        (bateria_id, tiempo, voltaje_corte, valor, unidad)
                                    )
                                    insertados += 1
                                except (ValueError, TypeError):
                                    logs.append(f"Fila {i}, Columna {col}: Valor no numérico.")
                                    errores += 1
                        except (ValueError, TypeError):
                            logs.append(f"Fila {i}: 'Tiempo_Min' no es válido.")
                            errores += 1

            return {'status': 'ok', 'insertados': insertados, 'errores': errores, 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs, 'insertados': 0, 'errores': 1}

    def actualizar_curvas_desde_form(self, bateria_id, form_data):
        """Actualiza curvas desde formulario editable."""
        insertados = 0
        logs = []
        unidad = form_data.get('unidad_curva', 'W')

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM baterias_curvas_descarga WHERE bateria_id = %s AND unidad = %s",
                    (bateria_id, unidad)
                )

                puntos_a_insertar = []
                for key, valor_str in form_data.items():
                    if key.startswith('curva-'):
                        if not valor_str.strip():
                            continue
                        try:
                            parts = key.split('-')
                            tiempo = int(parts[1])
                            voltaje = float(parts[2])
                            valor = float(valor_str)
                            puntos_a_insertar.append((bateria_id, tiempo, voltaje, valor, unidad))
                        except (ValueError, IndexError):
                            logs.append(f"Dato inválido: {key}={valor_str}")

                if puntos_a_insertar:
                    from psycopg2.extras import execute_values
                    execute_values(
                        cursor,
                        "INSERT INTO baterias_curvas_descarga (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad) VALUES %s",
                        puntos_a_insertar
                    )
                    insertados = len(puntos_a_insertar)

            return {'status': 'ok', 'insertados': insertados, 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}

    # =========================================================================
    # GESTIÓN DE PERSONAL
    # =========================================================================
    def obtener_personal(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM personal ORDER BY nombre")
            return [dict(row) for row in cursor.fetchall()]

    def agregar_personal(self, nombre, puesto):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO personal (nombre, puesto) VALUES (%s, %s)", (nombre, puesto))
                return True
        except Exception as e:
            logger.error("Error agregando personal: %s", e)
            return False

    def actualizar_personal(self, id_personal, nombre, puesto):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE personal SET nombre = %s, puesto = %s WHERE id = %s", (nombre, puesto, id_personal))
                return True
        except Exception as e:
            logger.error("Error actualizando personal: %s", e)
            return False

    def eliminar_personal(self, id_personal):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM personal WHERE id = %s", (id_personal,))
                return True
        except Exception as e:
            logger.error("Error eliminando personal: %s", e)
            return False

    # =========================================================================
    # TIPOS DE VENTILACIÓN
    # =========================================================================
    def obtener_tipos_ventilacion(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM tipos_ventilacion ORDER BY nombre")
            return [dict(row) for row in cursor.fetchall()]

    def agregar_tipo_ventilacion(self, datos, imagen_url=None):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tipos_ventilacion (nombre, descripcion, imagen_url) VALUES (%s, %s, %s)",
                    (datos['nombre'], datos.get('descripcion', ''), imagen_url)
                )
                logger.info("Tipo de ventilación agregado: %s", datos['nombre'])
                return True
        except Exception as e:
            logger.error("Error agregando tipo de ventilación: %s", e)
            return False

    def eliminar_tipo_ventilacion(self, id_tipo):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tipos_ventilacion WHERE id = %s", (id_tipo,))
                return True
        except Exception as e:
            logger.error("Error eliminando tipo de ventilación: %s", e)
            return False

    def obtener_tipo_ventilacion_id(self, id_tipo):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM tipos_ventilacion WHERE id = %s", (id_tipo,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def actualizar_tipo_ventilacion(self, id_tipo, datos, imagen_url=None):
        """Actualiza un tipo de ventilación existente."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                if imagen_url:
                    cursor.execute(
                        "UPDATE tipos_ventilacion SET nombre = %s, descripcion = %s, imagen_url = %s WHERE id = %s",
                        (datos.get('nombre'), datos.get('descripcion', ''), imagen_url, id_tipo)
                    )
                else:
                    cursor.execute(
                        "UPDATE tipos_ventilacion SET nombre = %s, descripcion = %s WHERE id = %s",
                        (datos.get('nombre'), datos.get('descripcion', ''), id_tipo)
                    )
                logger.info("Tipo de ventilación actualizado ID: %s", id_tipo)
                return True
        except Exception as e:
            logger.error("Error actualizando tipo de ventilación: %s", e)
            return False

    # =========================================================================
    # TABLA GENÉRICA (para exportación)
    # =========================================================================
    def obtener_datos_tabla(self, tabla):
        TABLAS_VALIDAS = ['clientes', 'ups_specs', 'baterias_modelos', 'baterias_curvas_descarga', 'proyectos_publicados']
        if tabla not in TABLAS_VALIDAS:
            return [], []
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {tabla}")
                filas = cursor.fetchall()
                headers = [desc[0] for desc in cursor.description]
                return headers, filas
        except Exception:
            return [], []

    # =========================================================================
    # VALIDACIÓN DE PROYECTOS
    # =========================================================================
    def validar_voltaje(self, voltaje, id_ups=None):
        """Valida que el voltaje sea positivo y razonable."""
        try:
            v = float(voltaje)
            if v <= 0:
                return False, "El voltaje debe ser positivo"
            if v > 1000:
                return False, "El voltaje parece demasiado alto (>1000V)"
            if id_ups:
                ups_data = self.obtener_ups_id(id_ups)
                if ups_data:
                    voltajes_validos = []
                    for i in [1, 2, 3]:
                        v_entrada = ups_data.get(f'Voltaje_Entrada_{i}_V')
                        if v_entrada:
                            voltajes_validos.append(v_entrada)
                    if voltajes_validos:
                        tolerancia = 0.1
                        compatible = any(abs(v - v_val) / v_val <= tolerancia for v_val in voltajes_validos)
                        if not compatible:
                            return False, f"Voltaje no compatible con UPS (acepta: {', '.join(map(str, voltajes_validos))}V)"
            return True, "OK"
        except (ValueError, TypeError):
            return False, "El voltaje debe ser un número válido"

    def validar_fases(self, fases):
        try:
            f = int(fases)
            if f not in [1, 3]:
                return False, "Las fases deben ser 1 o 3"
            return True, "OK"
        except (ValueError, TypeError):
            return False, "Las fases deben ser un número entero"

    def validar_longitud(self, longitud):
        try:
            l = float(longitud)
            if l <= 0:
                return False, "La longitud debe ser positiva"
            if l > 500:
                return False, "La longitud parece demasiado grande (>500m)"
            return True, "OK"
        except (ValueError, TypeError):
            return False, "La longitud debe ser un número válido"

    def validar_datos_proyecto(self, datos):
        errores = []
        if 'voltaje' in datos and datos['voltaje']:
            valido, msg = self.validar_voltaje(datos['voltaje'], datos.get('id_ups'))
            if not valido:
                errores.append(f"Voltaje: {msg}")
        if 'fases' in datos and datos['fases']:
            valido, msg = self.validar_fases(datos['fases'])
            if not valido:
                errores.append(f"Fases: {msg}")
        if 'longitud' in datos and datos['longitud']:
            valido, msg = self.validar_longitud(datos['longitud'])
            if not valido:
                errores.append(f"Longitud: {msg}")
        if 'tiempo_respaldo' in datos and datos['tiempo_respaldo']:
            try:
                t = float(datos['tiempo_respaldo'])
                if t <= 0:
                    errores.append("Tiempo de respaldo: Debe ser positivo")
                if t > 1440:
                    errores.append("Tiempo de respaldo: Demasiado largo (>24h)")
            except (ValueError, TypeError):
                errores.append("Tiempo de respaldo: Debe ser un número válido")
        return len(errores) == 0, errores

    def obtener_proyectos_incompletos(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, pedido, cliente_snap, sucursal_snap, modelo_snap, potencia_snap,
                       id_ups, voltaje, fases, longitud, tiempo_respaldo, id_bateria
                FROM proyectos_publicados
                WHERE voltaje IS NULL OR fases IS NULL OR longitud IS NULL
                ORDER BY id
            """)
            return [dict(row) for row in cursor.fetchall()]

    def completar_datos_proyecto(self, pedido, datos):
        """Actualiza datos de un proyecto con validación."""
        valido, errores = self.validar_datos_proyecto(datos)
        if not valido:
            return False, errores
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                set_parts = []
                values = []
                campos_permitidos = ['id_ups', 'voltaje', 'fases', 'longitud', 'tiempo_respaldo', 'id_bateria']

                for key, value in datos.items():
                    if key in campos_permitidos and value is not None:
                        set_parts.append(f"{key} = %s")
                        values.append(value)

                if not set_parts:
                    return False, ["No hay datos válidos para actualizar"]

                values.append(pedido)
                cursor.execute(
                    f"UPDATE proyectos_publicados SET {', '.join(set_parts)} WHERE pedido = %s",
                    values
                )
                return True, []
        except Exception as e:
            return False, [f"Error de base de datos: {str(e)}"]

    # =========================================================================
    # MEMORIA DE CALCULADORA
    # =========================================================================
    def obtener_calculo_por_pedido(self, pedido):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM proyectos_publicados WHERE pedido = %s", (pedido,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def guardar_calculo(self, pedido, datos):
        """Guarda o actualiza cálculo de un pedido."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT id FROM proyectos_publicados WHERE pedido = %s", (pedido,))
                existe = cursor.fetchone()

                if existe:
                    campos = []
                    valores = []
                    campos_validos = [
                        'voltaje', 'fases', 'longitud', 'tiempo_respaldo',
                        'id_ups', 'id_bateria', 'modelo_snap', 'potencia_snap',
                        'cliente_snap', 'sucursal_snap', 'calibre_fases',
                        'config_salida', 'calibre_tierra'
                    ]
                    for key in campos_validos:
                        if key in datos and datos[key] is not None:
                            campos.append(f"{key} = %s")
                            valores.append(datos[key])
                    if campos:
                        valores.append(pedido)
                        cursor.execute(
                            f"UPDATE proyectos_publicados SET {', '.join(campos)} WHERE pedido = %s",
                            valores
                        )
                        return True
                    return False
                else:
                    cursor.execute("""
                        INSERT INTO proyectos_publicados
                        (pedido, voltaje, fases, longitud, tiempo_respaldo, id_ups, id_bateria,
                         modelo_snap, potencia_snap, cliente_snap, sucursal_snap,
                         calibre_fases, config_salida, calibre_tierra, fecha_publicacion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        pedido,
                        datos.get('voltaje'), datos.get('fases'), datos.get('longitud'),
                        datos.get('tiempo_respaldo'), datos.get('id_ups'), datos.get('id_bateria'),
                        datos.get('modelo_snap'), datos.get('potencia_snap'),
                        datos.get('cliente_snap'), datos.get('sucursal_snap'),
                        datos.get('calibre_fases'), datos.get('config_salida'),
                        datos.get('calibre_tierra')
                    ))
                    return True
        except Exception as e:
            logger.error("Error guardando cálculo: %s", e)
            return False

    # =========================================================================
    # MONITOREO
    # =========================================================================
    def agregar_monitoreo_ups(self, datos):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monitoreo_config (ip, port, slave_id, nombre, protocolo, snmp_community, snmp_port)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    datos['ip'],
                    int(datos.get('port', 502)),
                    int(datos.get('slave_id', 1)),
                    datos.get('nombre', 'UPS'),
                    datos.get('protocolo', 'modbus'),
                    datos.get('snmp_community', 'public'),
                    int(datos.get('snmp_port', 161))
                ))
                return True
        except Exception as e:
            logger.error("Error agregando dispositivo monitoreo: %s", e)
            return False

    def obtener_monitoreo_ups(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM monitoreo_config ORDER BY nombre")
            return [dict(row) for row in cursor.fetchall()]

    def eliminar_monitoreo_ups(self, id_device):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM monitoreo_config WHERE id = %s", (id_device,))

    # =========================================================================
    # GESTIÓN DE USUARIOS
    # =========================================================================
    def obtener_usuario_por_username(self, username):
        """Busca un usuario por nombre de usuario."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cursor.fetchone()

    def obtener_usuario_por_id(self, user_id):
        """Busca un usuario por ID."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()

    def crear_usuario(self, username, password_hash, role='user'):
        """Crea un nuevo usuario."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    (username, password_hash, role)
                )
                return True
        except Exception as e:
            logger.error("Error creando usuario: %s", e)
            return False
