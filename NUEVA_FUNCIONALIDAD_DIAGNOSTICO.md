# 🎉 Nueva Funcionalidad: Terminal Web de Diagnóstico

## ✨ ¿Qué se agregó?

Se creó un **módulo completo de diagnóstico de red** integrado directamente en tu aplicación web. Ya no necesitas abrir PowerShell o ejecutar scripts de Python separados.

## 🚀 Acceso Rápido

```
http://localhost:5000/diagnostico
```

Verás una nueva pestaña "DIAGNÓSTICO" en la barra de navegación.

## 🎯 Problema que Resuelve

**Antes:**
- "El UPS no conecta"
- Tenías que abrir PowerShell
- Ejecutar scripts manualmente
- Copiar/pegar resultados
- Cambiar entre ventanas

**Ahora:**
- Todo desde el navegador
- Interfaz visual tipo terminal
- Resultados en tiempo real
- Herramientas organizadas
- Un solo lugar para todo

## 🛠️ Herramientas Integradas

### 1. Test de Ping 🔍
Verifica si el UPS responde en la red

### 2. Test de Puerto 🔌
Prueba si Modbus (502) o SNMP (161) están abiertos

### 3. Test SNMP Completo 📡
Conecta via SNMP y obtiene TODOS los datos del UPS

### 4. Test Modbus TCP 🔧
Verifica conexión Modbus

### 5. Escaneo de Red 🌐
Encuentra todos los dispositivos en un rango de IPs

### 6. Info del Sistema 📋
- Tabla de rutas
- Interfaces de red
- Útil para diagnosticar problemas de subredes

## 📁 Archivos Nuevos

```
app/
├── routes/
│   └── diagnostic_routes.py      ← Backend de diagnóstico
├── templates/
│   └── diagnostico.html           ← Interfaz web tipo terminal
└── __init__.py                    ← Modificado para registrar el módulo

docs/
└── GUIA_DIAGNOSTICO.md            ← Guía completa de uso
```

## 🎨 Características de la Interfaz

- **Estilo Terminal:** Interfaz oscura tipo consola
- **Tiempo Real:** Resultados inmediatos mientras ejecutas
- **Color-Coded:** Verde para éxito, rojo para errores, amarillo para warnings
- **IPs Rápidas:** Botones para seleccionar tus IPs comunes
- **Histórico:** La terminal mantiene todos los resultados
- **Limpieza Fácil:** Botón para limpiar la terminal

## 🔥 Casos de Uso Principales

### Para tu UPS nuevo (192.168.0.100):

1. **Un clic en "Test de Ping"**
   - Si falla → Problema de red/rutas
   - Si funciona → Continúa

2. **Un clic en "Test SNMP"**
   - Si funciona → ¡Listo! Usa protocolo SNMP
   - Si falla → Prueba Modbus

3. **Un clic en "Test Modbus"**
   - Si funciona → Usa protocolo Modbus
   - Si falla → SNMP y Modbus no habilitados

### Si no sabes la IP exacta:

1. **Escaneo de Red**
   - Red: `192.168.0`
   - Rango: 1-254
   - Te muestra TODOS los dispositivos con puertos abiertos

## 🎓 Ejemplo Real de Uso

**Escenario:** UPS nuevo en 192.168.0.100 no conecta

**En la Terminal Web:**

```
1. Test de Ping → 192.168.0.100
   ✅ Host responde

2. Test de Puerto → 192.168.0.100:161
   ✅ Puerto abierto

3. Test SNMP → 192.168.0.100
   ✅ Datos recibidos:
   - Voltaje entrada L1: 220.5V
   - Voltaje salida L1: 220.0V
   - Batería: 100%
   - etc...

Conclusión: El UPS funciona con SNMP
```

**Ahora puedes agregarlo al monitoreo con confianza:**
- IP: 192.168.0.100
- Protocolo: SNMP
- Puerto: 161
- Community: public

## 🚦 Cómo Empezar

### Paso 1: Reinicia la Aplicación

Si ya la tenías corriendo:

```bash
# Detén el servidor (CTRL+C)
# Inicia de nuevo
python run.py
```

### Paso 2: Abre el Diagnóstico

```
http://localhost:5000/diagnostico
```

### Paso 3: Prueba tu UPS Nuevo

1. Click en "Test de Ping"
2. Ingresa: `192.168.0.100`
3. Click en "Ejecutar Ping"
4. Observa los resultados en la terminal

### Paso 4: Continúa con SNMP o Modbus

Según qué funcione, ya sabrás cómo configurarlo.

## 📚 Documentación

**Guía completa:** `GUIA_DIAGNOSTICO.md`
- Explicación de cada herramienta
- Casos de uso detallados
- Troubleshooting
- Tips profesionales

## 🎯 Beneficios

✅ **Más rápido:** No cambiar entre herramientas  
✅ **Más visual:** Resultados formateados y coloreados  
✅ **Más completo:** Todas las herramientas en un lugar  
✅ **Más fácil:** Interfaz amigable vs. comandos de PowerShell  
✅ **Más útil:** Historial de pruebas en la misma sesión  

## 🔧 Requisitos

Las dependencias ya las tienes instaladas:
- `pymodbus` (para test Modbus)
- `pysnmp` (para test SNMP)
- `Flask` (para la interfaz web)

Si falta alguna:

```bash
pip install pymodbus pysnmp
```

## 💡 Tips

1. **Empieza simple:** Siempre test de ping primero

2. **IPs Rápidas:** Los botones predefinidos evitan errores de tipeo

3. **Copia resultados:** Click derecho → Copiar en la terminal

4. **Escaneo inteligente:** Si la red es grande, escanea por partes

5. **Documenta:** Los resultados te ayudan a recordar qué funciona

## 🎬 Demo Rápida

```
Usuario: "Mi UPS nuevo no conecta"

Solución con Terminal Web:
1. [10 segundos] Test de Ping → ✅ Funciona
2. [5 segundos] Test Puerto 161 → ✅ Abierto
3. [15 segundos] Test SNMP → ✅ Datos completos

Total: 30 segundos para diagnosticar completamente

Antes: Varios minutos entre scripts, PowerShell, CSV, etc.
```

## 🌟 Próximos Pasos

Con esta herramienta ya puedes:

1. ✅ Diagnosticar por qué 192.168.0.100 no conecta
2. ✅ Descubrir qué protocolo usa
3. ✅ Verificar conectividad de red
4. ✅ Escanear toda tu red si es necesario
5. ✅ Agregar el UPS con confianza al monitoreo

**Empieza ahora:**

```
http://localhost:5000/diagnostico
```

---

**¿Dudas?** Lee `GUIA_DIAGNOSTICO.md` para ejemplos detallados y troubleshooting.
