# Arquitectura del Sistema

> UPS Manager LBS — Documento de arquitectura técnica

[← Volver al README](../README.md) | [Índice de Documentación](README.md)

---

## Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                        NAVEGADOR WEB                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Dashboard │  │Calculadora│ │  SCADA   │  │ Gestión Datos │  │
│  └─────┬────┘  └─────┬────┘  └────┬─────┘  └──────┬────────┘  │
└────────┼─────────────┼────────────┼────────────────┼───────────┘
         │  HTTP/WS    │            │ SocketIO       │
─────────┴─────────────┴────────────┴────────────────┴────────────
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK + SOCKETIO                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   12 BLUEPRINTS                          │   │
│  │  auth · dashboard · calculator · api · management       │   │
│  │  documents · guia_rapida · monitoreo · test_snmp        │   │
│  │  diagnostic · vales · user_mgmt                         │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                       │
│  ┌──────────┐  ┌───────┴────────┐  ┌────────────────────┐     │
│  │ Permisos │  │   GestorDB     │  │     Services       │     │
│  │ (8 secc) │  │ (Repository)   │  │                    │     │
│  └──────────┘  └───────┬────────┘  │ MonitoringService  │     │
│                        │           │ ModbusMonitor      │     │
│                        │           │ SNMPClient         │     │
│                        │           │ InfluxDBService    │     │
│                        │           │ ServicioMDNS       │     │
│                        │           └─────┬──────────────┘     │
└────────────────────────┼─────────────────┼──────────────────────┘
                         │                 │
              ┌──────────┴──┐    ┌─────────┴──────────┐
              │ PostgreSQL  │    │  Dispositivos UPS   │
              │ ups_manager │    │  (SNMP / Modbus)    │
              └─────────────┘    └─────────┬──────────┘
                                           │
                                 ┌─────────┴──────────┐
                                 │    InfluxDB         │
                                 │ (series de tiempo)  │
                                 └────────────────────┘
```

---

## Patrones de Diseño

### App Factory

La aplicación se crea mediante el patrón Factory en `app/__init__.py`:

```python
def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])
    # Inicializa pool de conexiones, extensiones, blueprints, servicios
    return app
```

Esto permite crear instancias con distintas configuraciones (`development`, `production`) y facilita las pruebas.

### Blueprints

Cada módulo funcional se registra como un Blueprint de Flask, manteniendo separación de responsabilidades.

### Service Layer

Los servicios en `app/services/` encapsulan lógica de negocio compleja:
- **MonitoringService** — Orquesta monitoreo SNMP/Modbus en hilo de fondo
- **ModbusMonitor** — Lectura de registros Modbus TCP para UPS INVT
- **SNMPClient** — Consultas SNMP asíncronas (v1/v2c)
- **InfluxDBService** — Escritura de métricas en InfluxDB con circuit breaker
- **ServicioMDNS** — Descubrimiento de red vía Zeroconf/Bonjour

### Repository (GestorDB)

`app/base_datos.py` contiene la clase `GestorDB` que centraliza todas las operaciones de base de datos. Utiliza `psycopg3` con connection pooling vía `psycopg-pool`.

### Connection Pool

El pool de conexiones se inicializa una sola vez al arrancar la app y se inyecta en `GestorDB`:

```python
pool = ConnectionPool.initialize(app.config['DATABASE_URL'])
app.db = GestorDB(pool)
```

---

## Blueprints

| Blueprint | Archivo | Rutas Principales | Permiso | Descripción |
|---|---|---|---|---|
| `auth` | `routes/auth.py` | `/login`, `/logout`, `/cambiar-password` | — | Autenticación y sesión |
| `dashboard` | `routes/dashboard.py` | `/` | `tablero` | Panel principal, búsqueda de pedidos |
| `calculator` | `routes/calculator.py` | `/calculadora`, `/generar-pdf-calculadora` | `calculos` | Cálculos eléctricos NOM-001 |
| `api` | `routes/api.py` | `/api/buscar-pedido/<pedido>`, `/api/sucursales/<cliente>`, `/api/ups/<id>`, `/api/bateria/<id>` | login | Endpoints JSON de consulta |
| `management` | `routes/management.py` | `/gestion`, `/carga-masiva`, `/exportar-tabla/<tabla>` | `datos` | CRUD de UPS, baterías, clientes, personal |
| `documents` | `routes/documents.py` | `/reimprimir-guia/<pedido>`, `/generar-checklist/<pedido>` | `calculos` | Generación y reimpresión de PDFs |
| `guia_rapida` | `routes/guia_rapida.py` | `/guia-rapida`, `/generar-pdf-guia-rapida` | `guia_rapida` | Guía rápida de instalación |
| `monitoreo` | `routes/monitoreo_routes.py` | `/monitoreo`, `/api/monitoreo/*` | `scada` | Dashboard SCADA en tiempo real |
| `test_snmp` | `routes/test_snmp_routes.py` | `/snmp-test`, `/api/snmp/test` | login | Pruebas de conectividad SNMP |
| `diagnostic` | `routes/diagnostic_routes.py` | `/diagnostico`, `/api/diagnostic/*` | login | Diagnóstico de red (ping, puertos, scan) |
| `vales` | `routes/vales.py` | `/vales`, `/vales/historial` | `vales` | Control de vales de herramienta |
| `user_mgmt` | `routes/user_management.py` | `/gestionar-cuentas`, `/gestionar-cuentas/*` | admin | Gestión de usuarios y permisos |

---

## Esquema de Base de Datos

### Diagrama ER (simplificado)

```
┌──────────────┐       ┌───────────────────┐
│    users     │       │  user_permissions  │
│──────────────│       │───────────────────│
│ id (PK)      │──1:N─→│ user_id (FK)      │
│ username     │       │ seccion           │
│ password_hash│       │ permitido         │
│ role         │       └───────────────────┘
│ created_at   │
└──────────────┘

┌──────────────┐       ┌────────────────────────┐
│  clientes    │       │  proyectos_publicados  │
│──────────────│       │────────────────────────│
│ id (PK)      │──1:N─→│ pedido (PK)            │
│ cliente      │       │ cliente_id (FK)        │
│ sucursal     │       │ ups_id (FK)            │
│ direccion    │       │ bateria_id (FK)        │
│ link_maps    │       │ fecha_publicacion      │
│ lat, lon     │       │ snapshot_* (config)    │
└──────────────┘       │ pdf_url, checklist_url │
                       └────────────────────────┘

┌──────────────┐       ┌──────────────────────────┐
│  ups_specs   │       │  baterias_modelos        │
│──────────────│       │──────────────────────────│
│ id (PK)      │       │ id (PK)                  │
│ Nombre       │       │ modelo, serie            │
│ Serie        │       │ voltaje_nominal          │
│ Capacidad_kVA│       │ capacidad_nominal_ah     │
│ Capacidad_kW │       │ temp coefficients        │
│ Eficiencia_* │       │ charge specs             │
│ Bateria_Vdc  │       └───────────┬──────────────┘
│ (51+ cols)   │                   │
└──────────────┘       ┌───────────┴──────────────┐
                       │ baterias_curvas_descarga  │
                       │──────────────────────────│
                       │ bateria_id (FK)           │
                       │ tiempo_minutos            │
                       │ voltaje_corte_fv          │
                       │ valor, unidad             │
                       └──────────────────────────┘

┌──────────────────┐   ┌──────────────┐
│ monitoreo_config │   │   personal   │
│──────────────────│   │──────────────│
│ id (PK)          │   │ id (PK)      │
│ ip, port         │   │ nombre       │
│ protocolo        │   │ puesto       │
│ snmp_version     │   │ fecha        │
│ ups_type         │   └──────────────┘
│ community        │
│ slave_id         │   ┌──────────────────┐
│ nombre, estado   │   │ tipos_ventilacion│
└──────────────────┘   │──────────────────│
                       │ id, nombre       │
                       │ descripcion      │
                       │ imagen_url       │
                       └──────────────────┘
```

### Tablas Principales

| Tabla | Descripción |
|---|---|
| `users` | Usuarios del sistema (username, password_hash bcrypt, role admin/user) |
| `user_permissions` | Permisos granulares por sección (8 secciones disponibles) |
| `clientes` | Clientes y sucursales con geolocalización |
| `ups_specs` | Catálogo técnico de UPS (51+ columnas: capacidad, eficiencia, dimensiones, cables) |
| `baterias_modelos` | Modelos de baterías con coeficientes de temperatura y curvas de carga |
| `baterias_curvas_descarga` | Curvas de descarga por modelo (tiempo, voltaje de corte, valor) |
| `proyectos_publicados` | Proyectos calculados y publicados con snapshots de configuración y URLs de PDFs |
| `monitoreo_config` | Dispositivos UPS configurados para monitoreo SCADA (IP, protocolo, SNMP config) |
| `personal` | Registro de técnicos y personal de instalación |
| `tipos_ventilacion` | Catálogo de tipos de ventilación para UPS |
| `schema_migrations` | Control de migraciones aplicadas |

---

## Sistema de Migraciones

Las migraciones SQL se ejecutan automáticamente al iniciar la aplicación:

1. Se ubican en `database/migrations/` con convención `NNN_nombre.sql`
2. El runner (`app/migrations/runner.py`) verifica la tabla `schema_migrations`
3. Solo ejecuta migraciones no aplicadas previamente
4. Las migraciones son idempotentes (usan `IF NOT EXISTS`)

Migraciones actuales:
- `001_initial_schema.sql` — Esquema base (todas las tablas principales)
- `002_seed_data.sql` — Datos iniciales (ventilación, baterías LBS)
- `003_add_monitoring_columns.sql` — Columnas SNMP en monitoreo
- `007_permisos_pdf.sql` — Permisos granulares para PDFs
- `008_permiso_vales.sql` — Permiso de vales para usuarios existentes

---

## Flujo de Monitoreo en Tiempo Real

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Dispositivo │     │ MonitoringService │     │  Navegador   │
│    UPS      │     │   (hilo daemon)  │     │   (cliente)  │
└──────┬──────┘     └────────┬─────────┘     └──────┬───────┘
       │                     │                       │
       │  SNMP GET / Modbus  │                       │
       │◄────────────────────│                       │
       │                     │                       │
       │  Respuesta datos    │                       │
       │────────────────────►│                       │
       │                     │                       │
       │                     │──► InfluxDB (write)   │
       │                     │                       │
       │                     │  socketio.emit        │
       │                     │  'ups_data'           │
       │                     │──────────────────────►│
       │                     │                       │
       │                     │  (cada 2 segundos)    │
       │                     │                       │
```

- **Protocolos soportados:** SNMP v1/v2c, Modbus TCP
- **Tipos de UPS:** `invt_enterprise`, `invt_minimal`, `ups_mib_standard`, `hybrid`
- **Eventos SocketIO:** `ups_data` (namespace `/monitor`), `ups_update`
- **Persistencia opcional:** InfluxDB con circuit breaker (backoff 60s en error)

---

## Motor de Cálculos NOM-001

El módulo `app/calculos.py` implementa los cálculos eléctricos según **NOM-001-SEDE-2012**:

| Cálculo | Referencia NOM | Descripción |
|---|---|---|
| Calibre de conductor | Tabla 310-15(b)(16) | Selección por ampacidad a 75°C y 90°C |
| Protecciones (breakers) | Tabla 240-6(A) | Selección de interruptor termomagnético estándar |
| Conductor de tierra | Tabla 250-122 | Mínimo según capacidad del breaker |
| Caída de tensión | Art. 210-19 | Cálculo con impedancia del conductor (<3% óptimo) |
| Factor de temperatura | Tabla 310-15(b)(2)(a) | Derating por temperatura ambiente |

### Flujo de cálculo:
1. Usuario ingresa datos del UPS y la instalación
2. Se calcula corriente nominal y de protección
3. Se selecciona calibre mínimo por ampacidad
4. Se verifica caída de tensión (advertencia si >3%)
5. Se selecciona protección estándar y conductor de tierra
6. Se genera PDF con resultados y referencias normativas

---

## Sistema de Permisos

### Secciones Disponibles

| Sección | Descripción | Admin | User (default) |
|---|---|---|---|
| `tablero` | Dashboard principal | ✅ | ✅ |
| `calculos` | Calculadora eléctrica | ✅ | ✅ |
| `guia_rapida` | Guía rápida de instalación | ✅ | ✅ |
| `scada` | Monitoreo SNMP/Modbus | ✅ | ❌ |
| `datos` | Gestión de datos (CRUD) | ✅ | ✅ |
| `ejemplo_pdf` | Generar PDF de ejemplo | ✅ | ✅ |
| `publicar_pdf` | Publicar PDF oficial | ✅ | ❌ |
| `vales` | Vales de herramienta | ✅ | ✅ |

- Los administradores tienen acceso completo sin restricciones
- Los permisos se almacenan en `user_permissions` y son editables desde `/gestionar-cuentas`
- El decorador `@permiso_requerido('seccion')` protege cada ruta

---

## Generación de PDFs

El sistema utiliza dos librerías para generación de documentos:

| Librería | Archivo | Uso |
|---|---|---|
| **fpdf2** | `app/reporte.py` | Guías de instalación completas con diagramas, tablas y cálculos |
| **fpdf2** | `app/checklist.py` | Checklists de verificación de instalación |
| **ReportLab** | Disponible | Librería alternativa para reportes complejos |
| **Pillow** | Soporte | Procesamiento y optimización de imágenes para PDFs |

Características de los PDFs:
- Soporte UTF-8 con caracteres en español (ñ, acentos)
- Encabezados y pies de página corporativos
- Esquema de colores: Rojo (180,20,20), Gris (60,60,60), Negro (40,40,40)
- Numeración automática de secciones
- Imágenes optimizadas con Pillow
