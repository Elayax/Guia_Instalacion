# 🎉 SOLUCIÓN IMPLEMENTADA: Auto-Detección SNMP Avanzada

## 📋 Tu Problema

> "**Conecté la IP del UPS y jala**, pero cuando lo intento agregar al sistema no funciona. Creo que **usa protocolo SNMP diferente** o no sé exactamente qué está fallando. **Requiero que el SCADA me vaya avisando cómo va la conexión y todo el estatus**."

## ✅ Solución Implementada

He creado una **herramienta de AUTO-DETECCIÓN SNMP** que:

### 🔍 ¿Qué hace?

1. **Prueba automáticamente**:
   - SNMPv1
   - SNMPv2c
   - Diferentes community strings (public, private, admin, snmp, manager, ups, monitor)

2. **Detecta automáticamente**:
   - Qué versión de SNMP funciona
   - Qué community string es correcta
   - Qué tipo de UPS es (INVT Enterprise, UPS-MIB Est índar, o Genérico)
   - Qué OIDs están disponibles

3. **Te muestra EN TIEMPO REAL**:
   - Cada paso que está probando
   - Qué funciona y qué no
   - El status completo del diagnóstico

4. **Te da la configuración exacta** para agregar el UPS al monitoreo

## 🚀 Cómo Usarlo

### 1. Reinicia la aplicación
```bash
python run.py
```

### 2. Abre el diagnóstico
```
http://localhost:5000/diagnostico
```

### 3. Usa la herramienta "Auto-Detección SNMP" (CON BADGE "NUEVO" NARANJA)

- Ingresa la IP: `192.168.0.100`
- Click en **"Auto-Detectar Configuración"**

### 4. Observa la Terminal en Tiempo Real

Verás algo como esto:

```terminal
[15:25:30] 🔍 Iniciando auto-detección SNMP para 192.168.0.100

[15:25:31] 📡 Paso 1/4: Probando versiones SNMP y community strings...
[15:25:31]   → Probando SNMPv1...
[15:25:31]     • Community: 'public'
[15:25:32]     ✅ ¡ÉXITO! SNMPv2c con community 'public'

[15:25:32] 📋 Paso 2/4: Obteniendo información del sistema...
[15:25:33]   ✅ sysDescr: UPS Model XYZ
[15:25:33]   ✅ sysName: UPS-Office-01

[15:25:33] 🔌 Paso 3/4: Detectando tipo de UPS...
[15:25:34]   ✅ Detectado: UPS-MIB Estándar (5 OIDs)

[15:25:34] 🗂️ Paso 4/4: Escaneando OIDs disponibles...
[15:25:36]   ✅ 15 OIDs adicionales disponibles

[15:25:36] ============================================================
[15:25:36] 📊 RESUMEN DE DETECCIÓN:
[15:25:36]   Versión SNMP: SNMPv2c
[15:25:36]   Community: public
[15:25:36]   Dispositivo: UPS Model XYZ
[15:25:36]   OIDs funcionando: 25
[15:25:36]   Tipo UPS: UPS-MIB Estándar
[15:25:36] ============================================================

[15:25:36] ============================================================
[15:25:36] 💡 RECOMENDACIÓN PARA AGREGAR AL MONITOREO:
[15:25:36] ============================================================
[15:25:36]
[15:25:36] Ve a: http://localhost:5000/monitoreo
[15:25:36] Click en el botón "+" para agregar dispositivo
[15:25:36]
[15:25:36] Usa esta configuración:
[15:25:36]   • IP: 192.168.0.100
[15:25:36]   • Protocolo: SNMP
[15:25:36]   • Puerto: 161
[15:25:36]   • Community: public
[15:25:36]   • Versión: SNMPv2c
[15:25:36]   • Tipo detectado: UPS-MIB Estándar
[15:25:36]
[15:25:36] ============================================================
```

## 🎯 Soluciona Tu Problema

### Antes:
- ❌ "No sé qué protocolo usa"
- ❌ "No sé qué community string es"
- ❌ "No sé si es SNMPv1 o v2"
- ❌ "El sistema no me dice qué está pasando"

### Ahora:
- ✅ **Auto-detecta TODO automáticamente**
- ✅ **Te muestra cada paso en tiempo real**
- ✅ **Te da la configuración exacta para agregar el UPS**
- ✅ **Prueba 7 communities diferentes automáticamente**

## 📁 Archivos Creados

```
app/
├── services/
│   └── protocols/
│       └── snmp_scanner.py          ← Scanner SNMP avanzado
├── routes/
│   └── diagnostic_routes.py         ← Modificado: agregada ruta /api/diagnostic/snmp-autodetect
└── templates/
    └── diagnostico.html              ← Modificado: agregada herramienta con badge NUEVO

docs/
└── SOLUCION_SNMP_AUTODETECT.md      ← Este archivo
```

## 🔧 Funcionalidades Técnicas

### OIDs sopor tados:

**MIB-II Estándar** (Básico):
- sysDescr, sysName, sysUpTime, sysContact, sysLocation

**UPS-MIB RFC 1628** (Estándar UPS):
- Identificación (fabricante, modelo, versión SW)
- Batería (status, voltaje, corriente, temperatura, carga %, tiempo restante)
- Entrada (voltaje, frecuencia, corriente, potencia)
- Salida (fuente, voltaje, frecuencia, corriente, potencia, carga %)

**Enterprise INVT**:
- Modelo, serial, voltajes específicos INVT

### Versiones SNMP:
- SNMPv1 (mpModel=0)
- SNMPv2c (mpModel=1)

### Community Strings Probadas:
1. public
2. private
3. admin
4. snmp
5. manager
6. ups
7. monitor

## 📊 Diferencias entre Tipos de UPS

| Tipo | Descripción | OIDs |
|------|-------------|------|
| **INVT Enterprise** | UPS INVT con OIDs propietarios (.1.3.6.1.4.1.56788) | ~60 OIDs específicos |
| **UPS-MIB Estándar** | Cumple con RFC 1628 (.1.3.6.1.2.1.33) | ~30 OIDs estándar |
| **Genérico** | Solo responde a MIB-II básico | ~6 OIDs básicos |

## 💡 Casos de Uso

### Caso 1: UPS con Community No Estándar

**Problema**: El UPS usa community "admin" en vez de "public"

**Solución**: La auto-detección lo encuentra automáticamente:
```
[15:25:31]     • Community: 'public' ❌
[15:25:31]     • Community: 'private' ❌
[15:25:31]     • Community: 'admin' ✅ ¡ÉXITO!
```

### Caso 2: UPS que NO soporta OIDs INVT

**Problema**: Tu UPS actual usa INVT, pero el nuevo usa UPS-MIB estándar

**Solución**: La auto-detección identifica el tipo correcto:
```
[15:25:34]   ⚠️ INVT Enterprise: 0 OIDs (no soportado)
[15:25:34]   ✅ UPS-MIB Estándar: 25 OIDs (FUNCIONA)
[15:25:34]   Tipo detectado: UPS-MIB Estándar
```

### Caso 3: No Sabes Si Es SNMPv1 o v2

**Solución**: La auto-detección prueba ambas:
```
[15:25:31]   → Probando SNMPv1... ❌
[15:25:31]   → Probando SNMPv2c... ✅ ¡ÉXITO!
```

## 🔍 Comparación con Herramientas Anteriores

| Característica | Test SNMP Normal | **Auto-Detección SNMP** |
|----------------|------------------|-------------------------|
| Versión SNMP | Manual | ✅ Automática |
| Community | Manual | ✅ Prueba 7 automáticamente |
| Tipo de UPS | No detecta | ✅ Detecta (INVT/UPS-MIB/Genérico) |
| OIDs Disponibles | No muestra | ✅ Lista todos |
| Progreso en tiempo real | No | ✅ Sí, paso a paso |
| Recomendación configuración | No | ✅ Sí, lista completa |

## 📝 Próximos Pasos

1. **Reinicia la aplicación**:
   ```bash
   python run.py
   ```

2. **Abre diagnóstico**:
   ```
   http://localhost:5000/diagnostico
   ```

3. **Busca la tarjeta NARANJA con badge "NUEVO"**: "🔍 Auto-Detección SNMP"

4. **Ingresa la IP del UPS**: `192.168.0.100`

5. **Click en "Auto-Detectar Configuración"**

6. **Observa la terminal** - verás todo el proceso en tiempo real

7. **Copia la configuración recomendada**

8. **Ve a `/monitoreo`** y agrega el UPS con los datos detectados

## ⚡ Ventajas

✅ **Ahorra tiempo**: No más prueba y error manual  
✅ **100% visible**: Ves exactamente qué está probando  
✅ **Configuración garantizada**: Usa solo lo que funciona  
✅ **Soporta múltiples UPS**: INVT, estándar, genéricos  
✅ **Inteligente**: Prueba 14 combinaciones automáticamente  

## 🎬 ¿Listo?

```bash
python run.py
```

```
http://localhost:5000/diagnostico
```

**Busca la tarjeta NARANJA**  con el icono de rayo ⚡ y badge "NUEVO"

¡Pruébalo con tu UPS (192.168.0.100) y verás EN TIEMPO REAL qué configuración necesita! 🚀

---

**Fecha**: 2026-02-15  
**Versión**: 1.0  
**Status**: ✅ Implementado y listo para usar
