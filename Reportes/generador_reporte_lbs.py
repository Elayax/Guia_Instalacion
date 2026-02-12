#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Reportes de Servicio LBS - Versión Mejorada 2.0
============================================================

Este generador replica fielmente el diseño del reporte oficial de LBS,
trabajando por módulos independientes para facilitar mantenimiento.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime


class ReporteLBSMejorado:
    """
    Generador mejorado de reportes LBS con diseño fiel al original.
    """
    
    # ============ COLORES CORPORATIVOS ============
    COLOR_ROJO_BORDE = colors.HexColor('#C00000')      # Rojo oscuro para bordes
    COLOR_ROJO_TEXTO = colors.HexColor('#C00000')       # Rojo para folio
    COLOR_ROJO_CLARO = colors.HexColor('#FFC7CE')       # Fondo rojo claro
    COLOR_NEGRO = colors.black
    COLOR_GRIS = colors.HexColor('#666666')
    
    # ============ DIMENSIONES ============
    ANCHO_PAGINA = letter[0]
    ALTO_PAGINA = letter[1]
    
    # Márgenes
    MARGEN_IZQ = 15 * mm
    MARGEN_DER = 15 * mm
    MARGEN_SUP = 15 * mm
    MARGEN_INF = 15 * mm
    
    # Ancho útil
    ANCHO_UTIL = ANCHO_PAGINA - MARGEN_IZQ - MARGEN_DER
    
    # Tamaños de fuente
    FONT_TITULO = 14
    FONT_SECCION = 9
    FONT_LABEL = 7
    FONT_DATO = 8
    FONT_MINI = 6
    
    def __init__(self):
        """Inicializa el generador"""
        self.canvas = None
        self.y_actual = 0
        
    def generar_reporte(self, archivo_salida):
        """
        Genera el reporte completo en PDF.
        
        Args:
            archivo_salida (str): Ruta del archivo PDF a generar
        """
        self.canvas = canvas.Canvas(archivo_salida, pagesize=letter)
        
        # Generar página 1
        self._generar_pagina_1()
        
        # Guardar PDF
        self.canvas.save()
        print(f"✓ Reporte generado: {archivo_salida}")
        
    def _generar_pagina_1(self):
        """Genera la primera página del reporte"""
        c = self.canvas
        
        # Resetear posición Y desde arriba
        self.y_actual = self.ALTO_PAGINA - self.MARGEN_SUP
        
        # 1. Encabezado con logo y título
        self.y_actual = self._modulo_encabezado(c, self.y_actual)
        
        # 2. Información General del Cliente y Equipo
        self.y_actual = self._modulo_informacion_general(c, self.y_actual - 5*mm)
        
        # 3. Parámetros de Entrada y Salida
        self.y_actual = self._modulo_parametros_entrada_salida(c, self.y_actual - 5*mm)
        
        # 4. Operación del Sistema UPS
        self.y_actual = self._modulo_operacion_sistema(c, self.y_actual - 5*mm)
        
        # 5. Condiciones de Ventiladores y Capacitores
        self.y_actual = self._modulo_ventiladores_capacitores(c, self.y_actual - 5*mm)
        
        # 6. Limpieza al UPS
        self.y_actual = self._modulo_limpieza(c, self.y_actual - 5*mm)
        
        # 7. Firmas
        self._modulo_firmas(c, self.MARGEN_INF + 20*mm)
        
    # ========================================================================
    #                           MÓDULO 1: ENCABEZADO
    # ========================================================================
    
    def _modulo_encabezado(self, c, y_inicio):
        """
        Dibuja el encabezado del reporte con logo, título y datos de contacto.
        
        Returns:
            float: Nueva posición Y después del encabezado
        """
        x = self.MARGEN_IZQ
        y = y_inicio
        
        # Logo LBS (lado izquierdo)
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(self.COLOR_ROJO_BORDE)
        c.drawString(x, y, "🎵")
        c.setFillColor(self.COLOR_NEGRO)
        
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(self.COLOR_GRIS)
        c.drawString(x + 8*mm, y, "LBS")
        c.setFillColor(self.COLOR_NEGRO)
        
        # REPORTE DE SERVICIO (centro)
        c.setFont("Helvetica-Bold", self.FONT_TITULO)
        titulo_x = self.ANCHO_PAGINA / 2
        c.drawCentredString(titulo_x, y + 2*mm, "REPORTE DE SERVICIO")
        
        # Datos de contacto (centro, líneas pequeñas)
        c.setFont("Helvetica", self.FONT_MINI)
        y_contacto = y - 3*mm
        c.drawCentredString(titulo_x, y_contacto, 
                          "Calz. De la Viga 918, Col. Santa Cruz, Alcaldía Iztacalco C.P. 08910, CDMX")
        y_contacto -= 2.5*mm
        c.drawCentredString(titulo_x, y_contacto,
                          "lbs@lemonroy.com  /  servicio@lemonroy.com  /  www.lemonroy.com")
        y_contacto -= 2.5*mm
        c.drawCentredString(titulo_x, y_contacto,
                          "Atención al Cliente  24 x 7")
        
        # Folio (lado derecho en rojo)
        folio_x = self.ANCHO_PAGINA - self.MARGEN_DER
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.COLOR_ROJO_TEXTO)
        c.drawRightString(folio_x, y + 2*mm, "20105")
        c.setFillColor(self.COLOR_NEGRO)
        
        # Código de página (lado derecho)
        c.setFont("Helvetica", self.FONT_MINI)
        c.drawRightString(folio_x, y - 2*mm, "Página 1 de 5")
        c.drawRightString(folio_x, y - 5*mm, "PFO-EIPM-010")
        
        return y_contacto - 5*mm
    
    # ========================================================================
    #                    MÓDULO 2: INFORMACIÓN GENERAL
    # ========================================================================
    
    def _modulo_informacion_general(self, c, y_inicio):
        """
        Dibuja el módulo de información general del cliente y equipo.
        
        Returns:
            float: Nueva posición Y después del módulo
        """
        x = self.MARGEN_IZQ
        y = y_inicio
        altura_modulo = 32*mm
        
        # Rectángulo principal con borde rojo
        c.setStrokeColor(self.COLOR_ROJO_BORDE)
        c.setLineWidth(1.5)
        c.rect(x, y - altura_modulo, self.ANCHO_UTIL, altura_modulo)
        
        # Posición interna
        y_int = y - 4*mm
        x_int = x + 2*mm
        
        # ===== LÍNEA 1: Cliente, Usuario, Fecha =====
        c.setFont("Helvetica", self.FONT_LABEL)
        c.setFillColor(self.COLOR_NEGRO)
        
        # Cliente
        c.drawString(x_int, y_int, "Cliente:")
        # Línea para escribir
        c.setLineWidth(0.5)
        c.setStrokeColor(self.COLOR_NEGRO)
        c.line(x_int + 12*mm, y_int - 1*mm, x_int + 100*mm, y_int - 1*mm)
        
        # Usuario (mitad derecha)
        x_usuario = x + self.ANCHO_UTIL/2
        c.drawString(x_usuario, y_int, "Usuario:")
        c.line(x_usuario + 15*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 50*mm, y_int - 1*mm)
        
        # Fecha (extremo derecho)
        x_fecha = x + self.ANCHO_UTIL - 40*mm
        c.drawString(x_fecha, y_int, "Fecha:")
        c.line(x_fecha + 12*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== LÍNEA 2: Dirección, SID(GE) =====
        y_int -= 5*mm
        c.drawString(x_int, y_int, "Dirección:")
        c.line(x_int + 18*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 40*mm, y_int - 1*mm)
        
        # SID checkboxes
        x_sid = x + self.ANCHO_UTIL - 35*mm
        c.drawString(x_sid, y_int, "SID (GE):")
        # Checkbox Si
        c.rect(x_sid + 16*mm, y_int - 2*mm, 3*mm, 3*mm)
        c.setFont("Helvetica", 6)
        c.drawString(x_sid + 20*mm, y_int, "Si")
        # Checkbox No
        c.setFont("Helvetica", self.FONT_LABEL)
        c.rect(x_sid + 25*mm, y_int - 2*mm, 3*mm, 3*mm)
        c.setFont("Helvetica", 6)
        c.drawString(x_sid + 29*mm, y_int, "No")
        
        # ===== LÍNEA 3: Ubicación =====
        y_int -= 5*mm
        c.setFont("Helvetica", self.FONT_LABEL)
        c.drawString(x_int, y_int, "Ubicación:")
        c.line(x_int + 18*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== LÍNEA 4: Marca, Modelo, Capacidad, Horas UPS, No. de Serie =====
        y_int -= 6*mm
        
        # Marca
        c.drawString(x_int, y_int, "Marca:")
        c.line(x_int + 12*mm, y_int - 1*mm, x_int + 40*mm, y_int - 1*mm)
        
        # Modelo
        x_modelo = x_int + 45*mm
        c.drawString(x_modelo, y_int, "Modelo:")
        c.line(x_modelo + 14*mm, y_int - 1*mm, x_modelo + 45*mm, y_int - 1*mm)
        
        # Capacidad
        x_cap = x_modelo + 50*mm
        c.drawString(x_cap, y_int, "Capacidad:")
        c.line(x_cap + 18*mm, y_int - 1*mm, x_cap + 35*mm, y_int - 1*mm)
        
        # No de Serie (siguiente línea más corta o en la misma línea)
        x_serie = x_cap + 40*mm
        c.drawString(x_serie, y_int, "No. de Serie:")
        c.line(x_serie + 20*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== LÍNEA 5: Horas UPS, UPS (VSW), Display =====
        y_int -= 5*mm
        
        # Horas UPS
        c.drawString(x_int, y_int, "Horas UPS:")
        c.line(x_int + 18*mm, y_int - 1*mm, x_int + 35*mm, y_int - 1*mm)
        
        # Horas Inv
        x_hinv = x_int + 40*mm
        c.drawString(x_hinv, y_int, "Horas Inv.:")
        c.line(x_hinv + 18*mm, y_int - 1*mm, x_hinv + 35*mm, y_int - 1*mm)
        
        # UPS (VSW)
        x_vsw = x_hinv + 40*mm
        c.drawString(x_vsw, y_int, "UPS (VSW):")
        c.line(x_vsw + 18*mm, y_int - 1*mm, x_vsw + 35*mm, y_int - 1*mm)
        
        # Display (VSW)
        x_disp = x_vsw + 40*mm
        c.drawString(x_disp, y_int, "Display (VSW):")
        c.line(x_disp + 24*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== LÍNEA 6: Tipo de servicio - CHECKBOXES =====
        y_int -= 6*mm
        c.drawString(x_int, y_int, "Tipo de servicio")
        
        # Checkboxes horizontales
        y_checks = y_int - 5*mm
        x_check = x_int
        
        checkboxes = [
            ("☐ FPM", "☐ MITO", "☐ Cambio de Baterías", "☐ Reparación", "☑ Diagnóstico", 
             "☐ Pruebas de Laboratorio", "Otros")
        ]
        
        c.setFont("Helvetica", self.FONT_LABEL)
        espaciado = 28*mm
        
        # Primera fila de checkboxes
        c.drawString(x_check, y_checks, "☐ FPM")
        x_check += espaciado
        c.drawString(x_check, y_checks, "☐ MITO")
        x_check += espaciado
        c.drawString(x_check, y_checks, "☐ Cambio de Baterías")
        x_check += espaciado + 10*mm
        c.drawString(x_check, y_checks, "☐ Reparación")
        x_check += espaciado
        c.drawString(x_check, y_checks, "☑ Diagnóstico")
        
        # Segunda fila
        y_checks -= 4*mm
        x_check = x_int
        c.drawString(x_check, y_checks, "☐ Capacitativa")
        x_check += espaciado
        c.drawString(x_check, y_checks, "☐ Si")
        x_check += 8*mm
        c.drawString(x_check, y_checks, "☑ No")
        
        x_check += 12*mm
        c.drawString(x_check, y_checks, "Tipo de carga:")
        x_check += 24*mm
        c.drawString(x_check, y_checks, "☐ Inductiva")
        x_check += 20*mm
        c.drawString(x_check, y_checks, "☐ Capacitiva")
        x_check += 22*mm
        c.drawString(x_check, y_checks, "☐ Resistiva")
        x_check += 20*mm
        c.drawString(x_check, y_checks, "☑ Lineal")
        
        # Tercera fila
        y_checks -= 4*mm
        x_check = x_int
        c.drawString(x_check, y_checks, "Accesorios RPA:")
        x_check += 28*mm
        c.drawString(x_check, y_checks, "☐ Si")
        x_check += 8*mm
        c.drawString(x_check, y_checks, "☑ No")
        
        x_check += 12*mm
        c.drawString(x_check, y_checks, "SNMP:")
        x_check += 14*mm
        c.drawString(x_check, y_checks, "☑ Si")
        x_check += 8*mm
        c.drawString(x_check, y_checks, "☐ No")
        
        x_check += 12*mm
        c.drawString(x_check, y_checks, "No. de Sobrecargas:")
        c.line(x_check + 32*mm, y_checks - 1*mm, x + self.ANCHO_UTIL - 50*mm, y_checks - 1*mm)
        
        # Equipo UPS (derecha)
        x_equipo = x + self.ANCHO_UTIL - 45*mm
        c.drawString(x_equipo, y_checks, "El equipo UPS es:")
        x_equipo += 26*mm
        c.drawString(x_equipo, y_checks, "☐ Monolítico")
        x_equipo += 22*mm
        c.drawString(x_equipo, y_checks, "☑ Modular")
        
        return y - altura_modulo
    
    # ========================================================================
    #              MÓDULO 3: PARÁMETROS DE ENTRADA Y SALIDA
    # ========================================================================
    
    def _modulo_parametros_entrada_salida(self, c, y_inicio):
        """
        Dibuja el módulo de parámetros eléctricos de entrada y salida.
        
        Returns:
            float: Nueva posición Y después del módulo
        """
        x = self.MARGEN_IZQ
        y = y_inicio
        altura_modulo = 42*mm
        
        # Título de la sección
        c.setFont("Helvetica-Bold", self.FONT_SECCION)
        c.setFillColor(self.COLOR_NEGRO)
        c.drawString(x, y, "PARÁMETROS DE ENTRADA Y SALIDA:")
        
        y -= 4*mm
        
        # Rectángulo principal
        c.setStrokeColor(self.COLOR_ROJO_BORDE)
        c.setLineWidth(1.5)
        c.rect(x, y - altura_modulo, self.ANCHO_UTIL, altura_modulo)
        
        # Contenido interno
        y_int = y - 4*mm
        x_int = x + 2*mm
        
        # ===== PRIMERA LÍNEA: Medición de Voltaje en =====
        c.setFont("Helvetica", self.FONT_LABEL)
        c.drawString(x_int, y_int, "Medición de Voltaje en:")
        
        # Checkboxes de punto de medición
        x_check = x_int + 40*mm
        espaciado_check = 30*mm
        
        c.drawString(x_check, y_int, "☐ Tablero")
        x_check += espaciado_check
        c.drawString(x_check, y_int, "☐ Interruptor")
        x_check += espaciado_check
        c.drawString(x_check, y_int, "☐ En Contacto Duplex")
        x_check += espaciado_check + 5*mm
        c.drawString(x_check, y_int, "☑ UPS")
        x_check += 20*mm
        c.drawString(x_check, y_int, "☑ En Transformadores")
        x_check += espaciado_check + 8*mm
        c.drawString(x_check, y_int, "☐ STS")
        x_check += 18*mm
        c.drawString(x_check, y_int, "☐ ATS")
        
        # ===== SEGUNDA LÍNEA: Interruptores =====
        y_int -= 5*mm
        c.drawString(x_int, y_int, "Interruptor de Entrada:")
        
        x_check = x_int + 40*mm
        c.drawString(x_check, y_int, "☑ Si")
        c.drawString(x_check + 8*mm, y_int, "☐ No")
        c.drawString(x_check + 16*mm, y_int, "☐ N/A")
        
        c.drawString(x_check + 28*mm, y_int, "Capacidad:")
        c.line(x_check + 48*mm, y_int - 1*mm, x_check + 75*mm, y_int - 1*mm)
        
        # Observaciones (mitad derecha)
        x_obs = x + self.ANCHO_UTIL/2 + 10*mm
        c.drawString(x_obs, y_int, "Observaciones:")
        c.line(x_obs + 26*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== TERCERA LÍNEA: Interruptor de Salida =====
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Interruptor de Salida:")
        
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 8*mm, y_int, "☐ No")
        c.drawString(x_check + 16*mm, y_int, "☐ N/A")
        
        c.drawString(x_check + 28*mm, y_int, "Capacidad:")
        c.line(x_check + 48*mm, y_int - 1*mm, x_check + 75*mm, y_int - 1*mm)
        
        c.drawString(x_obs, y_int, "Observaciones:")
        c.line(x_obs + 26*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== CUARTA LÍNEA: Parámetros de Entrada (encabezado) =====
        y_int -= 5*mm
        c.setFont("Helvetica-Bold", self.FONT_LABEL)
        c.drawString(x_int, y_int, "Parámetros de Entrada:")
        
        # ===== QUINTA LÍNEA: Voltajes de entrada =====
        y_int -= 4*mm
        c.setFont("Helvetica", self.FONT_LABEL)
        
        # L1-L2
        c.drawString(x_int, y_int, "L1-L2:")
        c.line(x_int + 12*mm, y_int - 1*mm, x_int + 30*mm, y_int - 1*mm)
        
        # L2-L3
        x_col2 = x_int + 35*mm
        c.drawString(x_col2, y_int, "L1-L3:")
        c.line(x_col2 + 12*mm, y_int - 1*mm, x_col2 + 30*mm, y_int - 1*mm)
        
        # L3-N (mitad derecha)
        x_mitad = x + self.ANCHO_UTIL/2
        c.setFont("Helvetica-Bold", self.FONT_LABEL)
        c.drawString(x_mitad, y_int, "Parámetros de Salida:")
        
        # Checkboxes de estado
        x_est = x_mitad + 40*mm
        c.setFont("Helvetica", self.FONT_LABEL)
        c.drawString(x_est, y_int, "☑ Inversor Encendido")
        c.drawString(x_est + 38*mm, y_int, "☐ En Bypass")
        
        # ===== SEXTA LÍNEA: Más voltajes entrada y salida =====
        y_int -= 4*mm
        
        # L1-N entrada
        c.drawString(x_int, y_int, "L1-N:")
        c.line(x_int + 10*mm, y_int - 1*mm, x_int + 28*mm, y_int - 1*mm)
        
        # L2-N entrada
        c.drawString(x_col2, y_int, "L2-N:")
        c.line(x_col2 + 10*mm, y_int - 1*mm, x_col2 + 28*mm, y_int - 1*mm)
        
        # L1-L2 salida
        c.drawString(x_mitad, y_int, "L1-L2:")
        c.line(x_mitad + 12*mm, y_int - 1*mm, x_mitad + 32*mm, y_int - 1*mm)
        
        # L1-L3 salida
        x_sal2 = x_mitad + 37*mm
        c.drawString(x_sal2, y_int, "L1-L3:")
        c.line(x_sal2 + 12*mm, y_int - 1*mm, x_sal2 + 32*mm, y_int - 1*mm)
        
        # UPS apagado checkbox
        x_apag = x_sal2 + 37*mm
        c.drawString(x_apag, y_int, "☐ UPS apagado")
        
        # ===== SÉPTIMA LÍNEA: Frecuencia, más voltajes =====
        y_int -= 4*mm
        
        # N-T Física entrada
        c.drawString(x_int, y_int, "N-T Física:")
        c.line(x_int + 18*mm, y_int - 1*mm, x_int + 35*mm, y_int - 1*mm)
        
        # Frecuencia
        x_freq = x_col2
        c.drawString(x_freq, y_int, "Frecuencia:")
        c.line(x_freq + 20*mm, y_int - 1*mm, x_freq + 35*mm, y_int - 1*mm)
        c.drawString(x_freq + 38*mm, y_int, "Hz.")
        
        # L1-N salida
        c.drawString(x_mitad, y_int, "L1-N:")
        c.line(x_mitad + 10*mm, y_int - 1*mm, x_mitad + 28*mm, y_int - 1*mm)
        
        # L2-N salida
        c.drawString(x_sal2, y_int, "L2-N:")
        c.line(x_sal2 + 10*mm, y_int - 1*mm, x_sal2 + 28*mm, y_int - 1*mm)
        
        # L3-N salida
        c.drawString(x_apag, y_int, "L3-N:")
        c.line(x_apag + 10*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== OCTAVA LÍNEA: Temperatura, corriente, frecuencia salida =====
        y_int -= 4*mm
        
        # Temperatura del sistema
        c.drawString(x_int, y_int, "Temperatura del Sistema UPS en electrónica:")
        c.line(x_int + 78*mm, y_int - 1*mm, x_int + 95*mm, y_int - 1*mm)
        c.drawString(x_int + 97*mm, y_int, "°C")
        
        # N-T Física salida
        c.drawString(x_mitad, y_int, "N-T Física:")
        c.line(x_mitad + 18*mm, y_int - 1*mm, x_mitad + 35*mm, y_int - 1*mm)
        
        # Frecuencia salida
        x_freq_sal = x_sal2
        c.drawString(x_freq_sal, y_int, "Frecuencia:")
        c.line(x_freq_sal + 20*mm, y_int - 1*mm, x_freq_sal + 35*mm, y_int - 1*mm)
        c.drawString(x_freq_sal + 38*mm, y_int, "Hz.")
        
        # ===== NOVENA LÍNEA: Descarga de eventos, corriente, % carga =====
        y_int -= 4*mm
        
        # Descarga de eventos
        c.drawString(x_int, y_int, "Descarga de eventos antes de empezar el mantenimiento:")
        x_check_desc = x_int + 105*mm
        c.drawString(x_check_desc, y_int, "☑ Si")
        c.drawString(x_check_desc + 8*mm, y_int, "☐ No")
        c.drawString(x_check_desc + 16*mm, y_int, "☐ N/A")
        
        # Corriente salida
        c.drawString(x_mitad, y_int, "Corriente:")
        c.drawString(x_mitad + 18*mm, y_int, "L1:")
        c.line(x_mitad + 24*mm, y_int - 1*mm, x_mitad + 35*mm, y_int - 1*mm)
        c.drawString(x_mitad + 36*mm, y_int, "A")
        
        x_l2 = x_mitad + 40*mm
        c.drawString(x_l2, y_int, "L2:")
        c.line(x_l2 + 6*mm, y_int - 1*mm, x_l2 + 17*mm, y_int - 1*mm)
        c.drawString(x_l2 + 18*mm, y_int, "A")
        
        x_l3 = x_l2 + 22*mm
        c.drawString(x_l3, y_int, "L3:")
        c.line(x_l3 + 6*mm, y_int - 1*mm, x_l3 + 17*mm, y_int - 1*mm)
        c.drawString(x_l3 + 18*mm, y_int, "A")
        
        # ===== DÉCIMA LÍNEA: % de Carga =====
        y_int -= 4*mm
        c.drawString(x_mitad, y_int, "% de Carga:")
        c.drawString(x_mitad + 18*mm, y_int, "L1:")
        c.line(x_mitad + 24*mm, y_int - 1*mm, x_mitad + 35*mm, y_int - 1*mm)
        c.drawString(x_mitad + 36*mm, y_int, "%")
        
        c.drawString(x_l2, y_int, "L2:")
        c.line(x_l2 + 6*mm, y_int - 1*mm, x_l2 + 17*mm, y_int - 1*mm)
        c.drawString(x_l2 + 18*mm, y_int, "%")
        
        c.drawString(x_l3, y_int, "L3:")
        c.line(x_l3 + 6*mm, y_int - 1*mm, x_l3 + 17*mm, y_int - 1*mm)
        c.drawString(x_l3 + 18*mm, y_int, "%")
        
        return y - altura_modulo
    
    # ========================================================================
    #                  MÓDULO 4: OPERACIÓN DEL SISTEMA UPS
    # ========================================================================
    
    def _modulo_operacion_sistema(self, c, y_inicio):
        """
        Dibuja el módulo de operación del sistema UPS, STS, ATS.
        
        Returns:
            float: Nueva posición Y después del módulo
        """
        x = self.MARGEN_IZQ
        y = y_inicio
        altura_modulo = 42*mm
        
        # Título de la sección
        c.setFont("Helvetica-Bold", self.FONT_SECCION)
        c.setFillColor(self.COLOR_NEGRO)
        c.drawString(x, y, "OPERACIÓN DEL SISTEMA UPS, STS ,ATS:")
        
        y -= 4*mm
        
        # Rectángulo principal
        c.setStrokeColor(self.COLOR_ROJO_BORDE)
        c.setLineWidth(1.5)
        c.rect(x, y - altura_modulo, self.ANCHO_UTIL, altura_modulo)
        
        # Contenido interno
        y_int = y - 4*mm
        x_int = x + 2*mm
        
        c.setFont("Helvetica", self.FONT_LABEL)
        
        # ===== PRIMERA LÍNEA: Estado Inicial =====
        c.drawString(x_int, y_int, "Estado Inicial:")
        
        # Checkboxes
        x_check = x_int + 28*mm
        c.drawString(x_check, y_int, "☐ Apagado")
        x_check += 22*mm
        c.drawString(x_check, y_int, "☐ En Bayppass")
        x_check += 26*mm
        c.drawString(x_check, y_int, "☑ Inversor Encendido")
        x_check += 38*mm
        c.drawString(x_check, y_int, "Otro:")
        c.line(x_check + 10*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # Lado derecho - Cuantos módulos
        x_der = x + self.ANCHO_UTIL - 70*mm
        c.drawString(x_der, y_int, "Cuantos módulos tiene:")
        c.line(x_der + 36*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== SEGUNDA LÍNEA: El Modo del UPS se realiza =====
        y_int -= 5*mm
        c.drawString(x_int, y_int, "El Modo del UPS se realiza:")
        
        x_check = x_int + 48*mm
        c.drawString(x_check, y_int, "☐ Apagado")
        x_check += 22*mm
        c.drawString(x_check, y_int, "☐ Si")
        x_check += 10*mm
        c.drawString(x_check, y_int, "☑ En Bayppass")
        x_check += 26*mm
        c.drawString(x_check, y_int, "☐ Inversor Encendido")
        
        # Lado derecho
        c.drawString(x_der, y_int, "No. de Serie del Módulo:")
        c.line(x_der + 38*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== TERCERA LÍNEA: Diagnóstico =====
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Diagnóstico")
        
        x_check = x_int + 48*mm
        c.drawString(x_check, y_int, "☑ Si")
        x_check += 10*mm
        c.drawString(x_check, y_int, "☐ N/A")
        x_check += 12*mm
        c.drawString(x_check, y_int, "☐ Equipo Dañado")
        
        # Continúa lado derecho
        c.drawString(x_der, y_int, "No. de Serie del Módulo:")
        c.line(x_der + 38*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== CUARTA LÍNEA: Antes de Apagar el Sistema =====
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Antes de Apagar el Sistema:")
        
        x_check = x_int + 48*mm
        c.drawString(x_check, y_int, "☐ Si")
        x_check += 10*mm
        c.drawString(x_check, y_int, "☑ N/A")
        x_check += 12*mm
        c.drawString(x_check, y_int, "☐ Equipo Dañado")
        
        c.drawString(x_der, y_int, "No. de Serie del Módulo:")
        c.line(x_der + 38*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== QUINTA LÍNEA: Revisión de la etapa de =====
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Revisión de la etapa de")
        
        x_check = x_int + 40*mm
        c.drawString(x_check, y_int, "Inversor:")
        x_check += 18*mm
        c.drawString(x_check, y_int, "☑ Funcionando Correctamente")
        x_check += 52*mm
        c.drawString(x_check, y_int, "☐ Presenta Daño")
        
        c.drawString(x_der, y_int, "No. de Serie del Módulo:")
        c.line(x_der + 38*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== Líneas siguientes: Rectificador, Cargador, Banco de Baterías, Otras Etapas =====
        componentes = [
            ("Rectificador:", "☑ Funcionando Correctamente", "☐ Presenta Daño"),
            ("Cargador:", "☑ Funcionando Correctamente", "☐ Presenta Daño"),
            ("Banco de Baterías:", "☑ Funcionando Correctamente", "☐ Presenta Daño"),
            ("Otra Etapa", "☐ Funcionando Correctamente", "☐ Presenta Daño"),
            ("Otra Etapa", "☐ Funcionando Correctamente", "☐ Presenta Daño")
        ]
        
        for comp_nombre, estado1, estado2 in componentes:
            y_int -= 4*mm
            x_check = x_int + 40*mm
            c.drawString(x_check, y_int, comp_nombre)
            x_check += 35*mm
            c.drawString(x_check, y_int, estado1)
            x_check += 52*mm
            c.drawString(x_check, y_int, estado2)
            
            c.drawString(x_der, y_int, "No. de Serie del Módulo:")
            c.line(x_der + 38*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== Última línea: El Sistema UPS está conformado por =====
        y_int -= 5*mm
        c.drawString(x_int, y_int, "El Sistema UPS está conformado por:")
        
        x_check = x_int + 65*mm
        c.drawString(x_check, y_int, "☑ UPS")
        x_check += 15*mm
        c.drawString(x_check, y_int, "☑ Gabinete de Baterías")
        x_check += 42*mm
        c.drawString(x_check, y_int, "☑ Gabinete de Transformadores")
        
        # Segunda fila de conformado
        y_int -= 4*mm
        c.drawString(x_int, y_int, "El sistema UPS tiene el Horario correcto en pantalla:")
        
        x_check = x_int + 90*mm
        c.drawString(x_check, y_int, "☑ Si")
        x_check += 10*mm
        c.drawString(x_check, y_int, "☐ No")
        x_check += 10*mm
        c.drawString(x_check, y_int, "☐ N/A")
        x_check += 12*mm
        c.drawString(x_check, y_int, "Observaciones:")
        c.line(x_check + 26*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        return y - altura_modulo
    
    # ========================================================================
    #        MÓDULO 5: CONDICIONES DE VENTILADORES Y CAPACITORES
    # ========================================================================
    
    def _modulo_ventiladores_capacitores(self, c, y_inicio):
        """
        Dibuja el módulo de condiciones operacionales de ventiladores y capacitores.
        
        Returns:
            float: Nueva posición Y después del módulo
        """
        x = self.MARGEN_IZQ
        y = y_inicio
        altura_modulo = 28*mm
        
        # Título de la sección
        c.setFont("Helvetica-Bold", self.FONT_SECCION)
        c.setFillColor(self.COLOR_NEGRO)
        c.drawString(x, y, "CONDICIONES OPERACIONALES DE VENTILADORES Y CAPACITORES:")
        
        y -= 4*mm
        
        # Rectángulo principal
        c.setStrokeColor(self.COLOR_ROJO_BORDE)
        c.setLineWidth(1.5)
        c.rect(x, y - altura_modulo, self.ANCHO_UTIL, altura_modulo)
        
        # Dividir en dos columnas
        ancho_columna = self.ANCHO_UTIL / 2
        
        # ===== COLUMNA IZQUIERDA: VENTILADORES =====
        y_int = y - 4*mm
        x_int = x + 2*mm
        
        c.setFont("Helvetica-Bold", self.FONT_LABEL)
        c.drawString(x_int, y_int, "Funcionamiento de Ventiladores:")
        
        c.setFont("Helvetica", self.FONT_LABEL)
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Giran libremente:")
        x_check = x_int + 30*mm
        c.drawString(x_check, y_int, "☑ Si")
        c.drawString(x_check + 10*mm, y_int, "☐ No")
        
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Tiene ruido de rozamiento:")
        c.drawString(x_check, y_int, "☑ Si")
        c.drawString(x_check + 10*mm, y_int, "☐ No")
        
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Sustitución de Ventiladores a tiempo de Operación:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☐ No")
        
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Sustitución de Ventiladores por otro daño:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☐ No")
        c.drawString(x_check + 20*mm, y_int, "☑ N/A")
        
        y_int -= 4*mm
        c.drawString(x_int, y_int, "Qué daño Presenta:")
        c.line(x_int + 32*mm, y_int - 1*mm, x + ancho_columna - 2*mm, y_int - 1*mm)
        
        y_int -= 4*mm
        c.drawString(x_int, y_int, "No. de Pzas.:")
        c.line(x_int + 22*mm, y_int - 1*mm, x + ancho_columna - 2*mm, y_int - 1*mm)
        
        y_int -= 4*mm
        c.drawString(x_int, y_int, "No. de Pzas.:")
        c.line(x_int + 22*mm, y_int - 1*mm, x + ancho_columna - 2*mm, y_int - 1*mm)
        
        y_int -= 4*mm
        c.drawString(x_int, y_int, "No. de Pzas.:")
        c.line(x_int + 22*mm, y_int - 1*mm, x + ancho_columna - 2*mm, y_int - 1*mm)
        
        # ===== COLUMNA DERECHA: CAPACITORES =====
        y_int = y - 4*mm
        x_der = x + ancho_columna + 2*mm
        
        c.setFont("Helvetica-Bold", self.FONT_LABEL)
        c.drawString(x_der, y_int, "Condiciones de Capacitores AC y DC:")
        
        c.setFont("Helvetica", self.FONT_LABEL)
        y_int -= 4*mm
        c.drawString(x_der, y_int, "Estado físico de los capacitores:")
        x_check_der = x_der + 55*mm
        c.drawString(x_check_der, y_int, "☑ En buen estado")
        c.drawString(x_check_der + 30*mm, y_int, "☐ Presenta daño")
        
        y_int -= 4*mm
        c.drawString(x_der, y_int, "Requiere cambio de capacitores x tiempo de operación:")
        c.drawString(x_check_der, y_int, "☐ Si")
        c.drawString(x_check_der + 10*mm, y_int, "☐ No")
        
        y_int -= 4*mm
        c.drawString(x_der, y_int, "Sustitución de Capacitores por otro daño:")
        c.drawString(x_check_der, y_int, "☐ Si")
        c.drawString(x_check_der + 10*mm, y_int, "☐ No")
        c.drawString(x_check_der + 20*mm, y_int, "☑ N/A")
        
        y_int -= 4*mm
        c.drawString(x_der, y_int, "Qué daño Presenta:")
        c.line(x_der + 32*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        y_int -= 4*mm
        c.drawString(x_der, y_int, "No. de Pzas.:")
        c.line(x_der + 22*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        y_int -= 4*mm
        c.drawString(x_der, y_int, "No. de Pzas.:")
        c.line(x_der + 22*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        y_int -= 4*mm
        c.drawString(x_der, y_int, "Observaciones:")
        c.line(x_der + 26*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        return y - altura_modulo
    
    # ========================================================================
    #                      MÓDULO 6: LIMPIEZA AL UPS
    # ========================================================================
    
    def _modulo_limpieza(self, c, y_inicio):
        """
        Dibuja el módulo de limpieza al UPS, STS, ATS.
        
        Returns:
            float: Nueva posición Y después del módulo
        """
        x = self.MARGEN_IZQ
        y = y_inicio
        altura_modulo = 35*mm
        
        # Título de la sección
        c.setFont("Helvetica-Bold", self.FONT_SECCION)
        c.setFillColor(self.COLOR_NEGRO)
        c.drawString(x, y, "LIMPIEZA AL UPS, STS, ATS:")
        
        y -= 4*mm
        
        # Rectángulo principal
        c.setStrokeColor(self.COLOR_ROJO_BORDE)
        c.setLineWidth(1.5)
        c.rect(x, y - altura_modulo, self.ANCHO_UTIL, altura_modulo)
        
        # Contenido interno
        y_int = y - 4*mm
        x_int = x + 2*mm
        
        c.setFont("Helvetica-Bold", self.FONT_LABEL)
        c.drawString(x_int, y_int, "Limpieza interna en el UPS, STS, ATS:")
        
        c.setFont("Helvetica", self.FONT_LABEL)
        
        # ===== Sección de Rectificador =====
        y_int -= 5*mm
        c.drawString(x_int + 5*mm, y_int, "Sección de Rectificador:")
        x_check = x_int + 48*mm
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        
        x_porque = x_check + 22*mm
        c.drawString(x_porque, y_int, "¿Por qué no se realizó?")
        c.line(x_porque + 40*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== Sección de Inversor =====
        y_int -= 4*mm
        c.drawString(x_int + 5*mm, y_int, "Sección de Inversor:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        c.drawString(x_porque, y_int, "¿Por qué no se realizó?")
        c.line(x_porque + 40*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== Sección del cargador =====
        y_int -= 4*mm
        c.drawString(x_int + 5*mm, y_int, "Sección del cargador:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        c.drawString(x_porque, y_int, "¿Por qué no se realizó?")
        c.line(x_porque + 40*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== En otra sección =====
        y_int -= 4*mm
        c.drawString(x_int + 5*mm, y_int, "En otra sección:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        c.drawString(x_porque, y_int, "¿Por qué no se realizó?")
        c.line(x_porque + 40*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== Durante la limpieza se detectó =====
        y_int -= 5*mm
        c.drawString(x_int, y_int, "Durante la limpieza se detectó")
        
        # ===== Humedad =====
        y_int -= 4*mm
        c.drawString(x_int + 5*mm, y_int, "Humedad:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        
        x_cual = x_check + 22*mm
        c.drawString(x_cual, y_int, "Cualquiera de los puntos antes mencionados, en qué etapa del UPS se encontró:")
        c.line(x_cual + 135*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== Rastros de líquidos =====
        y_int -= 4*mm
        c.drawString(x_int + 5*mm, y_int, "Rastros de que existió líquidos:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        
        # ===== Rastros de roedores o plagas =====
        y_int -= 4*mm
        c.drawString(x_int + 5*mm, y_int, "Rastros de roedores o plagas:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        c.drawString(x_cual, y_int, "Observaciones:")
        c.line(x_cual + 26*mm, y_int - 1*mm, x + self.ANCHO_UTIL - 2*mm, y_int - 1*mm)
        
        # ===== Cables roídos =====
        y_int -= 4*mm
        c.drawString(x_int + 5*mm, y_int, "Cables roídos:")
        c.drawString(x_check, y_int, "☐ Si")
        c.drawString(x_check + 10*mm, y_int, "☑ No")
        
        return y - altura_modulo
    
    # ========================================================================
    #                          MÓDULO 7: FIRMAS
    # ========================================================================
    
    def _modulo_firmas(self, c, y_pos):
        """
        Dibuja el módulo de firmas del personal y cliente.
        
        Args:
            y_pos: Posición Y absoluta donde dibujar (desde abajo)
        """
        x = self.MARGEN_IZQ
        altura_firma = 18*mm
        ancho_caja = (self.ANCHO_UTIL - 5*mm) / 2
        
        # ===== CAJA IZQUIERDA: PERSONAL LBS =====
        c.setStrokeColor(self.COLOR_NEGRO)
        c.setLineWidth(1)
        c.rect(x, y_pos, ancho_caja, altura_firma)
        
        # Encabezado
        c.setFont("Helvetica-Bold", self.FONT_LABEL)
        c.drawCentredString(x + ancho_caja/2, y_pos + altura_firma - 4*mm,
                          "PERSONAL QUE EJECUTA LA ACTIVIDAD DE LBS:")
        
        # Campos
        c.setFont("Helvetica", 6)
        y_campo = y_pos + altura_firma - 8*mm
        
        c.drawString(x + 2*mm, y_campo, "NOMBRE:")
        c.line(x + 16*mm, y_campo - 1*mm, x + ancho_caja - 2*mm, y_campo - 1*mm)
        
        y_campo -= 4*mm
        c.drawString(x + 2*mm, y_campo, "PUESTO:")
        c.line(x + 16*mm, y_campo - 1*mm, x + ancho_caja - 2*mm, y_campo - 1*mm)
        
        # ===== CAJA DERECHA: CLIENTE =====
        x_der = x + ancho_caja + 5*mm
        c.rect(x_der, y_pos, ancho_caja, altura_firma)
        
        # Encabezado
        c.setFont("Helvetica-Bold", self.FONT_LABEL)
        c.drawCentredString(x_der + ancho_caja/2, y_pos + altura_firma - 4*mm,
                          "EXCLUSIVO LLENADO DEL CLIENTE")
        
        # Campos
        c.setFont("Helvetica", 6)
        y_campo = y_pos + altura_firma - 8*mm
        
        c.drawString(x_der + 2*mm, y_campo, "FECHA:")
        c.line(x_der + 14*mm, y_campo - 1*mm, x_der + 40*mm, y_campo - 1*mm)
        
        c.drawString(x_der + 45*mm, y_campo, "HORA:")
        c.line(x_der + 56*mm, y_campo - 1*mm, x_der + ancho_caja - 2*mm, y_campo - 1*mm)
        
        y_campo -= 4*mm
        c.drawString(x_der + 2*mm, y_campo, "MÓVIL:")
        c.line(x_der + 14*mm, y_campo - 1*mm, x_der + 40*mm, y_campo - 1*mm)
        
        c.drawString(x_der + 45*mm, y_campo, "CORREO:")
        c.line(x_der + 56*mm, y_campo - 1*mm, x_der + ancho_caja - 2*mm, y_campo - 1*mm)
        
        y_campo -= 4*mm
        c.drawString(x_der + 2*mm, y_campo, "NOMBRE:")
        c.line(x_der + 18*mm, y_campo - 1*mm, x_der + ancho_caja/2, y_campo - 1*mm)
        
        c.drawString(x_der + ancho_caja/2 + 2*mm, y_campo, "FIRMA:")
        c.line(x_der + ancho_caja/2 + 14*mm, y_campo - 1*mm, x_der + ancho_caja - 2*mm, y_campo - 1*mm)


def main():
    """Función principal para generar el reporte"""
    print("=" * 70)
    print("  GENERADOR DE REPORTES LBS - VERSIÓN MEJORADA 2.0")
    print("=" * 70)
    print()
    
    generador = ReporteLBSMejorado()
    generador.generar_reporte('reporte_lbs_mejorado_v2.pdf')
    
    print()
    print("=" * 70)
    print("  ✓ REPORTE GENERADO EXITOSAMENTE")
    print("=" * 70)


if __name__ == '__main__':
    main()