# Referencia de API

> UPS Manager LBS — Endpoints y rutas del sistema

[← Volver al README](../README.md) | [Índice de Documentación](README.md)

---

> **Nota:** Todas las rutas requieren autenticación excepto `/login`. Las rutas protegidas redirigen a `/login` si no hay sesión activa. Algunas rutas requieren permisos específicos (indicados en la columna "Permiso").

---

## Auth — Autenticación

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET/POST | `/login` | — | Formulario de inicio de sesión |
| GET | `/logout` | login | Cerrar sesión |
| GET/POST | `/cambiar-password` | login | Cambiar contraseña del usuario actual |

---

## Dashboard — Panel Principal

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET/POST | `/` | `tablero` | Dashboard principal con búsqueda de pedidos |
| GET | `/api/buscar-pedido-json` | `tablero` | Búsqueda de pedido (respuesta JSON) |

---

## Calculator — Calculadora Eléctrica

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET/POST | `/calculadora` | `calculos` | Calculadora de calibres, protecciones y autonomía |
| POST | `/generar-pdf-calculadora` | `calculos` | Generar PDF con resultados de cálculos |

---

## API — Endpoints de Consulta

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/buscar-pedido/<pedido>` | login | Obtener proyecto por número de pedido |
| GET | `/api/sucursales/<cliente>` | login | Obtener sucursales de un cliente |
| GET | `/api/ups/<id_ups>` | login | Obtener especificaciones de un UPS |
| GET | `/api/bateria/<id_bat>` | login | Obtener especificaciones de una batería |
| GET | `/api/bateria/<id_bat>/curvas` | login | Obtener curvas de descarga de una batería |
| GET | `/api/tipos-ventilacion` | login | Listar tipos de ventilación disponibles |

### Formato de respuesta JSON

```json
{
  "campo1": "valor1",
  "campo2": "valor2"
}
```

Los endpoints de API retornan JSON directamente. En caso de error, retornan un objeto con campo `error`:

```json
{
  "error": "Descripción del error"
}
```

---

## Management — Gestión de Datos

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/equipos` | `datos` | Redirige a pestaña de equipos UPS |
| GET | `/baterias` | `datos` | Redirige a pestaña de baterías |
| GET/POST | `/gestion` | `datos` | Interfaz principal de gestión (UPS, baterías, personal, ventilación) |
| GET/POST | `/carga-masiva` | `datos` | Importación masiva desde CSV |
| GET | `/descargar-plantilla/<tipo>` | `datos` | Descargar plantilla CSV (clientes, ups, baterias) |
| GET | `/exportar-tabla/<tabla>` | `datos` | Exportar tabla como CSV |
| GET/POST | `/recuperacion-proyectos` | `datos` | Recuperar proyectos incompletos |

---

## Documents — Documentos PDF

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/reimprimir-guia/<pedido>` | `calculos` | Reimprimir guía de instalación PDF |
| GET/POST | `/generar-checklist/<pedido>` | `calculos` | Generar checklist de verificación PDF |
| GET | `/reimprimir-checklist/<pedido>` | `calculos` | Reimprimir checklist existente |

---

## Guía Rápida — Guía de Instalación Rápida

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/guia-rapida` | `guia_rapida` | Formulario de guía rápida |
| POST | `/generar-pdf-guia-rapida` | `guia_rapida` | Generar PDF de guía rápida |
| GET | `/generar-ejemplo-pdf` | `ejemplo_pdf` | Generar PDF de ejemplo |

---

## Monitoreo — SCADA en Tiempo Real

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/monitoreo` | `scada` | Dashboard de monitoreo en tiempo real |
| GET | `/api/monitoreo/list` | `scada` | Listar dispositivos monitoreados |
| POST | `/api/monitoreo/add` | `scada` | Agregar dispositivo al monitoreo |
| DELETE | `/api/monitoreo/delete/<id>` | `scada` | Eliminar dispositivo del monitoreo |

---

## Test SNMP — Pruebas de Conectividad

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/snmp-test` | login | Página de pruebas SNMP |
| POST | `/api/snmp/test` | login | Probar conexión SNMP a un dispositivo |
| POST | `/api/snmp/query-oid` | login | Consultar OID personalizado |

---

## Diagnostic — Diagnóstico de Red

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/diagnostico` | login | Página de herramientas de diagnóstico |
| POST | `/api/diagnostic/ping` | login | Ping a dirección IP |
| POST | `/api/diagnostic/port` | login | Verificar puerto abierto |
| POST | `/api/diagnostic/snmp` | login | Probar conexión SNMP |
| POST | `/api/diagnostic/modbus` | login | Probar conexión Modbus TCP |
| POST | `/api/diagnostic/scan` | login | Escaneo de rango de IPs |
| POST | `/api/diagnostic/route` | login | Tabla de rutas del sistema |
| GET | `/api/diagnostic/interfaces` | login | Listar interfaces de red |
| POST | `/api/diagnostic/snmp-autodetect` | login | Auto-detectar configuración SNMP |
| POST | `/api/diagnostic/snmp-walk` | login | SNMP Walk (consulta asíncrona) |

---

## Vales — Control de Herramienta

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/vales` | `vales` | Formulario de vales de herramienta |
| GET | `/vales/historial` | `vales` | Historial de vales emitidos |

---

## User Management — Gestión de Usuarios (Solo Admin)

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/gestionar-cuentas` | admin | Lista de usuarios del sistema |
| POST | `/gestionar-cuentas/crear` | admin | Crear nuevo usuario |
| POST | `/gestionar-cuentas/reset-password` | admin | Restablecer contraseña de usuario |
| POST | `/gestionar-cuentas/permisos` | admin | Actualizar permisos de usuario |
| POST | `/gestionar-cuentas/eliminar` | admin | Eliminar usuario |

---

## Eventos SocketIO

El monitoreo en tiempo real utiliza WebSockets vía Flask-SocketIO:

| Evento | Namespace | Dirección | Descripción |
|---|---|---|---|
| `ups_data` | `/monitor` | Servidor → Cliente | Datos actualizados de UPS (SNMP) |
| `ups_update` | `/` | Servidor → Cliente | Datos actualizados de UPS (Modbus) |

### Estructura de datos `ups_data`

```json
{
  "device_name": "UPS-Oficina",
  "ip": "192.168.1.100",
  "status": "online",
  "battery_pct": 100,
  "load_pct": 45,
  "input_voltage": 120.5,
  "output_voltage": 120.0,
  "temperature": 25.3
}
```

Los datos se emiten cada ~2 segundos por cada dispositivo configurado en el monitoreo.
