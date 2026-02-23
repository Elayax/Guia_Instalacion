# Sprint 1: Infraestructura SNMP - Entregables

## ¿Qué se ha creado?

Este Sprint 1 implementa la infraestructura base para monitoreo SNMP de dispositivos UPS INC conectados via Teltonika RUT956.

## Archivos Creados

### 1. Cliente SNMP
**Archivo:** `app/services/protocols/snmp_client.py`

Clase `SNMPClient` con:
- Método `get_oid()` para lectura individual
- Método `get_multiple_oids()` para lectura batch (más eficiente)
- Método `walk_oid()` para exploración de MIB
- Timeout de 5s (optimizado para ZeroTier/VPN)
- Logging detallado
- Manejo robusto de errores

### 2. Mapeo de OIDs
**Archivo:** `app/utils/ups_oids.py`

Contiene:
- Todos los 60+ OIDs del MIB EINC (Enterprise ID 56788)
- Factores de escala documentados (x0.1, x0.01)
- Diccionarios de decodificación para valores enum
- Lista de OIDs críticos para monitoreo prioritario

Grupos:
- `UPS_INFO_OIDS`: Información del dispositivo
- `UPS_STATUS_OIDS`: Estado del UPS
- `UPS_BATTERY_OIDS`: Batería (MÁS CRÍTICO)
- `UPS_INPUT_OIDS`: Entrada
- `UPS_OUTPUT_OIDS`: Salida
- `UPS_LOAD_OIDS`: Carga
- `UPS_BYPASS_OIDS`: Bypass

### 3. Migración de Base de Datos
**Archivo:** `tests/migrate_snmp_schema.py`

Script ejecutable que crea:
- Tabla `snmp_devices`: Dispositivos UPS SNMP
- Tabla `snmp_readings`: Lecturas en tiempo real
- Tabla `snmp_alarms`: Sistema de alarmas
- Tabla `snmp_events`: Log de eventos
- Vista `unified_device_status`: Unifica Modbus + SNMP
- Índices optimizados para queries comunes

### 4. Script de Testing
**Archivo:** `tests/test_snmp_connection.py`

Pruebas completas:
- Test de conectividad básica
- Lectura de información del dispositivo
- Lectura de OIDs críticos (batería, voltaje, carga)
- Validación de rangos de valores
- Reporte formateado con estado del UPS

## Próximos Pasos

### 1. Instalar Dependencia
```bash
python -m pip install pysnmp
```

### 2. Ejecutar Migración
```bash
python tests/migrate_snmp_schema.py
```

### 3. Probar Conexión
```bash
python tests/test_snmp_connection.py
```

**(Asegúrate de que el RUT956 en 10.147.17.2:8161 esté accesible)**

## Integración con App Existente

- ✅ No rompe funcionalidad Modbus existente
- ✅ Reutiliza base de datos SQLite actual
- ✅ Compatible con arquitectura Flask actual
- ✅ Listo para Sprint 2: Worker de polling

## Siguientes Sprints

- **Sprint 2:** Worker de polling + Parsers + Alarmas
- **Sprint 3:** API REST endpoints
- **Sprint 4:** Dashboard web unificado

## Archivos de Referencia

- **Plan completo:** `snmp_implementation_plan.md`
- **Tareas:** `task.md`
- **Guía ZeroTier:** `zerotier_teltonika_guide.md`
