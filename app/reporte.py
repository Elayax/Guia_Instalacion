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
        self._es_publicado = False
        # Márgenes seguros para impresión (10mm izq/der, 10mm top, 15mm bottom para footer)
        self.set_margins(10, 10, 10)
        self.set_auto_page_break(True, margin=20)

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
        except Exception:
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

        # Fecha en la esquina superior derecha
        self.set_xy(150, 10)
        self.set_font('Arial', '', 7)
        self.set_text_color(*COLOR_GRIS_CLARO)
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(50, 5, fecha, 0, 0, 'R')

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
        self.cell(60, 10, "Doc. v1.0 | LBS", 0, 0, 'L')
        self.cell(70, 10, fecha, 0, 0, 'C')
        self.cell(60, 10, f"Página {self.page_no()}", 0, 0, 'R')

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
        except Exception:
            return texto

    def _preparar_imagen(self, ruta_imagen, ancho_mm=190, alto_mm=None, alto_max_mm=None):
        """
        Redimensiona y optimiza una imagen para el PDF
        - ruta_imagen: Path de la imagen original
        - ancho_mm: Ancho deseado en mm para el PDF
        - alto_mm: Alto deseado en mm (opcional, mantiene proporción si no se especifica)
        - alto_max_mm: Alto máximo en mm (limita la imagen si excede, ajustando ancho proporcionalmente)

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

                # Aplicar límite de alto máximo si se especificó
                if alto_max_mm:
                    alto_max_px = int(alto_max_mm * dpi / 25.4)
                    if alto_px > alto_max_px:
                        alto_px = alto_max_px
                        ancho_px = int(alto_px / ratio)

                img = img.resize((ancho_px, alto_px), Image.Resampling.LANCZOS)

            # Guardar en archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG', quality=85, optimize=True)
            temp_file.close()

            return temp_file.name

        except Exception as e:
            print(f"Error preparando imagen {ruta_imagen}: {e}")
            return ruta_imagen  # Retornar original si falla

    def _insertar_imagen_segura(self, ruta_imagen, ancho_mm=120, centrar=True, margen_inferior=15):
        """
        Inserta una imagen en el PDF asegurando que no se corte ni desborde la página.
        - ruta_imagen: Path de la imagen a insertar
        - ancho_mm: Ancho deseado en mm
        - centrar: Si True, centra la imagen horizontalmente
        - margen_inferior: Margen inferior mínimo en mm (para no pisar el footer)

        Retorna: True si se insertó correctamente, False si falló
        """
        try:
            # Calcular espacio disponible en la página actual
            espacio_disponible = self.h - self.get_y() - margen_inferior  # alto página - posición Y - margen

            # Obtener dimensiones reales de la imagen para calcular alto proporcional
            img = Image.open(ruta_imagen)
            ratio = img.height / img.width
            alto_proporcional_mm = ancho_mm * ratio

            # Si la imagen es más alta que el espacio disponible, limitar
            alto_max_mm = None
            if alto_proporcional_mm > espacio_disponible:
                alto_max_mm = max(espacio_disponible, 40)  # mínimo 40mm para que se vea algo

            # Preparar imagen con límite de alto
            img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=ancho_mm, alto_max_mm=alto_max_mm)

            # Calcular posición X para centrar
            if centrar:
                # Recalcular ancho real si se limitó por alto
                if alto_max_mm and alto_proporcional_mm > espacio_disponible:
                    ancho_real = alto_max_mm / ratio
                    x = (self.w - ancho_real) / 2
                    self.image(img_procesada, x=x, w=ancho_real)
                else:
                    x = (self.w - ancho_mm) / 2
                    self.image(img_procesada, x=x, w=ancho_mm)
            else:
                self.image(img_procesada, x=10, w=ancho_mm)

            # Limpiar archivo temporal
            if img_procesada != ruta_imagen:
                try:
                    os.unlink(img_procesada)
                except OSError:
                    pass

            return True

        except Exception as e:
            print(f"Error insertando imagen segura {ruta_imagen}: {e}")
            return False

    def _int_display(self, val):
        """Muestra entero si es número redondo, float si tiene decimales reales."""
        try:
            f = float(val)
            return str(int(f)) if f == int(f) else str(f)
        except (ValueError, TypeError):
            return str(val) if val else 'S/D'

    def generar_cuerpo(self, datos, res, es_publicado=False, ups=None, bateria=None, imagenes_temp=None):

        # Almacenar estado para watermarks en páginas internas
        self.imagenes_temp = imagenes_temp or {}
        self._es_publicado = es_publicado

        # Portada — siempre
        self.add_page()
        self._hoja_portada(datos, res, ups)

        # Normas de seguridad — siempre
        self.add_page()
        if not es_publicado:
            self.set_font('Arial', 'B', 40)
            self.set_text_color(230, 230, 230)
            self.set_xy(10, 100)
            self.cell(0, 10, "VISTA PREVIA - BORRADOR", 0, 0, 'C')
            self.set_xy(10, 120)
            self.cell(0, 10, "NO VALIDO PARA INSTALACIÓN", 0, 0, 'C')
            self.set_text_color(*COLOR_NEGRO)
            self.set_y(40)
        self._hoja_1_seguridad_instalacion()

        # Datos del sitio + Ingeniería — siempre
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._hoja_2_datos_sitio(datos, ups)
        self.ln(8)
        self._hoja_3_ingenieria(datos, res)

        # Baterías — SOLO si hay datos de baterías
        if res.get('baterias_total'):
            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_baterias(bateria, res)

        # Notas de instalación — siempre (tiene texto fijo útil)
        self.add_page()
        if not es_publicado: self._marca_agua_preview()
        self._seccion_notas_instalacion(ups, datos=datos, res=res)

        # Diagramas — SOLO si hay imagen temporal o de BD
        tiene_unifilar = bool(self.imagenes_temp.get('unifilar_ac'))
        tiene_bat_dc = bool(self.imagenes_temp.get('baterias_dc')) or (ups and ups.get('imagen_baterias_url'))

        if tiene_unifilar or tiene_bat_dc:
            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._hoja_4_diagrama(ups, res=res)

        # Ventilación — SOLO si hay tipo_ventilacion definido
        if res.get('tipo_ventilacion'):
            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_tipo_ventilacion(res.get('tipo_ventilacion'), res.get('tipo_ventilacion_data'))

        # Disposición equipos — SOLO si hay imagen
        tiene_layout = bool(self.imagenes_temp.get('layout_equipos')) or (ups and ups.get('imagen_layout_url'))
        if tiene_layout:
            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_fotografia("DISPOSICIÓN DE LOS EQUIPOS", ups.get('imagen_layout_url') if ups else None)

        # Conexión baterías foto — SOLO si hay baterías Y imagen
        if res.get('baterias_total') and (ups and ups.get('imagen_baterias_url')):
            self.add_page()
            if not es_publicado: self._marca_agua_preview()
            self._seccion_fotografia("CONEXIÓN DE BATERÍAS", ups.get('imagen_baterias_url'))

        return self.output()

    # ==========================================================================
    # HOJA PORTADA
    # ==========================================================================
    def _hoja_portada(self, datos, res, ups=None):
        self.ln(20)

        y_pos_after_image = self.get_y() + 85
        imagen_colocada = False

        # Prioridad 1: Imagen de portada subida por el usuario
        if self.imagenes_temp.get('portada'):
            try:
                img_procesada = self._preparar_imagen(self.imagenes_temp['portada'], ancho_mm=80)
                self.image(img_procesada, x=65, y=40, w=80)
                imagen_colocada = True
                if img_procesada != self.imagenes_temp['portada']:
                    try: os.unlink(img_procesada)
                    except OSError: pass
            except Exception:
                pass

        # Prioridad 2: Imagen del UPS desde BD
        if not imagen_colocada and ups and ups.get('imagen_url'):
            img_filename = os.path.basename(ups['imagen_url'])
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)

            if os.path.exists(ruta_imagen):
                try:
                    img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=80)
                    self.image(img_procesada, x=65, y=40, w=80)
                    imagen_colocada = True
                    if img_procesada != ruta_imagen:
                        try: os.unlink(img_procesada)
                        except OSError: pass
                except Exception:
                    pass

        # Si no hay imagen, no dibujar nada (sin caja negra)

        self.set_y(y_pos_after_image)

        self.set_font('Arial', 'B', 24); self.set_text_color(*COLOR_ROJO)
        self.cell(0, 12, "MEMORIA TÉCNICA", 0, 1, 'C')
        self.cell(0, 12, "DE INSTALACIÓN UPS", 0, 1, 'C')
        self.ln(20)
        self.set_font('Arial', '', 12); self.set_text_color(*COLOR_NEGRO)
        self.set_fill_color(245, 245, 245)
        y_box = self.get_y() + 5
        self.rect(35, y_box, 140, 50, 'F')
        self.set_y(y_box + 5)

        # DATOS CORREGIDOS - Usar los campos correctos del formulario
        proyecto_nombre = datos.get('cliente_texto', datos.get('nombre', 'S/D'))
        if datos.get('sucursal_texto'):
            proyecto_nombre = f"{proyecto_nombre} - {datos.get('sucursal_texto')}"

        equipo_nombre = (ups.get('Nombre_del_Producto') or ups.get('modelo')) if ups else None
        if not equipo_nombre:
            equipo_nombre = res.get('modelo_nombre', datos.get('modelo_nombre', 'S/D'))
        capacidad_valor = (ups.get('Capacidad_kVA') or ups.get('kva')) if ups else None
        if not capacidad_valor:
            capacidad_valor = datos.get('kva', 'S/D')

        self._fila_portada("PROYECTO:", proyecto_nombre)
        self._fila_portada("EQUIPO:", equipo_nombre)
        self._fila_portada("CAPACIDAD:", f"{capacidad_valor} kVA")
        self._fila_portada("FECHA:", datetime.now().strftime("%d/%m/%Y"))

    def _fila_portada(self, label, value):
        y_before = self.get_y()
        self.set_x(45); self.set_font('Arial', '', 11); self.set_text_color(*COLOR_NEGRO); self.cell(40, 8, label, 0, 0, 'L')
        self.set_font('Arial', 'B', 11); self.set_text_color(*COLOR_ROJO); self.multi_cell(90, 8, str(value), 0, 'L')
        self.set_text_color(*COLOR_NEGRO)

    # ==========================================================================
    # HOJA 1: NORMAS Y SEGURIDAD
    # ==========================================================================
    def _hoja_1_seguridad_instalacion(self):
        self._titulo_seccion("NORMAS DE SEGURIDAD")
        
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        
        intro = (
            "Con esta documentación, LBS le ofrece toda la información necesaria sobre la correcta instalación del UPS. "
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
        self.set_font('Arial', 'B', 12)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 8, "3. ESPECIFICACIONES DE INSTALACIÓN ELÉCTRICA", 0, 1, 'L')
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

        self.set_font('Arial', '', 8)
        self.set_text_color(*COLOR_NEGRO)
        norma_txt = (
            "Conductores de cobre, aislamiento THHN/THWN-2 a 75 °C / 90 °C. "
            "Dimensionamiento según NOM-001-SEDE-2012."
        )
        self.multi_cell(0, 4, norma_txt)
        self.ln(3)

        # 3.1 PROTECCIONES
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 5, "3.1 Protecciones Eléctricas", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.ln(1)

        self._dibujar_encabezado_tabla(["ELEMENTO / PARÁMETRO", "ESPECIFICACIÓN TÉCNICA", "DETALLE NOM"])
        self._dibujar_fila_tabla("Corriente de Diseño (+25%)", f"{res['i_diseno']} Amperes", f"Base: {res['i_nom']} A (In)", resaltar_col2=True)
        polos = datos.get('fases')
        self._dibujar_fila_tabla("Protección Principal (Breaker)", f"{res['breaker_sel']} Amperes", f"Termomagnético {polos} Polos", resaltar_col2=True)
        self.ln(3)

        # 3.2 CABLEADO
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 5, "3.2 Dimensionamiento de Conductores", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.ln(1)

        self._dibujar_encabezado_tabla(["CONDUCTOR", "CALIBRE SUGERIDO", "TIPO MATERIAL"])
        self._dibujar_fila_tabla("Fases (L1, L2, L3)", f"{res['fase_sel']} AWG/kcmil", "Cobre THHN/THWN-2", resaltar_col2=True)
        self._dibujar_fila_tabla("Neutro (N)", f"{res['fase_sel']} AWG/kcmil", "Cobre (No reducir)", resaltar_col2=True)
        self._dibujar_fila_tabla("Tierra Física (GND/PE)", f"{res['gnd_sel']} AWG", "Cobre Desnudo / Verde", resaltar_col2=True)
        self.ln(3)

        # 3.3 ANÁLISIS DE INGENIERÍA
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 5, "3.3 Análisis de Ingeniería y Validación", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.ln(1)

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
        self.ln(2)

    # ==========================================================================
    # UTILIDAD: Insertar imagen llenando el espacio disponible en la página
    # ==========================================================================
    def _insertar_imagen_llena(self, ruta_imagen, margen_inferior=25, ancho_max=190):
        """
        Inserta imagen expandiéndola para llenar todo el espacio disponible.
        Calcula el alto disponible y ajusta la imagen para llenar sin desbordar.
        Retorna True si se insertó, False si falló.
        """
        try:
            img = Image.open(ruta_imagen)
            ratio_img = img.height / img.width  # ratio de la imagen

            # Espacio disponible en la página
            y_actual = self.get_y()
            alto_disponible = self.h - y_actual - margen_inferior
            ancho_disponible = ancho_max

            # Calcular: si la imagen se pone al ancho máximo, qué alto tendría?
            alto_si_ancho_max = ancho_disponible * ratio_img

            if alto_si_ancho_max <= alto_disponible:
                # La imagen cabe al ancho máximo — usar ancho máximo
                ancho_final = ancho_disponible
                alto_final = alto_si_ancho_max
            else:
                # La imagen es más alta que el espacio — limitar por alto
                alto_final = alto_disponible
                ancho_final = alto_final / ratio_img

            # Preparar imagen a buena resolución
            img_procesada = self._preparar_imagen(ruta_imagen, ancho_mm=ancho_final)

            # Centrar horizontalmente
            x = (self.w - ancho_final) / 2
            self.image(img_procesada, x=x, y=y_actual, w=ancho_final, h=alto_final)

            # Mover cursor debajo de la imagen
            self.set_y(y_actual + alto_final + 2)

            # Limpiar temporal
            if img_procesada != ruta_imagen:
                try:
                    os.unlink(img_procesada)
                except OSError:
                    pass
            return True
        except Exception as e:
            print(f"Error insertando imagen llena {ruta_imagen}: {e}")
            return False

    # ==========================================================================
    # SECCIÓN BATERÍAS (Página 4) — Sin espacios en blanco
    # ==========================================================================
    def _seccion_baterias(self, bateria, res):
        self._titulo_seccion("BANCO DE BATERÍAS")

        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)

        if not res.get('baterias_total'):
            self.multi_cell(0, 5, "No se realizaron cálculos para el banco de baterías.")
            return

        # Intro
        self.multi_cell(0, 5, "A continuación se detallan las especificaciones del banco de baterías, "
                         "la configuración calculada y las validaciones correspondientes para garantizar "
                         "el tiempo de respaldo requerido por el proyecto.")
        self.ln(4)

        # --- DOBLE COLUMNA: Batería (izq) + Configuración (der) ---
        y_start = self.get_y()
        col_w = 92

        # COLUMNA IZQUIERDA — Batería seleccionada
        self.set_xy(10, y_start)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(col_w, 5, "Batería Seleccionada", 0, 1)
        self.ln(1)

        self.set_fill_color(245, 245, 245)
        y_box = self.get_y()
        self.rect(10, y_box, col_w, 36, 'F')

        bat_data = [
            ("Modelo:", bateria.get('modelo', 'S/D')),
            ("Fabricante:", bateria.get('fabricante', 'S/D')),
            ("Voltaje Nominal:", f"{bateria.get('voltaje_nominal', 'S/D')} V"),
            ("Capacidad:", f"{bateria.get('capacidad_ah', bateria.get('capacidad_nominal_ah', 'S/D'))} Ah"),
        ]
        self.set_font('Arial', '', 8)
        for i, (label, valor) in enumerate(bat_data):
            self.set_xy(12, y_box + 2 + i * 8)
            self.set_text_color(*COLOR_NEGRO)
            self.cell(35, 6, label, 0, 0)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(55, 6, str(valor), 0, 0)
            self.set_font('Arial', '', 8)

        # COLUMNA DERECHA — Configuración calculada
        self.set_xy(108, y_start)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(col_w, 5, "Configuración del Banco", 0, 1)
        self.set_xy(108, y_start + 6)
        self.ln(0)

        y_box2 = self.get_y()
        self.rect(108, y_box2, col_w, 36, 'F')

        config_data = [
            ("Total Baterías:", f"{self._int_display(res.get('baterias_total'))} pzas"),
            ("Strings en Paralelo:", f"{self._int_display(res.get('numero_strings'))} arreglo(s)"),
            ("Baterías/String:", f"{self._int_display(res.get('baterias_por_string'))} en serie"),
            ("Respaldo Calculado:", f"{self._int_display(res.get('autonomia_calculada_min'))} min"),
        ]
        self.set_font('Arial', '', 8)
        for i, (label, valor) in enumerate(config_data):
            self.set_xy(110, y_box2 + 2 + i * 8)
            self.set_text_color(*COLOR_NEGRO)
            self.cell(38, 6, label, 0, 0)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(50, 6, str(valor), 0, 0)
            self.set_font('Arial', '', 8)

        self.set_y(max(y_box + 38, y_box2 + 38))
        self.ln(4)

        # --- TABLA DE VALIDACIÓN ---
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "Validación de Autonomía", 0, 1)
        self.ln(1)

        self._dibujar_encabezado_tabla(["PARÁMETRO", "VALOR", "OBSERVACIÓN"])
        autonomia_calc = res.get('autonomia_calculada_min', 0)
        autonomia_des = res.get('autonomia_deseada_min', 0)
        cumple = "CUMPLE" if float(autonomia_calc or 0) >= float(autonomia_des or 0) else "NO CUMPLE"
        self._dibujar_fila_tabla("Autonomía Calculada", f"{self._int_display(autonomia_calc)} min",
                                 f"Objetivo: {self._int_display(autonomia_des)} min", resaltar_col2=True)
        self._dibujar_fila_tabla("Tiempo de Respaldo",
                                 f"{self._int_display(res.get('tiempo_respaldo'))} min", cumple, resaltar_col2=True)
        self._dibujar_fila_tabla("Total Baterías",
                                 f"{self._int_display(res.get('baterias_total'))} pzas",
                                 f"{self._int_display(res.get('numero_strings'))} strings x {self._int_display(res.get('baterias_por_string'))} serie")
        self._dibujar_fila_tabla("Modelo Batería", str(res.get('bateria_modelo', 'S/D')),
                                 f"{bateria.get('voltaje_nominal', '?')}V / {bateria.get('capacidad_ah', '?')}Ah")
        self.ln(4)

        # --- RECOMENDACIONES ---
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "Recomendaciones para el Banco de Baterías:", 0, 1)
        self.ln(1)

        notas_bat = [
            "Verificar la polaridad correcta antes de conectar cada string de baterías.",
            "Utilizar torquímetro calibrado para las terminales (consultar manual del fabricante).",
            "Mantener temperatura ambiente inferior a 25 °C para vida útil óptima.",
            "Realizar prueba de descarga controlada después de la primera carga completa (24-48 hrs).",
            "Realizar inspección visual trimestral del banco, verificando conexiones y estado de terminales.",
            "Registrar voltajes individuales por celda para detectar elementos degradados.",
        ]
        self._imprimir_lista_bullets(notas_bat)

        if res.get('bat_error'):
            self.ln(2)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ALERTA)
            self.multi_cell(0, 5, f"NOTA: {res.get('bat_error')}")

        # --- LLENAR ESPACIO RESTANTE: Tabla resumen extendida ---
        espacio_restante = self.h - self.get_y() - 25
        if espacio_restante > 30:
            self.ln(4)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, "Datos Técnicos de Referencia:", 0, 1)
            self.ln(1)

            self._dibujar_encabezado_tabla(["CONCEPTO", "VALOR NOMINAL", "OBSERVACIÓN"])
            vnom = bateria.get('voltaje_nominal', '?')
            self._dibujar_fila_tabla("Voltaje del String",
                                     f"{self._int_display(res.get('baterias_por_string', 0))} x {vnom}V = {self._int_display(float(res.get('baterias_por_string', 0) or 0) * float(vnom or 0))}VDC",
                                     "Nominal por string")
            self._dibujar_fila_tabla("Tipo de Conexión",
                                     f"{self._int_display(res.get('numero_strings'))} strings en paralelo",
                                     "Serie interna, paralelo entre strings")
            self._dibujar_fila_tabla("Interruptor DC",
                                     "Recomendado", "Protección entre banco y UPS")
            self._dibujar_fila_tabla("Cable DC",
                                     "Según fabricante", "Verificar sección mínima AWG")
            self._dibujar_fila_tabla("Temperatura Óptima",
                                     "20 °C - 25 °C", "Vida útil máxima de baterías")
            self._dibujar_fila_tabla("Mantenimiento",
                                     "Semestral recomendado", "Inspección visual + voltajes")

    # ==========================================================================
    # SECCIÓN NOTAS DE INSTALACIÓN (Página 5) — Sin espacios en blanco
    # ==========================================================================
    def _seccion_notas_instalacion(self, ups=None, datos=None, res=None):
        self._titulo_seccion("DISPOSICIÓN Y NOTAS DEL ESPACIO DE INSTALACIÓN")

        self.set_text_color(*COLOR_NEGRO)
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, "Para facilitar la operación y el mantenimiento del sistema UPS, es "
                         "indispensable respetar los espacios mínimos indicados alrededor del gabinete. "
                         "El incumplimiento de estas distancias puede afectar la ventilación, dificultar "
                         "el acceso para mantenimiento y reducir la vida útil del equipo.")
        self.ln(3)

        # --- TABLA DE REQUISITOS (ancho completo, no doble columna) ---
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "Requisitos del Espacio de Instalación:", 0, 1)
        self.ln(1)

        self._dibujar_encabezado_tabla(["PARÁMETRO", "REQUERIMIENTO", "NORMA / REFERENCIA"])
        self._dibujar_fila_tabla("Frente del gabinete", "800 mm mínimo", "Acceso para operación", resaltar_col2=True)
        self._dibujar_fila_tabla("Parte trasera", "800 mm mínimo", "Ventilación y cableado", resaltar_col2=True)
        self._dibujar_fila_tabla("Laterales", "300 mm mínimo", "Flujo de aire lateral", resaltar_col2=True)
        self._dibujar_fila_tabla("Temperatura ambiente", "< 25 °C óptima", "Vida útil de baterías", resaltar_col2=True)
        self._dibujar_fila_tabla("Humedad relativa", "< 90% sin condensación", "Protección de componentes", resaltar_col2=True)
        self._dibujar_fila_tabla("Ventilación", "Sin obstrucciones", "Evitar sobrecalentamiento", resaltar_col2=True)
        self.ln(4)

        # --- DIMENSIONES DEL EQUIPO ---
        dim_largo = (res or {}).get('dim_largo', (datos or {}).get('dim_largo', ''))
        dim_ancho = (res or {}).get('dim_ancho', (datos or {}).get('dim_ancho', ''))
        dim_alto = (res or {}).get('dim_alto', (datos or {}).get('dim_alto', ''))
        peso = (res or {}).get('peso', (datos or {}).get('peso', ''))

        if any([dim_largo, dim_ancho, dim_alto, peso]):
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, "Dimensiones y Peso del Equipo:", 0, 1)
            self.ln(1)

            self._dibujar_encabezado_tabla(["MEDIDA", "VALOR", "UNIDAD"])
            if dim_largo:
                self._dibujar_fila_tabla("Largo (Profundidad)", str(dim_largo), "mm", resaltar_col2=True)
            if dim_ancho:
                self._dibujar_fila_tabla("Ancho (Frente)", str(dim_ancho), "mm", resaltar_col2=True)
            if dim_alto:
                self._dibujar_fila_tabla("Alto", str(dim_alto), "mm", resaltar_col2=True)
            if peso:
                self._dibujar_fila_tabla("Peso Gabinete", str(peso), "kg", resaltar_col2=True)
            self.ln(4)

        # --- IMAGEN DE ESPACIOS (si hay de la BD) ---
        imagen_insertada = False
        if ups and ups.get('imagen_instalacion_url'):
            img_filename = os.path.basename(ups['imagen_instalacion_url'])
            ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
            if os.path.exists(ruta_imagen):
                try:
                    self.set_font('Arial', 'B', 9)
                    self.set_text_color(*COLOR_ROJO)
                    self.cell(0, 6, "Esquema de Espacios Recomendados:", 0, 1)
                    self.ln(1)
                    imagen_insertada = self._insertar_imagen_llena(ruta_imagen, margen_inferior=30)
                except Exception:
                    pass

        # --- PRECAUCIONES (siempre, llenando espacio) ---
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "Precauciones Generales de Instalación:", 0, 1)
        self.ln(1)

        notas = [
            "No instalar el UPS en ambientes húmedos, cerca de agua o en exposición directa al sol.",
            "La conexión a tierra es obligatoria antes de energizar el equipo.",
            "No bloquear las rejillas de ventilación; asegurar flujo de aire libre en todo momento.",
            "El suelo debe soportar el peso combinado del UPS y banco de baterías.",
            "Solo personal calificado y autorizado debe realizar la puesta en marcha.",
            "Los cables de alimentación y salida deben estar debidamente identificados y etiquetados.",
            "Mantener un registro de mantenimiento preventivo con periodicidad semestral.",
        ]
        self._imprimir_lista_bullets(notas)

        # Llenar espacio restante si queda mucho
        espacio_restante = self.h - self.get_y() - 25
        if espacio_restante > 25:
            self.ln(3)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, "Condiciones Ambientales:", 0, 1)
            self.ln(1)
            notas_extra = [
                "La sala debe contar con sistema de climatización independiente o dedicado.",
                "Evitar la instalación cercana a fuentes de interferencia electromagnética.",
                "Asegurar iluminación adecuada en la zona del UPS para labores de mantenimiento.",
                "En caso de incendio, utilizar exclusivamente extintores de CO2 o polvo químico seco.",
                "Verificar la capacidad estructural del piso para soportar el peso total del sistema.",
            ]
            self._imprimir_lista_bullets(notas_extra)

    # ==========================================================================
    # DIAGRAMAS (Páginas 6-7) — Imágenes llenan la página
    # ==========================================================================
    def _hoja_4_diagrama(self, ups=None, res=None):
        self._titulo_seccion("DIAGRAMAS DE CONEXIÓN")

        self.set_font('Arial', '', 8)
        self.set_text_color(*COLOR_GRIS)
        self.multi_cell(0, 4, "Los diagramas muestran la configuración eléctrica recomendada para "
                         "la alimentación AC y el banco de baterías DC del sistema UPS.")
        self.ln(2)

        # --- DIAGRAMA UNIFILAR AC ---
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 6, "Diagrama Unifilar AC", 0, 1)
        self.set_draw_color(*COLOR_ROJO)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

        imagen_unifilar_ok = False
        if self.imagenes_temp.get('unifilar_ac'):
            # margen_inferior=22: ref box(14mm) + footer(8mm)
            imagen_unifilar_ok = self._insertar_imagen_llena(
                self.imagenes_temp['unifilar_ac'], margen_inferior=22
            )

        if not imagen_unifilar_ok:
            self.set_font('Arial', 'I', 9)
            self.set_text_color(*COLOR_GRIS_CLARO)
            self.cell(0, 6, "Diagrama unifilar AC no disponible.", 0, 1, 'C')
        self.set_text_color(*COLOR_NEGRO)

        # Referencia técnica al pie — pegada al final, sin auto-break
        self.set_auto_page_break(False)
        y_ref = max(self.get_y(), self.h - 34)
        self.set_fill_color(245, 245, 250)
        self.rect(10, y_ref, 190, 14, 'F')
        self.set_xy(12, y_ref + 1)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(*COLOR_GRIS)
        self.cell(0, 4, "Ref: Arquitectura electrica de alimentacion AC - protecciones, conductores y conexiones principales segun NOM-001-SEDE-2012.", 0, 1)
        self.set_xy(12, y_ref + 6)
        self.cell(0, 4, "Los calibres y protecciones indicados son sugeridos. Validar con los calculos de ingenieria de la seccion 3.", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.set_auto_page_break(True, margin=20)

        # --- DIAGRAMA BATERÍAS DC (nueva página) ---
        tiene_bat_dc = bool(self.imagenes_temp.get('baterias_dc')) or (ups and ups.get('imagen_baterias_url'))
        if tiene_bat_dc:
            self.add_page()
            if not self._es_publicado:
                self._marca_agua_preview()

            self.set_font('Arial', 'B', 10)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, "Diagrama de Conexión de Baterías DC", 0, 1)
            self.set_draw_color(*COLOR_ROJO)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(2)

            self.set_font('Arial', '', 8)
            self.set_text_color(*COLOR_GRIS)
            self.multi_cell(0, 4, "Configuración del banco de baterías en serie/paralelo con interruptor de protección DC.")
            self.ln(2)
            self.set_text_color(*COLOR_NEGRO)

            imagen_bat_ok = False
            ruta_bat = self.imagenes_temp.get('baterias_dc')
            if not ruta_bat and ups and ups.get('imagen_baterias_url'):
                img_filename = os.path.basename(ups['imagen_baterias_url'])
                ruta_bat = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
                if not os.path.exists(ruta_bat):
                    ruta_bat = None

            if ruta_bat:
                # margen=28: summary box(20mm) + footer(8mm)
                margen_resumen = 28 if (res and res.get('baterias_total')) else 22
                imagen_bat_ok = self._insertar_imagen_llena(ruta_bat, margen_inferior=margen_resumen)

            if not imagen_bat_ok:
                self.set_font('Arial', 'I', 9)
                self.set_text_color(*COLOR_GRIS_CLARO)
                self.cell(0, 6, "Diagrama de baterías DC no disponible.", 0, 1, 'C')
                self.set_text_color(*COLOR_NEGRO)

            # Resumen de configuración DC — anclado al fondo, sin auto-break
            if res and res.get('baterias_total'):
                self.set_auto_page_break(False)
                y_box = max(self.get_y() + 1, self.h - 38)
                self.set_fill_color(245, 245, 250)
                self.rect(10, y_box, 190, 20, 'F')
                self.set_xy(12, y_box + 2)
                self.set_font('Arial', 'B', 8)
                self.set_text_color(*COLOR_ROJO)
                self.cell(0, 5, "Resumen de Configuración DC", 0, 1)
                self.set_xy(12, y_box + 9)
                self.set_font('Arial', '', 8)
                self.set_text_color(*COLOR_NEGRO)
                bat_total = self._int_display(res.get('baterias_total'))
                bat_str = self._int_display(res.get('numero_strings'))
                bat_ps = self._int_display(res.get('baterias_por_string'))
                bat_modelo = res.get('bateria_modelo', 'S/D')
                self.cell(0, 5, f"Total: {bat_total} baterías  |  {bat_str} string(s) x {bat_ps} en serie  |  Modelo: {bat_modelo}", 0, 1)
                self.set_auto_page_break(True, margin=20)

    # ==========================================================================
    # SECCIÓN FOTOGRAFÍA / LAYOUT (Páginas 7-8) — Imagen llena la página
    # ==========================================================================
    def _seccion_fotografia(self, titulo, imagen_url=None):
        self._titulo_seccion(titulo)

        # Descripción breve
        self.set_font('Arial', '', 8)
        self.set_text_color(*COLOR_GRIS)

        if "DISPOSICIÓN" in titulo.upper():
            desc = ("Distribución física recomendada de los equipos en el sitio de instalación, "
                    "incluyendo UPS, banco de baterías, tablero de distribución y espacios de ventilación.")
        elif "CONEXIÓN" in titulo.upper() and "BATERÍA" in titulo.upper():
            desc = ("Conexión física del banco de baterías al UPS: ubicación de terminales, "
                    "cableado DC, polaridad y protección del circuito de corriente directa.")
        elif "VENTILACIÓN" in titulo.upper():
            desc = "Sistema de ventilación recomendado para mantener la temperatura operativa del equipo."
        else:
            desc = "Imagen de referencia para la instalación del sistema."

        self.multi_cell(0, 4, desc)
        self.ln(3)
        self.set_text_color(*COLOR_NEGRO)

        imagen_ok = False

        # Determinar ruta de imagen
        ruta_img = None
        if "DISPOSICIÓN" in titulo.upper() and self.imagenes_temp.get('layout_equipos'):
            ruta_img = self.imagenes_temp['layout_equipos']
        elif imagen_url:
            img_filename = os.path.basename(imagen_url)
            ruta_img = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
            if not os.path.exists(ruta_img):
                ruta_img = None

        if ruta_img:
            # margen=20: ref box(10mm) + footer(10mm)
            imagen_ok = self._insertar_imagen_llena(ruta_img, margen_inferior=20)

        if not imagen_ok:
            self.set_font('Arial', 'I', 9)
            self.set_text_color(*COLOR_GRIS_CLARO)
            self.cell(0, 6, "Imagen no disponible.", 0, 1, 'C')
            self.set_text_color(*COLOR_NEGRO)

        # Pie de imagen — anclado al fondo, sin auto-break
        self.set_auto_page_break(False)
        y_pie = max(self.get_y() + 1, self.h - 28)
        self.set_fill_color(245, 245, 250)
        self.rect(10, y_pie, 190, 10, 'F')
        self.set_xy(12, y_pie + 2)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(*COLOR_GRIS)
        tipo_ref = titulo.title()
        self.cell(0, 5, f"Fig. - {tipo_ref}. Verificar dimensiones y configuracion en sitio antes de la instalacion.", 0, 1)
        self.set_text_color(*COLOR_NEGRO)
        self.set_auto_page_break(True, margin=20)

    # ==========================================================================
    # SECCIÓN VENTILACIÓN — Sin espacios en blanco
    # ==========================================================================
    def _seccion_tipo_ventilacion(self, tipo_ventilacion=None, tipo_ventilacion_data=None):
        self._titulo_seccion("TIPO DE VENTILACIÓN DEL SISTEMA")

        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)

        if tipo_ventilacion:
            intro_texto = (
                "El sistema de ventilación es un componente crítico para garantizar el funcionamiento "
                "óptimo y la vida útil del equipo UPS. Una ventilación adecuada previene el sobrecalentamiento, "
                "reduce el desgaste de componentes internos y asegura que el equipo opere dentro de los "
                "parámetros especificados por el fabricante."
            )
            self.multi_cell(0, 5, intro_texto)
            self.ln(4)

            # Recuadro tipo ventilación
            self.set_fill_color(*COLOR_FONDO)
            y_pos = self.get_y()
            self.rect(30, y_pos, 150, 20, 'F')
            self.set_xy(35, y_pos + 5)
            self.set_font('Arial', '', 9)
            self.set_text_color(*COLOR_NEGRO)
            self.cell(60, 6, "Sistema de Ventilación:", 0, 0)
            self.set_font('Arial', 'B', 13)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, tipo_ventilacion, 0, 1)
            self.set_y(y_pos + 24)

            # Descripción
            if tipo_ventilacion_data and tipo_ventilacion_data.get('descripcion'):
                self.set_font('Arial', '', 9)
                self.set_text_color(*COLOR_NEGRO)
                self.multi_cell(0, 5, tipo_ventilacion_data.get('descripcion'))
                self.ln(3)

            # Imagen de ventilación si existe
            if tipo_ventilacion_data and tipo_ventilacion_data.get('imagen_url'):
                img_filename = os.path.basename(tipo_ventilacion_data['imagen_url'])
                ruta_imagen = os.path.join(os.path.dirname(__file__), 'static', 'img', 'ups', img_filename)
                if os.path.exists(ruta_imagen):
                    self.set_font('Arial', 'B', 9)
                    self.set_text_color(*COLOR_ROJO)
                    self.cell(0, 6, "Diagrama de Referencia:", 0, 1)
                    self.ln(1)
                    self._insertar_imagen_llena(ruta_imagen, margen_inferior=22)

            # --- TABLA: Parámetros de Ventilación ---
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, "Parámetros de Ventilación Recomendados:", 0, 1)
            self.ln(1)

            self._dibujar_encabezado_tabla(["PARÁMETRO", "VALOR RECOMENDADO", "OBSERVACIÓN"])
            cfm = tipo_ventilacion_data.get('cfm_requeridos', 'Según modelo') if tipo_ventilacion_data else 'Según modelo'
            self._dibujar_fila_tabla("Flujo de Aire", f"{cfm} CFM mínimo" if isinstance(cfm, (int, float)) else str(cfm), "Caudal de extracción/inyección", resaltar_col2=True)
            self._dibujar_fila_tabla("Temperatura Operación", "20 °C - 25 °C", "Rango óptimo de operación", resaltar_col2=True)
            self._dibujar_fila_tabla("Temperatura Máxima", "40 °C absoluto", "No exceder bajo ningún motivo", resaltar_col2=True)
            self._dibujar_fila_tabla("Humedad Relativa", "30% - 70% HR", "Sin condensación", resaltar_col2=True)
            self._dibujar_fila_tabla("Filtración de Aire", "MERV 8 mínimo", "Prevenir polvo en componentes", resaltar_col2=True)
            self._dibujar_fila_tabla("Renovaciones/Hora", "6 - 10 renovaciones", "Según volumen de la sala", resaltar_col2=True)
            self.ln(3)

            # --- Consideraciones ---
            self.set_font('Arial', 'B', 9)
            self.set_text_color(*COLOR_ROJO)
            self.cell(0, 6, "Consideraciones Importantes:", 0, 1)
            self.ln(1)

            consideraciones = [
                "Mantener las rejillas de ventilación libres de obstrucciones en todo momento.",
                "Respetar las distancias mínimas especificadas (mínimo 800mm frontal y posterior).",
                "Verificar que la temperatura ambiente no exceda los 25 °C para vida útil óptima de baterías.",
                "Evitar la exposición directa a fuentes de calor, luz solar o ambientes húmedos.",
                "Realizar inspecciones periódicas para asegurar el flujo de aire adecuado.",
                "En ambientes con polvo o partículas, considerar filtros adicionales en las entradas de aire.",
            ]
            self._imprimir_lista_bullets(consideraciones)

            # --- Llenar espacio restante: Mantenimiento Preventivo ---
            espacio_restante = self.h - self.get_y() - 25
            if espacio_restante > 30:
                self.ln(3)
                self.set_font('Arial', 'B', 9)
                self.set_text_color(*COLOR_ROJO)
                self.cell(0, 6, "Plan de Mantenimiento de Ventilación:", 0, 1)
                self.ln(1)

                self._dibujar_encabezado_tabla(["ACTIVIDAD", "FRECUENCIA", "RESPONSABLE"])
                self._dibujar_fila_tabla("Inspección visual de rejillas", "Mensual", "Técnico de planta")
                self._dibujar_fila_tabla("Limpieza de filtros de aire", "Trimestral", "Técnico de planta")
                self._dibujar_fila_tabla("Verificación de temperatura", "Semanal", "Operador / Sistema SCADA")
                self._dibujar_fila_tabla("Revisión de extractores/ventiladores", "Semestral", "Servicio especializado")
                self._dibujar_fila_tabla("Calibración de sensores térmicos", "Anual", "Servicio especializado")

            # Si aún queda espacio, agregar notas adicionales
            espacio_restante = self.h - self.get_y() - 25
            if espacio_restante > 20:
                self.ln(3)
                notas_extra = [
                    "Documentar todas las lecturas de temperatura en bitácora de mantenimiento.",
                    "En caso de alarma por alta temperatura, verificar ventilación antes de reducir carga.",
                    "Instalar sensores de temperatura redundantes en instalaciones críticas.",
                ]
                for nota in notas_extra:
                    if self.get_y() < self.h - 30:
                        self._imprimir_lista_bullets([nota])

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