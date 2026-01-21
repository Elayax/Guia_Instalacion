import sqlite3
import os
import csv  # <--- IMPORTANTE: Necesario para leer el CSV correctamente
from datetime import datetime

class GestorDB:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, 'Equipos.db')
        self._inicializar_tablas()

    def _conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _inicializar_tablas(self):
        conn = self._conectar()
        cursor = conn.cursor()
        
        # 1. TABLA CLIENTES
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                sucursal TEXT NOT NULL,
                direccion TEXT,
                link_maps TEXT,
                lat TEXT,
                lon TEXT,
                UNIQUE(cliente, sucursal)
            )
        ''')

        # 1.5 TABLA TIPOS DE VENTILACION (NUEVO CATÁLOGO)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tipos_ventilacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT
            )
        ''')

        # 2. TABLA UPS_SPECS (NUEVO ESQUEMA)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ups_specs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre_del_Producto TEXT,
                Serie TEXT,
                Capacidad_kVA REAL,
                Capacidad_kW REAL,
                Eficiencia_Modo_AC_pct REAL,
                Eficiencia_Modo_Bateria_pct REAL,
                Eficiencia_Modo_ECO_pct REAL,
                FP_Salida REAL,
                Voltaje_Entrada_1_V REAL,
                Voltaje_Entrada_2_V REAL,
                Voltaje_Entrada_3_V REAL,
                Conexion_Entrada TEXT,
                Voltaje_Salida_1_V REAL,
                Voltaje_Salida_2_V REAL,
                Voltaje_Salida_3_V REAL,
                Conexion_Salida TEXT,
                Frecuencia_1_Hz REAL,
                Frecuencia_2_Hz REAL,
                Frecuencia_Precision_pct REAL,
                THDu_Lineal_pct REAL,
                THDu_NoLineal_pct REAL,
                Sobrecarga_110_pct_min REAL,
                Sobrecarga_125_pct_min REAL,
                Sobrecarga_150_pct_min REAL,
                Bateria_Vdc REAL,
                Bateria_Piezas_min REAL,
                Bateria_Piezas_max REAL,
                Bateria_Piezas_defecto REAL,
                Precision_Voltaje_pct REAL,
                TempTrabajo_min_C REAL,
                TempTrabajo_max_C REAL,
                Humedad_min_pct REAL,
                Humedad_max_pct REAL,
                Peso_Gabinete_kg REAL,
                Dim_Largo_mm REAL,
                Dim_Ancho_mm REAL,
                Dim_Alto_mm REAL,
                Nivel_Ruido_dB REAL,
                Cable_Entrada_mm2 REAL,
                Cable_Entrada_conductores REAL,
                Cable_Salida_mm2 REAL,
                Cable_Salida_conductores REAL,
                Cable_Bateria_mm2 REAL,
                Cable_Bateria_conductores REAL,
                Cable_PE_mm2 REAL
            )
        ''')
        
        # Creación de Índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_serie ON ups_specs(Serie);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nombre ON ups_specs(Nombre_del_Producto);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cap_kva ON ups_specs(Capacidad_kVA);")

        # Add image url columns to ups_specs if they don't exist
        cursor.execute("PRAGMA table_info(ups_specs)")
        columns = [row['name'] for row in cursor.fetchall()]
        if 'imagen_url' not in columns:
            cursor.execute("ALTER TABLE ups_specs ADD COLUMN imagen_url TEXT")
        if 'imagen_instalacion_url' not in columns:
            cursor.execute("ALTER TABLE ups_specs ADD COLUMN imagen_instalacion_url TEXT")
        if 'imagen_baterias_url' not in columns:
            cursor.execute("ALTER TABLE ups_specs ADD COLUMN imagen_baterias_url TEXT")
        if 'tipo_ventilacion_id' not in columns:
            cursor.execute("ALTER TABLE ups_specs ADD COLUMN tipo_ventilacion_id INTEGER REFERENCES tipos_ventilacion(id)")
        if 'imagen_diagrama_ac_url' not in columns:
            cursor.execute("ALTER TABLE ups_specs ADD COLUMN imagen_diagrama_ac_url TEXT")
        if 'imagen_diagrama_dc_url' not in columns:
            cursor.execute("ALTER TABLE ups_specs ADD COLUMN imagen_diagrama_dc_url TEXT")
        if 'imagen_layout_url' not in columns:
            cursor.execute("ALTER TABLE ups_specs ADD COLUMN imagen_layout_url TEXT")

        # 3. TABLA PROYECTOS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proyectos_publicados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido TEXT UNIQUE NOT NULL,
                fecha_publicacion TEXT,
                modelo_snap TEXT,
                potencia_snap REAL,
                cliente_snap TEXT,
                sucursal_snap TEXT,
                calibre_fases TEXT,
                config_salida TEXT,
                calibre_tierra TEXT
            )
        ''')

        # 4. TABLAS BATERIAS (NUEVO MODULO - ADAPTADO)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baterias_modelos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modelo TEXT UNIQUE NOT NULL,
                serie TEXT,
                voltaje_nominal REAL,
                capacidad_nominal_ah REAL,
                resistencia_interna_mohm REAL,
                max_corriente_descarga_5s_a REAL,
                largo_mm REAL,
                ancho_mm REAL,
                alto_contenedor_mm REAL,
                alto_total_mm REAL,
                peso_kg REAL,
                tipo_terminal TEXT,
                material_contenedor TEXT,
                carga_flotacion_v_min REAL,
                carga_flotacion_v_max REAL,
                coef_temp_flotacion_mv_c REAL,
                carga_ciclica_v_min REAL,
                carga_ciclica_v_max REAL,
                corriente_inicial_max_a REAL,
                coef_temp_ciclica_mv_c REAL,
                temp_descarga_min_c REAL,
                temp_descarga_max_c REAL,
                temp_carga_min_c REAL,
                temp_carga_max_c REAL,
                temp_almacenaje_min_c REAL,
                temp_almacenaje_max_c REAL,
                temp_nominal_c REAL,
                capacidad_40c_pct REAL,
                capacidad_25c_pct REAL,
                capacidad_0c_pct REAL,
                autodescarga_meses_max REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baterias_curvas_descarga (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bateria_id INTEGER NOT NULL,
                tiempo_minutos INTEGER,
                voltaje_corte_fv REAL,
                valor REAL,
                unidad TEXT DEFAULT 'W', -- 'W' para Watts/celda, 'A' para Amperes
                FOREIGN KEY(bateria_id) REFERENCES baterias_modelos(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_curva_descarga ON baterias_curvas_descarga(bateria_id, unidad, tiempo_minutos, voltaje_corte_fv);")

        # CARGA DE DATOS DE EJEMPLO PARA TIPOS DE VENTILACIÓN
        check_vent = cursor.execute("SELECT count(*) FROM tipos_ventilacion").fetchone()[0]
        if check_vent == 0:
            datos_ventilacion = [
                ("Aire Forzado", "Ventilación mediante ventiladores que impulsan el aire a través del equipo"),
                ("Convección Natural", "Ventilación pasiva mediante circulación natural del aire"),
                ("Flujo Cruzado", "Entrada y salida de aire en lados opuestos del equipo"),
                ("Flujo Frontal", "Entrada y salida de aire en la parte frontal del equipo")
            ]
            cursor.executemany("INSERT INTO tipos_ventilacion (nombre, descripcion) VALUES (?, ?)", datos_ventilacion)

        # CARGA DE DATOS DE EJEMPLO (SI LA TABLA ESTÁ VACÍA)
        check = cursor.execute("SELECT count(*) FROM baterias_modelos").fetchone()[0]
        if check == 0:
            datos_ejemplo = [
                ("LBS12-7.2","General Purpose",12,7.2,18.0,108.0,151,65,93.5,99,2.35,"T2","ABS",13.5,13.8,-20,14.4,15.0,2.16,-30,-15,50,0,40,-15,40,25,103,100,86,6),
                ("LBS12-9.0","General Purpose",12,8.6,19.0,129.0,151,65,93.5,99,2.66,"T2","ABS",13.5,13.8,-20,14.4,15.0,2.58,-30,-15,50,0,40,-15,40,25,103,100,86,6),
                ("LBS12-10","General Purpose",12,10.0,22.0,150.0,151,65,111,117,3.20,"T2","ABS",13.5,13.8,-20,14.4,15.0,3.00,-30,-15,50,0,40,-15,40,25,103,100,86,6),
                ("LBS12-55","General Purpose",12,55.0,7.5,660.0,229,138,205,211,16.2,"T6","ABS",13.5,13.8,-20,14.4,15.0,16.5,-30,-15,50,0,40,-15,40,25,103,100,86,6),
                ("LBS12-75","General Purpose",12,75.0,6.6,900.0,260,168,208,214,22.3,"T6","ABS",13.5,13.8,-20,14.4,15.0,22.5,-30,-15,50,0,40,-15,40,25,103,100,86,6),
                ("LBS12-100","General Purpose",12,100.0,4.9,1200.0,330,173,212,220,30.6,"T11","ABS",13.5,13.8,-20,14.4,15.0,30.0,-30,-15,50,0,40,-15,40,25,103,100,86,6)
            ]
            cols = "modelo,serie,voltaje_nominal,capacidad_nominal_ah,resistencia_interna_mohm,max_corriente_descarga_5s_a,largo_mm,ancho_mm,alto_contenedor_mm,alto_total_mm,peso_kg,tipo_terminal,material_contenedor,carga_flotacion_v_min,carga_flotacion_v_max,coef_temp_flotacion_mv_c,carga_ciclica_v_min,carga_ciclica_v_max,corriente_inicial_max_a,coef_temp_ciclica_mv_c,temp_descarga_min_c,temp_descarga_max_c,temp_carga_min_c,temp_carga_max_c,temp_almacenaje_min_c,temp_almacenaje_max_c,temp_nominal_c,capacidad_40c_pct,capacidad_25c_pct,capacidad_0c_pct,autodescarga_meses_max"
            placeholders = ",".join(["?"] * 31)
            cursor.executemany(f"INSERT INTO baterias_modelos ({cols}) VALUES ({placeholders})", datos_ejemplo)

        conn.commit()
        conn.close()

    # --- NUEVA FUNCIÓN DE IMPORTACIÓN CSV ---
    def cargar_clientes_desde_csv(self, ruta_csv):
        """
        Lee el archivo CSV y carga los datos en la tabla clientes.
        Maneja automáticamente la separación de coordenadas "Lat, Lon".
        """
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        conn = self._conectar()
        filas_insertadas = 0
        errores = 0
        logs = []

        try:
            # utf-8-sig maneja el BOM de Excel si existe
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                # Usamos csv.reader para manejar correctamente las comillas en direcciones
                lector = csv.reader(f)
                
                for fila in lector:
                    # El CSV tiene el formato: [Cliente, Sucursal, Dirección, Link, "Lat, Lon"]
                    if len(fila) < 5: 
                        logs.append(f"⚠️ Fila ignorada (columnas insuficientes): {fila}")
                        continue # Saltar filas incompletas

                    try:
                        cliente = fila[0].strip()
                        sucursal = fila[1].strip()
                        direccion = fila[2].strip()

                        # Insertamos usando INSERT OR IGNORE para no duplicar si ya existe
                        conn.execute('''
                            INSERT OR IGNORE INTO clientes (cliente, sucursal, direccion)
                            VALUES (?, ?, ?)
                        ''', (cliente, sucursal, direccion))
                        
                        filas_insertadas += 1
                        # logs.append(f"✅ Insertado: {cliente} - {sucursal}") # Opcional: mucho ruido

                    except Exception as e:
                        logs.append(f"❌ Error en fila {fila}: {e}")
                        errores += 1

            conn.commit()
            return {'status': 'ok', 'insertados': filas_insertadas, 'errores': errores, 'logs': logs}
            
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}
        finally:
            conn.close()

    # --- GESTIÓN DE UPS (NUEVO) ---
    def obtener_ups_todos(self):
        conn = self._conectar()
        res = conn.execute("SELECT * FROM ups_specs ORDER BY Capacidad_kVA").fetchall()
        conn.close()
        return [dict(row) for row in res]

    def _importar_csv_simple(self, ruta_csv, tabla):
        """Método genérico para importar CSV a una tabla plana (ups o baterias_modelos)"""
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        conn = self._conectar()
        filas_insertadas = 0
        errores = 0
        logs = []

        try:
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                lector = csv.DictReader(f)
                
                # Obtener columnas válidas de la BD
                cursor = conn.execute(f"PRAGMA table_info({tabla})")
                columnas_validas = {row['name'] for row in cursor.fetchall() if row['name'] != 'id'}

                for i, fila in enumerate(lector, start=1):
                    try:
                        # Limpiar datos: quitar espacios, ignorar vacíos o S/D
                        datos_limpios = {}
                        for k, v in fila.items():
                            if k and v and v.strip() and v.strip() != 'S/D':
                                key_clean = k.strip().replace(' ', '_') # Normalizar header si es necesario
                                if key_clean in columnas_validas:
                                    datos_limpios[key_clean] = v.strip()

                        if not datos_limpios: continue

                        columnas = ', '.join(datos_limpios.keys())
                        placeholders = ', '.join(['?'] * len(datos_limpios))
                        valores = list(datos_limpios.values())

                        sql = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
                        conn.execute(sql, valores)
                        filas_insertadas += 1
                    except Exception as e:
                        errores += 1
                        logs.append(f"Fila {i} Error: {str(e)}")

            conn.commit()
            return {'status': 'ok', 'insertados': filas_insertadas, 'errores': errores, 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}
        finally:
            conn.close()

    def cargar_ups_desde_csv(self, ruta_csv):
        return self._importar_csv_simple(ruta_csv, 'ups_specs')

    def cargar_baterias_modelos_desde_csv(self, ruta_csv):
        return self._importar_csv_simple(ruta_csv, 'baterias_modelos')

    def insertar_ups_manual(self, datos_dict):
        conn = self._conectar()
        try:
            # Filtrar para evitar que 'accion' u otros campos no deseados se inserten
            cursor = conn.execute("PRAGMA table_info(ups_specs)")
            columnas_validas = {row['name'] for row in cursor.fetchall() if row['name'] != 'id'}
            datos_limpios = {k: v for k, v in datos_dict.items() if k in columnas_validas}

            if not datos_limpios: return False

            columnas = ', '.join(datos_limpios.keys())
            placeholders = ', '.join(['?'] * len(datos_limpios))
            valores = list(datos_limpios.values())
            
            sql = f"INSERT INTO ups_specs ({columnas}) VALUES ({placeholders})"
            conn.execute(sql, valores)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error insertando UPS: {e}")
            return False
        finally:
            conn.close()

    def actualizar_ups(self, id_ups, datos):
        """Actualiza un registro existente en ups_specs"""
        conn = self._conectar()
        try:
            # Filtrar solo columnas válidas para evitar errores de SQL injection o campos extra
            cursor = conn.execute("PRAGMA table_info(ups_specs)")
            columnas_validas = {row['name'] for row in cursor.fetchall() if row['name'] != 'id'}
            
            datos_limpios = {k: v for k, v in datos.items() if k in columnas_validas}
            
            if not datos_limpios:
                return False

            set_clause = ', '.join([f"{k} = ?" for k in datos_limpios.keys()])
            valores = list(datos_limpios.values())
            valores.append(id_ups)
            
            conn.execute(f"UPDATE ups_specs SET {set_clause} WHERE id = ?", valores)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando UPS: {e}")
            return False
        finally:
            conn.close()

    # --- GESTIÓN DE CLIENTES (EXISTENTE) ---
    def agregar_cliente(self, datos):
        conn = self._conectar()
        try:
            conn.execute('''
                INSERT INTO clientes (cliente, sucursal, direccion)
                VALUES (?, ?, ?)
            ''', (datos['cliente'], datos['sucursal'], datos['direccion']))
            conn.commit()
        except Exception as e:
            print(f"Error agregando cliente: {e}")
        finally:
            conn.close()

    def obtener_clientes(self):
        conn = self._conectar()
        res = conn.execute("SELECT * FROM clientes ORDER BY cliente, sucursal").fetchall()
        conn.close()
        return [dict(row) for row in res]

    def eliminar_cliente(self, id_cliente):
        conn = self._conectar()
        conn.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
        conn.commit()
        conn.close()

    # --- MÉTODOS DE FILTRADO PARA LA UI ---
    def obtener_clientes_unicos(self):
        conn = self._conectar()
        cursor = conn.execute("SELECT DISTINCT cliente FROM clientes ORDER BY cliente")
        resultados = [row[0] for row in cursor.fetchall()]
        conn.close()
        return resultados

    def obtener_sucursales_por_cliente(self, nombre_cliente):
        conn = self._conectar()
        cursor = conn.execute("SELECT * FROM clientes WHERE cliente = ? ORDER BY sucursal", (nombre_cliente,))
        resultados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return resultados

    def obtener_ups_id(self, id_ups):
        conn = self._conectar()
        row = conn.execute("SELECT * FROM ups_specs WHERE id = ?", (id_ups,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def eliminar_ups(self, id_ups):
        conn = self._conectar()
        conn.execute("DELETE FROM ups_specs WHERE id = ?", (id_ups,))
        conn.commit()
        conn.close()

    def publicar_proyecto(self, datos_calculados, form_data):
        conn = self._conectar()
        try:
            conn.execute('''
                INSERT INTO proyectos_publicados 
                (pedido, fecha_publicacion, modelo_snap, potencia_snap, cliente_snap, sucursal_snap, calibre_fases, config_salida, calibre_tierra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                form_data['pedido'],
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                datos_calculados.get('Nombre_del_Producto', 'Desconocido'),
                datos_calculados.get('Capacidad_kVA', 0),
                form_data['cliente_nombre'],
                form_data['sucursal_nombre'],
                datos_calculados['fase_sel'],
                f"{form_data['fases']}F + N + GND",
                datos_calculados['gnd_sel']
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False 
        finally:
            conn.close()
            
    def obtener_proyectos(self):
        conn = self._conectar()
        res = conn.execute("SELECT * FROM proyectos_publicados ORDER BY id DESC").fetchall()
        conn.close()
        return [dict(row) for row in res]
    
    def obtener_proyecto_por_pedido(self, pedido):
        conn = self._conectar()
        cursor = conn.execute('''
            SELECT p.*, m.id as modelo_id_real 
            FROM proyectos_publicados p
            LEFT JOIN ups_specs m ON m.Nombre_del_Producto = p.modelo_snap
            WHERE p.pedido = ?
        ''', (pedido,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # --- GESTIÓN DE BATERÍAS (NUEVO MÓDULO) ---
    def agregar_modelo_bateria(self, datos_dict):
        conn = self._conectar()
        try:
            # Filtrar solo columnas válidas
            campos_validos = ['modelo','serie','voltaje_nominal','capacidad_nominal_ah','resistencia_interna_mohm','max_corriente_descarga_5s_a','largo_mm','ancho_mm','alto_contenedor_mm','alto_total_mm','peso_kg','tipo_terminal','material_contenedor','carga_flotacion_v_min','carga_flotacion_v_max','coef_temp_flotacion_mv_c','carga_ciclica_v_min','carga_ciclica_v_max','corriente_inicial_max_a','coef_temp_ciclica_mv_c','temp_descarga_min_c','temp_descarga_max_c','temp_carga_min_c','temp_carga_max_c','temp_almacenaje_min_c','temp_almacenaje_max_c','temp_nominal_c','capacidad_40c_pct','capacidad_25c_pct','capacidad_0c_pct','autodescarga_meses_max']
            datos_limpios = {k: datos_dict[k] for k in campos_validos if k in datos_dict}
            
            columnas = ', '.join(datos_limpios.keys())
            placeholders = ', '.join(['?'] * len(datos_limpios))
            valores = list(datos_limpios.values())
            
            sql = f"INSERT INTO baterias_modelos ({columnas}) VALUES ({placeholders})"
            conn.execute(sql, valores)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error agregando batería: {e}")
            return False
        finally:
            conn.close()

    def buscar_bateria_optima(self, watts_requeridos_celda, tiempo_minutos, fv_inversor):
        conn = self._conectar()
        try:
            # Buscamos registros que cumplan con los requisitos mínimos
            # Ordenamos por watts_celda ASC para encontrar la opción más ajustada (menor sobredimensionamiento)
            query = '''
                SELECT m.modelo, m.capacidad_nominal_ah, m.voltaje_nominal,
                       c.valor as watts_celda, c.tiempo_minutos, c.voltaje_corte_fv, c.unidad
                FROM baterias_curvas_descarga c
                JOIN baterias_modelos m ON c.bateria_id = m.id
                WHERE c.tiempo_minutos >= ?
                  AND c.voltaje_corte_fv >= ?
                  AND c.valor >= ?
                  AND c.unidad = 'W'
                ORDER BY c.valor ASC
                LIMIT 10
            '''
            cursor = conn.execute(query, (tiempo_minutos, fv_inversor, watts_requeridos_celda))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def obtener_baterias_modelos(self, solo_con_curvas=False):
        conn = self._conectar()
        if solo_con_curvas:
            sql = """
                SELECT DISTINCT m.* 
                FROM baterias_modelos m
                JOIN baterias_curvas_descarga c ON m.id = c.bateria_id
                ORDER BY m.modelo
            """
            res = conn.execute(sql).fetchall()
        else:
            res = conn.execute("SELECT * FROM baterias_modelos ORDER BY modelo").fetchall()
        conn.close()
        return [dict(row) for row in res]

    def eliminar_bateria(self, id_bateria):
        conn = self._conectar()
        conn.execute("DELETE FROM baterias_modelos WHERE id = ?", (id_bateria,))
        conn.commit()
        conn.close()

    def cargar_curvas_baterias_masiva(self, ruta_csv):
        """Carga curvas para múltiples baterías desde un CSV, reportando errores detallados."""
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo CSV no encontrado', 'logs': []}

        conn = self._conectar()
        insertados = 0
        errores = 0
        logs = []
        modelos_a_limpiar = set()

        try:
            # --- PRIMERA PASADA: Validar y encontrar modelos a limpiar ---
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                try:
                    lector_validacion = csv.DictReader(f)
                    if not lector_validacion.fieldnames:
                        return {'status': 'error', 'msg': 'El archivo CSV está vacío o no tiene cabecera.', 'logs':[]}
                    
                    headers = [h.strip() for h in lector_validacion.fieldnames if h]
                    if 'Modelo' not in headers: logs.append("La cabecera debe contener la columna 'Modelo'.")
                    if 'Tiempo_Min' not in headers: logs.append("La cabecera debe contener la columna 'Tiempo_Min'.")
                    cols_fv = [h for h in headers if h.upper().startswith('FV_')]
                    if not cols_fv: logs.append("Debe haber al menos una columna de voltaje (ej. 'FV_1.60').")
                    
                    if logs:
                        return {'status': 'error', 'msg': 'Error de formato en la cabecera.', 'logs': logs, 'insertados': 0, 'errores': 1}

                    for i, fila in enumerate(lector_validacion, start=2):
                        modelo = fila.get('Modelo', '').strip()
                        if not modelo:
                            logs.append(f"Fila {i}: Falta el 'Modelo' de la batería.")
                            errores += 1
                            continue
                        
                        row_bat = conn.execute("SELECT id FROM baterias_modelos WHERE modelo = ?", (modelo,)).fetchone()
                        if not row_bat:
                            logs.append(f"Fila {i}: Modelo '{modelo}' no existe. Agréguelo primero.")
                            errores += 1
                            continue
                        
                        modelos_a_limpiar.add(row_bat['id'])

                except Exception as e:
                    return {'status': 'error', 'msg': f'Error de formato en CSV: {e}', 'logs': [], 'insertados': 0, 'errores': 1}

            if errores > 0:
                 return {'status': 'error', 'msg': 'Se encontraron errores de validación.', 'logs': logs, 'insertados': 0, 'errores': errores}


            # --- LIMPIEZA ---
            if modelos_a_limpiar:
                # Usamos placeholders para seguridad
                placeholders = ','.join('?' for _ in modelos_a_limpiar)
                conn.execute(f"DELETE FROM baterias_curvas_descarga WHERE bateria_id IN ({placeholders})", list(modelos_a_limpiar))


            # --- SEGUNDA PASADA: Inserción de datos ---
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                lector_insercion = csv.DictReader(f)
                cols_fv = [h.strip() for h in lector_insercion.fieldnames if h and h.strip().upper().startswith('FV_')]

                for i, fila in enumerate(lector_insercion, start=2):
                    modelo = fila.get('Modelo', '').strip()
                    row_bat = conn.execute("SELECT id FROM baterias_modelos WHERE modelo = ?", (modelo,)).fetchone()
                    if not row_bat: continue # Ya se reportó el error en la primera pasada

                    bateria_id = row_bat['id']
                    
                    try:
                        unidad = fila.get('Unidad', 'W').strip().upper()
                        if unidad not in ['W', 'A']: unidad = 'W'

                        tiempo = int(fila.get('Tiempo_Min', 0))
                        if tiempo <= 0:
                            logs.append(f"Fila {i}: 'Tiempo_Min' debe ser un número positivo.")
                            errores += 1
                            continue
                        
                        puntos_fila = 0
                        for col in cols_fv:
                            try:
                                voltaje_corte = float(col.upper().replace('FV_', ''))
                                valor_str = fila.get(col, '').strip()
                                if not valor_str: continue

                                valor = float(valor_str)
                                
                                conn.execute('''
                                    INSERT INTO baterias_curvas_descarga 
                                    (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (bateria_id, tiempo, voltaje_corte, valor, unidad))
                                insertados += 1
                                puntos_fila += 1
                            except (ValueError, TypeError):
                                logs.append(f"Fila {i}, Columna {col}: Valor '{fila.get(col)}' no es numérico.")
                                errores += 1
                        
                        if puntos_fila == 0:
                            logs.append(f"Fila {i}: No se encontraron valores numéricos en las columnas FV.")
                            errores += 1

                    except (ValueError, TypeError):
                        logs.append(f"Fila {i}: 'Tiempo_Min' ('{fila.get('Tiempo_Min')}') no es un número válido.")
                        errores += 1
            
            conn.commit()
            return {'status': 'ok', 'insertados': insertados, 'errores': errores, 'logs': logs}

        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'msg': str(e), 'logs': logs, 'insertados': 0, 'errores': 1}
        finally:
            conn.close()

    def obtener_bateria_id(self, id_bateria):
        conn = self._conectar()
        row = conn.execute("SELECT * FROM baterias_modelos WHERE id = ?", (id_bateria,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def actualizar_bateria(self, id_bateria, datos):
        conn = self._conectar()
        try:
            cursor = conn.execute("PRAGMA table_info(baterias_modelos)")
            columnas_validas = {row['name'] for row in cursor.fetchall() if row['name'] != 'id'}
            
            datos_limpios = {k: v for k, v in datos.items() if k in columnas_validas}
            if not datos_limpios: return False

            set_clause = ', '.join([f"{k} = ?" for k in datos_limpios.keys()])
            valores = list(datos_limpios.values())
            valores.append(id_bateria)
            
            conn.execute(f"UPDATE baterias_modelos SET {set_clause} WHERE id = ?", valores)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando batería: {e}")
            return False
        finally:
            conn.close()

    def obtener_curvas_por_bateria(self, id_bateria):
        conn = self._conectar()
        res = conn.execute("SELECT * FROM baterias_curvas_descarga WHERE bateria_id = ? ORDER BY unidad, tiempo_minutos, voltaje_corte_fv", (id_bateria,)).fetchall()
        conn.close()
        return [dict(row) for row in res]

    def obtener_curvas_pivot(self, bateria_id, unidad='W'):
        """Retorna las curvas organizadas como matriz para visualización, con llaves string para ser compatible con JSON."""
        conn = self._conectar()
        rows = conn.execute("SELECT tiempo_minutos, voltaje_corte_fv, valor FROM baterias_curvas_descarga WHERE bateria_id = ? AND unidad = ? ORDER BY tiempo_minutos, voltaje_corte_fv", (bateria_id, unidad)).fetchall()
        conn.close()

        if not rows:
            return None

        # 1. Obtener columnas dinámicas (Voltajes de corte)
        voltajes = sorted(list(set(r['voltaje_corte_fv'] for r in rows)))
        
        # 2. Agrupar por tiempo, usando strings como llaves para los voltajes
        datos_por_tiempo = {}
        for r in rows:
            t = r['tiempo_minutos']
            if t not in datos_por_tiempo:
                datos_por_tiempo[t] = {'tiempo': t}
            # ¡IMPORTANTE! Usar el string del voltaje como llave
            datos_por_tiempo[t][str(r['voltaje_corte_fv'])] = r['valor']

        # 3. Convertir a lista ordenada por tiempo
        data_list = sorted(datos_por_tiempo.values(), key=lambda x: x['tiempo'])
        
        return {'headers': [str(v) for v in voltajes], 'data': data_list}

    def cargar_curvas_por_id_csv(self, bateria_id, ruta_csv):
        """Carga curvas para una batería específica, limpiando las anteriores y reportando errores."""
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        conn = self._conectar()
        insertados = 0
        logs = []
        try:
            conn.execute("DELETE FROM baterias_curvas_descarga WHERE bateria_id = ?", (bateria_id,))
            
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                try:
                    lector = csv.DictReader(f)
                    # Verificar que las columnas existan
                    if not lector.fieldnames:
                        return {'status': 'error', 'msg': 'El archivo CSV está vacío o no tiene cabecera.', 'logs': []}

                    cols_fv = [c for c in lector.fieldnames if c and c.upper().strip().startswith('FV_')]
                    
                    if 'Tiempo_Min' not in lector.fieldnames:
                        logs.append("La cabecera del CSV debe contener la columna 'Tiempo_Min'.")
                    
                    if not cols_fv:
                        logs.append("El CSV debe contener al menos una columna de voltaje con el formato 'FV_x.xx' (ej. 'FV_1.60').")

                    if logs:
                        conn.rollback()
                        return {'status': 'error', 'msg': 'Error de formato en la cabecera del CSV.', 'logs': logs}

                    for i, fila in enumerate(lector, start=2): # i=2 porque la fila 1 es la cabecera
                        try:
                            tiempo_str = fila.get('Tiempo_Min', '0').strip()
                            tiempo = int(tiempo_str)
                            unidad = fila.get('Unidad', 'W').strip().upper()
                            if unidad not in ['W', 'A']: unidad = 'W'
                            if tiempo <= 0:
                                logs.append(f"Fila {i}: El valor de 'Tiempo_Min' ({tiempo_str}) debe ser un número positivo.")
                                continue
                            
                            puntos_insertados_fila = 0
                            for col in cols_fv:
                                try:
                                    v_corte = float(col.upper().strip().replace('FV_', ''))
                                    valor_str = fila.get(col, '').strip()
                                    if not valor_str:
                                        # No es un error, simplemente un valor faltante en la matriz
                                        continue
                                    
                                    valor = float(valor_str)
                                    conn.execute("INSERT INTO baterias_curvas_descarga (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad) VALUES (?, ?, ?, ?, ?)", (bateria_id, tiempo, v_corte, valor, unidad))
                                    insertados += 1
                                    puntos_insertados_fila += 1
                                except (ValueError, TypeError):
                                    logs.append(f"Fila {i}, Columna {col}: Valor '{fila.get(col, '')}' no es un número válido.")
                                    continue
                            
                            if puntos_insertados_fila == 0:
                                logs.append(f"Fila {i}: No se encontraron valores numéricos válidos en las columnas FV_*.")

                        except (ValueError, TypeError):
                            logs.append(f"Fila {i}: El valor de 'Tiempo_Min' ('{fila.get('Tiempo_Min')}') no es un número entero válido.")
                            continue
                except Exception as e:
                    conn.rollback()
                    return {'status': 'error', 'msg': f'Error general al leer el archivo CSV. Verifique que el formato sea correcto. Detalle: {e}', 'logs':[]}

            if insertados > 0:
                conn.commit()
                return {'status': 'ok', 'insertados': insertados, 'logs': logs}
            else:
                conn.rollback() # No se insertó nada, revertir el DELETE inicial
                if not logs: # Si no hay logs, el archivo estaba vacío
                    logs.append("El archivo CSV no contenía filas de datos válidas para procesar.")
                return {'status': 'error', 'msg': 'No se insertaron nuevos datos.', 'logs': logs}

        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'msg': str(e), 'logs': logs}
        finally:
            conn.close()

    def actualizar_curvas_desde_form(self, bateria_id, form_data):
        """
        Actualiza las curvas de una batería para una unidad específica desde los datos de un formulario editable.
        Los datos vienen en formato 'curva-<tiempo>-<voltaje>'.
        """
        conn = self._conectar()
        insertados = 0
        logs = []
        
        unidad = form_data.get('unidad_curva', 'W')

        try:
            # 1. Borrar las curvas existentes para esta batería y unidad
            conn.execute("DELETE FROM baterias_curvas_descarga WHERE bateria_id = ? AND unidad = ?", (bateria_id, unidad))

            # 2. Parsear y re-insertar los datos del formulario
            puntos_a_insertar = []
            for key, valor_str in form_data.items():
                if key.startswith('curva-'):
                    if not valor_str.strip():
                        continue # Ignorar inputs vacíos

                    try:
                        parts = key.split('-')
                        tiempo = int(parts[1])
                        voltaje = float(parts[2])
                        valor = float(valor_str)
                        
                        puntos_a_insertar.append((bateria_id, tiempo, voltaje, valor, unidad))
                        
                    except (ValueError, IndexError):
                        logs.append(f"Dato inválido en el formulario: {key}={valor_str}")
                        continue
            
            if puntos_a_insertar:
                conn.executemany('''
                    INSERT INTO baterias_curvas_descarga (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad)
                    VALUES (?, ?, ?, ?, ?)
                ''', puntos_a_insertar)
                insertados = len(puntos_a_insertar)
            
            conn.commit()
            return {'status': 'ok', 'insertados': insertados, 'logs': logs}

        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'msg': str(e), 'logs': logs}
        finally:
            conn.close()

    def obtener_datos_tabla(self, tabla):
        conn = self._conectar()
        try:
            tablas_validas = ['clientes', 'ups_specs', 'baterias_modelos', 'baterias_curvas_descarga', 'proyectos_publicados']
            if tabla not in tablas_validas:
                return [], []

            cursor = conn.execute(f"SELECT * FROM {tabla}")
            filas = cursor.fetchall()
            headers = [d[0] for d in cursor.description]
            return headers, filas
        except Exception:
            return [], []
        finally:
            conn.close()

    # --- GESTIÓN DE TIPOS DE VENTILACIÓN (NUEVO) ---
    def obtener_tipos_ventilacion(self):
        conn = self._conectar()
        res = conn.execute("SELECT * FROM tipos_ventilacion ORDER BY nombre").fetchall()
        conn.close()
        return [dict(row) for row in res]

    def agregar_tipo_ventilacion(self, datos):
        conn = self._conectar()
        try:
            conn.execute("INSERT INTO tipos_ventilacion (nombre, descripcion) VALUES (?, ?)",
                        (datos['nombre'], datos.get('descripcion', '')))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error agregando tipo de ventilación: {e}")
            return False
        finally:
            conn.close()

    def eliminar_tipo_ventilacion(self, id_tipo):
        conn = self._conectar()
        try:
            conn.execute("DELETE FROM tipos_ventilacion WHERE id = ?", (id_tipo,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error eliminando tipo de ventilación: {e}")
            return False
        finally:
            conn.close()

    def obtener_tipo_ventilacion_id(self, id_tipo):
        conn = self._conectar()
        row = conn.execute("SELECT * FROM tipos_ventilacion WHERE id = ?", (id_tipo,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def verificar_modelo_ups_existe(self, nombre_modelo, excluir_id=None):
        """Verifica si existe un UPS con el nombre de modelo dado (excluyendo opcionalmente un ID)"""
        conn = self._conectar()
        try:
            if excluir_id:
                row = conn.execute("SELECT id FROM ups_specs WHERE Nombre_del_Producto = ? AND id != ?",
                                  (nombre_modelo, excluir_id)).fetchone()
            else:
                row = conn.execute("SELECT id FROM ups_specs WHERE Nombre_del_Producto = ?",
                                  (nombre_modelo,)).fetchone()
            return row is not None
        finally:
            conn.close()