# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**UPS Manager** — A Flask web application for managing UPS (Uninterruptible Power Supply) installations. It calculates electrical wire gauges, breaker protections per NOM-001-SEDE-2012 (Mexican electrical standard), manages client/equipment databases, monitors UPS devices via SNMP/Modbus in real-time, and generates PDF installation guides.

**Language:** The codebase, UI, comments, and variable names are primarily in **Spanish**.

## Commands

```bash
# Setup (Windows)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run the application (serves on http://127.0.0.1:5000)
python run.py

# Run tests
pytest
pytest tests/test_ups_final.py          # single test file
pytest -v --cov=app                     # with coverage

# Docker
docker-compose up                       # web + report_generator services
```

## Architecture

### Entry Point & App Factory
- `run.py` — Starts the Flask app with SocketIO (threading mode, port 5000)
- `app/__init__.py` — `create_app()` factory: loads config, initializes PostgreSQL pool, runs migrations, registers blueprints, starts background monitoring service

### Database Layer (`database/`)
- **Engine:** PostgreSQL (psycopg3 + psycopg_pool)
- **Connection:** `database/connection/db_connection.py` — Singleton `ConnectionPool` with thread-safe context manager
- **Config:** `database/config/config.py` — `BaseConfig`/`DevelopmentConfig`/`ProductionConfig`; `DATABASE_URL` env var overrides default
- **Migrations:** `database/migrations/*.sql` — Auto-run on app startup via `runner.py`. Tracked in `schema_migrations` table. To add a new migration: create `NNN_descriptive_name.sql` and restart the app
- **Data access:** `app/base_datos.py` — `GestorDB` class, the single DAL for all queries (clients, UPS specs, batteries, projects, monitoring, CSV import)
- **Compat shims:** `app/config.py`, `app/db_connection.py`, `app/models/user.py` re-export from `database/` to preserve old imports

### Flask Blueprints (`app/routes/`)
| Blueprint | File | Purpose |
|-----------|------|---------|
| `auth_bp` | `auth.py` | Login/logout, password change (Flask-Login + bcrypt) |
| `dashboard_bp` | `dashboard.py` | Main dashboard |
| `calculator_bp` | `calculator.py` | Electrical calculations form |
| `api_bp` | `api.py` | JSON API endpoints |
| `management_bp` | `management.py` | CRUD for clients, UPS specs, batteries |
| `documents_bp` | `documents.py` | PDF report generation and project management |
| `guia_rapida_bp` | `guia_rapida.py` | Quick-start guide |
| `monitoreo_bp` | `monitoreo_routes.py` | Real-time UPS monitoring UI |
| `test_snmp_bp` | `test_snmp_routes.py` | SNMP testing tools |
| `diagnostic_bp` | `diagnostic_routes.py` | System diagnostics |

### Core Domain Logic
- `app/calculos.py` — `CalculadoraUPS` (wire gauge, breaker, voltage drop per NOM-001) and `CalculadoraBaterias` (battery bank sizing from discharge curves). Uses Open-Meteo API for altitude/temperature derating
- `app/reporte.py` — `ReportePDF` (extends fpdf2 `FPDF`): generates multi-page PDF installation guides with cover, safety norms, engineering specs, battery config, diagrams, and ventilation sections

### Real-Time Monitoring (`app/services/`)
- `monitoring_service.py` — Background `threading.Thread` daemon that polls UPS devices every 2s
- `protocols/snmp_client.py`, `snmp_minimal_client.py`, `snmp_upsmib_client.py` — SNMP clients for different UPS types (INVT enterprise, UPS-MIB standard, hybrid)
- `modbus_monitor.py` — Modbus TCP polling for compatible UPS devices
- Data is pushed to the frontend via **Flask-SocketIO** (`/monitor` namespace)
- Optional **InfluxDB** integration for time-series storage (`services/influx_db.py`)

### Frontend
- Jinja2 templates in `app/templates/` with a single `app/static/js/main.js`
- Real-time monitoring dashboard uses Socket.IO client

### Extensions (`app/extensions.py`)
Flask-SocketIO, Flask-Login, Flask-WTF (CSRF) — initialized as singletons, bound in `create_app()`

## Git Branching
- `main` — main branch
- `produccion` — production releases
- Developer branches: `Samuel_Dev`, `Emmnanuel_DEV`, `Luis_Dev`

## Key Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://postgres:Lemonroy%231@localhost:5432/ups_manager` | PostgreSQL connection |
| `FLASK_CONFIG` | `development` | Config profile (`development` / `production`) |
| `SECRET_KEY` | Auto-generated | Flask session secret |
| `INFLUXDB_URL` | `http://localhost:8086` | InfluxDB for monitoring data |
| `INFLUXDB_TOKEN` | `my-token` | InfluxDB auth token |
| `CORS_ORIGINS` | `*` | Allowed CORS origins for SocketIO |
| `APP_DOMAIN` | `lbs.local` | Domain name for the app (used by mDNS and CORS) |
| `MDNS_ENABLED` | `true` | Enable mDNS (Bonjour) auto-discovery on LAN |
| `MDNS_SERVICE_NAME` | `UPS Manager LBS` | Service name announced via mDNS |
