import os
from fpdf import FPDF
from datetime import datetime
from PIL import Image
import tempfile

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
    Soporte UTF-8 para caracteres especiales (ñ, á, é, í, ó, ú)
    """
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation=orientation, unit=unit, format=format, font_cache_dir=None)
        self.section_counter = 1

        # AGREGAR SOPORTE UTF-8 PARA Ñ Y ACENTOS
        # FPDF soporta Latin-1 (ISO-8859-1) que incluye caracteres españoles
        # Solo necesitamos asegurarnos de usar la codificación correcta

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
        self.cell(0, 8, 'GUÍA DE INSTALACIÓN Y MEMORIA TÉCNICA', 0, 1, 'L') 
        
        self.set_x(50)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_GRIS_CLARO)
        self.cell(0, 5, 'SISTEMA DE ENERGÍA ININTERRUMPIDA (UPS) - BAJA TENSIÓN', 0, 1, 'L')
        
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
        texto = f"Página {self.page_no()}"
        self.cell(0, 10, texto, 0, 0, 'C')

    # ==========================================================================
    # EL DIRECTOR DE ORQUESTA
    # ==========================================================================
    def _texto_utf8(self, texto):
        """Convierte texto UTF-8 a Latin-1 (ISO-8859-1) para FPDF con soporte para ñ y acentos"""
        if not texto:
            return ""
        try:
            # FPDF usa Latin-1 que soporta caracteres españoles
            return texto.encode('latin-1', 'replace').decode('latin-1')
        except:
            return texto

    def _preparar_imagen(self, ruta_imagen, ancho_mm=190, alto_mm=None):
        """
        Redimensiona y optimiza una imagen para el PDF
        - ruta_imagen: Path de la imagen original
        - ancho_mm: Ancho deseado en mm para el PDF
        - alto_mm: Alto deseado en mm (opcional, mantiene proporción si no se especifica)

        Retorna: Path de la imagen procesada (temporal)
        """
        try:
            # Abrir imagen original
            img = Image.open(ruta_imagen)

            # Convertir SVG o imágenes con canal alpha a RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # Crear fondo blanco
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Calcular tamaño objetivo en píxeles (300 DPI para calidad)
            dpi = 300
            ancho_px = int(ancho_mm * dpi / 25.4)

            if alto_mm:
                alto_px = int(alto_mm * dpi / 25.4)
                # Redimensionar exacto (puede distorsionar)
                img = img.resize((ancho_px, alto_px), Image.Resampling.LANCZOS)
            else:
                # Mantener proporción
                ratio = img.height / img.width
                alto_px = int(ancho_px * ratio)
                img = img.resize((ancho_px, alto_px), Image.Resampling.LANCZOS)

            # Guardar en archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG', quality=85, optimize=True)
            temp_file.close()

            return temp_file.name

        except Exception as e:
            print(f"Error preparando imagen {ruta_imagen}: {e}")
            return ruta_imagen  # Retornar original si falla

    def generar_cuerpo(self, datos, res, es_publicado=False, ups=None, bateria=None, imagenes_temp=None):

        # Almacenar imágenes temporales como atributo de la instancia
        self.imagenes_temp = imagenes_temp or {}

        # NO convertir datos ni res, dejar los valores originales
        # La conversión UTF-8 se hará solo cuando sea necesario en cell/multi_cell

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
            self.cell(0, 10, "NO VALIDO PARA INSTALACIÓN", 0, 0, 'C')

            # Restauramos color normal
            self.set_text_color(*COLOR_NEGRO)
            self.set_y(40)
        self._hoja_1_seguridad_instalacion()

        # HOJA 2 Y 3 COMBINADAS
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._hoja_2_datos_sitio(datos, ups)

        # Continuar con página 3 en la misma hoja (sin add_page)
        self.ln(8)  # Espacio entre secciones
        self._hoja_3_ingenieria(datos, res)

        # Baterias
        if res.get('baterias_total'):
            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_baterias(bateria, res)

            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_fotografia("CONEXIÓN DE BATERÍAS", ups.get('imagen_baterias_url'))

        # Notas de Instalación
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_notas_instalacion(ups)

        # Diagrama de Conexión
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._hoja_4_diagrama(ups)

        # Sección de Tipo de Ventilación
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_tipo_ventilacion(res.get('tipo_ventilacion'), res.get('tipo_ventilacion_data'))

        # Sección de Disposición de los Equipos
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_fotografia("DISPOSICIÓN DE LOS EQUIPOS", ups.get('imagen_layout_url'))

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
                    img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=80)
                    self.image(img_procesada, x=65, y=40, w=80)
                    draw_black_box = False
                    # Limpiar archivo temporal
                    if img_procesada != ruta_imagen:
                        try:
                            os.unlink(img_procesada)
                        except:
                            pass
                except Exception:
                    pass

        if draw_black_box:
            self.set_fill_color(0, 0, 0)
            self.rect(x=65, y=40, w=80, h=60, style='F')

        self.set_y(y_pos_after_image)

        self.set_font('Arial', 'B', 24); self.set_text_color(*COLOR_ROJO)
        self.cell(0, 12, "MEMORIA TÉCNICA", 0, 1, 'C')
        self.cell(0, 12, "DE INSTALACIÓN UPS", 0, 1, 'C')
        self.ln(20)
        self.set_font('Arial', '', 12); self.set_text_color(*COLOR_NEGRO)
        self.set_fill_color(245, 245, 245)
        self.rect(35, self.get_y() + 5, 140, 55, 'F')
        self.set_y(self.get_y() + 10)

        # DATOS CORREGIDOS - Usar los campos correctos del formulario
        proyecto_nombre = datos.get('cliente_texto', datos.get('nombre', 'S/D'))
        if datos.get('sucursal_texto'):
            proyecto_nombre = f"{proyecto_nombre} - {datos.get('sucursal_texto')}"

        equipo_nombre = ups.get('Nombre_del_Producto') if ups else res.get('modelo_nombre', 'S/D')
        capacidad_valor = ups.get('Capacidad_kVA') if ups else datos.get('kva', 'S/D')

        self._fila_portada("PROYECTO:", proyecto_nombre)
        self._fila_portada("EQUIPO:", equipo_nombre)
        self._fila_portada("CAPACIDAD:", f"{capacidad_valor} kVA")
        self._fila_portada("FECHA:", datetime.now().strftime("%d/%m/%Y"))

    def _fila_portada(self, label, value):
        self.set_x(45); self.set_font('Arial', '', 11); self.set_text_color(*COLOR_NEGRO); self.cell(40, 10, label, 0, 0, 'L')
        self.set_font('Arial', 'B', 11); self.set_text_color(*COLOR_ROJO); self.multi_cell(90, 10, str(value), 0, 'L')
        self.set_text_color(*COLOR_NEGRO)

    # ==========================================================================
    # HOJA 1: NORMAS Y SEGURIDAD
    # ==========================================================================
    def _hoja_1_seguridad_instalacion(self):
        self._titulo_seccion("NORMAS DE SEGURIDAD")
        
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        
        intro = (
            "Con esta documentación, LBS le ofrece toda la información necesaria sobre la correcta instalación del UPS."
            "Antes de instalar o manejar el UPS lea esta GUÍA, asimismo recomendamos que lo guarde para una futura consulta."
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
            "Mover el UPS en posición vertical en su embalaje original hasta su destino final.",
            "Para levantar los armarios, usar una carretilla elevadora o cintas apropiadas.",
            "Comprobar la suficiente capacidad del suelo y del ascensor.",
            "Comprobar la integridad del equipo cuidadosamente.",
            "Si observa algún daño, no instalar o arrancar el UPS y contactar con el Centro de Servicio más cercano inmediatamente."
        ]
        self._imprimir_lista_bullets(normas)
        self.ln(4)

        # SUBSECCIÓN: ALMACENAMIENTO
        self._subtitulo_rojo("ALMACENAMIENTO")
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        texto_almacen = (
            "Almacenar el UPS en un lugar seco, la temperatura debe estar entre -25 C y +30 C.\n"
            "Si la unidad está almacenada por un período mayor a 3 meses, la batería debe recargarse periódicamente "
            "(el tiempo depende de la temperatura del almacén)."
        )
        self.multi_cell(0, 5, texto_almacen)
        self.ln(4)

        # SUBSECCIÓN: INSTALACION
        self._subtitulo_rojo("INSTALACIÓN")
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        textos_instalacion = [
            "La conexión de alimentación del UPS y salida hacia la carga, debe ser realizada como más adelante se indica por un técnico electricista calificado.",
            "La puesta en marcha debe ser realizada por personal adecuadamente entrenado por LBS.",
            "Si se han quitado los paneles del armario, al momento de colocarlos comprobar que todas las puestas a tierra o conexiones de tierra esten correctamente conectadas."
        ]
        for t in textos_instalacion:
            self.multi_cell(0, 5, t)
            self.ln(2)
        self.ln(4)

        # SUBSECCIÓN: CORRIENTES A TIERRA
        self._subtitulo_rojo("CORRIENTES DE DESCARGA A TIERRA")
        puntos_tierra = [
            "La conexión a tierra es fundamental antes de conectar la tensión de entrada.",
            "No instalar el UPS en un ambiente húmedo o cerca de agua.",
            "No derramar líquidos o dejar objetos extraños dentro del UPS.",
            "La unidad debe ser colocada en un área bien ventilada; la temperatura ambiente no debe exceder los 25 °C.",
            "Un tiempo de vida óptimo de la batería solo se obtiene si la temperatura no excede 25 °C.",
            "Es importante que el aire se pueda mover libremente a través de la unidad.",
            "No bloquear las rejillas de ventilación.",
            "Evitar ubicaciones en exposición al sol y fuentes de calor."
        ]
        self._imprimir_lista_bullets(puntos_tierra)
        
    # ==========================================================================
    # HOJA 2: DATOS DEL SITIO
    # ==========================================================================
    def _hoja_2_datos_sitio(self, datos, ups=None):
        self._titulo_seccion("DATOS DEL SITIO DE INSTALACIÓN")

        self.set_fill_color(*COLOR_FONDO)
        self.set_font('Arial', '', 9)

        y_inicio = self.get_y()
        self.rect(10, y_inicio, 190, 30, 'F')

        col1 = 12
        col2 = 110

        # Separar Cliente y Sucursal para evitar amontonamiento
        cliente_texto = str(datos.get('cliente_texto', datos.get('nombre', 'SIN NOMBRE'))).upper()
        sucursal_texto = str(datos.get('sucursal_texto', '')).upper()

        # Capacidad del UPS o de los datos del formulario
        capacidad_valor = ups.get('Capacidad_kVA') if ups else datos.get('kva', 'S/D')

        # COLUMNA IZQUIERDA
        self.set_xy(col1, y_inicio + 3)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(50, 6, "Cliente:             ", 0, 0)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, cliente_texto, 0, 1)

        self.set_xy(col1, y_inicio + 9)
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(50, 6, "Sucursal / Proyecto: ", 0, 0)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, sucursal_texto, 0, 1)

        self.set_xy(col1, y_inicio + 15)
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(50, 6, "Capacidad UPS:       ", 0, 0)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, f"{capacidad_valor} kVA", 0, 1)

        self.set_xy(col1, y_inicio + 21)
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(50, 6, "Voltaje de Operación:   ", 0, 0)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, f"{datos.get('voltaje')} VCA", 0, 1)

        # COLUMNA DERECHA
        self.set_xy(col2, y_inicio + 3)
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(48, 6, "Configuración:       ", 0, 0)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, f"{datos.get('fases')} Fases + N + Tierra", 0, 1)

        self.set_xy(col2, y_inicio + 9)
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(48, 6, "Longitud Circuito:   ", 0, 0)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, f"{datos.get('longitud')} metros", 0, 1)

        # Restaurar fuente y color
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)

        self.set_y(y_inicio + 30)
        
        
          # ==========================================================================
    # HOJA 3: INGENIERÍA
    # ==========================================================================
    def _hoja_3_ingenieria(self, datos, res):
        # TÍTULO MANUAL CON PUNTO 3 EXPLÍCITO
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 10, "3. ESPECIFICACIONES DE INSTALACIÓN ELÉCTRICA", 0, 1, 'L')
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        norma_txt = (
            "Para la puesta en marcha deben existir las condiciones eléctricas adecuadas. "
            "Utilizar conductores de cobre, aislamiento tipo THHN/THWN-2 a 75 °C / 90 °C. "
            "Dimensionamiento basado estrictamente en la NOM-001-SEDE-2012."
        )
        self.multi_cell(0, 5, norma_txt)
        self.ln(5)

        # 3.1 PROTECCIONES
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "3.1 Protecciones Eléctricas", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.ln(2)

        self._dibujar_encabezado_tabla(["ELEMENTO / PARÁMETRO", "ESPECIFICACIÓN TÉCNICA", "DETALLE NOM"])
        self._dibujar_fila_tabla("Corriente de Diseño (+25%)", f"{res['i_diseno']} Amperes", f"Base: {res['i_nom']} A (In)", resaltar_col2=True)
        polos = datos.get('fases')
        self._dibujar_fila_tabla("Protección Principal (Breaker)", f"{res['breaker_sel']} Amperes", f"Termomagnético {polos} Polos", resaltar_col2=True)
        self.ln(5)

        # 3.2 CABLEADO
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "3.2 Dimensionamiento de Conductores", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.ln(2)

        self._dibujar_encabezado_tabla(["CONDUCTOR", "CALIBRE SUGERIDO", "TIPO MATERIAL"])
        self._dibujar_fila_tabla("Fases (L1, L2, L3)", f"{res['fase_sel']} AWG/kcmil", "Cobre THHN/THWN-2", resaltar_col2=True)
        self._dibujar_fila_tabla("Neutro (N)", f"{res['fase_sel']} AWG/kcmil", "Cobre (No reducir)", resaltar_col2=True)
        self._dibujar_fila_tabla("Tierra Física (GND/PE)", f"{res['gnd_sel']} AWG", "Cobre Desnudo / Verde", resaltar_col2=True)
        self.ln(5)

        # 3.3 ANÁLISIS DE INGENIERÍA
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "3.3 Análisis de Ingeniería y Validación", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.ln(2)

        # Análisis de Caída de Tensión
        dv_pct = res.get('dv_pct', 0)
        self.set_font('Arial', 'B', 9)
        self.cell(0, 5, "  A) Caída de Tensión:", 0, 1)
        self.set_font('Arial', '', 9)
        self.set_x(self.l_margin + 5)

        # Texto con variable resaltada - ARREGLADO PARA NO IRSE A LA DERECHA
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, f"El cálculo arroja una caída de tensión de {dv_pct}%.")

        self.set_x(self.l_margin + 5)
        if dv_pct <= 3.0:
            self.set_text_color(*COLOR_VERDE)
            self.multi_cell(0, 5, "Este valor es ÓPTIMO y se encuentra dentro de los límites recomendados por la norma (<3%), asegurando que el equipo y la carga operarán con un voltaje adecuado.")
        else:
            self.set_text_color(*COLOR_ALERTA)
            self.multi_cell(0, 5, "ALERTA: Este valor excede el límite recomendado por la norma (>3%). Se recomienda utilizar un calibre de conductor superior para mitigar riesgos de sobrecalentamiento y asegurar el correcto funcionamiento de la carga.")
        self.set_text_color(*COLOR_NEGRO)
        self.ln(3)

        # Análisis de Ampacidad
        i_real = res.get('i_real_cable', 0)
        i_diseno = res.get('i_diseno', 0)
        calibre = res.get('fase_sel', 'S/D')

        self.set_font('Arial', 'B', 9)
        self.cell(0, 5, "  B) Ampacidad del Conductor:", 0, 1)
        self.set_font('Arial', '', 9)
        self.set_x(self.l_margin + 5)

        # Texto con variables - ARREGLADO PARA NO IRSE A LA DERECHA
        self.set_font('Arial', '', 9)
        texto_ampacidad = f"El conductor seleccionado (calibre {calibre} AWG) tiene una ampacidad real de {i_real} A, considerando factores de agrupamiento y temperatura."
        self.multi_cell(0, 5, texto_ampacidad)

        self.set_x(self.l_margin + 5)
        if i_real > i_diseno:
            self.set_text_color(*COLOR_VERDE)
            texto_suficiente = f"Esta capacidad es SUFICIENTE para la corriente de diseño de {i_diseno} A, garantizando una operación segura y sin sobrecalentamiento del cableado."
            self.multi_cell(0, 5, texto_suficiente)
        else:
            self.set_text_color(*COLOR_ALERTA)
            texto_alerta = f"ALERTA: La capacidad del conductor ({i_real} A) es MENOR a la corriente de diseño ({i_diseno} A). Se requiere un conductor de mayor calibre para cumplir con la norma y evitar fallas críticas."
            self.multi_cell(0, 5, texto_alerta)
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
        self._titulo_seccion("BANCO DE BATERÍAS")
        
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        
        if not res.get('baterias_total'):
            self.multi_cell(0, 5, "No se realizaron cálculos para el banco de baterías.")
            return
            
        self.ln(5)
        self._subtitulo_rojo("BATERÍA SELECCIONADA")
        self._dibujar_encabezado_tabla(["MODELO / FABRICANTE", "VOLTAJE NOMINAL", "CAPACIDAD"])
        self._dibujar_fila_tabla(f"{bateria.get('modelo', 'S/D')} / {bateria.get('fabricante', 'S/D')}", f"{bateria.get('voltaje_nominal', 'S/D')} V", f"{bateria.get('capacidad_ah', 'S/D')} Ah", resaltar_col2=True)

        self.ln(5)

        self._subtitulo_rojo("CONFIGURACIÓN CALCULADA")
        self._dibujar_encabezado_tabla(["PARÁMETRO", "VALOR", "DESCRIPCIÓN"])
        self._dibujar_fila_tabla("Tiempo de Respaldo Calculado", f"{res.get('autonomia_calculada_min', 'S/D')} min", f"Objetivo: {res.get('autonomia_deseada_min', 'S/D')} min", resaltar_col2=True)
        self._dibujar_fila_tabla("Total de Baterías", f"{res.get('baterias_total', 'S/D')} pzas", f"{res.get('numero_strings', 'S/D')} arreglo(s) en paralelo", resaltar_col2=True)
        self._dibujar_fila_tabla("Baterías por Arreglo", f"{res.get('baterias_por_string', 'S/D')} pzas", "En serie para alcanzar el voltaje DC del UPS", resaltar_col2=True)

        self.ln(5)

        if res.get('bat_error'):
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ALERTA)
            self.multi_cell(0, 5, f"NOTA: {res.get('bat_error')}")

    # ==========================================================================
    # SECCIÓN NOTAS DE INSTALACION
    # ==========================================================================
    def _seccion_notas_instalacion(self, ups=None):
        self._titulo_seccion("DISPOSICIÓN Y NOTAS DEL ESPACIO DE INSTALACIÓN")
        
        self.set_text_color(*COLOR_NEGRO)
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, "Nota: Tenga en cuenta que, para facilitar la operación y el mantenimiento, el espacio en la parte delantera y trasera del gabinete debe dejarse al menos 800 mm y 800 mm respectivamente al instalar el gabinete.")
        self.ln(5)

        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "Esquema de Espacios Mínimos:", 0, 1)

        draw_placeholder = True
        if ups and ups.get('imagen_instalacion_url'):
            img_filename = os.path.basename(ups['imagen_instalacion_url'])
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)

            if os.path.exists(ruta_imagen):
                try:
                    img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=120)
                    self.image(img_procesada, x=45, w=120)
                    draw_placeholder = False
                    # Limpiar archivo temporal
                    if img_procesada != ruta_imagen:
                        try:
                            os.unlink(img_procesada)
                        except:
                            pass
                except Exception as e:
                    print(f"Error cargando imagen de instalación: {e}")
        
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
        self._titulo_seccion("DIAGRAMA DE CONEXIÓN SUGERIDO")

        # DESCRIPCIÓN GENERAL
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        descripcion = (
            "Los diagramas siguientes muestran la configuración eléctrica recomendada para la instalación del sistema UPS, "
            "incluyendo el diagrama unifilar de corriente alterna (AC) y el esquema de conexión del banco de baterías (DC)."
        )
        self.multi_cell(0, 5, descripcion)
        self.ln(5)

        # Main Diagram - Unifilar AC (usar imagen temporal si está disponible)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "4.1 Diagrama Unifilar AC:", 0, 1)

        # Descripción del diagrama unifilar
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_GRIS)
        self.multi_cell(0, 4, "Representa la arquitectura eléctrica de alimentación AC del UPS, mostrando protecciones, conductores y conexiones principales.")
        self.ln(3)
        self.set_text_color(*COLOR_NEGRO)

        draw_placeholder_unifilar = True
        if self.imagenes_temp.get('unifilar_ac'):
            # Usar imagen temporal cargada - REDIMENSIONADA
            try:
                img_procesada = self._preparar_imagen(self.imagenes_temp['unifilar_ac'], ancho_mm=190)
                self.image(img_procesada, x=10, w=190)
                draw_placeholder_unifilar = False
                # Limpiar archivo temporal
                if img_procesada != self.imagenes_temp['unifilar_ac']:
                    try:
                        os.unlink(img_procesada)
                    except:
                        pass
            except Exception as e:
                print(f"Error cargando imagen temporal unifilar AC: {e}")

        if draw_placeholder_unifilar:
            self.set_fill_color(230, 230, 230)
            y = self.get_y()
            self.rect(10, y, 190, 80, 'F')
            self.set_xy(10, y + 35)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(150, 150, 150)
            self.cell(190, 10, "[ ESPACIO PARA DIAGRAMA UNIFILAR AC ]", 0, 0, 'C')
            self.set_y(y + 85)
        self.ln(5)

        # NUEVA PÁGINA PARA DIAGRAMA DE BATERÍAS DC
        self.add_page()
        if not self.imagenes_temp.get('es_publicado', True):
            self._marca_agua_preview()

        # Battery Connection Diagram (usar imagen temporal si está disponible)
        self.set_text_color(*COLOR_NEGRO)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, "4.2 Diagrama de Conexión de Baterías DC:", 0, 1)

        # Descripción del diagrama de baterías
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_GRIS)
        self.multi_cell(0, 4, "Muestra la configuración del banco de baterías en serie/paralelo, incluyendo el interruptor de protección DC y las conexiones al UPS.")
        self.ln(3)

        self.set_text_color(*COLOR_NEGRO)
        self.multi_cell(0, 5, "En el siguiente diagrama se muestra la manera recomendada de conexión de baterías en serie así como la conexión del interruptor de DC.")
        self.ln(3)

        draw_placeholder = True

        # Prioridad 1: Imagen temporal cargada - REDIMENSIONADA
        if self.imagenes_temp.get('baterias_dc'):
            try:
                img_procesada = self._preparar_imagen(self.imagenes_temp['baterias_dc'], ancho_mm=120)
                self.image(img_procesada, x=45, w=120)
                draw_placeholder = False
                # Limpiar archivo temporal
                if img_procesada != self.imagenes_temp['baterias_dc']:
                    try:
                        os.unlink(img_procesada)
                    except:
                        pass
            except Exception as e:
                print(f"Error cargando imagen temporal baterías DC: {e}")
        # Prioridad 2: Imagen desde BD del UPS - REDIMENSIONADA
        elif ups and ups.get('imagen_baterias_url'):
            img_filename = os.path.basename(ups['imagen_baterias_url'])
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)

            if os.path.exists(ruta_imagen):
                try:
                    img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=120)
                    self.image(img_procesada, x=45, w=120)
                    draw_placeholder = False
                    # Limpiar archivo temporal
                    if img_procesada != ruta_imagen:
                        try:
                            os.unlink(img_procesada)
                        except:
                            pass
                except Exception as e:
                    print(f"Error cargando imagen de conexion de baterias: {e}")

        if draw_placeholder:
            y = self.get_y()
            self.set_fill_color(230, 230, 230)
            self.rect(45, y, 120, 80, 'F')
            self.set_xy(45, y + 35)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(150, 150, 150)
            self.cell(120, 10, "[ IMAGEN CONEXIÓN BATERÍAS ]", 0, 0, 'C')
            self.set_text_color(*COLOR_NEGRO)

    def _seccion_fotografia(self, titulo, imagen_url=None):
        self._titulo_seccion(titulo)

        # AGREGAR DESCRIPCIÓN SEGÚN EL TIPO DE IMAGEN
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_GRIS)

        if "DISPOSICIÓN" in titulo.upper():
            descripcion = (
                "La siguiente imagen muestra la distribución física recomendada de los equipos en el sitio de instalación, "
                "incluyendo el UPS, banco de baterías, y espacios de ventilación requeridos."
            )
        elif "CONEXIÓN" in titulo.upper() and "BATERÍA" in titulo.upper():
            descripcion = (
                "Fotografía de referencia que ilustra la conexión física del banco de baterías al sistema UPS, "
                "mostrando terminales, cableado DC y polaridad correcta."
            )
        elif "VENTILACIÓN" in titulo.upper():
            descripcion = (
                "Imagen de referencia del sistema de ventilación recomendado para mantener la temperatura operativa "
                "del equipo dentro de los parámetros especificados por el fabricante."
            )
        else:
            descripcion = "Imagen de referencia para la instalación del sistema."

        self.multi_cell(0, 4, descripcion)
        self.ln(5)
        self.set_text_color(*COLOR_NEGRO)

        draw_placeholder = True

        # Si el título es "DISPOSICION DE LOS EQUIPOS", usar imagen temporal si existe - REDIMENSIONADA
        if "DISPOSICIÓN" in titulo.upper() and self.imagenes_temp.get('layout_equipos'):
            try:
                img_procesada = self._preparar_imagen(self.imagenes_temp['layout_equipos'], ancho_mm=120)
                self.image(img_procesada, x=45, w=120)
                draw_placeholder = False
                # Limpiar archivo temporal
                if img_procesada != self.imagenes_temp['layout_equipos']:
                    try:
                        os.unlink(img_procesada)
                    except:
                        pass
            except Exception as e:
                print(f"Error cargando imagen temporal layout: {e}")
        # Si no hay imagen temporal, usar imagen desde BD - REDIMENSIONADA
        elif imagen_url:
            img_filename = os.path.basename(imagen_url)
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)

            if os.path.exists(ruta_imagen):
                try:
                    img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=120)
                    self.image(img_procesada, x=45, w=120)
                    draw_placeholder = False
                    # Limpiar archivo temporal
                    if img_procesada != ruta_imagen:
                        try:
                            os.unlink(img_procesada)
                        except:
                            pass
                except Exception as e:
                    print(f"Error cargando imagen de sección '{titulo}': {e}")

        if draw_placeholder:
            y = self.get_y()
            self.set_fill_color(230, 230, 230)
            self.rect(45, y, 120, 80, 'F')
            self.set_xy(45, y + 35)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(150, 150, 150)
            self.cell(120, 10, f"[ FOTOGRAFÍA: {titulo.upper()} ]", 0, 0, 'C')
            self.set_text_color(*COLOR_NEGRO)

    def _seccion_tipo_ventilacion(self, tipo_ventilacion=None, tipo_ventilacion_data=None):
        self._titulo_seccion("TIPO DE VENTILACIÓN DEL SISTEMA")

        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)

        if tipo_ventilacion:
            # INTRODUCCIÓN CON TEXTO NEGRO
            intro_texto = (
                "El sistema de ventilación es un componente crítico para garantizar el funcionamiento "
                "óptimo y la vida útil del equipo UPS. Una ventilación adecuada previene el sobrecalentamiento, "
                "reduce el desgaste de componentes internos y asegura que el equipo opere dentro de los "
                "parámetros especificados por el fabricante."
            )
            self.multi_cell(0, 5, intro_texto)
            self.ln(5)

            # RECUADRO CON TIPO DE VENTILACIÓN
            self.set_fill_color(*COLOR_FONDO)
            y_pos = self.get_y()
            self.rect(40, y_pos, 130, 30, 'F')

            self.set_xy(50, y_pos + 8)
            self.set_font('Arial', 'B', 10)
            self.set_text_color(*COLOR_NEGRO)
            self.cell(0, 6, "Sistema de Ventilación Especificado:", 0, 1)

            self.set_xy(50, y_pos + 16)
            self.set_font('Arial', 'B', 13)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, tipo_ventilacion, 0, 1)

            self.set_y(y_pos + 35)
            self.ln(8)

            # DESCRIPCIÓN DEL TIPO DE VENTILACIÓN (si existe)
            if tipo_ventilacion_data and tipo_ventilacion_data.get('descripcion'):
                self.set_font('Arial', '', 9)
                self.set_text_color(*COLOR_NEGRO)
                self.multi_cell(0, 5, tipo_ventilacion_data.get('descripcion'))
                self.ln(3)

            # IMAGEN DEL SISTEMA DE VENTILACIÓN
            draw_placeholder = True
            if tipo_ventilacion_data and tipo_ventilacion_data.get('imagen_url'):
                img_filename = os.path.basename(tipo_ventilacion_data['imagen_url'])
                ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)

                if os.path.exists(ruta_imagen):
                    try:
                        self.set_font('Arial', 'B', 10)
                        self.set_text_color(*COLOR_NEGRO)
                        self.cell(0, 6, "Diagrama de Referencia:", 0, 1)
                        self.ln(3)

                        img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=140)
                        self.image(img_procesada, x=35, w=140)
                        draw_placeholder = False
                        # Limpiar archivo temporal
                        if img_procesada != ruta_imagen:
                            try:
                                os.unlink(img_procesada)
                            except:
                                pass
                    except Exception as e:
                        print(f"Error cargando imagen de ventilación: {e}")

            if draw_placeholder:
                self.ln(3)

            # CONSIDERACIONES ADICIONALES
            self.ln(5)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 5, "Consideraciones Importantes:", 0, 1)
            self.ln(2)

            consideraciones = [
                "Mantener las rejillas de ventilación libres de obstrucciones en todo momento.",
                "Respetar las distancias mínimas especificadas (mínimo 800mm frontal y posterior).",
                "Verificar que la temperatura ambiente no exceda los 25 °C para vida útil óptima de baterías.",
                "Evitar la exposición directa a fuentes de calor, luz solar o ambientes húmedos.",
                "Realizar inspecciones periódicas para asegurar el flujo de aire adecuado."
            ]

            self.set_font('Arial', '', 9)
            self.set_text_color(*COLOR_NEGRO)
            self._imprimir_lista_bullets(consideraciones)

        else:
            self.ln(5)
            self.set_text_color(*COLOR_GRIS_CLARO)
            self.set_font('Arial', 'I', 10)
            self.multi_cell(0, 5, "No se ha especificado el tipo de ventilación para este equipo.")
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

    def _dibujar_fila_tabla(self, c1, c2, c3, resaltar_col2=False):
        self.set_text_color(*COLOR_NEGRO)
        self.set_font('Arial', '', 9)
        self.set_draw_color(220, 220, 220)
        self.cell(60, 7, c1, 1, 0, 'L')

        # Aplicar negrita y color rojo si se solicita resaltar
        if resaltar_col2:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(*COLOR_ROJO)
        else:
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_NEGRO)

        self.cell(65, 7, c2, 1, 0, 'C')

        self.set_font('Arial', '', 8)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(65, 7, c3, 1, 1, 'C')