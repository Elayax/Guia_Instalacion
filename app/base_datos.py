import sqlite3
import os
from datetime import datetime

class GestorDB:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, 'sistema_ups_master.db') # Nuevo nombre
        self._inicializar_tablas()

    def _conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _inicializar_tablas(self):
        conn = self._conectar()
        cursor = conn.cursor()
        
        # 1. TABLA CLIENTES [Cliente, Sucursal, Direccion, Maps, Coordenadas]
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                sucursal TEXT NOT NULL,
                direccion TEXT,
                link_maps TEXT,
                lat TEXT,
                lon TEXT,
                UNIQUE(cliente, sucursal) -- Evita duplicados exactos
            )
        ''')

        # 2. TABLA UPS [Fabricante, Modelo, Potencia, V_In, V_Out]
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

        # 3. TABLA FINAL PROYECTOS [Pedido, Modelo, Potencia, Cliente, Sucursal, Cables...]
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proyectos_publicados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido TEXT UNIQUE NOT NULL,
                fecha_publicacion TEXT,
                modelo_snap TEXT,      -- Guardamos copia por si borras el modelo original
                potencia_snap REAL,
                cliente_snap TEXT,
                sucursal_snap TEXT,
                calibre_fases TEXT,
                config_salida TEXT,    -- Ej: "3F+N+T"
                calibre_tierra TEXT
            )
        ''')
        conn.commit()
        conn.close()

    # --- GESTIÓN DE CLIENTES ---
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

    # --- GESTIÓN DE UPS ---
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

    # --- PUBLICACIÓN FINAL ---
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
                datos_calculados['modelo_nombre'], # Snapshot del modelo
                datos_calculados['kva'],
                form_data['cliente_nombre'],       # Snapshot del cliente
                form_data['sucursal_nombre'],
                datos_calculados['fase_sel'],      # Calibre Fases
                f"{form_data['fases']}F + N + GND",# Configuración
                datos_calculados['gnd_sel']        # Calibre Tierra
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # El pedido ya existe
        finally:
            conn.close()
            
    def obtener_proyectos(self):
        conn = self._conectar()
        res = conn.execute("SELECT * FROM proyectos_publicados ORDER BY id DESC").fetchall()
        conn.close()
        return [dict(row) for row in res]
    

    def obtener_proyecto_por_pedido(self, pedido):
        """Busca un proyecto completo dado su número de pedido"""
        conn = self._conectar()
        # Hacemos un JOIN para traer también los datos del modelo original si existe
        cursor = conn.execute('''
            SELECT p.*, m.id as modelo_id_real 
            FROM proyectos_publicados p
            LEFT JOIN ups_catalogo m ON m.modelo = p.modelo_snap
            WHERE p.pedido = ?
        ''', (pedido,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ... (métodos anteriores) ...

    def obtener_clientes_unicos(self):
        """Devuelve solo la lista de nombres de clientes (sin repetir)"""
        conn = self._conectar()
        cursor = conn.execute("SELECT DISTINCT cliente FROM clientes ORDER BY cliente")
        resultados = [row[0] for row in cursor.fetchall()]
        conn.close()
        return resultados

    def obtener_sucursales_por_cliente(self, nombre_cliente):
        """Devuelve las sucursales y datos de un cliente específico"""
        conn = self._conectar()
        cursor = conn.execute("SELECT * FROM clientes WHERE cliente = ? ORDER BY sucursal", (nombre_cliente,))
        resultados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return resultados