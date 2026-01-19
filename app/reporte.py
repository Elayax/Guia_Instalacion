import os
import urllib.request
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE COLORES ---
COLOR_ROJO = (180, 20, 20)      
COLOR_GRIS = (60, 60, 60)       
COLOR_NEGRO = (40, 40, 40) 
COLOR_GRIS_CLARO = (100, 100, 100) 
COLOR_FONDO = (245, 245, 245)  
COLOR_ALERTA = (200, 50, 50)         

class ReportePDF(FPDF):
    def header(self):
        directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio, 'static', 'logo.png')
        if os.path.exists(ruta_logo):
            self.image(ruta_logo, 10, 10, 33)
        self.set_y(10); self.set_x(50)
        self.set_font('Arial', 'B', 16); self.set_text_color(*COLOR_ROJO)
        self.cell(0, 8, 'GUIA DE INSTALACION Y MEMORIA TECNICA', 0, 1, 'L')
        self.set_x(50); self.set_font('Arial', 'B', 10); self.set_text_color(*COLOR_GRIS_CLARO)
        self.cell(0, 5, 'SISTEMA DE ENERGIA ININTERRUMPIDA (UPS)', 0, 1, 'L')
        self.ln(4); self.set_draw_color(*COLOR_ROJO); self.set_line_width(0.4)
        self.line(10, 28, 200, 28); self.ln(10)

    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 7); self.set_text_color(*COLOR_GRIS_CLARO)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 10, f"Documento generado el {fecha} | Pagina {self.page_no()}", 0, 0, 'C')

    def generar_cuerpo(self, datos, res, ups=None, bateria=None, curvas=None, es_publicado=False):
        self.add_page()
        self._hoja_portada(datos, res, ups)
        self.add_page()
        if not es_publicado: self._marca_agua_simple("VISTA PREVIA - BORRADOR\nNO VALIDO PARA INSTALACION")
        self._hoja_1_seguridad_instalacion()
        self.add_page()
        if not es_publicado: self._marca_agua_simple()
        self._hoja_2_datos_sitio(datos, res, ups)
        self.add_page()
        if not es_publicado: self._marca_agua_simple()
        self._hoja_3_ingenieria(datos, res)
        self.ln(5)
        if res.get('bat_total'):
            self._seccion_baterias(bateria, res)
        self.add_page()
        if not es_publicado: self._marca_agua_simple()
        self._hoja_4_diagrama()
        return self.output(dest='S').encode('latin-1')

    def _marca_agua_simple(self, texto="VISTA PREVIA"):
        self.set_font('Arial', 'B', 50); self.set_text_color(235, 235, 235)
        self.rotate(45, 50, 150)
        self.text(50, 150, texto)
        self.rotate(0)
        self.set_text_color(*COLOR_NEGRO)

    def _hoja_portada(self, datos, res, ups=None):
        self.ln(20)
        
        y_pos_after_image = self.get_y() + 85
        
        draw_black_box = True
        
        if ups and ups.get('imagen_url'):
            img_filename = os.path.basename(ups['imagen_url'])
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
            
            if os.path.exists(ruta_imagen):
                try:
                    self.image(ruta_imagen, x=65, y=40, w=80)
                    draw_black_box = False
                except Exception:
                    pass

        if draw_black_box:
            self.set_fill_color(0, 0, 0)
            self.rect(x=65, y=40, w=80, h=60, style='F')

        self.set_y(y_pos_after_image)

        self.set_font('Arial', 'B', 24); self.set_text_color(*COLOR_ROJO)
        self.cell(0, 12, "MEMORIA TECNICA", 0, 1, 'C')
        self.cell(0, 12, "DE INSTALACION UPS", 0, 1, 'C')
        self.ln(20)
        self.set_font('Arial', '', 12); self.set_text_color(*COLOR_NEGRO)
        self.set_fill_color(245, 245, 245)
        self.rect(35, self.get_y() + 5, 140, 55, 'F')
        self.set_y(self.get_y() + 10)
        self._fila_portada("PROYECTO:", datos.get('nombre', 'S/D'))
        self._fila_portada("UBICACION:", f"{datos.get('lat', '')}, {datos.get('lon', '')}")
        self._fila_portada("EQUIPO:", res.get('modelo_nombre', 'S/D'))
        self._fila_portada("CAPACIDAD:", f"{res.get('kva', 'S/D')} kVA")
        self._fila_portada("FECHA:", datetime.now().strftime("%d/%m/%Y"))

    def _fila_portada(self, label, value):
        self.set_x(45); self.set_font('Arial', 'B', 11); self.cell(40, 10, label, 0, 0, 'L')
        self.set_font('Arial', '', 11); self.multi_cell(90, 10, str(value), 0, 'L')

    def _hoja_1_seguridad_instalacion(self):
        pass # Contenido estático

    def _hoja_2_datos_sitio(self, datos, res, ups=None):
        self._titulo_seccion("2. DATOS DEL SITIO DE INSTALACION")
        # ... tabla de datos
        self._subtitulo_rojo("CROQUIS DE UBICACION")
        
        y_before = self.get_y()
        if y_before > 180:
            self.add_page()
            y_before = self.get_y()

        map_generated = False
        if datos.get('lat') and datos.get('lon'):
            try:
                url_mapa = f"https://static-map.openstreetmap.de/staticmap.php?center={datos['lat']},{datos['lon']}&zoom=15&size=500x300&maptype=mapnik"
                map_filename = os.path.join(os.path.dirname(__file__), "temp_map.png")
                
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(url_mapa, map_filename)

                self.image(map_filename, w=170)
                os.remove(map_filename)
                map_generated = True
            except Exception:
                pass
        
        if not map_generated:
            self.set_fill_color(0, 0, 0)
            self.rect(x=self.get_x(), y=y_before, w=170, h=100, style='F')
            self.set_y(y_before + 105)
            self.set_font('Arial', 'I', 9)
            self.set_text_color(*COLOR_GRIS_CLARO)
            self.cell(0, 5, "(No fue posible generar el croquis de la ubicacion)", 0, 1, 'C')
            self.set_text_color(*COLOR_NEGRO)

    def _hoja_3_ingenieria(self, datos, res):
        self._titulo_seccion("3. ESPECIFICACIONES DE INSTALACION")
        # ... tablas de ingeniería

    def _seccion_baterias(self, bateria, res):
        self._titulo_seccion("4. BANCO DE BATERIAS")
        # ... tabla de datos de batería
        if res.get('bat_total'):
            self._subtitulo_rojo("CONFIGURACION CALCULADA")
            # ... tabla de configuración
            self.ln(5)
            # ... texto de rendimiento
            if res.get('grafica_data'):
                if self.get_y() > 170: self.add_page()
                self._dibujar_grafico_rendimiento(res['grafica_data'])

    def _dibujar_grafico_rendimiento(self, data):
        self._subtitulo_rojo("GRAFICA DE RENDIMIENTO ESTIMADO")
        # ... código de dibujo del gráfico

    def _hoja_4_diagrama(self):
        self._titulo_seccion("5. DIAGRAMA DE CONEXION")
        # ... 
    
    def _titulo_seccion(self, texto): pass
    def _subtitulo_rojo(self, texto): pass
    def _dibujar_encabezado_tabla(self, c): pass
    def _dibujar_fila_tabla(self, c1, c2, c3): pass
