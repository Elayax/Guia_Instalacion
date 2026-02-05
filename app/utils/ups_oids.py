"""
Definiciones de OIDs para UPS INVT (INVT-MIB).

Este módulo contiene todos los OIDs del MIB propietario de INVT
(Enterprise ID: 56788), organizados por grupos funcionales con sus
factores de escala, diccionarios de decodificación y clasificación de polling.

OID Base: .1.3.6.1.4.1.56788.1.1.1
"""

# OID Base del fabricante INVT
ENTERPRISE_OID = '.1.3.6.1.4.1.56788'
UPS_BASE_OID = '.1.3.6.1.4.1.56788.1.1.1'
THS_BASE_OID = '.1.3.6.1.4.1.56788.1.1.2'
TRAP_BASE_OID = '.1.3.6.1.4.1.56788.1.1.3'
MODULE_BASE_OID = '.1.3.6.1.4.1.56788.1.1.4'

# ============================================================================
# GRUPO 1: INFORMACIÓN DEL DISPOSITIVO (upsInfo - OID .1)
# ============================================================================
UPS_INFO_OIDS = {
    'monitor_version': f'{UPS_BASE_OID}.1.1.0',
    'company_name': f'{UPS_BASE_OID}.1.2.0',
    'model': f'{UPS_BASE_OID}.1.3.0',
    'serial_number': f'{UPS_BASE_OID}.1.4.0',
    'input_phases': f'{UPS_BASE_OID}.1.5.0',
    'output_phases': f'{UPS_BASE_OID}.1.6.0',
    'battery_count': f'{UPS_BASE_OID}.1.7.0',
    'battery_ah': f'{UPS_BASE_OID}.1.8.0',
    'battery_rated_voltage': f'{UPS_BASE_OID}.1.9.0',
    'battery_type': f'{UPS_BASE_OID}.1.10.0',
    'rated_power': f'{UPS_BASE_OID}.1.11.0',
    'rated_input_voltage': f'{UPS_BASE_OID}.1.12.0',
    'rated_input_frequency': f'{UPS_BASE_OID}.1.13.0',
    'rated_output_voltage': f'{UPS_BASE_OID}.1.14.0',
    'rated_output_frequency': f'{UPS_BASE_OID}.1.15.0',
}

# ============================================================================
# GRUPO 2: ESTADO DEL UPS (upsStatus - OID .2)
# ============================================================================
UPS_STATUS_OIDS = {
    'connected': f'{UPS_BASE_OID}.2.1.0',
    'power_source': f'{UPS_BASE_OID}.2.2.0',
    'battery_status': f'{UPS_BASE_OID}.2.3.0',
    'maintain_breaker': f'{UPS_BASE_OID}.2.4.0',
    'battery_test_result': f'{UPS_BASE_OID}.2.5.0',
    'battery_maintain_result': f'{UPS_BASE_OID}.2.6.0',
}

# ============================================================================
# GRUPO 3: DATOS BYPASS (upsDataBypass - OID .3.1)
# ============================================================================
UPS_DATA_BYPASS_OIDS = {
    'voltage_a': f'{UPS_BASE_OID}.3.1.1.0',
    'voltage_b': f'{UPS_BASE_OID}.3.1.2.0',
    'voltage_c': f'{UPS_BASE_OID}.3.1.3.0',
    'frequency': f'{UPS_BASE_OID}.3.1.4.0',
}

# ============================================================================
# GRUPO 4: DATOS ENTRADA (upsDataInput - OID .3.2)
# ============================================================================
UPS_DATA_INPUT_OIDS = {
    'voltage_a': f'{UPS_BASE_OID}.3.2.1.0',
    'voltage_b': f'{UPS_BASE_OID}.3.2.2.0',
    'voltage_c': f'{UPS_BASE_OID}.3.2.3.0',
    'frequency': f'{UPS_BASE_OID}.3.2.4.0',
}

# ============================================================================
# GRUPO 5: DATOS SALIDA (upsDataOutput - OID .3.3)
# ============================================================================
UPS_DATA_OUTPUT_OIDS = {
    'voltage_a': f'{UPS_BASE_OID}.3.3.1.0',
    'voltage_b': f'{UPS_BASE_OID}.3.3.2.0',
    'voltage_c': f'{UPS_BASE_OID}.3.3.3.0',
    'frequency': f'{UPS_BASE_OID}.3.3.4.0',
    'load_a': f'{UPS_BASE_OID}.3.3.5.0',
    'load_b': f'{UPS_BASE_OID}.3.3.6.0',
    'load_c': f'{UPS_BASE_OID}.3.3.7.0',
    'current_a': f'{UPS_BASE_OID}.3.3.8.0',
    'current_b': f'{UPS_BASE_OID}.3.3.9.0',
    'current_c': f'{UPS_BASE_OID}.3.3.10.0',
}

# ============================================================================
# GRUPO 6: DATOS BATERÍA (upsDataBattery - OID .3.4)
# ============================================================================
UPS_DATA_BATTERY_OIDS = {
    'voltage': f'{UPS_BASE_OID}.3.4.1.0',
    'current': f'{UPS_BASE_OID}.3.4.2.0',
    'remain_time': f'{UPS_BASE_OID}.3.4.3.0',
    'capacity': f'{UPS_BASE_OID}.3.4.4.0',
    'temperature': f'{UPS_BASE_OID}.3.4.5.0',
    'positive_voltage': f'{UPS_BASE_OID}.3.4.6.0',
    'negative_voltage': f'{UPS_BASE_OID}.3.4.7.0',
}

# ============================================================================
# TEMPERATURA INTERNA UPS (upsDataInternalTemperature - OID .3.5)
# ============================================================================
UPS_INTERNAL_TEMP_OID = f'{UPS_BASE_OID}.3.5.0'

# ============================================================================
# GRUPO 7: ALARMAS (upsAlarm - OID .4)
# ============================================================================
UPS_ALARM_OIDS = {
    'switch_normal': f'{UPS_BASE_OID}.4.1.0',
    'on_bypass': f'{UPS_BASE_OID}.4.2.0',
    'on_battery': f'{UPS_BASE_OID}.4.3.0',
    'battery_low': f'{UPS_BASE_OID}.4.4.0',
    'battery_depleted': f'{UPS_BASE_OID}.4.5.0',
    'input_abnormal': f'{UPS_BASE_OID}.4.6.0',
    'output_overload': f'{UPS_BASE_OID}.4.7.0',
    'over_temperature': f'{UPS_BASE_OID}.4.8.0',
    'output_short': f'{UPS_BASE_OID}.4.9.0',
    'output_over_voltage': f'{UPS_BASE_OID}.4.10.0',
    'output_under_voltage': f'{UPS_BASE_OID}.4.11.0',
    'bypass_abnormal': f'{UPS_BASE_OID}.4.12.0',
    'charger_fail': f'{UPS_BASE_OID}.4.13.0',
    'fan_fail': f'{UPS_BASE_OID}.4.14.0',
    'bus_over_voltage': f'{UPS_BASE_OID}.4.15.0',
    'bus_under_voltage': f'{UPS_BASE_OID}.4.16.0',
    'bus_unbalance': f'{UPS_BASE_OID}.4.17.0',
    'inverter_fail': f'{UPS_BASE_OID}.4.18.0',
    'rectifier_fail': f'{UPS_BASE_OID}.4.19.0',
    'emergency_stop': f'{UPS_BASE_OID}.4.20.0',
    'battery_open': f'{UPS_BASE_OID}.4.21.0',
    'system_fault': f'{UPS_BASE_OID}.4.22.0',
    'rectifier_over_current': f'{UPS_BASE_OID}.4.23.0',
    'inverter_over_current': f'{UPS_BASE_OID}.4.24.0',
    'fuse_fail': f'{UPS_BASE_OID}.4.25.0',
    'maintenance_closed': f'{UPS_BASE_OID}.4.26.0',
}

# ============================================================================
# GRUPO 8: CONFIGURACIÓN (upsConfig - OID .5)
# ============================================================================
UPS_CONFIG_OIDS = {
    'output_voltage': f'{UPS_BASE_OID}.5.1.0',
    'output_frequency': f'{UPS_BASE_OID}.5.2.0',
    'battery_number': f'{UPS_BASE_OID}.5.3.0',
    'battery_ah': f'{UPS_BASE_OID}.5.4.0',
}

# ============================================================================
# CONTROL (upsControl - OID .6) — NUNCA POLLEAR, solo escritura
# ============================================================================
UPS_CONTROL_OIDS = {
    'battery_self_test': f'{UPS_BASE_OID}.6.1.0',
    'battery_deep_self_test': f'{UPS_BASE_OID}.6.2.0',
    'battery_stop_self_test': f'{UPS_BASE_OID}.6.3.0',
    'turn_on_ups': f'{UPS_BASE_OID}.6.4.0',
    'turn_off_ups': f'{UPS_BASE_OID}.6.5.0',
}

# ============================================================================
# SENSOR THS (Temperatura/Humedad)
# ============================================================================
THS_SENSOR_OIDS = {
    'temperature': f'{THS_BASE_OID}.1.1.1',
    'humidity': f'{THS_BASE_OID}.1.1.2',
    'high_temp_threshold': f'{THS_BASE_OID}.1.1.3',
    'low_temp_threshold': f'{THS_BASE_OID}.1.1.4',
    'high_humidity_threshold': f'{THS_BASE_OID}.1.1.5',
    'low_humidity_threshold': f'{THS_BASE_OID}.1.1.6',
    'high_temp_alarm_enable': f'{THS_BASE_OID}.1.1.7',
    'low_temp_alarm_enable': f'{THS_BASE_OID}.1.1.8',
    'high_humidity_alarm_enable': f'{THS_BASE_OID}.1.1.9',
    'low_humidity_alarm_enable': f'{THS_BASE_OID}.1.1.10',
}

# ============================================================================
# ALARMAS DI (Digital Input)
# ============================================================================
DI_ALARM_OIDS = {
    'di1_name': f'{THS_BASE_OID}.2.1.2',
    'di1_status': f'{THS_BASE_OID}.2.1.3',
    'di1_enable': f'{THS_BASE_OID}.2.1.4',
    'di2_name': f'{THS_BASE_OID}.2.2.2',
    'di2_status': f'{THS_BASE_OID}.2.2.3',
    'di2_enable': f'{THS_BASE_OID}.2.2.4',
    'di3_name': f'{THS_BASE_OID}.2.3.2',
    'di3_status': f'{THS_BASE_OID}.2.3.3',
    'di3_enable': f'{THS_BASE_OID}.2.3.4',
    'di4_name': f'{THS_BASE_OID}.2.4.2',
    'di4_status': f'{THS_BASE_OID}.2.4.3',
    'di4_enable': f'{THS_BASE_OID}.2.4.4',
}

# ============================================================================
# DATOS MÓDULO (modInfo/modData/modAlarm)
# ============================================================================
MODULE_OIDS = {
    'connected': f'{MODULE_BASE_OID}.1.1.2',
    'input_voltage_a': f'{MODULE_BASE_OID}.1.1.3',
    'input_voltage_b': f'{MODULE_BASE_OID}.1.1.4',
    'input_voltage_c': f'{MODULE_BASE_OID}.1.1.5',
    'input_frequency': f'{MODULE_BASE_OID}.1.1.6',
    'output_voltage_a': f'{MODULE_BASE_OID}.1.1.7',
    'output_voltage_b': f'{MODULE_BASE_OID}.1.1.8',
    'output_voltage_c': f'{MODULE_BASE_OID}.1.1.9',
    'output_frequency': f'{MODULE_BASE_OID}.1.1.10',
    'output_load_a': f'{MODULE_BASE_OID}.1.1.11',
    'output_load_b': f'{MODULE_BASE_OID}.1.1.12',
    'output_load_c': f'{MODULE_BASE_OID}.1.1.13',
    'battery_voltage': f'{MODULE_BASE_OID}.1.1.14',
    'battery_current': f'{MODULE_BASE_OID}.1.1.15',
    'internal_temperature': f'{MODULE_BASE_OID}.1.1.16',
    'alarm_rectifier_fail': f'{MODULE_BASE_OID}.1.1.17',
    'alarm_inverter_fail': f'{MODULE_BASE_OID}.1.1.18',
    'alarm_charger_fail': f'{MODULE_BASE_OID}.1.1.19',
    'alarm_fan_fail': f'{MODULE_BASE_OID}.1.1.20',
    'alarm_over_temperature': f'{MODULE_BASE_OID}.1.1.21',
    'alarm_output_overload': f'{MODULE_BASE_OID}.1.1.22',
    'alarm_inverter_over_current': f'{MODULE_BASE_OID}.1.1.23',
    'alarm_pos_bus_over_voltage': f'{MODULE_BASE_OID}.1.1.24',
    'alarm_neg_bus_over_voltage': f'{MODULE_BASE_OID}.1.1.25',
    'alarm_pos_bus_under_voltage': f'{MODULE_BASE_OID}.1.1.26',
    'alarm_neg_bus_under_voltage': f'{MODULE_BASE_OID}.1.1.27',
    'alarm_input_abnormal': f'{MODULE_BASE_OID}.1.1.28',
    'alarm_pfc_over_current': f'{MODULE_BASE_OID}.1.1.29',
    'alarm_battery_open': f'{MODULE_BASE_OID}.1.1.30',
    'alarm_fuse_fail': f'{MODULE_BASE_OID}.1.1.31',
    'alarm_communication_lost': f'{MODULE_BASE_OID}.1.1.32',
}

# ============================================================================
# DICCIONARIO UNIFICADO (grupos polleables)
# ============================================================================
UPS_OIDS = {
    'info': UPS_INFO_OIDS,
    'status': UPS_STATUS_OIDS,
    'data_bypass': UPS_DATA_BYPASS_OIDS,
    'data_input': UPS_DATA_INPUT_OIDS,
    'data_output': UPS_DATA_OUTPUT_OIDS,
    'data_battery': UPS_DATA_BATTERY_OIDS,
    'alarm': UPS_ALARM_OIDS,
    'config': UPS_CONFIG_OIDS,
    'ths': THS_SENSOR_OIDS,
    'di': DI_ALARM_OIDS,
    'module': MODULE_OIDS,
}

# ============================================================================
# CLASIFICACIÓN DE POLLING
# ============================================================================
FAST_POLL_GROUPS = ['status', 'data_input', 'data_output', 'data_battery', 'alarm']
SLOW_POLL_GROUPS = ['info', 'data_bypass', 'config', 'ths']

# ============================================================================
# FACTORES DE ESCALA (OID -> factor multiplicador)
# ============================================================================
SCALE_FACTORS = {
    # Bypass voltajes
    f'{UPS_BASE_OID}.3.1.1.0': 0.1,
    f'{UPS_BASE_OID}.3.1.2.0': 0.1,
    f'{UPS_BASE_OID}.3.1.3.0': 0.1,
    f'{UPS_BASE_OID}.3.1.4.0': 0.1,  # Bypass frequency
    # Input voltajes
    f'{UPS_BASE_OID}.3.2.1.0': 0.1,
    f'{UPS_BASE_OID}.3.2.2.0': 0.1,
    f'{UPS_BASE_OID}.3.2.3.0': 0.1,
    f'{UPS_BASE_OID}.3.2.4.0': 0.1,  # Input frequency
    # Output voltajes
    f'{UPS_BASE_OID}.3.3.1.0': 0.1,
    f'{UPS_BASE_OID}.3.3.2.0': 0.1,
    f'{UPS_BASE_OID}.3.3.3.0': 0.1,
    f'{UPS_BASE_OID}.3.3.4.0': 0.1,  # Output frequency
    # Output corrientes
    f'{UPS_BASE_OID}.3.3.8.0': 0.1,
    f'{UPS_BASE_OID}.3.3.9.0': 0.1,
    f'{UPS_BASE_OID}.3.3.10.0': 0.1,
    # Battery
    f'{UPS_BASE_OID}.3.4.1.0': 0.1,  # Battery voltage
    f'{UPS_BASE_OID}.3.4.2.0': 0.1,  # Battery current
    f'{UPS_BASE_OID}.3.4.5.0': 0.1,  # Battery temperature
    f'{UPS_BASE_OID}.3.4.6.0': 0.1,  # Positive battery voltage
    f'{UPS_BASE_OID}.3.4.7.0': 0.1,  # Negative battery voltage
    # Internal temperature
    f'{UPS_BASE_OID}.3.5.0': 0.1,
    # THS sensor
    f'{THS_BASE_OID}.1.1.1': 0.1,  # THS temperature
    f'{THS_BASE_OID}.1.1.2': 0.1,  # THS humidity
    # Module
    f'{MODULE_BASE_OID}.1.1.3': 0.1,   # Module input voltage A
    f'{MODULE_BASE_OID}.1.1.4': 0.1,
    f'{MODULE_BASE_OID}.1.1.5': 0.1,
    f'{MODULE_BASE_OID}.1.1.6': 0.1,   # Module input frequency
    f'{MODULE_BASE_OID}.1.1.7': 0.1,   # Module output voltage A
    f'{MODULE_BASE_OID}.1.1.8': 0.1,
    f'{MODULE_BASE_OID}.1.1.9': 0.1,
    f'{MODULE_BASE_OID}.1.1.10': 0.1,  # Module output frequency
    f'{MODULE_BASE_OID}.1.1.14': 0.1,  # Module battery voltage
    f'{MODULE_BASE_OID}.1.1.15': 0.1,  # Module battery current
    f'{MODULE_BASE_OID}.1.1.16': 0.1,  # Module internal temperature
}

# ============================================================================
# DICCIONARIOS DE DECODIFICACIÓN
# ============================================================================
BATTERY_TYPE = {
    0: 'VRLA',
    1: 'Litio',
    2: 'NiCd',
}

CONNECTION_STATUS = {
    0: 'Desconectado',
    1: 'Conectado',
}

POWER_SOURCE = {
    0: 'Ninguna',
    1: 'UPS Normal',
    2: 'Bypass',
}

BATTERY_STATUS = {
    0: 'No Conectada',
    1: 'No Operativa',
    2: 'Carga Flotante',
    3: 'Carga Rápida',
    4: 'Descargando',
}

MAINTAIN_BREAKER_STATUS = {
    0: 'Abierto',
    1: 'Cerrado',
}

BATTERY_TEST_RESULT = {
    0: 'Sin Test',
    1: 'Exitoso',
    2: 'Fallido',
    3: 'En Progreso',
}

BATTERY_MAINTAIN_RESULT = {
    0: 'Sin Mantenimiento',
    1: 'Exitoso',
    2: 'Fallido',
    3: 'En Progreso',
}

DECODERS = {
    'battery_type': BATTERY_TYPE,
    'connection_status': CONNECTION_STATUS,
    'power_source': POWER_SOURCE,
    'battery_status': BATTERY_STATUS,
    'maintain_breaker': MAINTAIN_BREAKER_STATUS,
    'battery_test_result': BATTERY_TEST_RESULT,
    'battery_maintain_result': BATTERY_MAINTAIN_RESULT,
}

# ============================================================================
# ETIQUETAS DE ALARMAS (español)
# ============================================================================
ALARM_LABELS = {
    'switch_normal': 'Switch Normal',
    'on_bypass': 'Operando en Bypass',
    'on_battery': 'Operando con Batería',
    'battery_low': 'Batería Baja',
    'battery_depleted': 'Batería Agotada',
    'input_abnormal': 'Entrada Anormal',
    'output_overload': 'Sobrecarga en Salida',
    'over_temperature': 'Sobretemperatura',
    'output_short': 'Cortocircuito en Salida',
    'output_over_voltage': 'Sobrevoltaje en Salida',
    'output_under_voltage': 'Bajo Voltaje en Salida',
    'bypass_abnormal': 'Bypass Anormal',
    'charger_fail': 'Falla del Cargador',
    'fan_fail': 'Falla de Ventilador',
    'bus_over_voltage': 'Sobrevoltaje en Bus',
    'bus_under_voltage': 'Bajo Voltaje en Bus',
    'bus_unbalance': 'Desbalance en Bus',
    'inverter_fail': 'Falla del Inversor',
    'rectifier_fail': 'Falla del Rectificador',
    'emergency_stop': 'Paro de Emergencia',
    'battery_open': 'Batería Abierta',
    'system_fault': 'Falla del Sistema',
    'rectifier_over_current': 'Sobrecorriente Rectificador',
    'inverter_over_current': 'Sobrecorriente Inversor',
    'fuse_fail': 'Falla de Fusible',
    'maintenance_closed': 'Mantenimiento Cerrado',
}

# ============================================================================
# LISTA DE OIDs CRÍTICOS
# ============================================================================
CRITICAL_OIDS = [
    UPS_STATUS_OIDS['power_source'],
    UPS_STATUS_OIDS['battery_status'],
    UPS_DATA_BATTERY_OIDS['voltage'],
    UPS_DATA_BATTERY_OIDS['current'],
    UPS_DATA_BATTERY_OIDS['capacity'],
    UPS_DATA_BATTERY_OIDS['remain_time'],
    UPS_DATA_BATTERY_OIDS['temperature'],
    UPS_DATA_INPUT_OIDS['voltage_a'],
    UPS_DATA_INPUT_OIDS['frequency'],
    UPS_DATA_OUTPUT_OIDS['voltage_a'],
    UPS_DATA_OUTPUT_OIDS['current_a'],
    UPS_DATA_OUTPUT_OIDS['frequency'],
    UPS_DATA_OUTPUT_OIDS['load_a'],
]

# ============================================================================
# HELPERS
# ============================================================================
def get_group_oids(group_name: str) -> dict:
    """Retorna todos los OIDs de un grupo específico."""
    return UPS_OIDS.get(group_name, {})


def get_all_oids_flat() -> list:
    """Retorna una lista plana de todos los OIDs definidos."""
    all_oids = []
    for group in UPS_OIDS.values():
        all_oids.extend(group.values())
    return all_oids


def get_pollable_oids(fast_only=True) -> dict:
    """
    Retorna un dict plano {group_field: oid} de OIDs polleables.

    Args:
        fast_only: Si True, solo retorna grupos de polling rápido.
                   Si False, retorna todos los grupos polleables.
    """
    groups = FAST_POLL_GROUPS if fast_only else FAST_POLL_GROUPS + SLOW_POLL_GROUPS
    result = {}
    for group_name in groups:
        group = UPS_OIDS.get(group_name, {})
        for field_name, oid in group.items():
            result[f'{group_name}.{field_name}'] = oid
    return result
