<div align="center">

# UPS Manager LBS

**Sistema de Gestion y Monitoreo para Instalaciones UPS**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![SocketIO](https://img.shields.io/badge/SocketIO-Realtime-010101?logo=socketdotio&logoColor=white)](https://socket.io)
[![NOM-001](https://img.shields.io/badge/NOM--001--SEDE--2012-Compliant-green)]()
[![Idioma](https://img.shields.io/badge/Idioma-Espa%C3%B1ol-red)]()

---

Plataforma web para automatizar calculos electricos, generar guias de instalacion PDF y monitorear equipos UPS en tiempo real via SNMP/Modbus. Disenada para equipos de ingenieria que trabajan bajo la norma **NOM-001-SEDE-2012**.

*Desarrollado por [Lemonroy Business Solutions](https://lemonroy.com)*

</div>

---

## Caracteristicas Principales

| | Modulo | Descripcion |
|---|---|---|
| **Calculos Electricos** | Calculadora NOM-001 | Calibre de conductores, protecciones, tierra, caida de tension y derating por temperatura |
| **Monitoreo SCADA** | Dashboard tiempo real | Monitoreo de UPS via SNMP (v1/v2c) y Modbus TCP con SocketIO |
| **Generacion de PDFs** | Guias e instalacion | Guias de instalacion, checklists y reportes con diagramas y tablas |
| **Gestion de Datos** | CRUD completo | Clientes, sucursales, equipos UPS (51+ specs), baterias con curvas de descarga |
| **Red y Conectividad** | Diagnosticos | Ping, escaneo de puertos, SNMP walk, auto-deteccion, mDNS (lbs.local) |
| **Seguridad** | Auth y permisos | Login con bcrypt, CSRF, roles admin/user, 8 secciones de permisos granulares |

<!-- TODO: Capturas de pantalla -->

---

## Stack Tecnologico

| Capa | Tecnologias |
|---|---|
| **Backend** | Python 3.10+, Flask 3.1, Flask-SocketIO, eventlet |
| **Base de Datos** | PostgreSQL 15+ (psycopg3 + connection pool) |
| **Monitoreo** | PySNMP 7, PyModbus 3.6, InfluxDB (series de tiempo) |
| **Frontend** | HTML5, CSS3, JavaScript, Jinja2, SocketIO Client |
| **PDFs** | fpdf2, ReportLab, Pillow |
| **Autenticacion** | Flask-Login, bcrypt, Flask-WTF (CSRF) |
| **Red** | Zeroconf/mDNS (lbs.local), ZeroTier compatible |
| **Despliegue** | Docker, docker-compose, systemd |

---

## Inicio Rapido

### Requisitos previos

- Python 3.10+
- PostgreSQL 15+
- Git

### Pasos

```bash
# 1. Clonar
git clone https://github.com/TU_ORG/Guia_Instalacion.git
cd Guia_Instalacion

# 2. Entorno virtual
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/macOS

# 3. Dependencias
pip install -r requirements.txt

# 4. Configurar
cp .env.example .env
# Editar .env con tu DATABASE_URL y SECRET_KEY

# 5. Ejecutar
python run.py

# 6. Abrir en el navegador
# http://localhost:5000  o  http://lbs.local:5000
```

Las migraciones de base de datos se ejecutan automaticamente al iniciar.

---

## Despliegue con Docker

```bash
docker-compose up --build
```

Para mas opciones de despliegue (produccion, nginx, systemd), consulta [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Arquitectura del Proyecto

```
Guia_Instalacion/
├── app/
│   ├── __init__.py              # App Factory (create_app)
│   ├── base_datos.py            # GestorDB — capa de acceso a datos
│   ├── calculos.py              # Motor de calculos NOM-001
│   ├── reporte.py               # Generacion de PDFs (fpdf2)
│   ├── checklist.py             # PDFs de checklist
│   ├── permisos.py              # Sistema de permisos (8 secciones)
│   ├── security.py              # Headers de seguridad
│   ├── extensions.py            # SocketIO, LoginManager, CSRF
│   ├── routes/
│   │   ├── auth.py              # Login, logout, cambiar password
│   │   ├── dashboard.py         # Panel principal
│   │   ├── calculator.py        # Calculadora electrica
│   │   ├── api.py               # Endpoints JSON
│   │   ├── management.py        # CRUD datos (UPS, baterias, clientes)
│   │   ├── documents.py         # Generacion de documentos PDF
│   │   ├── guia_rapida.py       # Guia rapida de instalacion
│   │   ├── monitoreo_routes.py  # Dashboard SCADA
│   │   ├── test_snmp_routes.py  # Pruebas SNMP
│   │   ├── diagnostic_routes.py # Diagnostico de red
│   │   ├── vales.py             # Vales de herramienta
│   │   └── user_management.py   # Gestion de usuarios (admin)
│   ├── services/
│   │   ├── monitoring_service.py # Orquestador de monitoreo
│   │   ├── modbus_monitor.py     # Cliente Modbus TCP
│   │   ├── influx_db.py          # Escritura a InfluxDB
│   │   ├── mdns_service.py       # Descubrimiento mDNS/Bonjour
│   │   └── protocols/
│   │       ├── snmp_client.py        # Cliente SNMP async
│   │       ├── snmp_scanner.py       # Auto-deteccion SNMP
│   │       ├── snmp_upsmib_client.py # Cliente UPS-MIB (RFC 1628)
│   │       └── snmp_minimal_client.py
│   ├── models/
│   │   └── user.py              # Modelo de usuario (Flask-Login)
│   ├── templates/               # Plantillas Jinja2
│   ├── static/                  # CSS, JS, imagenes
│   └── utils/
│       └── ups_oids.py          # Definiciones de OIDs SNMP
├── database/
│   ├── config/config.py         # Configuracion (BaseConfig, Dev, Prod)
│   ├── connection/db_connection.py # Pool de conexiones psycopg3
│   ├── migrations/              # Migraciones SQL auto-ejecutables
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_seed_data.sql
│   │   └── ...
│   └── models/user.py
├── scripts/                     # Scripts utilitarios
├── tests/                       # Tests con pytest
├── docs/                        # Documentacion tecnica
├── Reportes/                    # PDFs generados
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── run.py                       # Punto de entrada
├── CONTRIBUTING.md
└── README.md
```

---

## Diagrama de Arquitectura

```
  Navegador                Flask + SocketIO               Infraestructura
 ──────────               ─────────────────              ────────────────

 ┌──────────┐  HTTP/WS   ┌──────────────────┐           ┌─────────────┐
 │ Dashboard ├───────────►│   12 Blueprints  ├──────────►│ PostgreSQL  │
 │ Calculos  │            │                  │           │ ups_manager │
 │ SCADA     │◄──── WS ──┤  GestorDB (repo) │           └─────────────┘
 │ Gestion   │            │  Permisos        │
 └──────────┘            │  Flask-Login     │           ┌─────────────┐
                          └────────┬─────────┘     ┌───►│  InfluxDB   │
                                   │               │    │ (metricas)  │
                          ┌────────┴─────────┐     │    └─────────────┘
                          │    Services      │     │
                          │ MonitoringService ├────┘    ┌─────────────┐
                          │ SNMPClient       ├────────►│ UPS Devices │
                          │ ModbusMonitor    ├────────►│ SNMP/Modbus │
                          │ mDNS Service     │         └─────────────┘
                          └──────────────────┘
```

---

## Variables de Entorno

Copia `.env.example` como `.env` y configura:

| Variable | Default | Descripcion |
|---|---|---|
| `DATABASE_URL` | `postgresql://localhost:5432/ups_manager` | Conexion PostgreSQL |
| `SECRET_KEY` | Auto-generada | Clave secreta Flask (obligatoria en prod) |
| `FLASK_CONFIG` | `development` | Perfil: `development` / `production` |
| `APP_DOMAIN` | `lbs.local` | Dominio de la aplicacion |
| `APP_HOST` | `0.0.0.0` | Host de escucha |
| `APP_PORT` | `5000` | Puerto |
| `MDNS_ENABLED` | `true` | Descubrimiento mDNS/Bonjour |
| `INFLUXDB_URL` | `http://localhost:8086` | InfluxDB para monitoreo |
| `INFLUXDB_TOKEN` | — | Token InfluxDB |
| `INFLUXDB_ORG` | — | Organizacion InfluxDB |
| `INFLUXDB_BUCKET` | `ups_monitoring` | Bucket de metricas |

Ver tabla completa en [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#variables-de-entorno).

---

## Documentacion

| Documento | Contenido |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Patrones de diseno, blueprints, esquema de BD, monitoreo, permisos |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Instalacion local, Docker, produccion, troubleshooting |
| [docs/API.md](docs/API.md) | Referencia completa de endpoints y eventos SocketIO |
| [docs/SNMP_TESTING_GUIDE.md](docs/SNMP_TESTING_GUIDE.md) | Guia de pruebas SNMP |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como contribuir, estilo de codigo, flujo Git |

---

## Tests

```bash
pytest --cov=app
```

---

## Licencia

Proyecto propietario de **Lemonroy Business Solutions SA de CV**. Todos los derechos reservados.

---

<div align="center">

Desarrollado con dedicacion por el equipo de **Lemonroy Business Solutions**

</div>
