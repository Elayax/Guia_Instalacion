# ⚡ Configuración de Monitoreo Dual de UPS - Guía Rápida

## 🎯 Resumen

Tienes **DOS UPS** que necesitas monitorear:
- **UPS Actual:** `192.168.10.198` ✅ Ya funciona
- **UPS Nuevo:** `192.168.0.100` 🆕 Por configurar

## ✅ Buenas Noticias

**¡El sistema YA soporta múltiples UPS!** No necesitas cambiar código, solo agregar el nuevo dispositivo.

## 🚀 Forma Más Rápida (3 pasos)

### 1️⃣ Ejecuta el Script de Configuración

```bash
python agregar_ups.py
```

Sigue las instrucciones en pantalla. El script te preguntará:
- IP del UPS (default: `192.168.0.100`)
- Nombre descriptivo
- Protocolo (Modbus o SNMP)
- Parámetros de conexión

### 2️⃣ Abre la Interfaz Web

```
http://localhost:5000/monitoreo
```

(o la dirección donde corre tu aplicación)

### 3️⃣ ¡Listo!

Verás ambos UPS en la lista lateral. Haz clic en cualquiera para ver sus datos en tiempo real.

## 🌐 Forma Alternativa: Desde la Web

1. Abre `http://localhost:5000/monitoreo`
2. Haz clic en el botón **"+"** (rojo) en la barra lateral
3. Completa el formulario:
   - **DEVICE ID:** `UPS-Nuevo`
   - **PROTOCOL:** `MODBUS TCP` o `SNMP v2`
   - **IP ADDRESS:** `192.168.0.100`
   - **PORT:** `502` (Modbus) o `161` (SNMP)
   - **SLAVE ID:** `1` (para Modbus)
   - **COMMUNITY:** `public` (para SNMP)
4. Clic en **"CONNECT DEVICE"**

## 🔍 Verifica la Conexión

Antes de agregar el UPS, verifica que sea alcanzable:

```bash
# Prueba de ping
ping 192.168.0.100

# Prueba específica del protocolo
python test_ups_connections.py --production
```

## ⚠️ Problema de Red (Si no conecta)

Si las IPs están en redes diferentes (`192.168.10.x` vs `192.168.0.x`):

### Solución 1: Ruta Estática (Windows)

```powershell
# Como Administrador
route add 192.168.0.0 MASK 255.255.255.0 <IP_DEL_GATEWAY>

# Hacer permanente
route -p add 192.168.0.0 MASK 255.255.255.0 <IP_DEL_GATEWAY>
```

### Solución 2: Segunda Interfaz de Red

- Conecta físicamente el servidor a la red `192.168.0.x`
- Configura IP estática (ej: `192.168.0.50`)

## 🧪 Scripts de Ayuda

### `agregar_ups.py`
Script interactivo para agregar UPS a la configuración.

```bash
python agregar_ups.py
```

### `test_ups_connections.py`
Diagnóstico de conexiones SNMP.

```bash
# Modo interactivo
python test_ups_connections.py

# Probar todos los dispositivos configurados
python test_ups_connections.py --all

# Probar IPs en producción
python test_ups_connections.py --production

# Probar IP específica
python test_ups_connections.py --ip 192.168.0.100 --community public
```

## 📖 Documentación Completa

Para detalles técnicos, arquitectura del sistema y troubleshooting avanzado:

📄 **[DUAL_UPS_MONITORING_GUIDE.md](DUAL_UPS_MONITORING_GUIDE.md)**

## 🎛️ Uso de la Interfaz

Una vez configurados ambos UPS:

1. **Lista lateral:** Verás todos los UPS
2. **Click para seleccionar:** El panel principal cambia automáticamente
3. **Indicadores de estado:** Verde (online) / Gris (offline)
4. **Gráficos en tiempo real:** Voltaje, frecuencia, temperatura, etc.

## 🔧 Estructura de la Base de Datos

Los dispositivos se guardan en:
```
app/Equipos.db → tabla `monitoreo_config`
```

Campos importantes:
- `ip`: Dirección IP del UPS
- `protocolo`: 'modbus' o 'snmp'
- `nombre`: Nombre descriptivo
- `port`: Puerto Modbus (default 502)
- `snmp_port`: Puerto SNMP (default 161)
- `snmp_community`: Community string (default 'public')
- `slave_id`: ID Modbus (default 1)

## ❓ FAQ

### ¿Puedo agregar más de 2 UPS?
✅ Sí, el sistema soporta N dispositivos.

### ¿Se pueden mezclar protocolos?
✅ Sí, puedes tener UPS con Modbus y otros con SNMP simultáneamente.

### ¿Los datos se guardan?
⚠️ Actualmente solo se muestran en tiempo real. Si necesitas historiales, revisa el módulo `influx_db.py`.

### ¿Y si el UPS no responde?
El sistema lo marcará como "offline" en la lista. Verifica:
1. Conectividad de red
2. Protocolo correcto
3. Firewall no está bloqueando el puerto

## 🛠️ Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| UPS no aparece en lista | Recarga la página (CTRL+F5) |
| Status "offline" | Verifica IP y firewall |
| No hay datos en gráficos | Verifica protocolo y parámetros |
| Error al agregar | IP duplicada, verifica BD |

## 📞 Soporte

Si algo no funciona:
1. Ejecuta `python test_ups_connections.py --all`
2. Revisa logs en `logs/app.log`
3. Verifica configuración en la interfaz web del UPS

---

**¿Necesitas más ayuda?** Revisa la documentación completa en `DUAL_UPS_MONITORING_GUIDE.md`
