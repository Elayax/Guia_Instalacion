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
        return conn

    def _inicializar_tablas(self):
        conn = self._conectar()
        cursor = conn.cursor()
        
        # LIMPIEZA: Eliminar tabla antigua para asegurar que solo se use la nueva
        cursor.execute("DROP TABLE IF EXISTS ups_catalogo")
        cursor.execute("DROP TABLE IF EXISTS ups_specs")
        
        # 1. TABLA CLIENTES
        # Nota: Mantenemos lat y lon separados porque es mejor para futuros cálculos
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
                Fuente TEXT,
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
                Torque_M6_Nm REAL,
                Torque_M8_Nm REAL,
                Torque_M10_Nm REAL,
                Torque_M12_Nm REAL,
                Torque_M16_Nm REAL,
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

    def cargar_ups_desde_csv(self, ruta_csv):
        """
        Carga masiva de equipos UPS desde CSV.
        Las columnas del CSV deben coincidir con los nombres de la tabla ups_specs.
        """
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        conn = self._conectar()
        filas_insertadas = 0
        errores = 0
        logs = []

        try:
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                lector = csv.DictReader(f)
                
                # 1. Obtener columnas válidas de la BD para evitar errores
                cursor = conn.execute("PRAGMA table_info(ups_specs)")
                columnas_validas = {row['name'] for row in cursor.fetchall() if row['name'] != 'id'}

                for i, fila in enumerate(lector, start=1):
                    try:
                        # Normalizar claves del CSV (reemplazar espacios por guiones bajos)
                        fila_norm = {k.strip().replace(' ', '_'): v.strip() for k, v in fila.items() if k}
                        
                        # 2. Filtrar datos del CSV: Solo columnas que existen en la BD y no están vacías
                        datos_limpios = {k: v for k, v in fila_norm.items() if k in columnas_validas and v}
                        
                        if not datos_limpios:
                            continue

                        # 3. Construcción dinámica del INSERT
                        columnas = ', '.join(datos_limpios.keys())
                        placeholders = ', '.join(['?'] * len(datos_limpios))
                        valores = list(datos_limpios.values())

                        sql = f"INSERT INTO ups_specs ({columnas}) VALUES ({placeholders})"
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