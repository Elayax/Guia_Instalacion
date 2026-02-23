# 🎉 PLAN DE IMPLEMENTACIÓN - UPS MONOFÁSICO CON 35 OIDs Detectados

## ✅ OIDs Detectados (35 Total)

### MIB-II Básico (6 OIDs):
```
1.3.6.1.2.1.1.1.0  - sysDescr
1.3.6.1.2.1.1.2.0  - sysObjectID (1.3.6.1.4.1.935)
1.3.6.1.2.1.1.3.0  - sysUpTime
1.3.6.1.2.1.1.4.0  - sysContact
1.3.6.1.2.1.1.5.0  - sysName
1.3.6.1.2.1.1.6.0  - sysLocation
```

### UPS-MIB RFC 1624 (24 OIDs):

**Identificación (5 OIDs):**
```
1.3.6.1.2.1.33.1.1.1.0 - upsIdentManufacturer
1.3.6.1.2.1.33.1.1.2.0 - upsIdentModel
1.3.6.1.2.1.33.1.1.3.0 - upsIdentUPSSoftwareVersion
1.3.6.1.2.1.33.1.1.4.0 - upsIdentAgentSoftwareVersion
1.3.6.1.2.1.33.1.2.1.0 - upsBatteryStatus
```

**Batería (6 OIDs):**
```
1.3.6.1.2.1.33.1.2.2.0 - upsSecondsOnBattery
1.3.6.1.2.1.33.1.2.3.0 - upsEstimatedMinutesRemaining
1.3.6.1.2.1.33.1.2.4.0 - upsEstimatedChargeRemaining (%)
1.3.6.1.2.1.33.1.2.5.0 - upsBatteryVoltage
1.3.6.1.2.1.33.1.2.6.0 - upsBatteryCurrent
1.3.6.1.2.1.33.1.2.7.0 - upsBatteryTemperature
```

**Entrada (5 OIDs):**
```
1.3.6.1.2.1.33.1.3.1.0     - upsInputLineBads
1.3.6.1.2.1.33.1.3.2.0     - upsInputNumLines (1 = monofásico)
1.3.6.1.2.1.33.1.3.3.1.2.1 - upsInputFrequency
1.3.6.1.2.1.33.1.3.3.1.3.1 - upsInputVoltage
1.3.6.1.2.1.33.1.3.3.1.4.1 - upsInputCurrent
1.3.6.1.2.1.33.1.3.3.1.5.1 - upsInputTruePower
```

**Salida (6 OIDs):**
```
1.3.6.1.2.1.33.1.4.1.0     - upsOutputSource
1.3.6.1.2.1.33.1.4.2.0     - upsOutputFrequency
1.3.6.1.2.1.33.1.4.3.0     - upsOutputNumLines (1 = monofásico)
1.3.6.1.2.1.33.1.4.4.1.2.1 - upsOutputVoltage
1.3.6.1.2.1.33.1.4.4.1.3.1 - upsOutputCurrent
1.3.6.1.2.1.33.1.4.4.1.4.1 - upsOutputPower
1.3.6.1.2.1.33.1.4.4.1.5.1 - upsOutputPercentLoad
```

### INVT Enterprise (5 OIDs):
```
1.3.6.1.4.1.56788.1.1.1.0     - invt_model
1.3.6.1.4.1.56788.1.1.2.0     - invt_serial
1.3.6.1.4.1.56788.1.3.1.2.1   - invt_input_voltage_a
1.3.6.1.4.1.56788.1.4.1.2.1   - invt_output_voltage_a
1.3.6.1.4.1.56788.1.6.1.0     - invt_battery_voltage
```

## 📝 IMPLEMENTACIÓN

### Paso 1: Crear Cliente SNMP para UPS-MIB Estándar

Crear archivo: `app/services/protocols/snmp_upsmib_client.py`

Este cliente:
- Usa SOLO los 35 OIDs detectados
- Maneja sistemas MONOFÁSICOS (1 línea)
- No consulta OIDs que no existen
- Devuelve datos en formato compatible con el dashboard

### Paso 2: Actualizar Base de Datos

Agregar campo `ups_type` a la tabla `monitoreo_config`:
- `'invt_enterprise'` - Para UPS trifásicos con OIDs INVT completos
- `'ups_mib_standard'` - Para UPS monofásicos con UPS-MIB estándar
- `'hybrid'` - Para UPS con mix de OIDs (como el tuyo)

### Paso 3: Modificar Servicio de Monitoreo

`monitoring_service.py` debe:
- Leer el campo `ups_type`
- Seleccionar el cliente correcto (INVT vs UPS-MIB)
- Pasar datos al dashboard con indicador de número de fases

### Paso 4: Adaptar Dashboard para Monofásico

Frontend (`templates/*.html`):
- Detectar `phases` en los datos
- Si `phases == 1`: Mostrar solo L1, ocultar L2/L3
- Si `phases == 3`: Mostrar L1, L2, L3

## 🎯 DATOS QUE OBTENDRÁS

Con los 35 OIDs detectados, tendrás:

### Estado General:
- ✅ Fabricante y Modelo
- ✅ Versión Software
- ✅ Tiempo de Operación

### Batería:
- ✅ Estado (cargando/descargando/normal)
- ✅ Carga % 
- ✅ Tiempo restante (minutos)
- ✅ Voltaje
- ✅ Corriente
- ✅ Temperatura

### Entrada (Monofásica):
- ✅ Voltaje L1
- ✅ Frecuencia
- ✅ Corriente
- ✅ Potencia Real

### Salida (Monofásica):
- ✅ Fuente (Normal/Batería/Bypass)
- ✅ Voltaje L1
- ✅ Frecuencia
- ✅ Corriente
- ✅ Potencia
- ✅ Carga %

## 🚀 SIGUIENTE ACCIÓN

**¿Procedo a implementar?**

Esto incluye:
1. ✅ Cliente SNMP optimizado para tus 35 OIDs
2. ✅ Actualización de BD con campo `ups_type`
3. ✅ Lógica de selección de cliente en monitoring_service
4. ✅ Dashboard adaptable monofásico/trifásico

**Tiempo estimado:** 15-20 minutos

**Resultado:** UPS 192.168.0.100 ONLINE con datos en tiempo real ✅

---

**¿Confirmas que proceda con la implementación completa?**
