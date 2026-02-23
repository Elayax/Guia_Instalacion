# 🔌 Guía de Uso - Test SNMP

## Resumen

Se han agregado dos formas de probar la conexión SNMP con tus dispositivos UPS:

1. **Script de Terminal** (Rápido) - Para pruebas inmediatas sin iniciar la app
2. **Interfaz Web** - Para pruebas visuales y monitoreo

---

## 1️⃣ Método Terminal (test_snmp_quick.py)

### Uso Básico

```bash
# Probar con IP local
python tests/test_snmp_quick.py --ip 192.168.1.100

# Probar con IP ZeroTier
python tests/test_snmp_quick.py --ip 10.147.17.2

# Con puerto personalizado (ej: RUT956)
python tests/test_snmp_quick.py --ip 10.147.17.2 --port 8161

# Con community diferente
python tests/test_snmp_quick.py --ip 192.168.1.100 --community private
```

### Argumentos Disponibles

- `--ip` (requerido): IP del UPS
- `--port` (opcional): Puerto SNMP (default: 161)
- `--community` (opcional): Community string (default: public)
- `--method` (opcional): Método de prueba: `async`, `client`, `both` (default: both)

### Ejemplo de Salida Exitosa

```
======================================================================
📡 PROBANDO CONEXIÓN SNMP
======================================================================
  IP: 192.168.1.100
  Puerto: 161
  Community: public
======================================================================

✅ Modelo: INV-200KVA
✅ Voltaje Batería: 384.5 V
✅ Carga Batería: 95 %
✅ Temperatura: 25 °C
✅ Voltaje Entrada: 220 V
✅ Voltaje Salida: 220 V

======================================================================
  📋 RESUMEN
======================================================================
  Estado General: ✅ CONEXIÓN EXITOSA
======================================================================
```

---

## 2️⃣ Método Interfaz Web

### Acceder

1. Inicia la aplicación Flask:
   ```bash
   python run.py
   ```

2. Abre tu navegador en: **http://localhost:5000/snmp-test**

3. Verás un enlace "TEST SNMP" en el menú de navegación

### Uso de la Interfaz

#### Prueba de Conexión Principal

1. Ingresa la **Dirección IP** del UPS
   - Ejemplos: `192.168.1.100` (red local) o `10.147.17.2` (ZeroTier)

2. Configura el **Puerto SNMP**
   - `161` - Puerto estándar SNMP
   - `8161` - Puerto forward típico para RUT956

3. Ingresa el **Community String**
   - Default: `public`

4. Haz clic en **"PROBAR CONEXIÓN"**

5. Los resultados mostrarán:
   - ✅ Estado de conexión
   - 📦 Información del dispositivo (Modelo, S/N, Fabricante)
   - 🔋 Datos de batería (Voltaje, Carga %, Temperatura, Autonomía)
   - ⚙️ Estado del sistema (Fuente de alimentación, Estado de batería)
   - ⚡ Datos eléctricos (Voltaje entrada/salida, Potencia)

#### Consulta OID Personalizada

En la sección "Consulta OID Personalizado":

1. Primero ejecuta una prueba de conexión (arriba) para configurar IP/puerto/community

2. Ingresa el OID que quieres consultar:
   - Ejemplo: `.1.3.6.1.4.1.56788.1.1.1.1.3.0` (Modelo UPS)

3. Haz clic en **"Consultar OID"**

4. Verás el valor exacto retornado por ese OID

---

## 📋 OIDs Útiles para Pruebas

Aquí algunos OIDs clave que puedes usar para probar:

### Información del Dispositivo
- **Modelo**: `.1.3.6.1.4.1.56788.1.1.1.1.3.0`
- **Número de Serie**: `.1.3.6.1.4.1.56788.1.1.1.1.4.0`
- **Fabricante**: `.1.3.6.1.4.1.56788.1.1.1.1.2.0`

### Batería (⚠️ Más Críticos)
- **Voltaje** (x0.1): `.1.3.6.1.4.1.56788.1.1.1.3.5.1.0`
- **Carga %**: `.1.3.6.1.4.1.56788.1.1.1.3.5.3.0`
- **Temperatura**: `.1.3.6.1.4.1.56788.1.1.1.3.5.5.0`
- **Autonomía (min)**: `.1.3.6.1.4.1.56788.1.1.1.3.5.4.0`

### Entrada/Salida
- **Voltaje Entrada**: `.1.3.6.1.4.1.56788.1.1.1.3.2.1.0`
- **Voltaje Salida**: `.1.3.6.1.4.1.56788.1.1.1.3.3.1.0`

---

## 🔧 Troubleshooting

### Error: "Error de conexión: Timeout"

**Causas posibles:**
- IP incorrecta o dispositivo apagado
- Firewall bloqueando puerto UDP 161
- ZeroTier no conectado

**Soluciones:**
```bash
# Verificar conectividad básica
ping 192.168.1.100

# Verificar ZeroTier
zerotier-cli listnetworks

# Probar con diferentes puertos
python tests/test_snmp_quick.py --ip 192.168.1.100 --port 8161
```

### Error: "Community string inválido"

**Solución:**
- Prueba con `public` primero (default)
- Si no funciona, consulta la configuración SNMP del UPS
- Algunos UPS usan `private` o un community personalizado

### El script funciona pero la web no

**Verificar:**
```bash
# Ver si Flask está corriendo
python run.py

# Revisar logs en la terminal por errores
```

---

## 🎯 Próximos Pasos con ZeroTier

### Para probar tu conexión ZeroTier:

1. **Verifica que ZeroTier esté activo:**
   ```bash
   zerotier-cli info
   zerotier-cli listnetworks
   ```

2. **Obtén la IP ZeroTier del UPS:**
   - Revisa en tu panel ZeroTier central
   - Debe ser algo como `10.147.17.X`

3. **Prueba con el script:**
   ```bash
   python tests/test_snmp_quick.py --ip 10.147.17.2 --port 8161
   ```

4. **Si funciona el script, prueba la interfaz web**
   - Ve a http://localhost:5000/snmp-test
   - Usa la misma IP y puerto

---

## 📖 Documentación Adicional

- **OIDs completos**: Ver archivo `app/utils/ups_oids.py`
- **Test avanzado**: Ver archivo `tests/test_snmp_connection.py`
- **Cliente SNMP**: Ver archivo `app/services/protocols/snmp_client.py`

Todos los archivos están documentados y listos para usar.
