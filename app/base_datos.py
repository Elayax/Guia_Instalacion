import sqlite3
import os
import csv  # <--- IMPORTANTE: Necesario para leer el CSV correctamente
from datetime import datetime

class GestorDB:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, 'sistema_ups_master.db')
        self._inicializar_tablas()

    def _conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _inicializar_tablas(self):
        conn = self._conectar()
        cursor = conn.cursor()
        
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

        # 2. TABLA UPS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ups_catalogo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fabricante TEXT,
                modelo TEXT UNIQUE NOT NULL,
                kva REAL,
                v_entrada INTEGER,
                v_salida INTEGER
            )
        ''')

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

    def cargar_ups_desde_csv(self, ruta_csv):
        """
        Carga equipos UPS desde CSV con formato: [Marca, Modelo, Capacidad]
        """
        if not os.path.exists(ruta_csv):
            return {'status': 'error', 'msg': 'Archivo no encontrado', 'logs': []}

        conn = self._conectar()
        filas_insertadas = 0
        errores = 0
        logs = []

        try:
            with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
                lector = csv.reader(f)
                for fila in lector:
                    # Formato esperado: Marca, Modelo, Capacidad
                    if len(fila) < 3:
                        logs.append(f"⚠️ Fila ignorada (datos insuficientes): {fila}")
                        continue

                    try:
                        marca = fila[0].strip()      # Se guarda en 'fabricante'
                        modelo = fila[1].strip()     # Se guarda en 'modelo'
                        capacidad = fila[2].strip()  # Se guarda en 'kva'
                        
                        # Insertamos asumiendo voltajes estándar (220V) si no se especifican
                        conn.execute('''
                            INSERT OR IGNORE INTO ups_catalogo (fabricante, modelo, kva, v_entrada, v_salida)
                            VALUES (?, ?, ?, 220, 220)
                        ''', (marca, modelo, capacidad))
                        
                        filas_insertadas += 1
                    except Exception as e:
                        logs.append(f"❌ Error en fila {fila}: {e}")
                        errores += 1
            conn.commit()
            return {'status': 'ok', 'insertados': filas_insertadas, 'errores': errores, 'logs': logs}
        except Exception as e:
            return {'status': 'error', 'msg': str(e), 'logs': logs}
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

    # --- RESTO DE MÉTODOS (UPS Y PROYECTOS) IGUAL QUE ANTES ---
    def agregar_ups(self, datos):
        conn = self._conectar()
        try:
            conn.execute('''
                INSERT INTO ups_catalogo (fabricante, modelo, kva, v_entrada, v_salida)
                VALUES (?, ?, ?, ?, ?)
            ''', (datos['fabricante'], datos['modelo'], datos['kva'], datos['v_in'], datos['v_out']))
            conn.commit()
        except:
            pass
        finally:
            conn.close()

    def obtener_ups_todos(self):
        conn = self._conectar()
        res = conn.execute("SELECT * FROM ups_catalogo ORDER BY fabricante").fetchall()
        conn.close()
        return [dict(row) for row in res]
        
    def obtener_ups_id(self, id_ups):
        conn = self._conectar()
        row = conn.execute("SELECT * FROM ups_catalogo WHERE id = ?", (id_ups,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def eliminar_ups(self, id_ups):
        conn = self._conectar()
        conn.execute("DELETE FROM ups_catalogo WHERE id = ?", (id_ups,))
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
                datos_calculados['modelo_nombre'],
                datos_calculados['kva'],
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
            LEFT JOIN ups_catalogo m ON m.modelo = p.modelo_snap
            WHERE p.pedido = ?
        ''', (pedido,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None