import os
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
    """
    Generador Modular de Reportes.
    """

    def header(self):
        # 1. LOGO
        directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio, 'static', 'logo.png')

        try:
            if os.path.exists(ruta_logo):
                self.image(ruta_logo, 10, 10, 33) 
            else:
                print(f"ADVERTENCIA: No se encontro el logo en {ruta_logo}")
                raise FileNotFoundError("Archivo de logo no encontrado")
        except Exception as e:
            print(f"ERROR CARGANDO LOGO: {e}")
            self.set_fill_color(*COLOR_ROJO)
            self.rect(10, 10, 33, 15, 'F')

        # 2. ENCABEZADO
        self.set_y(10)
        self.set_x(50) 
        self.set_font('Arial', 'B', 16)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 8, 'GUIA DE INSTALACION Y MEMORIA TECNICA', 0, 1, 'L') 
        
        self.set_x(50)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_GRIS_CLARO)
        self.cell(0, 5, 'SISTEMA DE ENERGIA ININTERRUMPIDA (UPS) ', 0, 1, 'L')
        
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
    def generar_cuerpo(self, datos, res, bateria=None, es_publicado=False):
        
        # HOJA 1: PORTADA (NUEVA)
        self.add_page()
        self._hoja_portada(datos, res)
        
        # HOJA 2: NORMAS Y SEGURIDAD (ANTES HOJA 1)
        self.add_page()
        
        # --- MARCA DE AGUA ---
        if not es_publicado:
            self.set_font('Arial', 'B', 40) # Bajé un poco la fuente para que quepa mejor
            self.set_text_color(230, 230, 230) # Más clarito para que no estorbe
            self.set_xy(10, 100)
            self.cell(0, 10, "VISTA PREVIA - BORRADOR", 0, 0, 'C')
            self.set_xy(10, 120)
            self.cell(0, 10, "NO VALIDO PARA INSTALACION", 0, 0, 'C')
            
            # Restauramos color normal
            self.set_text_color(*COLOR_NEGRO)
        
        # --- IMPORTANTE: RESETEAR CURSOR ---
        # Regresamos el "lápiz" arriba para escribir el texto normal
        self.set_y(40) 

        self._hoja_1_seguridad_instalacion()
        
        # HOJA 3: DATOS SITIO (ANTES HOJA 2)
        self.add_page()
        if not es_publicado: 
            self.set_font('Arial', 'B', 40)
            self.set_text_color(230, 230, 230)
            self.set_xy(10, 100)
            self.cell(0, 10, "VISTA PREVIA", 0, 0, 'C')
            self.set_text_color(*COLOR_NEGRO)
        
        # --- RESETEAR CURSOR HOJA 2 ---
        self.set_y(40)

        self._hoja_2_datos_sitio(datos, res)
        
        # HOJA 4: INGENIERIA (ANTES HOJA 3)
        self.add_page()
        if not es_publicado: self._marca_agua_simple()
        self._hoja_3_ingenieria(datos, res)
        
        # SECCIÓN BATERÍAS (NUEVA - EN LA MISMA HOJA 4 O NUEVA SI NO CABE)
        # Para limpieza, forzamos nueva página si hay datos, o lo agregamos a continuación
        self.ln(5)
        self._seccion_baterias(bateria)
        
        # HOJA 5: DIAGRAMA (ANTES HOJA 4)
        self.add_page()
        if not es_publicado: self._marca_agua_simple()
        self._hoja_4_diagrama()

        return self.output()

    def _marca_agua_simple(self):
        self.set_font('Arial', 'B', 40)
        self.set_text_color(240, 240, 240)
        self.set_xy(10, 100)
        self.cell(0, 10, "VISTA PREVIA", 0, 0, 'C')
        self.set_text_color(*COLOR_NEGRO)
        self.set_y(40)

    # ==========================================================================
    # HOJA 1: PORTADA
    # ==========================================================================
    def _hoja_portada(self, datos, res):
        self.ln(40)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 12, "MEMORIA TECNICA", 0, 1, 'C')
        self.cell(0, 12, "DE INSTALACION UPS", 0, 1, 'C')
        
        self.ln(20)
        self.set_font('Arial', '', 12)
        self.set_text_color(*COLOR_NEGRO)
        
        # Caja de Información
        self.set_fill_color(245, 245, 245)
        self.rect(35, 110, 140, 70, 'F')
        
        self.set_y(120)
        self._fila_portada("PROYECTO:", datos.get('nombre', 'S/D'))
        self._fila_portada("UBICACION:", f"{datos.get('lat', '')}, {datos.get('lon', '')}")
        self._fila_portada("EQUIPO:", res.get('modelo_nombre', 'S/D'))
        self._fila_portada("CAPACIDAD:", f"{res.get('kva', 'S/D')} kVA")
        self._fila_portada("FECHA:", datetime.now().strftime("%d/%m/%Y"))

    def _fila_portada(self, label, value):
        self.set_x(45)
        self.set_font('Arial', 'B', 11)
        self.cell(40, 10, label, 0, 0, 'L')
        self.set_font('Arial', '', 11)
        self.cell(90, 10, str(value), 0, 1, 'L')

    # ==========================================================================
    # HOJA 1: NORMAS Y SEGURIDAD
    # ==========================================================================
    def _hoja_1_seguridad_instalacion(self):
        self._titulo_seccion("1. NORMAS DE SEGURIDAD")
        
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        
        intro = (
            "Con esta documentacion, LBS ofrece al usuario toda la informacion necesaria sobre el uso correcto del UPS. "
            "Antes de instalar o manejar el UPS lea esta GUIA, recomendamos guarde para una futura consulta."
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
            "Si observa algun danio, no instalar o arrancar el UPS y contactar con el Centro de Servicio mas cercano inmediatamente."
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
    def _hoja_2_datos_sitio(self, datos, res):
        self._titulo_seccion("2. DATOS DEL SITIO DE INSTALACION")

        self.set_fill_color(*COLOR_FONDO)
        self.set_font('Arial', '', 9)
        
        y_inicio = self.get_y()
        self.rect(10, y_inicio, 190, 24, 'F')
        
        col1 = 12
        col2 = 110
        
        # Recuperamos nombre compuesto si viene, sino intentamos armarlo
        nombre_completo = str(datos.get('nombre', 'SIN NOMBRE')).upper()
        
        self.set_xy(col1, y_inicio + 2)
        self.cell(90, 6, f"Proyecto / Cliente:  {nombre_completo}", 0, 1)
        self.set_x(col1)
        self.cell(90, 6, f"Capacidad UPS:       {datos.get('kva')} kVA", 0, 1)
        self.set_x(col1)
        self.cell(90, 6, f"Voltaje Operacion:   {datos.get('voltaje')} VCA", 0, 1)

        self.set_xy(col2, y_inicio + 2)
        self.cell(90, 6, f"Configuracion:       {datos.get('fases')} Fases + N + Tierra", 0, 1)
        self.set_x(col2)
        self.cell(90, 6, f"Longitud Circuito:   {datos.get('longitud')} metros", 0, 1)
        self.set_x(col2)
        self.cell(90, 6, f"Ubicacion:           {datos.get('lat')}, {datos.get('lon')}", 0, 1)
        
        # Agregamos Tiempo de Respaldo
        self.set_x(col1)
        respaldo = datos.get('tiempo_respaldo')
        txt_respaldo = f"{respaldo} minutos" if respaldo else "Estandar"
        self.cell(90, 6, f"Tiempo Respaldo:     {txt_respaldo}", 0, 1)
        
        self.set_y(y_inicio + 28)
        self.ln(5)

        # --- NUEVA SECCIÓN: DIMENSIONES ---
        self._subtitulo_rojo("DIMENSIONES Y ESPACIO FISICO")
        self.set_font('Arial', '', 9)
        self.set_text_color(*COLOR_NEGRO)
        
        largo = datos.get('dim_largo', 'S/D')
        ancho = datos.get('dim_ancho', 'S/D')
        alto = datos.get('dim_alto', 'S/D')
        peso = datos.get('peso', 'S/D')
        modelo = datos.get('modelo_nombre', 'el equipo')

        texto_dims = (
            f"Para el correcto emplazamiento del gabinete modelo {modelo}, se deben considerar sus dimensiones fisicas de "
            f"{largo} mm de largo (profundidad), {ancho} mm de ancho (frente) y {alto} mm de alto. "
            f"El equipo ocupa un volumen considerable en sala, por lo que se recomienda prever un espacio libre adicional perimetral para ventilacion y mantenimiento. "
            f"El peso operativo aproximado es de {peso} kg, dato critico para verificar la capacidad de carga del suelo en el sitio de instalacion."
        )
        self.multi_cell(0, 5, texto_dims)
        self.ln(5)

    # ==========================================================================
    # HOJA 3: INGENIERÍA
    # ==========================================================================
    def _hoja_3_ingenieria(self, datos, res):
        self._titulo_seccion("3. ESPECIFICACIONES DE INSTALACION ELECTRICA")

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
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*COLOR_NEGRO)
        self.cell(0, 8, "VERIFICACION DE DESEMPENIO:", 0, 1)
        
        self.set_font('Arial', '', 9)
        icono = "OK" if res['dv_pct'] <= 3.0 else "ALERTA"
        self.cell(0, 5, f"- Caida de Tension Calculada: {res['dv_pct']}% ..... [{icono}]", 0, 1)
        self.cell(0, 5, f"- Ampacidad Real del Conductor (con derrateo): {res['i_real_cable']} A", 0, 1)

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
    def _seccion_baterias(self, bateria):
        self._titulo_seccion("4. BANCO DE BATERIAS")
        
        if not bateria:
            bateria = {}

        # Preparar datos con valor por defecto S/D
        modelo = bateria.get('modelo', 'S/D')
        voltaje = f"{bateria.get('voltaje_nominal', 'S/D')} V"
        capacidad = f"{bateria.get('capacidad_nominal_ah', 'S/D')} Ah"
        resistencia = f"{bateria.get('resistencia_interna_mohm', 'S/D')} mOhm"
        dims = f"{bateria.get('largo_mm', 'S/D')}x{bateria.get('ancho_mm', 'S/D')}x{bateria.get('alto_total_mm', 'S/D')} mm"
        peso = f"{bateria.get('peso_kg', 'S/D')} kg"
        terminal = bateria.get('tipo_terminal', 'S/D')

        self._dibujar_encabezado_tabla(["PARAMETRO", "VALOR", "UNIDAD"])
        self._dibujar_fila_tabla("Modelo Bateria", str(modelo), "-")
        self._dibujar_fila_tabla("Voltaje Nominal", str(voltaje), "Volts DC")
        self._dibujar_fila_tabla("Capacidad", str(capacidad), "Amper-Hora")
        self._dibujar_fila_tabla("Resistencia Interna", str(resistencia), "mOhm")
        self._dibujar_fila_tabla("Dimensiones", str(dims), "Milimetros")
        self._dibujar_fila_tabla("Peso Aprox.", str(peso), "Kilogramos")
        self._dibujar_fila_tabla("Tipo Terminal", str(terminal), "-")
        self.ln(5)

    # ==========================================================================
    # HOJA 4: DIAGRAMA
    # ==========================================================================
    def _hoja_4_diagrama(self):
        self._titulo_seccion("5. DIAGRAMA DE CONEXION SUGERIDO")
        
        self.set_fill_color(230, 230, 230)
        y = self.get_y()
        self.rect(10, y, 190, 55, 'F')
        
        self.set_xy(10, y + 25)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(150, 150, 150) 
        self.cell(190, 10, "[ ESPACIO PARA DIAGRAMA UNIFILAR ]", 0, 0, 'C')

    # ==========================================================================
    # HERRAMIENTAS REUTILIZABLES (HELPERS)
    # ==========================================================================
    def _titulo_seccion(self, texto):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*COLOR_ROJO)
        self.cell(0, 8, texto.upper(), 0, 1, 'L')
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