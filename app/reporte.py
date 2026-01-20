import os
import tempfile
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
COLOR_VERDE = (0, 100, 0)         

class ReportePDF(FPDF):
    """
    Generador Modular de Reportes.
    """
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation=orientation, unit=unit, format=format, font_cache_dir=None)
        self.section_counter = 1

    def header(self):
        # 1. LOGO
        directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio, 'static', 'logo.png')

        try:
            if os.path.exists(ruta_logo):
                self.image(ruta_logo, 10, 10, 33) 
            else:
                self.set_fill_color(*COLOR_ROJO)
                self.rect(10, 10, 33, 15, 'F')
        except:
            pass

        # 2. ENCABEZADO
        self.set_y(10)
        self.set_x(50) 
        self.set_font('Arial', 'B', 16)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 8, 'GUIA DE INSTALACION Y MEMORIA TECNICA', 0, 1, 'L') 
        
        self.set_x(50)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_GRIS_CLARO)
        self.cell(0, 5, 'SISTEMA DE ENERGIA ININTERRUMPIDA (UPS) - BAJA TENSION', 0, 1, 'L')
        
        self.ln(4)
        self.set_draw_color(*COLOR_ROJO)
        self.set_line_width(0.4)
        self.line(10, 28, 200, 28)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(*COLOR_GRIS_CLARO)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        texto = f"Documento generado el {fecha} | Cumplimiento NOM-001-SEDE-2012 | Pagina {self.page_no()}"
        self.cell(0, 10, texto, 0, 0, 'C')

    # ==========================================================================
    # EL DIRECTOR DE ORQUESTA
    # ==========================================================================
    def generar_cuerpo(self, datos, res, es_publicado=False, ups=None, bateria=None):
        
        # Portada
        self.add_page()
        self._hoja_portada(datos, res, ups)
        
        # HOJA 1
        self.add_page()
        if not es_publicado:
            self.set_font('Arial', 'B', 40) # Bajé un poco la fuente para que quepa mejor
            self.set_text_color(230, 230, 230) # Más clarito para que no estorbe
            self.set_xy(10, 100)
            self.cell(0, 10, "VISTA PREVIA - BORRADOR", 0, 0, 'C')
            self.set_xy(10, 120)
            self.cell(0, 10, "NO VALIDO PARA INSTALACION", 0, 0, 'C')
            
            # Restauramos color normal
            self.set_text_color(*COLOR_NEGRO)
            self.set_y(40) 
        self._hoja_1_seguridad_instalacion()
        
        # HOJA 2
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._hoja_2_datos_sitio(datos)
        
        # HOJA 3
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._hoja_3_ingenieria(datos, res)
        
        # Baterias
        if res.get('baterias_total'):
            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_baterias(bateria, res)

            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_fotografia("CONEXION DE BATERIAS", ups.get('imagen_baterias_url'))

        # Notas de Instalación
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_notas_instalacion(ups)

        # Diagrama de Conexión
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._hoja_4_diagrama(ups)

        # Fotografias Adicionales
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_fotografia("VISTA GENERAL DEL SISTEMA", ups.get('imagen_general_url'))

        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_fotografia("PLANO DE UBICACION DEL EQUIPO", ups.get('imagen_plano_url'))

        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_fotografia("VENTILACION Y AREA DE TRABAJO", ups.get('imagen_ventilacion_url'))

        return self.output()

    # ==========================================================================
    # HOJA PORTADA
    # ==========================================================================
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
        self._fila_portada("EQUIPO:", res.get('modelo_nombre', 'S/D'))
        self._fila_portada("CAPACIDAD:", f"{datos.get('kva', 'S/D')} kVA")
        self._fila_portada("FECHA:", datetime.now().strftime("%d/%m/%Y"))

    def _fila_portada(self, label, value):
        self.set_x(45); self.set_font('Arial', 'B', 11); self.cell(40, 10, label, 0, 0, 'L')
        self.set_font('Arial', '', 11); self.multi_cell(90, 10, str(value), 0, 'L')

    # ==========================================================================
    # HOJA 1: NORMAS Y SEGURIDAD
    # ==========================================================================
    def _hoja_1_seguridad_instalacion(self):
        self._titulo_seccion("NORMAS DE SEGURIDAD")
        
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        
        intro = (
            "Con esta documentacion, LBS le ofrece toda la informacion necesaria sobre la correcta instalacion del UPS."
            "Antes de instalar o manejar el UPS lea esta GUIA, asi mismo recomendamos que lo guarde para una futura consulta."
        )
        self.multi_cell(0, 5, intro)
        self.ln(3)

        # Advertencia Principal
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO) 
        self.multi_cell(0, 5, "Solo el personal instruido y autorizado debe llevar a cabo la puesta en marcha, uso y mantenimiento del UPS.")
        self.ln(3)

        # SUBSECCIÓN: IMPORTANTES NORMAS
        self._subtitulo_rojo("IMPORTANTES NORMAS DE SEGURIDAD")
        normas = [
            "Mover el UPS en posicion vertical en su embalaje original hasta su destino final.",
            "Para levantar los armarios, usar una carretilla elevadora o cintas apropiadas.",
            "Comprobar la suficiente capacidad del suelo y del ascensor.",
            "Comprobar la integridad del equipo cuidadosamente.",
            "Si observa algun daño, no instalar o arrancar el UPS y contactar con el Centro de Servicio mas cercano inmediatamente."
        ]
        self._imprimir_lista_bullets(normas)
        self.ln(4)

        # SUBSECCIÓN: ALMACENAMIENTO
        self._subtitulo_rojo("ALMACENAMIENTO")
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        texto_almacen = (
            "Almacenar el UPS en un lugar seco, la temperatura debe estar entre -25 C y +30 C.\n"
            "Si la unidad esta almacenada por un periodo mayor a 3 meses, la bateria debe recargarse periodicamente "
            "(el tiempo depende de la temperatura del almacen)."
        )
        self.multi_cell(0, 5, texto_almacen)
        self.ln(4)

        # SUBSECCIÓN: INSTALACION
        self._subtitulo_rojo("INSTALACION")
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        textos_instalacion = [
            "La conexion de alimentacion del UPS y salida hacia la carga, debe ser realizada como mas adelante se indica por un electricista calificado.",
            "La puesta en marcha debe ser realizada por personal adecuadamente entrenado (LBS).",
            "Si se han quitado los paneles del armario, al momento de colocarlos comprobar que todas las puestas a tierra o conexiones de tierra esten correctamente conectadas."
        ]
        for t in textos_instalacion:
            self.multi_cell(0, 5, t)
            self.ln(2)
        self.ln(4)

        # SUBSECCIÓN: CORRIENTES A TIERRA
        self._subtitulo_rojo("CORRIENTES DE DESCARGA A TIERRA")
        puntos_tierra = [
            "La conexion a tierra es fundamental antes de conectar la tension de entrada.",
            "No instalar el UPS en un ambiente excesivamente humedo o cerca de agua.",
            "No derramar liquidos o dejar objetos extranios dentro del UPS.",
            "La unidad debe ser colocada en un area bien ventilada; la temperatura ambiente no debe exceder los 25 C.",
            "Un tiempo de vida optimo de la bateria solo se obtiene si la temperatura no excede 25 C.",
            "Es importante que el aire se pueda mover libremente a traves de la unidad.",
            "No bloquear las rejillas de ventilacion.",
            "Evitar ubicaciones en exposicion al sol o a fuentes de calor."
        ]
        self._imprimir_lista_bullets(puntos_tierra)
        
    # ==========================================================================
    # HOJA 2: DATOS DEL SITIO
    # ==========================================================================
    def _hoja_2_datos_sitio(self, datos):
        self._titulo_seccion("DATOS DEL SITIO DE INSTALACION")

        self.set_fill_color(*COLOR_FONDO)
        self.set_font('Arial', '', 9)
        
        y_inicio = self.get_y()
        self.rect(10, y_inicio, 190, 30, 'F')
        
        col1 = 12
        col2 = 110
        
        nombre_completo = str(datos.get('nombre', 'SIN NOMBRE')).upper()
        
        # COLUMNA IZQUIERDA
        self.set_xy(col1, y_inicio + 3)
        self.cell(90, 6, f"Proyecto / Cliente:  {nombre_completo}", 0, 1)
        self.set_xy(col1, y_inicio + 9)
        self.cell(90, 6, f"Capacidad UPS:       {datos.get('kva')} kVA", 0, 1)
        self.set_xy(col1, y_inicio + 15)
        self.cell(90, 6, f"Voltaje Operacion:   {datos.get('voltaje')} VCA", 0, 1)

        # COLUMNA DERECHA
        self.set_xy(col2, y_inicio + 3)
        self.cell(90, 6, f"Configuracion:       {datos.get('fases')} Fases + N + Tierra", 0, 1)
        self.set_xy(col2, y_inicio + 9)
        self.cell(90, 6, f"Longitud Circuito:   {datos.get('longitud')} metros", 0, 1)
        self.set_xy(col2, y_inicio + 15)
        self.cell(90, 6, f"Ubicacion:           {datos.get('lat')}, {datos.get('lon')}", 0, 1)
        
        self.set_y(y_inicio + 35)

        self._subtitulo_rojo("CROQUIS DE UBICACION")
        
        y_before = self.get_y()
        if y_before > 180:
            self.add_page()
            y_before = self.get_y()

        map_generated = False
        
        if datos.get('lat') and datos.get('lon'):
            try:
                lat = str(datos['lat']).strip()
                lon = str(datos['lon']).strip()
                
                # Validar coordenadas
                lat_float = float(lat)
                lon_float = float(lon)
                
                print(f"Intentando generar mapa para: {lat}, {lon}")
                
                # Lista de servicios de mapas (intentar en orden)
                map_urls = [
                    # Usar un servicio de mapas estáticos más confiable y sin API Key
                    f"https://static-map.openstreetmap.de/staticmap.php?center={lat},{lon}&zoom=14&size=600x400&maptype=mapnik&markers={lat},{lon},red-pushpin"
                ]
                
                for idx, url_mapa in enumerate(map_urls):
                    try:
                        print(f"Intentando servicio {idx + 1}...")
                        
                        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                            map_filename = tmp_file.name
                        
                        # Headers más completos
                        req = urllib.request.Request(url_mapa)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                        req.add_header('Accept', 'image/png,image/*;q=0.8,*/*;q=0.5')
                        req.add_header('Accept-Language', 'es-MX,es;q=0.9,en;q=0.8')
                        
                        # Descargar con timeout
                        with urllib.request.urlopen(req, timeout=10) as response:
                            with open(map_filename, 'wb') as out_file:
                                out_file.write(response.read())
                        
                        # Verificar que se descargó correctamente
                        if os.path.exists(map_filename) and os.path.getsize(map_filename) > 1000:  # Al menos 1KB
                            print(f"Mapa descargado exitosamente con servicio {idx + 1}")
                            self.image(map_filename, x=20, y=y_before, w=170, h=100)
                            self.set_y(y_before + 105)
                            map_generated = True
                            
                            try:
                                os.remove(map_filename)
                            except:
                                pass
                            
                            break  # Salir del loop si fue exitoso
                        else:
                            print(f"Archivo muy pequeño o vacío con servicio {idx + 1}")
                            try:
                                os.remove(map_filename)
                            except:
                                pass
                            
                    except Exception as e:
                        print(f"Error con servicio {idx + 1}: {e}")
                        try:
                            if 'map_filename' in locals():
                                os.remove(map_filename)
                        except:
                            pass
                        continue
                        
            except Exception as e:
                print(f"Error general al generar mapa: {e}")
                import traceback
                traceback.print_exc()
        
        # Si no se generó, mostrar placeholder
        if not map_generated:
            print("No se pudo generar el mapa, mostrando placeholder")
            self.set_fill_color(40, 40, 40)
            self.rect(x=20, y=y_before, w=170, h=100, style='F')
            
            # Agregar coordenadas en el placeholder
            self.set_y(y_before + 45)
            self.set_font('Arial', 'B', 11)
            self.set_text_color(200, 200, 200)
            self.cell(0, 5, f"COORDENADAS: {datos.get('lat')}, {datos.get('lon')}", 0, 1, 'C')
            
            self.set_y(y_before + 105)
            self.set_font('Arial', 'I', 9)
            self.set_text_color(*COLOR_GRIS_CLARO)
            self.cell(0, 5, "(No fue posible generar el croquis de la ubicacion)", 0, 1, 'C')
            self.set_text_color(*COLOR_NEGRO)
        
        
          # ==========================================================================
    # HOJA 3: INGENIERÍA
    # ==========================================================================
    def _hoja_3_ingenieria(self, datos, res):
        self._titulo_seccion("ESPECIFICACIONES DE INSTALACION ELECTRICA")

        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        norma_txt = (
            "Para la puesta en marcha deben existir las condiciones electricas adecuadas. "
            "Utilizar conductores de cobre, aislamiento tipo THHN/THWN-2 a 75 C / 90 C. "
            "Dimensionamiento basado estrictamente en la NOM-001-SEDE-2012."
        )
        self.multi_cell(0, 5, norma_txt)
        self.ln(5)

        # TABLA 1: PROTECCIONES
        self._dibujar_encabezado_tabla(["ELEMENTO / PARAMETRO", "ESPECIFICACION TECNICA", "DETALLE NOM"])
        self._dibujar_fila_tabla("Corriente de Disenio (+25%)", f"{res['i_diseno']} Amperes", f"Base: {res['i_nom']} A (In)")
        polos = datos.get('fases')
        self._dibujar_fila_tabla("Proteccion Principal (Breaker)", f"{res['breaker_sel']} Amperes", f"Termomagnetico {polos} Polos")
        self.ln(5)

        # TABLA 2: CABLEADO
        self._dibujar_encabezado_tabla(["CONDUCTOR", "CALIBRE SUGERIDO", "TIPO MATERIAL"])
        self._dibujar_fila_tabla("Fases (L1, L2, L3)", f"{res['fase_sel']} AWG/kcmil", "Cobre THHN/THWN-2")
        self._dibujar_fila_tabla("Neutro (N)", f"{res['fase_sel']} AWG/kcmil", "Cobre (No reducir)")
        self._dibujar_fila_tabla("Tierra Fisica (GND/PE)", f"{res['gnd_sel']} AWG", "Cobre Desnudo / Verde")
        self.ln(5)

        # VALIDACIÓN
        # ANÁLISIS DE INGENIERÍA
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(0, 8, "ANÁLISIS DE INGENIERÍA:", 0, 1)
        self.set_font('Arial', '', 9)
        self.ln(2)
        
        # Análisis de Caída de Tensión
        dv_pct = res.get('dv_pct', 0)
        self.set_font('Arial', 'B', 9)
        self.cell(0, 5, "  - Caida de Tension:", 0, 1)
        self.set_font('Arial', '', 9)
        self.set_x(self.l_margin + 5)
        self.multi_cell(0, 5, f"El calculo arroja una caida de tension de {dv_pct}%.")
        self.set_x(self.l_margin + 5)
        if dv_pct <= 3.0:
            self.set_text_color(*COLOR_VERDE)
            self.multi_cell(0, 5, "Este valor es OPTIMO y se encuentra dentro de los limites recomendados por la norma (<3%), asegurando que el equipo y la carga operaran con un voltaje adecuado.")
        else:
            self.set_text_color(*COLOR_ALERTA)
            self.multi_cell(0, 5, "ALERTA: Este valor excede el limite recomendado por la norma (>3%). Se recomienda utilizar un calibre de conductor superior para mitigar riesgos de sobrecalentamiento y asegurar el correcto funcionamiento de la carga.")
        self.set_text_color(*COLOR_NEGRO)
        self.ln(3)

        # Análisis de Ampacidad
        i_real = res.get('i_real_cable', 0)
        i_diseno = res.get('i_diseno', 0)
        self.set_font('Arial', 'B', 9)
        self.cell(0, 5, "  - Ampacidad del Conductor:", 0, 1)
        self.set_font('Arial', '', 9)
        self.set_x(self.l_margin + 5)
        self.multi_cell(0, 5, f"El conductor seleccionado (calibre {res.get('fase_sel', 'S/D')} AWG) tiene una ampacidad real de {i_real} A, considerando factores de agrupamiento y temperatura.")
        self.set_x(self.l_margin + 5)
        if i_real > i_diseno:
            self.set_text_color(*COLOR_VERDE)
            self.multi_cell(0, 5, f"Esta capacidad es SUFICIENTE para la corriente de disenio de {i_diseno} A, garantizando una operacion segura y sin sobrecalentamiento del cableado.")
        else:
            self.set_text_color(*COLOR_ALERTA)
            self.multi_cell(0, 5, f"ALERTA: La capacidad del conductor ({i_real} A) es MENOR a la corriente de disenio ({i_diseno} A). Se requiere un conductor de mayor calibre para cumplir con la norma y evitar fallas criticas.")
        self.set_text_color(*COLOR_NEGRO)
        self.ln(3)

        if res.get('nota_altitud'):
            self.ln(2)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ALERTA)
            nota = res['nota_altitud'].replace("⚠️", "!!").encode('latin-1', 'replace').decode('latin-1')
            self.multi_cell(0, 5, f"NOTA IMPORTANTE: {nota}")
        self.ln(5)

    # ==========================================================================
    # SECCIÓN BATERÍAS
    # ==========================================================================
    def _seccion_baterias(self, bateria, res):
        self._titulo_seccion("BANCO DE BATERIAS")
        
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        
        if not res.get('baterias_total'):
            self.multi_cell(0, 5, "No se realizaron calculos para el banco de baterias.")
            return
            
        self.ln(5)
        self._subtitulo_rojo("BATERIA SELECCIONADA")
        self._dibujar_encabezado_tabla(["MODELO / FABRICANTE", "VOLTAJE NOMINAL", "CAPACIDAD"])
        self._dibujar_fila_tabla(f"{bateria.get('modelo', 'S/D')} / {bateria.get('fabricante', 'S/D')}", f"{bateria.get('voltaje_nominal', 'S/D')} V", f"{bateria.get('capacidad_ah', 'S/D')} Ah")

        self.ln(5)

        self._subtitulo_rojo("CONFIGURACION CALCULADA")
        self._dibujar_encabezado_tabla(["PARAMETRO", "VALOR", "DESCRIPCION"])
        self._dibujar_fila_tabla("Tiempo de Respaldo Calculado", f"{res.get('autonomia_calculada_min', 'S/D')} min", f"Objetivo: {res.get('autonomia_deseada_min', 'S/D')} min")
        self._dibujar_fila_tabla("Total de Baterias", f"{res.get('baterias_total', 'S/D')} pzas", f"{res.get('numero_strings', 'S/D')} arreglo(s) en paralelo")
        self._dibujar_fila_tabla("Baterias por Arreglo", f"{res.get('baterias_por_string', 'S/D')} pzas", "En serie para alcanzar el voltaje DC del UPS")

        self.ln(5)

        if res.get('bat_error'):
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ALERTA)
            self.multi_cell(0, 5, f"NOTA: {res.get('bat_error')}")

    # ==========================================================================
    # SECCIÓN NOTAS DE INSTALACION
    # ==========================================================================
    def _seccion_notas_instalacion(self, ups=None):
        self._titulo_seccion("NOTAS IMPORTANTES DE INSTALACION")
        
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, "Nota: Tenga en cuenta que, para facilitar la operacion y el mantenimiento, el espacio en la parte delantera y trasera del gabinete debe dejarse al menos 800 mm y 800 mm respectivamente al instalar el gabinete.")
        self.ln(5)

        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "Esquema de Espacios Mínimos:", 0, 1)

        draw_placeholder = True
        if ups and ups.get('imagen_instalacion_url'):
            img_filename = os.path.basename(ups['imagen_instalacion_url'])
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
            
            if os.path.exists(ruta_imagen):
                try:
                    self.image(ruta_imagen, x=45, w=120) 
                    draw_placeholder = False
                except Exception as e:
                    print(f"Error cargando imagen de instalacion: {e}")
        
        if draw_placeholder:
            y = self.get_y()
            self.set_fill_color(230, 230, 230)
            self.rect(45, y, 120, 80, 'F')
            self.set_xy(45, y + 35)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(150, 150, 150)
            self.cell(120, 10, "[ IMAGEN NOTAS 1 ]", 0, 0, 'C')
            self.set_text_color(*COLOR_NEGRO)

    # ==========================================================================
    # HOJA 4: DIAGRAMA
    # ==========================================================================
    def _hoja_4_diagrama(self, ups=None):
        self._titulo_seccion("DIAGRAMA DE CONEXION SUGERIDO")
        
        # Main Diagram Placeholder
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "Diagrama Unifilar AC:", 0, 1)
        self.set_fill_color(230, 230, 230)
        y = self.get_y()
        self.rect(10, y, 190, 80, 'F')
        self.set_xy(10, y + 35)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(150, 150, 150) 
        self.cell(190, 10, "[ ESPACIO PARA DIAGRAMA UNIFILAR AC ]", 0, 0, 'C')
        self.set_y(y + 85)
        self.ln(5)

        # Battery Connection Diagram
        self.set_text_color(*COLOR_NEGRO)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "Diagrama de Conexión de Baterías DC:", 0, 1)
        
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, "En el siguiente diagrama se muestra la manera recomendada de conexion de baterias en serie asi como la conexion del interruptor de DC.")
        self.ln(3)

        draw_placeholder = True
        if ups and ups.get('imagen_baterias_url'):
            img_filename = os.path.basename(ups['imagen_baterias_url'])
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
            
            if os.path.exists(ruta_imagen):
                try:
                    self.image(ruta_imagen, x=45, w=120) 
                    draw_placeholder = False
                except Exception as e:
                    print(f"Error cargando imagen de conexion de baterias: {e}")
        
        if draw_placeholder:
            y = self.get_y()
            self.set_fill_color(230, 230, 230)
            self.rect(45, y, 120, 80, 'F')
            self.set_xy(45, y + 35)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(150, 150, 150)
            self.cell(120, 10, "[ IMAGEN CONEXION BATERIAS ]", 0, 0, 'C')
            self.set_text_color(*COLOR_NEGRO)

    def _seccion_fotografia(self, titulo, imagen_url=None):
        self._titulo_seccion(titulo)
        
        draw_placeholder = True
        if imagen_url:
            img_filename = os.path.basename(imagen_url)
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
            
            if os.path.exists(ruta_imagen):
                try:
                    self.image(ruta_imagen, x=45, w=120) 
                    draw_placeholder = False
                except Exception as e:
                    print(f"Error cargando imagen de seccion '{titulo}': {e}")

        if draw_placeholder:
            y = self.get_y()
            self.set_fill_color(230, 230, 230)
            self.rect(45, y, 120, 80, 'F')
            self.set_xy(45, y + 35)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(150, 150, 150)
            self.cell(120, 10, f"[ FOTOGRAFIA: {titulo.upper()} ]", 0, 0, 'C')
            self.set_text_color(*COLOR_NEGRO)

    def _marca_agua_preview(self):
        self.set_font('Arial', 'B', 40)
        self.set_text_color(230, 230, 230)
        self.set_xy(10, 100)
        self.cell(0, 10, "VISTA PREVIA", 0, 0, 'C')
        self.set_text_color(*COLOR_NEGRO)
        self.set_y(40)

    # ==========================================================================
    # HERRAMIENTAS REUTILIZABLES (HELPERS)
    # ==========================================================================
    def _titulo_seccion(self, texto):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 8, f"{self.section_counter}. {texto.upper()}", 0, 1, 'L')
        self.section_counter += 1
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def _subtitulo_rojo(self, texto):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, texto, 0, 1)

    def _imprimir_lista_bullets(self, items):
        ancho_pagina = 190
        ancho_bullet = 5
        ancho_texto = ancho_pagina - ancho_bullet
        
        for item in items:
            self.set_text_color(*COLOR_ROJO)
            self.set_font('Arial', 'B', 10)
            self.cell(ancho_bullet, 5, "-", 0, 0) # Guion seguro
            
            self.set_text_color(*COLOR_NEGRO)
            self.set_font('Arial', '', 9)
            self.multi_cell(ancho_texto, 5, item)
            self.ln(1)

    def _dibujar_encabezado_tabla(self, columnas):
        self.set_fill_color(*COLOR_GRIS)
        self.set_text_color(255, 255, 255) 
        self.set_font('Arial', 'B', 8)
        self.cell(60, 7, columnas[0], 0, 0, 'C', True)
        self.cell(65, 7, columnas[1], 0, 0, 'C', True)
        self.cell(65, 7, columnas[2], 0, 1, 'C', True)

    def _dibujar_fila_tabla(self, c1, c2, c3):
        self.set_text_color(*COLOR_NEGRO)
        self.set_font('Arial', '', 9)
        self.set_draw_color(220, 220, 220) 
        self.cell(60, 7, c1, 1, 0, 'L')
        self.set_font('Arial', 'B', 9) 
        self.cell(65, 7, c2, 1, 0, 'C')
        self.set_font('Arial', '', 8) 
        self.cell(65, 7, c3, 1, 1, 'C')