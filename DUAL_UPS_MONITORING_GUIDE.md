# Guía de Configuración de Monitoreo Dual de UPS

## 📋 Resumen de la Situación

**UPS Actual:**
- IP: `192.168.10.198`
- Estado: En producción, monitoreando correctamente

**Nuevo UPS a Agregar:**
- IP: `192.168.0.100`
- Estado: Pendiente de configuración

## 🎯 Objetivo

Configurar el sistema para monitorear **ambos UPS simultáneamente** en la interfaz SCADA.

## ✅ Buenas Noticias

**El sistema YA está preparado para múltiples dispositivos!** No necesitas modificar código. La arquitectura actual soporta:

- ✅ Monitoreo de múltiples UPS
- ✅ Protocolos diferentes (Modbus TCP y SNMP)
- ✅ Cambio entre dispositivos en la interfaz
- ✅ Actualización en tiempo real vía WebSockets
- ✅ Base de datos SQLite con tabla `monitoreo_config`

## 🚀 Pasos para Agregar el Segundo UPS

### Opción 1: Desde la Interfaz Web (Recomendado)

1. **Accede al sistema de monitoreo:**
   ```
   http://localhost:5000/monitoreo
   ```
   (o la dirección donde corra tu aplicación)

2. **Haz clic en el botón "+" (rojo)** en la barra lateral izquierda donde dice "DISPOSITIVOS"

3. **Completa el formulario:**
   - **DEVICE ID:** `UPS-Nuevo` (o el nombre que prefieras)
   - **PROTOCOL:** Selecciona `MODBUS TCP` o `SNMP v2` según tu dispositivo
   - **IP ADDRESS:** `192.168.0.100`
   
   **Si es Modbus:**
   - **PORT:** `502`
   - **SLAVE ID:** `1` (verifica esto con la configuración de tu UPS)
   
   **Si es SNMP:**
   - **PORT:** `161`
   - **COMMUNITY:** `public` (o tu community string)

4. **Haz clic en "CONNECT DEVICE"**

5. **El nuevo UPS aparecerá en la lista lateral**

### Opción 2: Agregar Manualmente a la Base de Datos

Si prefieres agregar directamente a la BD:

```python
# Ejecuta este código en Python o crea un script
from app.base_datos import GestorDB

db = GestorDB()

# Para Modbus TCP
datos_nuevo_ups = {
    'ip': '192.168.0.100',
    'port': 502,
    'slave_id': 1,
    'nombre': 'UPS-Sucursal-Nueva',
    'protocolo': 'modbus',  # o 'snmp'
    'snmp_community': 'public',
    'snmp_port': 161
}

db.agregar_monitoreo_ups(datos_nuevo_ups)
print("✅ UPS agregado correctamente!")
```

### Opción 3: Inserción SQL Directa

```sql
-- Abre la base de datos: app/Equipos.db
INSERT INTO monitoreo_config (ip, port, slave_id, nombre, protocolo, snmp_community, snmp_port)
VALUES ('192.168.0.100', 502, 1, 'UPS-Nueva-Oficina', 'modbus', 'public', 161);
```

## 🔍 Verificación de Conectividad

### Verifica que el UPS sea alcanzable:

**Para Modbus:**
```bash
# Desde PowerShell
Test-NetConnection -ComputerName 192.168.0.100 -Port 502
```

**Para SNMP:**
```bash
# Desde PowerShell
Test-NetConnection -ComputerName 192.168.0.100 -Port 161
```

Si la red tiene subredes diferentes (192.168.10.x vs 192.168.0.x), necesitarás:
- ✅ Configurar enrutamiento entre redes
- ✅ O configurar una interfaz adicional en el servidor
- ✅ O usar ZeroTier/VPN si están en ubicaciones remotas

## ⚙️ Configuración de Red (Si las subredes son diferentes)

### Problema: 192.168.10.x vs 192.168.0.x

Si tu servidor está en `192.168.10.x`, no podrá acceder directamente a `192.168.0.100`.

**Soluciones:**

1. **Agregar una segunda interfaz de red al servidor:**
   - Conecta físicamente a la red `192.168.0.x`
   - Configura la interfaz con IP estática (ej: `192.168.0.50`)

2. **Configurar el Gateway/Router:**
   - Asegúrate de que el router puede enrutar entre ambas subredes
   - Agrega rutas estáticas si es necesario

3. **Bridge Virtual:**
   ```powershell
   # Agregar ruta estática en Windows
   route add 192.168.0.0 MASK 255.255.255.0 192.168.10.1
   ```

## 🧪 Prueba de Conexión SNMP (Script de Diagnóstico)

Crea este archivo: `test_conexion_ups.py`

```python
import asyncio
from app.services.protocols.snmp_client import SNMPClient

async def test_ups(ip, community='public', port=161):
    print(f"\n🔍 Probando conexión a {ip}...")
    client = SNMPClient(community=community, port=port)
    
    try:
        data = await client.get_ups_data(ip)
        if data:
            print(f"✅ CONEXIÓN EXITOSA!")
            print(f"📊 Datos recibidos:")
            for key, value in data.items():
                print(f"   - {key}: {value}")
        else:
            print(f"❌ Sin respuesta del UPS")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Prueba UPS actual
    asyncio.run(test_ups('192.168.10.198'))
    
    # Prueba UPS nuevo
    asyncio.run(test_ups('192.168.0.100'))
```

Ejecuta:
```bash
python test_conexion_ups.py
```

## 📱 Uso de la Interfaz con Múltiples UPS

Una vez configurados ambos UPS:

1. **Ver ambos en la lista lateral:**
   - UPS-Actual (192.168.10.198)
   - UPS-Nuevo (192.168.0.100)

2. **Cambiar entre dispositivos:**
   - Haz clic en cualquiera de los UPS en la lista
   - El panel principal cambiará automáticamente
   - Los gráficos se actualizarán con los datos del dispositivo seleccionado

3. **Ambos se actualizan simultáneamente:**
   - El servicio `monitoring_service.py` consulta todos los dispositivos
   - Las actualizaciones llegan vía WebSocket (`socket.io`)
   - Los indicadores de estado (online/offline) se actualizan en la lista

## 🔧 Configuración del Protocolo

### ¿Modbus o SNMP?

**Usa Modbus TCP si:**
- El UPS INVT soporta Modbus (puerto 502)
- Necesitas datos más detallados
- Tienes documentación de los registros Modbus

**Usa SNMP si:**
- El UPS tiene agente SNMP habilitado (puerto 161)
- El fabricante proporciona MIBs
- Es más estándar y fácil de configurar

**Para verificar cuál protocolo usa tu UPS:**
- Revisa la configuración web del UPS (`http://192.168.0.100`)
- Busca opciones de "Comunicación" o "Protocolos"
- Consulta el manual del fabricante

## 🐛 Troubleshooting

### Problema: El UPS no aparece en la lista

**Solución:**
1. Verifica que la entrada esté en la BD:
   ```python
   from app.base_datos import GestorDB
   db = GestorDB()
   devices = db.obtener_monitoreo_ups()
   for d in devices:
       print(d)
   ```

2. Recarga la página web (CTRL+F5)

### Problema: El UPS aparece pero está "offline"

**Posibles causas:**
- ❌ IP incorrecta o no alcanzable
- ❌ Puerto bloqueado por firewall
- ❌ Protocolo incorrecto (Modbus vs SNMP)
- ❌ Community string incorrecta (SNMP)
- ❌ Slave ID incorrecto (Modbus)

**Debugging:**
1. Verifica conectividad de red
2. Revisa los logs del servidor:
   ```bash
   # Ver logs en tiempo real
   tail -f logs/app.log
   ```

3. Confirma que el servicio esté corriendo:
   ```python
   # En run.py verifica que MonitoringService esté activo
   ```

### Problema: El servidor no puede acceder a 192.168.0.100

**Solución de red:**
```powershell
# 1. Ver interfaces de red
ipconfig

# 2. Ver tabla de rutas
route print

# 3. Agregar ruta estática (si es necesario)
route add 192.168.0.0 MASK 255.255.255.0 <GATEWAY_IP>

# 4. Hacer ruta persistente
route -p add 192.168.0.0 MASK 255.255.255.0 <GATEWAY_IP>
```

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR WEB                         │
│              http://server/monitoreo                     │
└───────────────────┬─────────────────────────────────────┘
                    │ WebSocket (Socket.IO)
                    ↓
┌─────────────────────────────────────────────────────────┐
│              FLASK APPLICATION (run.py)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │   routes/monitoreo_routes.py                     │   │
│  │   - /monitoreo (HTML)                            │   │
│  │   - /api/monitoreo/list (GET devices)            │   │
│  │   - /api/monitoreo/add (POST new)                │   │
│  │   - /api/monitoreo/delete/<id> (DELETE)          │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                               │
│                          ↓                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │   services/monitoring_service.py                 │   │
│  │   - Thread que hace polling cada 2 seg           │   │
│  │   - Lee todos los dispositivos de la BD          │   │
│  │   - Consulta via SNMP o Modbus                   │   │
│  │   - Emite datos via WebSocket                    │   │
│  └─────────────────────────────────────────────────┘   │
│           │                              │               │
│           ↓                              ↓               │
│  ┌──────────────┐            ┌──────────────────┐      │
│  │ SNMP Client  │            │ Modbus Monitor   │      │
│  │ (asyncio)    │            │ (pymodbus)       │      │
│  └──────────────┘            └──────────────────┘      │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         base_datos.py (GestorDB)                 │   │
│  │         SQLite: app/Equipos.db                   │   │
│  │         Tabla: monitoreo_config                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                    │                    │
                    ↓                    ↓
        ┌────────────────┐    ┌────────────────┐
        │  UPS #1        │    │  UPS #2        │
        │  192.168.10.198│    │  192.168.0.100 │
        │  Modbus/SNMP   │    │  Modbus/SNMP   │
        └────────────────┘    └────────────────┘
```

## ✨ Características Adicionales

### Expandir a más UPS en el futuro

El sistema puede manejar **N dispositivos simultáneamente**:
- No hay límite en la BD
- El servicio consulta todos en cada ciclo
- La interfaz muestra todos en la lista lateral

### Alertas y Alarmas

El sistema ya incluye:
- ✅ Detección de voltaje bajo
- ✅ Batería crítica
- ✅ Sobrecarga
- ✅ Sobretemperatura

### Personalización

Puedes editar:
- **Intervalos de polling:** `monitoring_service.py` línea 19
- **Umbrales de alarma:** `monitoring_service.py` líneas 137-161
- **Colores y estilos:** `templates/monitoreo.html`

## 📝 Checklist de Implementación

- [ ] Verificar conectividad de red al nuevo UPS (192.168.0.100)
- [ ] Confirmar protocolo soportado (Modbus o SNMP)
- [ ] Obtener parámetros de conexión (puerto, community, slave_id)
- [ ] Agregar UPS nuevo via interfaz web o BD
- [ ] Verificar que aparece en la lista
- [ ] Confirmar que el estado cambia a "online"
- [ ] Probar cambio entre dispositivos
- [ ] Verificar gráficos y datos en tiempo real
- [ ] Documentar configuración específica del UPS

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs de la aplicación
2. Verifica conectividad de red
3. Confirma configuración del UPS
4. Prueba con el script de diagnóstico

---

**Creado:** 2026-02-15
**Sistema:** UPS Engineering Monitor - Guía de Instalación
**Versión:** 1.0
