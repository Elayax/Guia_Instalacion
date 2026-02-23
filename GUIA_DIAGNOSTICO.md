# 🔧 Módulo de Diagnóstico de Red - Guía de Uso

## 🎯 ¿Qué es esto?

Una **terminal web integrada** para diagnosticar problemas de red y conectividad con tus UPS **sin salir del navegador**.

## 🚀 Cómo Acceder

1. **Inicia tu aplicación Flask:**
   ```bash
   python run.py
   ```

2. **Abre tu navegador en:**
   ```
   http://localhost:5000/diagnostico
   ```

3. **Verás una interfaz con:**
   - Panel izquierdo: Herramientas de diagnóstico
   - Panel derecho: Terminal con resultados en tiempo real

## 🛠️ Herramientas Disponibles

### 1. 🔍 Test de Ping
**Para qué sirve:** Verificar si el UPS es alcanzable en la red

**Cómo usar:**
1. Ingresa la IP del UPS (ej: `192.168.0.100`)
2. O haz clic en "IPs Rápidas" para seleccionar una predefinida
3. Click en "Ejecutar Ping"

**Resultado:**
- ✅ **Éxito:** El UPS responde, la red está OK
- ❌ **Fallo:** El UPS no responde, hay problema de red/firewall/IP incorrecta

### 2. 🔌 Test de Puerto
**Para qué sirve:** Verificar si un puerto específico está abierto

**Cómo usar:**
1. Ingresa IP y puerto
2. O usa botones rápidos:
   - **Modbus (502):** Para UPS con protocolo Modbus TCP
   - **SNMP (161):** Para UPS con protocolo SNMP
   - **HTTP (80):** Para interfaz web del UPS

**Resultado:**
- ✅ **Puerto ABIERTO:** El servicio está escuchando
- ❌ **Puerto CERRADO:** El servicio no está disponible o bloqueado

### 3. 📡 Test SNMP
**Para qué sirve:** Probar conexión SNMP y obtener datos del UPS

**Cómo usar:**
1. Ingresa la IP del UPS
2. Puerto (default: 161)
3. Community string (default: "public")
4. Click en "Probar SNMP"

**Resultado:**
- ✅ **Éxito:** Muestra todos los datos disponibles (voltajes, batería, potencia, etc.)
- ❌ **Fallo:** SNMP no habilitado, community incorrecta, o puerto bloqueado

**💡 Tip:** Si falla, prueba con diferentes community strings:
- `public`
- `private`
- El que te dé el fabricante del UPS

### 4. 🔧 Test Modbus TCP
**Para qué sirve:** Probar conexión Modbus TCP

**Cómo usar:**
1. Ingresa la IP del UPS
2. Puerto (default: 502)
3. Slave ID (default: 1)
4. Click en "Probar Modbus"

**Resultado:**
- ✅ **Éxito:** La conexión Modbus funciona
- ❌ **Fallo:** Modbus no habilitado, slave ID incorrecto, o puerto bloqueado

### 5. 🌐 Escaneo de Red
**Para qué sirve:** Encontrar todos los dispositivos activos en una red

⚠️ **ADVERTENCIA:** Puede tardar varios minutos

**Cómo usar:**
1. Ingresa la red base (ej: `192.168.0`)
2. Rango de IPs a escanear (ej: 1 a 254)
3. Click en "Escanear Red"

**Resultado:**
- Lista de todos los hosts activos
- Puertos abiertos detectados (Modbus 502, SNMP 161, HTTP 80)

**💡 Útil cuando:**
- No sabes la IP exacta del UPS
- Quieres descubrir todos los UPS en la red
- Necesitas mapear dispositivos disponibles

### 6. 📋 Información del Sistema

#### Ver Tabla de Rutas
**Para qué sirve:** Ver cómo el sistema enruta el tráfico de red

**Útil cuando:**
- Tienes UPS en diferentes subredes (192.168.10.x vs 192.168.0.x)
- No puedes alcanzar una IP específica
- Necesitas configurar rutas estáticas

#### Ver Interfaces de Red
**Para qué sirve:** Ver todas las interfaces de red del servidor

**Útil cuando:**
- Necesitas saber qué IPs tiene tu servidor
- Verificas conectividad física
- Configuras múltiples redes

## 🎓 Casos de Uso Comunes

### Caso 1: UPS Nuevo No Conecta

**Síntomas:** Agregaste el UPS pero aparece "offline"

**Diagnóstico paso a paso:**

1. **Test de Ping:**
   ```
   IP: 192.168.0.100
   Resultado esperado: ✅ 4 paquetes recibidos
   ```

2. **Si ping falla:**
   - Verifica la IP con "Ver Interfaces de Red"
   - Revisa rutas con "Ver Tabla de Rutas"
   - El UPS puede estar en otra subred

3. **Si ping funciona, test de puerto:**
   ```
   IP: 192.168.0.100
   Puerto: 161 (para SNMP) o 502 (para Modbus)
   Resultado esperado: ✅ Puerto ABIERTO
   ```

4. **Si puerto cerrado:**
   - SNMP/Modbus no está habilitado en el UPS
   - Firewall bloqueando el puerto
   - Puerto incorrecto

5. **Si puerto abierto, test de protocolo:**
   - Prueba SNMP completo
   - O Modbus según corresponda

### Caso 2: No Sé Qué Protocolo Usa Mi UPS

**Solución:**

1. Ejecuta **Test de Puerto** para 502 y 161
2. Si 161 está abierto → Prueba **Test SNMP**
3. Si 502 está abierto → Prueba **Test Modbus**
4. El que funcione, ese es tu protocolo

### Caso 3: UPS en Otra Subred

**Síntomas:**
- UPS actual: 192.168.10.198 ✅ Funciona
- UPS nuevo: 192.168.0.100 ❌ No conecta

**Diagnóstico:**

1. **Ver Interfaces de Red:**
   - ¿Tu servidor tiene IP en ambas redes?
   - Si no, necesitas configurar segunda interfaz

2. **Ver Tabla de Rutas:**
   - ¿Hay ruta a 192.168.0.0/24?
   - Si no, agregar ruta estática:
   
   ```powershell
   # Windows (como Administrador)
   route add 192.168.0.0 MASK 255.255.255.0 <GATEWAY>
   ```

### Caso 4: Descubrir UPS en la Red

**No sabes la IP exacta del UPS nuevo**

**Solución:**

1. **Escaneo de Red:**
   ```
   Red: 192.168.0
   Desde: 1
   Hasta: 254
   ```

2. Espera los resultados (varios minutos)

3. Busca IPs con puertos 161 o 502 abiertos

4. Prueba cada IP con Test SNMP o Modbus

## 📊 Interpretando Resultados

### Ejemplo: Test SNMP Exitoso

```
✅ CONEXIÓN SNMP EXITOSA a 192.168.0.100:161
Community: public

📊 Datos obtenidos:
──────────────────────────────────────────────────

Entrada:
  input_voltage_l1         : 220.5
  input_voltage_l2         : 219.8
  input_voltage_l3         : 221.2
  input_frequency          : 60.0

Salida:
  output_voltage_l1        : 220.0
  output_load              : 45.2
  
Batería:
  battery_voltage          : 54.2
  battery_capacity         : 100.0
  battery_status           : Normal
```

**Esto significa:**
- ✅ SNMP funciona perfecto
- ✅ El UPS es trifásico (3 fases)
- ✅ Puedes agregarlo al monitoreo con protocolo SNMP

### Ejemplo: Puerto Cerrado

```
❌ Puerto 161 CERRADO o FILTRADO en 192.168.0.100
Error code: 10061
```

**Posibles causas:**
1. SNMP no habilitado → Revisa configuración del UPS
2. Firewall bloqueando → Verifica Windows Firewall
3. IP incorrecta → Verifica con ping primero

## 🐛 Troubleshooting

### La página no carga

**Verifica:**
1. El servidor Flask está corriendo
2. El módulo `diagnostic_routes.py` está importado en `__init__.py`
3. No hay errores en la consola

### "Error: Módulo pymodbus no instalado"

**Solución:**
```bash
pip install pymodbus
```

### "Error: Módulo pysnmp no instalado"

**Solución:**
```bash
pip install pysnmp
```

### Los comandos no retornan nada

**Verifica:**
1. JavaScript está habilitado en el navegador
2. La consola del navegador (F12) no muestra errores
3. El backend responde (revisa consola del servidor)

## 💡 Tips Profesionales

1. **Usa IPs Rápidas:** Los botones de IPs predefinidas evitan errores de tipeo

2. **Ejecuta ping primero:** Antes de cualquier test complejo, verifica conectividad básica

3. **Documenta tus hallazgos:** Copia los resultados de la terminal para referencia

4. **Escaneo progresivo:** Si la red es grande, escanea en rangos pequeños (1-50, 51-100, etc.)

5. **Community strings:** Si "public" no funciona, contacta al administrador del UPS

## 🎯 Workflow Recomendado

Para agregar un UPS nuevo:

```
1. Test de Ping
   ↓
2. Test de Puerto (161 y 502)
   ↓
3. Test SNMP (si 161 abierto)
   ↓
4. Test Modbus (si 502 abierto)
   ↓
5. Agregar a monitoreo con datos confirmados
```

---

**¿Problemas?** Todos los resultados aparecen en la terminal web en tiempo real. Copia y pega para debugging.
