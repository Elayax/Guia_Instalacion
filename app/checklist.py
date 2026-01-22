import os
from fpdf import FPDF
from datetime import datetime
from PIL import Image
import tempfile

# Colores
COLOR_AZUL_HEADER = (69, 115, 172)
COLOR_AZUL_CLARO = (200, 220, 240)
COLOR_NEGRO = (0, 0, 0)
COLOR_GRIS = (128, 128, 128)

class ChecklistPDF(FPDF):
    """Generador de Checklist de UPS"""

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(False)

    def header(self):
        """Encabezado del checklist"""
        # Logo
        directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio, 'static', 'logo.png')

        if os.path.exists(ruta_logo):
            try:
                self.image(ruta_logo, 15, 15, 40)
            except:
                pass

        # Título
        self.set_xy(60, 20)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Checklist de UPS', 0, 0, 'C')

        # Borde de encabezado
        self.set_line_width(0.5)
        self.line(10, 38, 200, 38)

    def _preparar_imagen(self, ruta_imagen, ancho_mm=60, alto_mm=None):
        """Redimensiona y optimiza una imagen para el PDF"""
        try:
            img = Image.open(ruta_imagen)

            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            dpi = 300
            ancho_px = int(ancho_mm * dpi / 25.4)

            if alto_mm:
                alto_px = int(alto_mm * dpi / 25.4)
                img = img.resize((ancho_px, alto_px), Image.Resampling.LANCZOS)
            else:
                ratio = img.height / img.width
                alto_px = int(ancho_px * ratio)
                img = img.resize((ancho_px, alto_px), Image.Resampling.LANCZOS)

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG', quality=85, optimize=True)
            temp_file.close()

            return temp_file.name
        except Exception as e:
            print(f"Error preparando imagen {ruta_imagen}: {e}")
            return ruta_imagen

    def generar_checklist(self, datos, imagenes=None):
        """
        Genera el checklist completo

        Args:
            datos: dict con toda la información del proyecto
            imagenes: dict con las rutas de las imágenes opcionales
        """
        imagenes = imagenes or {}

        # Página 1
        self.add_page()
        self._pagina_1_datos_proyecto(datos)

        # Página 2
        self.add_page()
        self._pagina_2_puesta_marcha(datos)

        # Página 3
        self.add_page()
        self._pagina_3_criterios(datos)

        return self.output()

    def _pagina_1_datos_proyecto(self, datos):
        """Primera página: Datos del proyecto y condiciones"""
        self.set_y(45)

        # Fila de fecha
        self.set_font('Arial', 'B', 8)
        self.cell(10, 6, 'FECHA', 1, 0, 'C', True)
        self.set_fill_color(*COLOR_AZUL_CLARO)

        fecha_actual = datetime.now()
        self.cell(10, 6, 'DIA', 1, 0, 'C', True)
        self.cell(10, 6, 'MES', 1, 0, 'C', True)
        self.cell(10, 6, 'ANO', 1, 0, 'C', True)

        self.cell(90, 6, 'NOMBRE DEL PROYECTO', 1, 0, 'C', True)
        self.cell(50, 6, 'No. CONTRATO', 1, 1, 'C', True)

        # Valores de fecha
        self.set_font('Arial', '', 8)
        self.set_fill_color(255, 255, 255)
        self.cell(10, 6, '', 1, 0, 'C')  # FECHA vacío
        self.cell(10, 6, str(fecha_actual.day), 1, 0, 'C')
        self.cell(10, 6, str(fecha_actual.month), 1, 0, 'C')
        self.cell(10, 6, str(fecha_actual.year), 1, 0, 'C')
        self.cell(90, 6, datos.get('cliente_nombre', ''), 1, 0, 'L')
        self.cell(50, 6, datos.get('pedido', ''), 1, 1, 'C')

        # Área/Frente
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 8)
        self.cell(50, 6, 'AREA / FRENTE', 1, 0, 'C', True)
        self.cell(140, 6, 'DICIPLINA / CONCEPTO', 1, 1, 'C', True)

        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', '', 8)
        self.cell(50, 6, datos.get('area_frente', ''), 1, 0, 'L')
        self.cell(140, 6, '', 1, 1, 'L')

        # Información del equipo
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 8)
        self.cell(50, 6, 'NOMBRE DE JEFE DE AREA / FRENTE', 1, 0, 'C', True)
        self.cell(50, 6, 'MODELO DE UPS', 1, 0, 'C', True)
        self.cell(40, 6, 'CAPACIDAD', 1, 0, 'C', True)
        self.cell(50, 6, 'NUMERO DE SERIE', 1, 1, 'C', True)

        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', '', 8)
        self.cell(50, 6, datos.get('nombre_jefe', ''), 1, 0, 'L')
        self.cell(50, 6, datos.get('modelo_ups', ''), 1, 0, 'L')
        self.cell(40, 6, datos.get('capacidad', ''), 1, 0, 'C')
        self.cell(50, 6, '', 1, 1, 'L')

        self.ln(3)

        # Sección: Instalación Eléctrica
        self.set_fill_color(*COLOR_AZUL_HEADER)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 9)
        self.cell(190, 6, 'Instalacion Electrica', 1, 1, 'C', True)

        # Tabla de condiciones (simplificada)
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'B', 7)
        self.cell(95, 6, 'Condiciones de Entrada', 1, 0, 'C', True)
        self.cell(95, 6, 'Condiciones de Salida', 1, 1, 'C', True)

        # Contenido simplificado de condiciones
        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', '', 7)

        items_entrada = [
            '1.- Presencia de Voltaje',
            '2.- Interruptor de Entrada',
            '3.- Canalizacion',
            '4.- Cableado'
        ]

        items_salida = [
            '1.- Carga, Capacidad',
            '2.- Interruptor de Salida',
            '3.- Canalizacion',
            '4.- Cableado'
        ]

        for entrada, salida in zip(items_entrada, items_salida):
            self.cell(95, 5, entrada, 1, 0, 'L')
            self.cell(95, 5, salida, 1, 1, 'L')

        self.ln(2)

        # Observaciones
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 8)
        self.cell(190, 6, 'Observaciones para conexion entre banco de baterias y UPS:', 1, 1, 'L', True)

        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', '', 7)
        obs_texto = datos.get('observaciones_conexion', '')
        self.multi_cell(190, 4, obs_texto if obs_texto else ' ')

        self.ln(2)

        # Sección de imágenes
        self.set_fill_color(*COLOR_AZUL_HEADER)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 9)
        self.cell(190, 6, 'IMAGENES', 1, 1, 'C', True)

        # Espacio para imágenes (placeholder)
        self.set_fill_color(240, 240, 240)
        y_img = self.get_y()
        self.rect(10, y_img, 190, 40, 'D')
        self.set_xy(10, y_img + 17)
        self.set_text_color(150, 150, 150)
        self.set_font('Arial', 'I', 10)
        self.cell(190, 6, '[Espacio para imagenes del sitio]', 0, 1, 'C')

        self.set_y(y_img + 40)
        self.ln(3)

        # Sección de comentarios
        self.set_text_color(0, 0, 0)
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 7)
        self.cell(38, 5, 'COMENTARIOS:', 1, 0, 'L', True)
        self.cell(38, 5, '1 SEGURIDAD', 1, 0, 'C', True)
        self.cell(38, 5, '2 CALIDAD', 1, 0, 'C', True)
        self.cell(38, 5, '3  MEDIO AMBIENTE', 1, 0, 'C', True)
        self.cell(38, 5, '4 GENERAL', 1, 1, 'C', True)

        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', '', 7)
        comentarios = datos.get('comentarios', '')
        self.multi_cell(190, 4, comentarios if comentarios else ' ', 1)

        # Firmas
        self.ln(3)
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 8)
        self.cell(63, 6, 'LBS', 1, 0, 'C', True)
        self.cell(64, 6, '', 1, 0, 'C', True)
        self.cell(63, 6, 'CLIENTE', 1, 1, 'C', True)

        self.set_fill_color(255, 255, 255)
        self.cell(63, 10, '', 1, 0, 'C')
        self.cell(64, 10, '', 1, 0, 'C')
        self.cell(63, 10, '', 1, 1, 'C')

        self.set_font('Arial', '', 7)
        self.cell(63, 5, 'Jefe de Servicio', 1, 0, 'C')
        self.cell(64, 5, 'Elaboro', 1, 0, 'C')
        self.cell(63, 5, 'JEFE DE AREA / FRENTE', 1, 1, 'C')

    def _pagina_2_puesta_marcha(self, datos):
        """Segunda página: Puesta en marcha y referencias"""
        self.set_y(45)

        # Título
        self.set_fill_color(*COLOR_AZUL_HEADER)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        self.cell(190, 7, 'PUESTA EN MARCHA', 1, 1, 'C', True)

        # Texto de estimado cliente
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'B', 7)
        self.cell(190, 5, 'Estimado cliente:', 1, 1, 'L')

        self.set_font('Arial', '', 6)
        texto_intro = (
            "Para llevar a cabo la puesta en marcha del sistema UPS de manera adecuada y conforme a los procedimientos "
            "tecnicos del fabricante, es indispensable que el sitio se haya acondicionado previamente conforme a las especificaciones "
            "establecidas, asi como los puntos de revisión del presente Checklist denominado 'Criterios de Cumplimiento para Garantias del UPS'."
        )
        self.multi_cell(190, 3, texto_intro, 1)

        self.ln(1)

        texto_solicitud = (
            "Le solicitamos amablemente revisar la hoja 3 de este documento y firmarla, leida y comprendida, a fin de formalizar "
            "que esta enterado de los lineamientos y requisitos necesarios para la correcta puesta en marcha y la validez de la garantia del equipo."
        )
        self.multi_cell(190, 3, texto_solicitud, 1)

        self.ln(2)

        # Sección SITIO
        self.set_fill_color(*COLOR_AZUL_HEADER)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 9)
        self.cell(190, 6, 'SITIO', 1, 1, 'C', True)

        # Checklist items (simplificado)
        items_sitio = [
            "1.- Existen los espacios adecuados para la colocacion de gabinete de baterias",
            "2.- Piso: Tipo _______________",
            "3.- Analeja: Tipo _______________",
            "4.- Existe canalizacion para interconexion entre gabinetes? SI ____ NO ____",
            "5.- Existe Aire Acondicionado en el lugar donde quedara instalado el UPS? SI ____ NO ____",
            "6.- Limpieza de Area"
        ]

        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 7)
        for item in items_sitio:
            self.multi_cell(190, 4, item, 1)

        self.ln(2)

        # Dirección
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 8)
        self.cell(190, 6, 'DIRECCION DONDE ESTA EL EQUIPO INSTALADO', 1, 1, 'C', True)

        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', '', 8)
        direccion = datos.get('direccion_instalacion', '')
        self.multi_cell(190, 5, direccion if direccion else ' ', 1)

        self.ln(2)

        # Referencias y Contacto
        self.set_font('Arial', 'B', 8)
        self.cell(95, 6, 'REFERENCIAS PARA LLEGAR A SITIO', 1, 0, 'C')
        self.cell(95, 6, 'DATOS DE CONTACTO EN SITIO', 1, 1, 'C')

        self.set_font('Arial', '', 7)
        # Referencias (vacío)
        y_start = self.get_y()
        self.multi_cell(95, 4, '\n\n\n', 1)

        # Datos de contacto
        self.set_xy(105, y_start)
        self.cell(95, 4, f"NOMBRE: {datos.get('contacto_nombre', '')}", 1, 1, 'L')
        self.set_x(105)
        self.cell(95, 4, f"CARGO: {datos.get('contacto_cargo', '')}", 1, 1, 'L')
        self.set_x(105)
        self.cell(95, 4, f"TELEFONO: {datos.get('contacto_telefono', '')}", 1, 1, 'L')
        self.set_x(105)
        self.cell(95, 4, f"MOVIL: ", 1, 1, 'L')
        self.set_x(105)
        self.cell(95, 4, f"E-MAIL: {datos.get('contacto_email', '')}", 1, 1, 'L')

        self.ln(2)

        # Nota sobre conformación del sistema
        self.set_font('Arial', '', 6)
        nota = (
            "El sistema UPS esta conformado de: UPS, Gabinete de baterias y/o Gabinete de Transformadores, existen casos donde "
            "el mismo banco de bateria es interno."
        )
        self.multi_cell(190, 3, nota, 1)

        self.ln(2)

        # Sección de imágenes del sitio
        self.set_fill_color(*COLOR_AZUL_HEADER)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 9)
        self.cell(190, 6, 'IMAGENES DEL SITIO DE INSTALACION', 1, 1, 'C', True)

        self.set_fill_color(240, 240, 240)
        y_img = self.get_y()
        self.rect(10, y_img, 190, 35, 'D')
        self.set_xy(10, y_img + 15)
        self.set_text_color(150, 150, 150)
        self.set_font('Arial', 'I', 10)
        self.cell(190, 6, '[Espacio para imagenes del sitio de instalacion]', 0, 1, 'C')

        self.set_y(y_img + 35)
        self.ln(3)

        # Firmas
        self.set_text_color(0, 0, 0)
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 8)
        self.cell(63, 6, 'LBS', 1, 0, 'C', True)
        self.cell(64, 6, '', 1, 0, 'C', True)
        self.cell(63, 6, 'CLIENTE', 1, 1, 'C', True)

        self.set_fill_color(255, 255, 255)
        self.cell(63, 10, '', 1, 0, 'C')
        self.cell(64, 10, '', 1, 0, 'C')
        self.cell(63, 10, '', 1, 1, 'C')

        self.set_font('Arial', '', 7)
        self.cell(63, 5, 'Jefe de Servicio', 1, 0, 'C')
        self.cell(64, 5, 'Elaboro', 1, 0, 'C')
        self.cell(63, 5, 'JEFE DE AREA / FRENTE', 1, 1, 'C')

    def _pagina_3_criterios(self, datos):
        """Tercera página: Criterios de cumplimiento para garantías"""
        self.set_y(45)

        # Título
        self.set_fill_color(*COLOR_AZUL_HEADER)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 9)
        self.cell(190, 6, 'CRITERIOS DE CUMPLIMIENTO PARA GARANTIAS DEL UPS', 1, 1, 'C', True)

        # Lista de criterios
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 6)

        criterios = [
            "1. Condiciones del Area de Instalacion\n   El cuarto del UPS debe encontrarse en buen estado estructural, limpio y libre de humedad.",
            "2. Control Ambiental\n   Contar con sistema de aire acondicionado suficiente para mantener temperatura recomendada (20C - 25C).",
            "3. Condiciones Electricas\n   La instalacion debe cumplir con las normas electricas aplicables.",
            "4. Ubicacion Fisica\n   El UPS debe colocarse en superficie nivelada y estable.",
            "5. Operacion y Seguridad\n   Prohibido alterar tapas o cubiertas del personal no certificado.",
            "6. Consideraciones que invalidan la garantia\n   Instalacion en condiciones ambientales fuera de especificacion."
        ]

        for criterio in criterios:
            self.multi_cell(190, 4, criterio, 1)
            self.ln(1)

        self.ln(5)

        # Texto de advertencia
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 7)
        texto_advertencia = (
            "EN CASO DE QUE LA INSTALACION NO CUMPLA CON LAS ESPECIFICACIONES TECNICAS MINIMAS ESTABLECIDAS EN LA GUIA "
            "DE INSTALACION, EL CLIENTE ASUME ALGUNA FALLA O DANO EN EL EQUIPO COMO RESULTADO DE DICHAS CONDICIONES."
        )
        self.multi_cell(190, 4, texto_advertencia, 1, 'C', True)

        self.ln(5)

        # Declaración de conformidad
        self.set_fill_color(255, 255, 255)
        self.set_font('Arial', '', 7)
        self.cell(63, 5, 'NOMBRE:', 1, 0, 'L')
        self.cell(64, 5, '', 1, 0)
        self.cell(63, 5, 'FIRMA:', 1, 1, 'L')

        self.cell(63, 10, '', 1, 0)
        self.cell(64, 10, '', 1, 0)
        self.cell(63, 10, '', 1, 1)

        self.ln(10)

        # Firmas finales
        self.set_fill_color(*COLOR_AZUL_CLARO)
        self.set_font('Arial', 'B', 8)
        self.cell(63, 6, 'LBS', 1, 0, 'C', True)
        self.cell(64, 6, '', 1, 0, 'C', True)
        self.cell(63, 6, 'CLIENTE', 1, 1, 'C', True)

        self.set_fill_color(255, 255, 255)
        self.cell(63, 10, '', 1, 0, 'C')
        self.cell(64, 10, '', 1, 0, 'C')
        self.cell(63, 10, '', 1, 1, 'C')

        self.set_font('Arial', '', 7)
        self.cell(63, 5, 'Jefe de Servicio', 1, 0, 'C')
        self.cell(64, 5, 'Elaboro', 1, 0, 'C')
        self.cell(63, 5, 'JEFE DE AREA / FRENTE', 1, 1, 'C')
