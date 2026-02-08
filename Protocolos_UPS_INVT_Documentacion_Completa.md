# Documentación Completa: Protocolos de Comunicación UPS INVT

## Información General

**Fabricante:** INVT  
**Protocolos Soportados:** Modbus TCP/RTU & SNMP v1/v2c  
**Versión del Documento:** 1.1 (Modbus) / 1.2 (SNMP)  
**Alcance:** Monitorización exhaustiva de parámetros eléctricos, ambientales, alarmas y sistemas modulares

---

## 📋 Tabla de Contenidos

1. [Introducción a los Protocolos](#introducción-a-los-protocolos)
2. [Configuración de Conexión](#configuración-de-conexión)
3. [Sistema de Direccionamiento Modbus](#sistema-de-direccionamiento-modbus)
4. [Parámetros Eléctricos](#parámetros-eléctricos)
5. [Registros de Estado](#registros-de-estado)
6. [Sistema de Alarmas](#sistema-de-alarmas)
7. [UPS Modulares](#ups-modulares)
8. [Sensores Ambientales](#sensores-ambientales)
9. [Mapeo SNMP](#mapeo-snmp)
10. [Buenas Prácticas y Optimización](#buenas-prácticas-y-optimización)

---

## 1. Introducción a los Protocolos

### ¿Qué son estos protocolos?

Los UPS INVT ofrecen dos protocolos industriales para monitorización y control:

- **Modbus TCP/RTU:** Protocolo maestro-esclavo para lectura/escritura de registros
- **SNMP v1/v2c:** Protocolo de gestión de red con sistema de OIDs y traps

### ¿Cuándo usar cada uno?

| Protocolo | Mejor para | Ventajas |
|-----------|------------|----------|
| **Modbus TCP** | SCADA, PLC, sistemas industriales | Polling eficiente, bajo overhead |
| **Modbus RTU** | Conexiones serie RS485 | Amplia compatibilidad hardware |
| **SNMP** | Gestión de red, NMS, alarmas | Traps automáticas, integración IT |

---

## 2. Configuración de Conexión

### 2.1. Parámetros Modbus TCP

```
Puerto TCP:        502
Unit ID (Slave):   1 (valor por defecto)
Function Codes:    03 (Read Holding Registers)
                   04 (Read Input Registers)
Formato de Datos:  16-bit Integer, Big Endian
Timeout:           3-5 segundos recomendado
```

**Importante:** La mayoría de valores analógicos requieren aplicar un coeficiente de escalado. Por ejemplo:
```
Valor crudo:  2205
Coeficiente:  0.1
Valor real:   220.5 V
```

### 2.2. Parámetros SNMP

```
Puerto Consulta (GET):     161/UDP
Puerto Traps (TRAP):       162/UDP
OID Raíz (Enterprise):     .1.3.6.1.4.1.56788
Community String Lectura:  public
Community String Escritura: private (si aplica)
Versión SNMP:              v1 o v2c
```

### 2.3. Ejemplo de Conexión Modbus TCP (Python)

```python
from pymodbus.client import ModbusTcpClient

# Conectar al UPS
client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# Leer voltaje de entrada Fase A (Registro 112)
# Dirección = Offset UPS (100) + ID Registro (12) = 112
result = client.read_holding_registers(112, 1, unit=1)

if not result.isError():
    # Aplicar coeficiente 0.1
    voltage = result.registers[0] * 0.1
    print(f"Voltaje Entrada Fase A: {voltage} V")

client.close()
```

---

## 3. Sistema de Direccionamiento Modbus

### 3.1. Regla del Offset

⚠️ **REGLA CRÍTICA:** Para calcular la dirección Modbus real de cualquier registro:

```
Dirección Final = Offset del Equipo + ID del Registro
```

### 3.2. Tabla de Offsets por Tipo de Equipo

| Tipo de Equipo | Offset Base | Rango de IDs | Descripción |
|----------------|-------------|--------------|-------------|
| **Gabinete** | 0 | 0 - 99 | Información general del sistema |
| **UPS** | 100 | 100 - 3171 | Datos eléctricos principales |
| **Sensor Temp/Humedad (THS)** | 3271 | 0 - 39 | Sensores ambientales |
| **Sensor Fugas de Agua** | 3311 | 0 - 9 | Detección de inundación |

### 3.3. Ejemplos de Cálculo de Direcciones

**Ejemplo 1: Leer voltaje de entrada Fase A**
```
ID del Registro: 12
Offset UPS: 100
Dirección Final: 100 + 12 = 112
```

**Ejemplo 2: Leer temperatura de batería**
```
ID del Registro: 49
Offset UPS: 100
Dirección Final: 100 + 49 = 149
```

**Ejemplo 3: Leer temperatura ambiental**
```
ID del Registro: 0
Offset THS: 3271
Dirección Final: 3271 + 0 = 3271
```

---

## 4. Parámetros Eléctricos

### 4.1. Entrada (Input) - Offset Base: 100

| ID | Parámetro | Coef. | Unidad | Dirección | OID SNMP |
|----|-----------|-------|--------|-----------|----------|
| 12 | Input Voltage Phase A | 0.1 | V | 112 | .1.1.1.3.2.1 |
| 13 | Input Voltage Phase B | 0.1 | V | 113 | .1.1.1.3.2.2 |
| 14 | Input Voltage Phase C | 0.1 | V | 114 | .1.1.1.3.2.3 |
| 15 | Input Current Phase A | 0.1 | A | 115 | .1.1.1.3.2.4 |
| 16 | Input Current Phase B | 0.1 | A | 116 | .1.1.1.3.2.5 |
| 17 | Input Current Phase C | 0.1 | A | 117 | .1.1.1.3.2.6 |
| 18 | Input Frequency Phase A | 0.01 | Hz | 118 | .1.1.1.3.2.7 |
| 19 | Input Frequency Phase B | 0.01 | Hz | 119 | .1.1.1.3.2.8 |
| 20 | Input Frequency Phase C | 0.01 | Hz | 120 | .1.1.1.3.2.9 |
| 21 | Input Power Factor A | 0.01 | - | 121 | .1.1.1.3.2.10 |
| 22 | Input Power Factor B | 0.01 | - | 122 | .1.1.1.3.2.11 |
| 23 | Input Power Factor C | 0.01 | - | 123 | .1.1.1.3.2.12 |

**Nota:** Todos los OIDs SNMP deben tener el prefijo `.1.3.6.1.4.1.56788`

### 4.2. Bypass - Offset Base: 100

| ID | Parámetro | Coef. | Unidad | Dirección | OID SNMP |
|----|-----------|-------|--------|-----------|----------|
| 0 | Bypass Voltage Phase A | 0.1 | V | 100 | .1.1.1.3.1.1 |
| 1 | Bypass Voltage Phase B | 0.1 | V | 101 | .1.1.1.3.1.2 |
| 2 | Bypass Voltage Phase C | 0.1 | V | 102 | .1.1.1.3.1.3 |
| 3 | Bypass Current Phase A | 0.1 | A | 103 | .1.1.1.3.1.4 |
| 6 | Bypass Frequency Phase A | 0.01 | Hz | 106 | .1.1.1.3.1.7 |
| 56 | Bypass Fan Run Time | 1 | h | 156 | .1.1.1.3.1.13 |

### 4.3. Salida (Output) - Offset Base: 100

| ID | Parámetro | Coef. | Unidad | Dirección | OID SNMP |
|----|-----------|-------|--------|-----------|----------|
| 24 | Output Voltage Phase A | 0.1 | V | 124 | .1.1.1.3.3.1 |
| 25 | Output Voltage Phase B | 0.1 | V | 125 | .1.1.1.3.3.2 |
| 26 | Output Voltage Phase C | 0.1 | V | 126 | .1.1.1.3.3.3 |
| 27 | Output Current Phase A | 0.1 | A | 127 | .1.1.1.3.3.4 |
| 28 | Output Current Phase B | 0.1 | A | 128 | .1.1.1.3.3.5 |
| 29 | Output Current Phase C | 0.1 | A | 129 | .1.1.1.3.3.6 |
| 30 | Output Frequency Phase A | 0.01 | Hz | 130 | .1.1.1.3.3.7 |
| 33 | Output Power Factor A | 0.01 | - | 133 | .1.1.1.3.3.10 |
| 36 | Output Apparent Power A | 0.1 | kVA | 136 | .1.1.1.3.4.1 |
| 39 | Output Active Power A | 0.1 | kW | 139 | .1.1.1.3.4.4 |
| 45 | Load Percentage Phase A | 0.1 | % | 145 | .1.1.1.3.4.10 |
| 46 | Load Percentage Phase B | 0.1 | % | 146 | .1.1.1.3.4.11 |
| 47 | Load Percentage Phase C | 0.1 | % | 147 | .1.1.1.3.4.12 |

### 4.4. Batería (Battery) - Offset Base: 100

| ID | Parámetro | Coef. | Unidad | Dirección | OID SNMP |
|----|-----------|-------|--------|-----------|----------|
| 49 | Battery Temperature | 0.1 | °C | 149 | .1.1.1.3.5.1 |
| 50 | Battery Voltage (+) | 0.1 | V | 150 | .1.1.1.3.5.2 |
| 51 | Battery Voltage (-) | 0.1 | V | 151 | .1.1.1.3.5.3 |
| 52 | Battery Current (+) | 0.1 | A | 152 | .1.1.1.3.5.4 |
| 53 | Battery Current (-) | 0.1 | A | 153 | .1.1.1.3.5.5 |
| 54 | Remain Time | 0.1 | Min | 154 | .1.1.1.3.5.6 |
| 55 | Capacity Percentage | 0.1 | % | 155 | .1.1.1.3.5.7 |

---

## 5. Registros de Estado

### 5.1. Estados del Sistema (Offset: 100)

Estos registros devuelven valores enteros que representan estados específicos.

#### 5.1.1. Modo de Suministro de Energía (ID: 71, Dirección: 171)

```
Valores posibles:
0 = No Load (Sin carga)
1 = Load On UPS (Carga en inversor/batería)
2 = Load On Bypass (Carga en bypass/red)
```

**Ejemplo de interpretación:**
```python
mode = read_register(171)
if mode == 0:
    print("Sistema sin carga")
elif mode == 1:
    print("Carga alimentada por UPS (inversor)")
elif mode == 2:
    print("Carga alimentada por bypass")
```

#### 5.1.2. Estado de Batería (ID: 72, Dirección: 172)

```
Valores posibles:
0 = Not Connected (Batería no conectada)
1 = Not Work (Batería en falla)
2 = Float Charge (Carga de flotación/mantenimiento)
3 = Boost Charge (Carga rápida)
4 = Discharge (Descargando - usando batería)
```

#### 5.1.3. Estado del Breaker de Mantenimiento (ID: 73, Dirección: 173)

```
Valores posibles:
0 = Open (Normal - breaker abierto)
1 = Close (Mantenimiento activo - breaker cerrado)
```

#### 5.1.4. Estado de Prueba de Batería (ID: 74, Dirección: 174)

```
Valores posibles:
0 = No Test (Sin prueba)
1 = Test OK (Prueba exitosa)
2 = Test Fail (Prueba fallida)
3 = Testing (Prueba en progreso)
```

#### 5.1.5. Estado del Rectificador (ID: 76, Dirección: 176)

```
Valores posibles:
0 = Close (Cerrado/Apagado)
1 = Softstart (Arranque suave en progreso)
2 = Normal Working (Operación normal)
```

#### 5.1.6. Configuración de Fases (ID: 91, Dirección: 191)

```
Valores posibles:
0 = 3/3 (Trifásico entrada / Trifásico salida)
1 = 3/1 (Trifásico entrada / Monofásico salida)
2 = 1/1 (Monofásico entrada / Monofásico salida)
```

#### 5.1.7. Tipo de Batería (ID: 95, Dirección: 195)

```
Valores posibles:
0 = VRLA (Plomo-ácido regulada por válvula)
1 = Lithium (Litio)
2 = NiCd (Níquel-cadmio)
```

---

## 6. Sistema de Alarmas

### 6.1. Alarmas SNMP (Traps)

Las alarmas se envían como traps SNMP con el OID base: `.1.3.6.1.4.1.56788.0.X`

#### 6.1.1. Alarmas de Red y Bypass

| OID | Código | Nombre | Descripción | Severidad |
|-----|--------|--------|-------------|-----------|
| .0.1 | Communication Lost | Pérdida de comunicación | Falla en tarjeta de red | 🔴 Crítica |
| .0.7 | Input Fail | Falla de red comercial | Apagón o voltaje fuera de rango | 🟠 Alta |
| .0.9 | Bypass Fail | Falla en bypass | Circuito bypass no disponible | 🟠 Alta |
| .0.11 | Bypass Sequence Fail | Error de secuencia | Fases incorrectas en bypass | 🔴 Crítica |
| .0.13 | Bypass Voltage Fail | Voltaje bypass fuera de rango | Voltaje no aceptable | 🟠 Alta |
| .0.15 | Bypass Untrack | Bypass desincronizado | Frecuencia fuera de sincronía | 🟡 Media |
| .0.17 | Bypass Overload | Sobrecarga en bypass | Carga excede capacidad | 🔴 Crítica |

#### 6.1.2. Alarmas de Batería

| OID | Código | Nombre | Descripción | Severidad |
|-----|--------|--------|-------------|-----------|
| .0.23 | Battery EOD | Fin de descarga | Shutdown inminente | 🔴 Crítica |
| .0.25 | Battery Volt Low | Voltaje bajo | Pre-alarma de batería baja | 🟠 Alta |
| .0.27 | Battery Reverse | Polaridad invertida | Batería conectada al revés | 🔴 Crítica |
| .0.47 | Charger Fail | Falla del cargador | Cargador no funciona | 🔴 Crítica |

#### 6.1.3. Alarmas Críticas del UPS

| OID | Código | Nombre | Descripción | Severidad |
|-----|--------|--------|-------------|-----------|
| .0.5 | EPO | Parada de emergencia | EPO activado | 🔴 Crítica |
| .0.21 | Output Shorted | Cortocircuito en salida | Protección activada | 🔴 Crítica |
| .0.29 | UPS Over Temperature | Sobretemperatura | Temperatura interna alta | 🔴 Crítica |
| .0.33 | Rectifier Fail | Falla del rectificador | Rectificador no opera | 🔴 Crítica |
| .0.35 | Invertor Fail | Falla del inversor | Inversor no opera | 🔴 Crítica |
| .0.37 | Fan Fail | Falla de ventilador | Sistema de refrigeración | 🟠 Alta |
| .0.39 | Invertor Overload | Sobrecarga en inversor | Carga excede capacidad | 🔴 Crítica |
| .0.67 | DC Bus Over Voltage | Sobrevoltaje en Bus DC | Bus DC fuera de rango | 🔴 Crítica |

### 6.2. Detección de Alarmas vía Modbus

Aunque las traps SNMP son el método preferido, puedes detectar alarmas monitoreando:

1. **Registros de Estado:** Cambios en Power Supply Mode (171) o Battery Status (172)
2. **Valores Analógicos:** Umbrales en voltajes, corrientes, temperatura
3. **Registros de Alarma Específicos:** Si están implementados

**Ejemplo de lógica de alarma:**
```python
# Detectar corte de luz
input_voltage = read_register(112) * 0.1  # Fase A
battery_status = read_register(172)
power_mode = read_register(171)

if input_voltage < 100 and battery_status == 4 and power_mode == 1:
    print("⚠️ ALARMA: Corte de luz - Operando en batería")
```

---

## 7. UPS Modulares

### 7.1. Sistema de Direccionamiento para Módulos

Los UPS modulares tienen múltiples módulos de potencia redundantes. Cada módulo tiene su propio conjunto de parámetros.

#### Fórmula de Dirección Modbus:

```
Dirección = Offset_UPS (100) + ID_Base (111) + (Nº_Módulo - 1) × 96 + ID_Relativo
```

**Donde:**
- `Offset_UPS` = 100 (constante)
- `ID_Base` = 111 (inicio del bloque modular)
- `Nº_Módulo` = 1, 2, 3, ... (número del módulo a leer)
- `ID_Relativo` = Posición del parámetro dentro del bloque (ver tabla)

### 7.2. Parámetros por Módulo

| ID Relativo | Parámetro | Coef. | Unidad |
|-------------|-----------|-------|--------|
| +0 | AC Input Voltage Phase A | 0.1 | V |
| +3 | AC Input Current Phase A | 0.1 | A |
| +12 | DC Bus Voltage (+) | 0.1 | V |
| +14 | Battery Voltage (+) | 0.1 | V |
| +20 | Discharge Current (+) | 0.1 | A |
| +34 | AC Output Voltage A | 0.1 | V |
| +84 | Inlet Temperature | 0.1 | °C |
| +85 | Outlet Temperature | 0.1 | °C |
| +95 | Input SCR Temperature | 0.1 | °C |

### 7.3. Ejemplos de Cálculo

**Ejemplo 1: Leer voltaje de entrada del Módulo 1**
```
Parámetro: AC Input Voltage Phase A (ID_Relativo = 0)
Dirección = 100 + 111 + (1-1)×96 + 0 = 211
```

**Ejemplo 2: Leer temperatura de entrada del Módulo 2**
```
Parámetro: Inlet Temperature (ID_Relativo = 84)
Dirección = 100 + 111 + (2-1)×96 + 84
Dirección = 100 + 111 + 96 + 84 = 391
```

**Ejemplo 3: Leer voltaje de salida del Módulo 3**
```
Parámetro: AC Output Voltage A (ID_Relativo = 34)
Dirección = 100 + 111 + (3-1)×96 + 34
Dirección = 100 + 111 + 192 + 34 = 437
```

### 7.4. Código de Ejemplo

```python
def leer_parametro_modulo(client, num_modulo, id_relativo, coeficiente):
    """
    Lee un parámetro de un módulo específico
    
    Args:
        client: Cliente Modbus
        num_modulo: Número del módulo (1, 2, 3, ...)
        id_relativo: ID del parámetro dentro del módulo
        coeficiente: Factor de escala
    """
    direccion = 100 + 111 + (num_modulo - 1) * 96 + id_relativo
    resultado = client.read_holding_registers(direccion, 1, unit=1)
    
    if not resultado.isError():
        valor = resultado.registers[0] * coeficiente
        return valor
    return None

# Ejemplo: Leer temperatura de entrada de 3 módulos
for modulo in range(1, 4):
    temp = leer_parametro_modulo(client, modulo, 84, 0.1)
    print(f"Módulo {modulo} - Temp. Entrada: {temp}°C")
```

---

## 8. Sensores Ambientales

### 8.1. Sensor de Temperatura y Humedad (THS)

**Offset Modbus:** 3271

| ID | Parámetro | Coef. | Unidad | Dirección | OID SNMP |
|----|-----------|-------|--------|-----------|----------|
| 0 | Temperature | 0.1 | °C | 3271 | .1.1.2.2.1 |
| 1 | Humidity | 0.1 | % | 3272 | .1.1.2.2.2 |

#### Alarmas THS (SNMP Traps)

| OID | Nombre | Descripción |
|-----|--------|-------------|
| .0.103 | High Temperature | Temperatura alta |
| .0.105 | Low Temperature | Temperatura baja |
| .0.107 | High Humidity | Humedad alta |
| .0.109 | Low Humidity | Humedad baja |

**Ejemplo de lectura:**
```python
# Leer temperatura ambiente
temp = client.read_holding_registers(3271, 1, unit=1).registers[0] * 0.1
print(f"Temperatura ambiente: {temp}°C")

# Leer humedad
humidity = client.read_holding_registers(3272, 1, unit=1).registers[0] * 0.1
print(f"Humedad relativa: {humidity}%")
```

### 8.2. Sensor de Fugas de Agua

**Offset Modbus:** 3311

| ID | Parámetro | Valores | Unidad | Dirección | OID SNMP |
|----|-----------|---------|--------|-----------|----------|
| 0 | Leakage Location | Entero | - | 3311 | .1.1.3.2.1 |

**Interpretación del valor:**
- El valor entero indica la ubicación/zona donde se detectó la fuga
- 0 = Sin fugas detectadas
- 1-N = Zona específica con fuga

#### Alarmas de Fugas (SNMP Traps)

| OID | Nombre | Descripción |
|-----|--------|-------------|
| .0.113 | Leakage Detected | Fuga de agua detectada |
| .0.115 | Cable Abnormal | Cable del sensor roto o desconectado |

---

## 9. Mapeo SNMP

### 9.1. Estructura de OIDs

Todos los OIDs tienen el prefijo base:
```
.1.3.6.1.4.1.56788
```

**Estructura general:**
```
.1.3.6.1.4.1.56788.[categoría].[subcategoría].[parámetro]
```

### 9.2. Categorías Principales

| Categoría | OID Base | Descripción |
|-----------|----------|-------------|
| System Info | .1.1.1 | Información del sistema |
| Environmental | .1.1.2 | Sensores ambientales |
| Leakage | .1.1.3 | Sensores de agua |
| Traps | .0.X | Alarmas y eventos |

### 9.3. Ejemplos de Consultas SNMP

**Usando snmpget (Linux):**

```bash
# Leer voltaje de entrada Fase A
snmpget -v2c -c public 192.168.1.100 .1.3.6.1.4.1.56788.1.1.1.3.2.1

# Leer temperatura de batería
snmpget -v2c -c public 192.168.1.100 .1.3.6.1.4.1.56788.1.1.1.3.5.1

# Leer temperatura ambiente
snmpget -v2c -c public 192.168.1.100 .1.3.6.1.4.1.56788.1.1.2.2.1
```

**Usando Python (pysnmp):**

```python
from pysnmp.hlapi import *

def leer_oid_snmp(ip, community, oid):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    
    if errorIndication or errorStatus:
        print(f"Error: {errorIndication or errorStatus}")
    else:
        for varBind in varBinds:
            return varBind[1]

# Ejemplo
voltage = leer_oid_snmp('192.168.1.100', 'public', 
                        '1.3.6.1.4.1.56788.1.1.1.3.2.1')
print(f"Voltaje: {int(voltage) * 0.1} V")
```

### 9.4. Configuración de Traps SNMP

Para recibir traps automáticas, configura un trap receiver:

```python
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.proto import api

def callback_trap(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        if msgVer in api.protoModules:
            pMod = api.protoModules[msgVer]
        else:
            print('Versión SNMP no soportada')
            return
        
        reqMsg, wholeMsg = pMod.Message().decodePartially(wholeMsg)
        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        
        print(f'Trap recibido de {transportAddress[0]}:')
        for oid, val in pMod.apiTrapPDU.getVarBinds(reqPDU):
            print(f'  {oid.prettyPrint()} = {val.prettyPrint()}')
    
    return wholeMsg

# Configurar listener
transportDispatcher = AsyncoreDispatcher()
transportDispatcher.registerRecvCbFun(callback_trap)
transportDispatcher.registerTransport(
    udp.domainName, udp.UdpTransport().openServerMode(('0.0.0.0', 162))
)
transportDispatcher.jobStarted(1)

try:
    transportDispatcher.runDispatcher()
except:
    transportDispatcher.closeDispatcher()
```

---

## 10. Buenas Prácticas y Optimización

### 10.1. Lectura Eficiente de Registros

❌ **MAL - Lectura individual:**
```python
# Ineficiente - 50 llamadas para 50 registros
for i in range(100, 150):
    valor = client.read_holding_registers(i, 1)
```

✅ **BIEN - Lectura en bloques:**
```python
# Eficiente - 1 llamada para 50 registros
valores = client.read_holding_registers(100, 50)
voltage_a = valores.registers[12] * 0.1  # ID 12 (pos 12)
voltage_b = valores.registers[13] * 0.1  # ID 13 (pos 13)
# ... procesar todos los valores
```

### 10.2. Estrategia de Polling Recomendada

| Tipo de Dato | Intervalo | Justificación |
|--------------|-----------|---------------|
| **Parámetros eléctricos críticos** | 1-2 seg | Detección rápida de problemas |
| **Batería** | 5-10 seg | Cambios lentos |
| **Temperatura/Humedad** | 30-60 seg | Cambios muy lentos |
| **Estados del sistema** | 2-5 seg | Balance entre velocidad y carga |

### 10.3. Manejo de Errores

```python
def leer_seguro(client, direccion, cantidad, coeficiente=1.0, reintentos=3):
    """
    Lectura robusta con reintentos y manejo de errores
    """
    for intento in range(reintentos):
        try:
            resultado = client.read_holding_registers(direccion, cantidad, unit=1)
            
            if resultado.isError():
                print(f"Error en lectura: {resultado}")
                continue
            
            valores = [r * coeficiente for r in resultado.registers]
            return valores
            
        except Exception as e:
            print(f"Excepción en intento {intento + 1}: {e}")
            if intento < reintentos - 1:
                time.sleep(1)
            else:
                return None
    
    return None
```

### 10.4. Consideraciones sobre Drivers Modbus

⚠️ **IMPORTANTE:** Algunos drivers Modbus usan direccionamiento base 1 en lugar de base 0:

| Software | Notación | Ejemplo |
|----------|----------|---------|
| **Python pymodbus** | Base 0 | Dirección 112 |
| **Wonderware** | Base 1 (40001+) | Dirección 40113 |
| **Rockwell RSLinx** | Base 1 (40001+) | Dirección 40113 |
| **Schneider Unity** | Base 0 | Dirección 112 |

**Si tus valores no cuadran:**
```
Dirección esperada: 112
Dirección en driver base 1: 40113 (40001 + 112)
```

### 10.5. Validación de Datos

```python
def validar_voltaje(voltaje, min_v=190, max_v=250):
    """Validar que el voltaje esté en rango aceptable"""
    if voltaje < min_v or voltaje > max_v:
        print(f"⚠️ Voltaje fuera de rango: {voltaje}V")
        return False
    return True

def validar_coeficiente(valor_crudo, coef):
    """Verificar que el coeficiente se aplicó correctamente"""
    valor_calculado = valor_crudo * coef
    # El valor no debería ser ni muy grande ni muy pequeño
    if valor_calculado > 10000 or valor_calculado < 0.01:
        print(f"⚠️ Posible error en coeficiente: {valor_crudo} × {coef} = {valor_calculado}")
        return False
    return True
```

### 10.6. Logging y Depuración

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ups_monitor.log'),
        logging.StreamHandler()
    ]
)

def leer_con_log(client, direccion, nombre_parametro, coef):
    """Lectura con logging detallado"""
    logging.debug(f"Leyendo {nombre_parametro} en dirección {direccion}")
    
    resultado = client.read_holding_registers(direccion, 1, unit=1)
    
    if resultado.isError():
        logging.error(f"Error leyendo {nombre_parametro}: {resultado}")
        return None
    
    valor_crudo = resultado.registers[0]
    valor_final = valor_crudo * coef
    
    logging.info(f"{nombre_parametro}: {valor_final} (crudo: {valor_crudo}, coef: {coef})")
    
    return valor_final
```

### 10.7. Checklist de Integración

- [ ] Verificar conectividad de red (ping al UPS)
- [ ] Confirmar puerto TCP 502 abierto (telnet o nmap)
- [ ] Validar Unit ID (probar 1, 0, 255)
- [ ] Probar lectura de un registro simple (ej: 112)
- [ ] Verificar que los coeficientes se aplican correctamente
- [ ] Validar que los valores tienen sentido físicamente
- [ ] Configurar timeouts apropiados (3-5 segundos)
- [ ] Implementar reconexión automática
- [ ] Configurar traps SNMP si se usa SNMP
- [ ] Documentar offsets específicos de tu driver

### 10.8. Troubleshooting Común

| Problema | Causa Probable | Solución |
|----------|----------------|----------|
| **Valores incorrectos** | Coeficiente no aplicado | Verificar multiplicación por 0.1 o 0.01 |
| **Timeout de conexión** | Firewall, puerto incorrecto | Verificar puerto 502, revisar firewall |
| **Registros fuera de rango** | Offset mal calculado | Revisar fórmula: Base + ID |
| **Valores negativos** | Interpretación signed/unsigned | Convertir a unsigned 16-bit |
| **Conexión intermitente** | Saturación de red UPS | Reducir frecuencia de polling |
| **Traps no reciben** | Puerto 162 bloqueado | Abrir UDP 162, verificar community |

---

## 📚 Apéndices

### A. Tabla de Conversión Rápida (Ejemplo)

| Valor Crudo | Coef. 0.1 | Coef. 0.01 |
|-------------|-----------|------------|
| 2205 | 220.5 V | 22.05 |
| 500 | 50.0 Hz | 5.00 |
| 980 | 98.0 % | 9.80 |
| 4800 | 480.0 V | 48.00 |

### B. Códigos de Error Modbus Comunes

| Código | Nombre | Significado |
|--------|--------|-------------|
| 01 | Illegal Function | Función no soportada |
| 02 | Illegal Data Address | Dirección inválida |
| 03 | Illegal Data Value | Valor fuera de rango |
| 04 | Slave Device Failure | Falla en dispositivo |
| 06 | Slave Device Busy | Dispositivo ocupado |

### C. Plantilla de Monitoreo Python Completa

```python
#!/usr/bin/env python3
"""
Monitor completo para UPS INVT
Lectura de parámetros críticos vía Modbus TCP
"""

from pymodbus.client import ModbusTcpClient
import time
import logging

# Configuración
UPS_IP = '192.168.1.100'
UPS_PORT = 502
UNIT_ID = 1
POLL_INTERVAL = 5  # segundos

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UPSMonitor:
    def __init__(self, ip, port=502, unit=1):
        self.client = ModbusTcpClient(ip, port=port)
        self.unit = unit
        
    def conectar(self):
        """Establecer conexión con el UPS"""
        if self.client.connect():
            logger.info(f"Conectado a UPS en {UPS_IP}:{UPS_PORT}")
            return True
        else:
            logger.error("No se pudo conectar al UPS")
            return False
    
    def leer_bloque(self, direccion, cantidad):
        """Leer bloque de registros"""
        try:
            resultado = self.client.read_holding_registers(
                direccion, cantidad, unit=self.unit
            )
            if not resultado.isError():
                return resultado.registers
            else:
                logger.error(f"Error leyendo dirección {direccion}")
                return None
        except Exception as e:
            logger.error(f"Excepción: {e}")
            return None
    
    def leer_parametros_basicos(self):
        """Leer parámetros eléctricos principales"""
        # Leer bloque de entrada, salida y batería (100-155)
        datos = self.leer_bloque(100, 56)
        
        if datos is None:
            return None
        
        return {
            'input': {
                'voltage_a': datos[12] * 0.1,  # ID 12
                'voltage_b': datos[13] * 0.1,
                'voltage_c': datos[14] * 0.1,
                'current_a': datos[15] * 0.1,
                'frequency': datos[18] * 0.01,
            },
            'output': {
                'voltage_a': datos[24] * 0.1,  # ID 24
                'voltage_b': datos[25] * 0.1,
                'voltage_c': datos[26] * 0.1,
                'current_a': datos[27] * 0.1,
                'load_pct_a': datos[45] * 0.1,
            },
            'battery': {
                'temperature': datos[49] * 0.1,  # ID 49
                'voltage': datos[50] * 0.1,
                'current': datos[52] * 0.1,
                'capacity_pct': datos[55] * 0.1,
                'remain_time': datos[54] * 0.1,
            }
        }
    
    def leer_estados(self):
        """Leer registros de estado"""
        datos = self.leer_bloque(171, 25)  # Desde 171 hasta ~195
        
        if datos is None:
            return None
        
        return {
            'power_mode': datos[0],      # 171
            'battery_status': datos[1],  # 172
            'maint_breaker': datos[2],   # 173
            'battery_test': datos[3],    # 174
            'rectifier_status': datos[5],# 176
        }
    
    def monitorear_continuo(self, intervalo=5):
        """Monitoreo continuo con impresión de datos"""
        logger.info(f"Iniciando monitoreo continuo (intervalo: {intervalo}s)")
        
        try:
            while True:
                parametros = self.leer_parametros_basicos()
                estados = self.leer_estados()
                
                if parametros and estados:
                    print("\n" + "="*60)
                    print(f"ESTADO DEL UPS - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*60)
                    
                    print(f"\n[ENTRADA]")
                    print(f"  Voltaje: {parametros['input']['voltage_a']:.1f}V")
                    print(f"  Corriente: {parametros['input']['current_a']:.1f}A")
                    print(f"  Frecuencia: {parametros['input']['frequency']:.2f}Hz")
                    
                    print(f"\n[SALIDA]")
                    print(f"  Voltaje: {parametros['output']['voltage_a']:.1f}V")
                    print(f"  Corriente: {parametros['output']['current_a']:.1f}A")
                    print(f"  Carga: {parametros['output']['load_pct_a']:.1f}%")
                    
                    print(f"\n[BATERÍA]")
                    print(f"  Voltaje: {parametros['battery']['voltage']:.1f}V")
                    print(f"  Corriente: {parametros['battery']['current']:.1f}A")
                    print(f"  Capacidad: {parametros['battery']['capacity_pct']:.1f}%")
                    print(f"  Tiempo restante: {parametros['battery']['remain_time']:.1f} min")
                    print(f"  Temperatura: {parametros['battery']['temperature']:.1f}°C")
                    
                    # Interpretar estados
                    modos = ['Sin carga', 'En UPS', 'En Bypass']
                    bat_estados = ['No conectada', 'Falla', 'Flotación', 'Carga rápida', 'Descargando']
                    
                    print(f"\n[ESTADO DEL SISTEMA]")
                    print(f"  Modo de alimentación: {modos[estados['power_mode']]}")
                    print(f"  Estado de batería: {bat_estados[estados['battery_status']]}")
                    
                    # Detectar alarmas básicas
                    if parametros['input']['voltage_a'] < 180:
                        print("\n⚠️  ALARMA: Voltaje de entrada bajo")
                    
                    if estados['battery_status'] == 4:
                        print("\n⚠️  ALARMA: Operando en batería (apagón)")
                    
                    if parametros['battery']['capacity_pct'] < 20:
                        print("\n🔴 ALARMA CRÍTICA: Batería baja (<20%)")
                
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            logger.info("\nMonitoreo detenido por el usuario")
        finally:
            self.client.close()

# Ejecución principal
if __name__ == "__main__":
    monitor = UPSMonitor(UPS_IP, UPS_PORT, UNIT_ID)
    
    if monitor.conectar():
        monitor.monitorear_continuo(POLL_INTERVAL)
```

---

## 📞 Soporte y Referencias

**Documentación Original:**
- upsViewer ModbusTCP Protocol EN (v1.1)
- snmp mibV1.2

**Protocolos Estándar:**
- Modbus TCP: [modbus.org](https://www.modbus.org)
- SNMP: RFC 1157 (v1), RFC 3416 (v2c)

**Bibliotecas Recomendadas:**
- Python Modbus: pymodbus
- Python SNMP: pysnmp
- Node.js Modbus: node-modbus
- C#/.NET Modbus: NModbus

---

**Última actualización:** Febrero 2026  
**Versión del documento:** 1.0  
**Autor:** Documentación técnica generada desde especificaciones INVT
