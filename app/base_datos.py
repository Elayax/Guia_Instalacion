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
                        link = fila[3].strip()
                        raw_coords = fila[4].strip() # Viene como "24.77, -107.45"

                        # Lógica para separar Latitud y Longitud
                        lat, lon = "", ""
                        if "," in raw_coords:
                            partes = raw_coords.split(',')
                            lat = partes[0].strip()
                            lon = partes[1].strip()
                        else:
                            # Si viene sin coma, asumimos que es todo latitud o error
                            lat = raw_coords

                        # Insertamos usando INSERT OR IGNORE para no duplicar si ya existe
                        conn.execute('''
                            INSERT OR IGNORE INTO clientes (cliente, sucursal, direccion, link_maps, lat, lon)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (cliente, sucursal, direccion, link, lat, lon))
                        
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
            columnas = ', '.join(datos_dict.keys())
            placeholders = ', '.join(['?'] * len(datos_dict))
            valores = list(datos_dict.values())
            
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
                INSERT INTO clientes (cliente, sucursal, direccion, link_maps, lat, lon)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datos['cliente'], datos['sucursal'], datos['direccion'], datos.get('maps'), datos['lat'], datos['lon']))
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
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo CSV no encontrado', 'logs': []}

        conn = self._conectar()
        insertados = 0
        errores = 0
        logs = []

        try:
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                lector = csv.DictReader(f)
                cols_fv = [c for c in lector.fieldnames if c.upper().startswith('FV_')]
                
                if not cols_fv:
                     return {'status': 'error', 'msg': 'No se encontraron columnas de voltaje (FV_x.xx)', 'logs': []}

                for i, fila in enumerate(lector, start=1):
                    modelo = fila.get('Modelo')
                    unidad = fila.get('Unidad', 'W').strip().upper() # Default W si no se especifica
                    if unidad not in ['W', 'A']: unidad = 'W'

                    if not modelo:
                        logs.append(f"Fila {i}: Falta columna 'Modelo'")
                        errores += 1
                        continue
                    
                    row_bat = conn.execute("SELECT id FROM baterias_modelos WHERE modelo = ?", (modelo,)).fetchone()
                    if not row_bat:
                        logs.append(f"Fila {i}: Modelo '{modelo}' no existe en BD")
                        errores += 1
                        continue
                    
                    bateria_id = row_bat['id']
                    
                    try:
                        tiempo = int(fila.get('Tiempo_Min', 0))
                        if tiempo <= 0: continue
                        
                        for col in cols_fv:
                            try:
                                voltaje_corte = float(col.upper().replace('FV_', ''))
                                valor = float(fila[col])
                                
                                conn.execute('''
                                    INSERT INTO baterias_curvas_descarga 
                                    (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (bateria_id, tiempo, voltaje_corte, valor, unidad))
                                insertados += 1
                            except ValueError:
                                continue
                    except ValueError as e:
                        logs.append(f"Fila {i}: Error de datos - {e}")
                        errores += 1

            conn.commit()
            return {'status': 'ok', 'insertados': insertados, 'errores': errores, 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}
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
        """Retorna las curvas organizadas como matriz para visualización: {headers: [1.60, 1.70...], data: [{tiempo: 5, 1.60: 100...}]}"""
        conn = self._conectar()
        rows = conn.execute("SELECT tiempo_minutos, voltaje_corte_fv, valor FROM baterias_curvas_descarga WHERE bateria_id = ? AND unidad = ? ORDER BY tiempo_minutos, voltaje_corte_fv", (bateria_id, unidad)).fetchall()
        conn.close()

        if not rows:
            return None

        # 1. Obtener columnas dinámicas (Voltajes de corte)
        voltajes = sorted(list(set(r['voltaje_corte_fv'] for r in rows)))
        
        # 2. Agrupar por tiempo
        datos_por_tiempo = {}
        for r in rows:
            t = r['tiempo_minutos']
            if t not in datos_por_tiempo:
                datos_por_tiempo[t] = {'tiempo': t}
            datos_por_tiempo[t][r['voltaje_corte_fv']] = r['valor']

        # 3. Convertir a lista ordenada por tiempo
        data_list = sorted(datos_por_tiempo.values(), key=lambda x: x['tiempo'])
        
        return {'headers': voltajes, 'data': data_list}

    def cargar_curvas_por_id_csv(self, bateria_id, ruta_csv):
        """Carga curvas para una batería específica, limpiando las anteriores."""
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado'}
        
        conn = self._conectar()
        insertados = 0
        try:
            # Limpiar curvas anteriores de esta batería para evitar duplicados
            conn.execute("DELETE FROM baterias_curvas_descarga WHERE bateria_id = ?", (bateria_id,))
            
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                lector = csv.DictReader(f)
                cols_fv = [c for c in lector.fieldnames if c.upper().startswith('FV_')]
                
                for fila in lector:
                    try:
                        tiempo = int(fila.get('Tiempo_Min', 0))
                        unidad = fila.get('Unidad', 'W').strip().upper()
                        if unidad not in ['W', 'A']: unidad = 'W'
                        if tiempo <= 0: continue
                        
                        for col in cols_fv:
                            try:
                                v_corte = float(col.upper().replace('FV_', ''))
                                valor = float(fila[col])
                                conn.execute("INSERT INTO baterias_curvas_descarga (bateria_id, tiempo_minutos, voltaje_corte_fv, valor, unidad) VALUES (?, ?, ?, ?, ?)", (bateria_id, tiempo, v_corte, valor, unidad))
                                insertados += 1
                            except ValueError: continue
                    except ValueError: continue
            
            conn.commit()
            return {'status': 'ok', 'insertados': insertados}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
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