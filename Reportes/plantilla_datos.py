#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plantillas de Datos para Reportes LBS
======================================

Este módulo contiene plantillas pre-configuradas para diferentes tipos
de reportes, basadas en la especificación técnica FormularioV1.

Uso:
    from plantilla_datos import obtener_plantilla_diagnostico
    
    datos = obtener_plantilla_diagnostico()
    datos['nombre_cliente'] = 'Mi Cliente'
    
    from generador_reporte_lbs import ReporteServicioLBS
    generador = ReporteServicioLBS(datos)
    generador.generar_pdf('reporte.pdf')
"""

from datetime import datetime


def obtener_plantilla_vacia():
    """
    Retorna una plantilla vacía con todos los campos definidos.
    Útil para entender la estructura completa de datos.
    """
    return {
        # ========== BLOQUE 01: ENCABEZADO Y METADATOS ==========
        'es_equipo_ge': False,
        'folio_ticket': '',
        'fecha_servicio': datetime.now().strftime('%d/%m/%Y'),
        
        # Datos del Cliente
        'nombre_cliente': '',
        'sucursal_sitio': '',
        'direccion': '',
        'usuario': '',
        'ubicacion': '',
        'gm_gd': '',
        
        # Tipo de Servicio
        'tipo_de_servicio': 'Preventivo',  # Preventivo, Correctivo, Diagnóstico, etc.
        'capacitacion_impartida': False,   # Solo visible si tipo == "Arranque / Puesta en Marcha"
        
        # Datos del Equipo
        'marca_equipo': '',
        'modelo_equipo': '',
        'arquitectura_ups': 'Monolítico',  # Monolítico o Modular
        'tipo_carga_conectada': 'Lineal',  # Lineal o No Lineal
        'numero_sobrecargas': 0,           # Solo GE
        'capacidad': '',
        'numero_serie': '',
        
        # Checkboxes de tipo de servicio
        'preventivo': False,
        'correctivo': False,
        'diagnostico': False,
        'capacitacion': False,
        'arranque': False,
        'cambio_baterias': False,
        'laboratorio': False,
        
        # ========== BLOQUE 02: LECTURAS ENTRADA/SALIDA ==========
        'configuracion_fases': 'Trifásico',  # Monofásico, Bifásico, Trifásico
        
        # Punto de medición
        'medicion_voltaje': {
            'punto_medicion': [],  # Lista: Tablero, Interruptor, Bornes UPS, Transformador
            'cap_entrada': '',
            'cap_salida': ''
        },
        
        'interruptor_entrada_existe': False,
        'capacidad_int_entrada': 0,
        'interruptor_salida_existe': False,
        'capacidad_int_salida': 0,
        
        # Parámetros de Entrada
        'parametros_entrada': {
            'l1_l2': 0.0,
            'l2_l3': 0.0,
            'l1_l3': 0.0,
            'l1_n': 0.0,
            'l2_n': 0.0,
            'l3_n': 0.0,
            'frecuencia_hz': 60.0
        },
        
        # Parámetros de Salida
        'parametros_salida': {
            'estado': 'Inversor Encendido',  # Inversor Encendido, Bypass Estático, Bypass Manual
            'l1_l2': 0.0,
            'l2_l3': 0.0,
            'l1_l3': 0.0,
            'l1_n': 0.0,
            'l2_n': 0.0,
            'l3_n': 0.0
        },
        
        # ========== BLOQUE 03: OPERACIÓN Y ESTADO ==========
        'operacion_sistema': {
            'estado_inicial': '',  # Inversor Encendido, Bypass Estático, Apagado, Bypass Manual
            'modo_durante_mantenimiento': '',
            'modulos': {
                'activos': '',
                'pasivos': '',
                'serie_modulo': '',
                'serie_chasis': ''
            }
        },
        
        'numero_serie_chasis': '',
        'seriales_modulos_potencia': [],  # Lista de seriales (solo si Modular)
        
        # Diagnóstico de Etapas
        'estado_rectificador': 'Funcionando',  # Funcionando, Dañado, N/A
        'estado_inversor': 'Funcionando',
        'estado_cargador': 'Funcionando',
        'estado_baterias': 'Funcionando',
        
        # Conformado Por (Multi-select)
        'conformado_por': [],  # UPS, Gabinete de Baterías, Gabinete de Transformadores, STS, ATS
        
        # ========== BLOQUE 04: VENTILADORES Y CAPACITORES ==========
        'ventiladores': {
            'giran_libre': False,
            'ruido': False,
            'sustitucion_operacion': False,
            'sustitucion_daño': False,
            'que_daño_presenta': '',
            'num_piezas': 0
        },
        
        'capacitores': {
            'estado_fisico': 'Buen estado',  # Buen estado, Mal estado
            'sustitucion_operacion': False,
            'sustitucion_daño': False,
            'que_daño_presenta': '',
            'num_piezas': 0,
            'buen_estado': True
        },
        
        # ========== BLOQUE 05: LIMPIEZA ==========
        'limpieza': {
            'rectificador': False,
            'motivo_no_rectif': '',
            'inversor': False,
            'motivo_no_inv': '',
            'cargador': False,
            'motivo_no_carg': '',
            'otras_secciones': False,
            'motivo_no_otras': '',
            
            # Hallazgos
            'humedad_detectada': False,
            'en_que_etapa_humedad': '',
            'rastros_liquidos': False,
            'en_que_etapa_liquido': '',
            'plagas_roedores': False,
            'en_que_etapa_plaga': '',
            'cables_roidos': False,
            'observaciones_cables': ''
        },
        
        # ========== BLOQUE 06: CABLEADO Y CONEXIONES ==========
        'cableado': {
            'estado_cable_control': 'Buen estado',  # Buen estado, Daño forro, Calentamiento
            'estado_cable_potencia': 'Buen estado',
            'requiere_cambio': False,
            'descripcion_y_piezas': '',
            
            # Torque Entrada
            'estado_torque_entrada': 'Conexión bien',  # Conexión bien, Conexión floja
            'problema_conexion_entrada': False,
            'tipo_problema_ent': '',  # No se torqueó, Barrido, Cabeza degollada, Otro
            
            # Torque Salida
            'estado_torque_salida': 'Conexión bien',
            'problema_conexion_salida': False,
            'tipo_problema_sal': ''
        },
        
        # ========== BLOQUE 07: MANTENIMIENTO EXTERIOR ==========
        'mantenimiento_exterior': {
            'limpieza_gabinete_ups': False,
            'limpieza_tapas_int_ups': False,
            'gabinete_baterias_humedad': False,  # Visible solo si hay Baterías
            'gabinete_trafo_humedad': False      # Visible solo si hay Trafo
        },
        
        # ========== BLOQUE 08: BATERÍAS ==========
        'baterias': {
            'tipo_bateria': 'Plomo-Ácido',  # Plomo-Ácido, Litio, NiCd, Otro
            'conexion_baterias': 'Correcto',  # Correcto, Terminal floja
            'condicion_fisica': 'Buen estado',  # Buen estado, Sulfatada, Inflada, Rota
            'numeros_baterias_dañadas': '',
            'numero_baterias': 0,
            'numero_bancos': 0,
            'voltajes_bancos': []  # Lista de voltajes
        },
        
        # ========== BLOQUE 09: TRANSFORMADORES ==========
        'transformadores': {
            'ubicacion': '',  # Entrada, Salida, Ambos
            
            # Trafo Entrada
            'tipo_trafo_entrada': '',  # Transformador Aislamiento, Autotransformador
            'conexion_trafo_entrada': '',  # Delta-Estrella, Estrella-Delta
            'voltajes_trafo_entrada': '',
            
            # Trafo Salida
            'tipo_trafo_salida': '',
            'conexion_trafo_salida': '',
            'voltajes_trafo_salida': ''
        },
        
        # ========== BLOQUE 10: PRUEBAS FUNCIONALES ==========
        'pruebas': {
            'bypass_a_inversor': False,
            'inversor_a_bypass': False,
            'descarga_eventos_realizada': False,
            'obs_eventos': '',
            'realizo_prueba_baterias': False,
            
            # Detalles de 3 pruebas
            'prueba_1': {
                'metodo': '',  # Test UPS, Bajar Interruptor
                'carga': '',   # Vacío, Parcial, Completa
                'obs': ''
            },
            'prueba_2': {
                'metodo': '',
                'carga': '',
                'obs': ''
            },
            'prueba_3': {
                'metodo': '',
                'carga': '',
                'obs': ''
            }
        },
        
        # ========== BLOQUE 11: CONDICIONES SITIO ==========
        'condiciones_sitio': {
            'tipo_cuarto': 'Cerrado',  # Cerrado, Hermético
            'tipo_piso': 'Falso',  # Falso, Concreto, Azulejo, Epóxico
            'temperatura_cuarto_c': 0.0,
            
            'humedad_ambiente': False,
            'polvo_ambiente': False,
            'particulas_volatiles': False,
            
            'aire_acondicionado_existe': False,
            'funciona_aa': False,
            
            'obstruccion_ups': False,
            'obstruccion_ventilacion': False,
            'obstruccion_acceso': False,
            'evidencia_roedores_sitio': False,
            
            'condicion_instalacion_elec': 'Óptimas',  # Óptimas, Buenas, Malas, Provisional, No existe
            
            # Espacios libres
            'libre_parte_trasera': False,
            'libre_costados': False,
            'libre_parte_superior': False
        },
        
        # ========== BLOQUE 12: PRUEBAS GE (Solo si es_equipo_ge == True) ==========
        'pruebas_ge': {
            'validacion_configuracion': False,
            'conectividad_perifericos': False,
            'conectividad_monitoreo': False,
            'operatividad_puertos': False,
            'pruebas_conectividad_red': False,
            'continuidad_puesta_tierra': False,
            'resistencia_aislamiento': False,
            'corriente_fuga_tierra': False
        },
        
        # ========== BLOQUE 13: LOGÍSTICA ENTREGA ==========
        'logistica': {
            'servicio_entrega': False,
            'entrega_por': '',  # Personal Propio, Externo
            'items_entregados': [],  # UPS, Baterías, Trafo, Tableros
            'lugar_entrega': '',  # Pie de camión, Sitio final, Descarga cliente
            'destino_final': '',  # Sitio final, Bodega, Cuarto UPS, Subestación
            
            'servicio_maniobra': False,
            'realizada_por': '',  # Personal Propio, Externo
            'cambio_ubicacion': False,
            
            # Maniobras específicas
            'retiro_materiales': 'N/A',  # Si, No, N/A
            'subir_a_camion': 'N/A',
            'bajar_de_camion': 'N/A',
            'arrastre_en_sitio': 'N/A',
            'subir_escaleras': 'N/A',
            'obstaculos': 'N/A',
            'movimiento_camper': 'N/A'
        },
        
        # ========== OBSERVACIONES ==========
        'observaciones': [],  # Lista de strings
        
        # ========== FIRMAS ==========
        'personal': {
            'nombre': '',
            'puesto': ''
        },
        'cliente_firma': {
            'fecha': '',
            'movil': '',
            'nombre': '',
            'correo': '',
            'firma': ''
        }
    }


def obtener_plantilla_diagnostico():
    """
    Retorna una plantilla pre-configurada para un servicio de diagnóstico.
    Basada en el reporte 20105 del PDF.
    """
    plantilla = obtener_plantilla_vacia()
    
    # Actualizar con datos de diagnóstico
    plantilla.update({
        'tipo_de_servicio': 'Diagnóstico',
        'diagnostico': True,
        'preventivo': False,
        'configuracion_fases': 'Trifásico',
        
        'medicion_voltaje': {
            'punto_medicion': ['UPS', 'Transformador'],
            'cap_entrada': '600 A',
            'cap_salida': ''
        },
        
        'parametros_entrada': {
            'l1_l2': 213.0,
            'l1_l3': 480.6,
            'frecuencia_hz': 60.0
        },
        
        'parametros_salida': {
            'estado': 'Inversor Encendido',
            'l1_l2': 213.0,
            'l1_l3': 213.0
        },
        
        'conformado_por': ['UPS', 'Gabinete de Baterías', 'Gabinete de Transformadores'],
        
        'ventiladores': {
            'giran_libre': True,
            'ruido': False
        },
        
        'capacitores': {
            'estado_fisico': 'Buen estado',
            'buen_estado': True
        },
        
        'limpieza': {
            'rectificador': False,
            'motivo_no_rectif': 'no aplica en servicio de diagnostico',
            'inversor': False,
            'motivo_no_inv': 'no aplica en servicio de diagnostico'
        }
    })
    
    return plantilla


def obtener_plantilla_preventivo():
    """
    Retorna una plantilla pre-configurada para un servicio preventivo.
    """
    plantilla = obtener_plantilla_vacia()
    
    plantilla.update({
        'tipo_de_servicio': 'Preventivo',
        'preventivo': True,
        
        'limpieza': {
            'rectificador': True,
            'inversor': True,
            'cargador': True,
            'otras_secciones': True
        },
        
        'ventiladores': {
            'giran_libre': True,
            'sustitucion_operacion': False
        },
        
        'cableado': {
            'estado_cable_control': 'Buen estado',
            'estado_cable_potencia': 'Buen estado',
            'estado_torque_entrada': 'Conexión bien',
            'estado_torque_salida': 'Conexión bien'
        },
        
        'pruebas': {
            'bypass_a_inversor': True,
            'inversor_a_bypass': True,
            'realizo_prueba_baterias': True,
            'prueba_1': {
                'metodo': 'Test UPS',
                'carga': 'Parcial',
                'obs': 'Prueba exitosa'
            }
        }
    })
    
    return plantilla


def obtener_plantilla_correctivo():
    """
    Retorna una plantilla pre-configurada para un servicio correctivo.
    """
    plantilla = obtener_plantilla_vacia()
    
    plantilla.update({
        'tipo_de_servicio': 'Correctivo',
        'correctivo': True,
        
        # En correctivo generalmente hay fallas detectadas
        'estado_rectificador': 'Funcionando',
        'estado_inversor': 'Dañado',
        
        # Puede requerir refacciones
        'ventiladores': {
            'sustitucion_daño': True,
            'que_daño_presenta': 'Ventilador con rodamiento dañado',
            'num_piezas': 2
        }
    })
    
    return plantilla


def obtener_plantilla_ge():
    """
    Retorna una plantilla pre-configurada para equipos GE.
    Incluye el bloque 12 de pruebas especiales.
    """
    plantilla = obtener_plantilla_vacia()
    
    plantilla.update({
        'es_equipo_ge': True,
        'numero_sobrecargas': 0,
        
        'pruebas_ge': {
            'validacion_configuracion': True,
            'conectividad_perifericos': True,
            'conectividad_monitoreo': True,
            'operatividad_puertos': True,
            'pruebas_conectividad_red': True,
            'continuidad_puesta_tierra': True,
            'resistencia_aislamiento': True,
            'corriente_fuga_tierra': False
        }
    })
    
    return plantilla


def obtener_plantilla_completa():
    """
    Retorna una plantilla con datos de ejemplo completos.
    Útil para testing y desarrollo.
    """
    return {
        'folio_ticket': '20105',
        'fecha_servicio': '06/02/2026',
        'nombre_cliente': 'Radio Movil DYPSA',
        'usuario': 'P8076 Telcel CDMX Popotla',
        'direccion': 'Eje 5 Servicio Trujillo 211 San Álvaro, Azcapotzalco CDMX',
        'ubicacion': 'Sala UPS Telcel',
        'gm_gd': '☐ si ☑ no',
        
        'tipo_de_servicio': 'Diagnóstico',
        'diagnostico': True,
        'preventivo': False,
        
        'marca_equipo': 'OPA FXD',
        'modelo_equipo': 'OPA FXD',
        'capacidad': '400 kVA',
        'numero_serie': '5U-1434',
        'arquitectura_ups': 'Modular',
        
        'configuracion_fases': 'Trifásico',
        
        'medicion_voltaje': {
            'punto_medicion': ['UPS', 'Transformador'],
            'cap_entrada': '600 A',
            'cap_salida': ''
        },
        
        'parametros_entrada': {
            'l1_l2': 213.0,
            'l1_l3': 480.6,
            'frecuencia_hz': 60.0
        },
        
        'parametros_salida': {
            'estado': 'Inversor Encendido',
            'l1_l2': 213.0,
            'l1_l3': 213.0
        },
        
        'operacion_sistema': {
            'modulos': {
                'activos': '4 Activos',
                'pasivos': '4 Pasivos',
                'serie_modulo': 'DM461'
            }
        },
        
        'conformado_por': ['UPS', 'Gabinete de Baterías', 'Gabinete de Transformadores'],
        
        'ventiladores': {
            'giran_libre': True
        },
        
        'capacitores': {
            'buen_estado': True,
            'estado_fisico': 'Buen estado'
        },
        
        'limpieza': {
            'rectificador': False,
            'motivo_no_rectif': 'no aplica en servicio de diagnostico',
            'inversor': False,
            'motivo_no_inv': 'no aplica en servicio de diagnostico'
        },
        
        'baterias': {
            'tipo_bateria': 'Litio',
            'numero_bancos': 6,
            'voltajes_bancos': [510.6, 510.2]
        },
        
        'observaciones': [
            'Se encuentra UPS en linea con alarma presente "512L Li-Ion BATT WARNING"',
            'Se encuentra Gabinete de Baterias RACK3, con interruptor Upsilon GPJO SHU',
            'Se busca voltajes en sistema BMS, de limites de equilibrador ajustados.',
            '',
            'Se realiza reset del sistema de baterias correctamente',
            'Se verifica voltajes de todas las baterias',
            'Se verifica voltajes de cada banco de baterias.',
            'Se recupera valor de arranques RACK3 corregir memoria.',
            'Se deja UPS en linea sin alarmas respaldando correctamente la carga.'
        ],
        
        'personal': {
            'nombre': 'Juan Rosales / Víctor Domínguez',
            'puesto': 'Ing. servicio'
        },
        
        'cliente_firma': {
            'fecha': '6/2/26',
            'movil': '5554000330',
            'nombre': 'Roberto Vazquez'
        }
    }


# Constantes útiles
TIPOS_SERVICIO = [
    'Preventivo',
    'Correctivo',
    'Diagnóstico',
    'Arranque / Puesta en Marcha',
    'Cambio de Baterías',
    'Laboratorio'
]

ARQUITECTURAS = ['Monolítico', 'Modular']
CONFIGURACIONES_FASES = ['Monofásico', 'Bifásico', 'Trifásico']
ESTADOS_COMPONENTE = ['Funcionando', 'Dañado', 'N/A']
TIPOS_BATERIA = ['Plomo-Ácido', 'Litio', 'NiCd', 'Otro']
