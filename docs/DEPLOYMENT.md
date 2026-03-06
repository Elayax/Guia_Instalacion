# Guía de Despliegue

> UPS Manager LBS — Instalación y configuración en distintos entornos

[← Volver al README](../README.md) | [Índice de Documentación](README.md)

---

## Requisitos Previos

| Componente | Versión Mínima | Notas |
|---|---|---|
| Python | 3.10+ | Recomendado 3.12 |
| PostgreSQL | 15+ | Recomendado 16 |
| Git | 2.30+ | Para clonar el repositorio |
| Docker | 24+ | Solo para despliegue con contenedores (opcional) |

---

## Desarrollo Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_ORG/Guia_Instalacion.git
cd Guia_Instalacion
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

Crea la base de datos y un usuario:

```sql
CREATE DATABASE ups_manager;
CREATE USER ups_user WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE ups_manager TO ups_user;
```

### 5. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores (ver [tabla completa de variables](#variables-de-entorno) más abajo).

### 6. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`. Las migraciones de base de datos se ejecutan automáticamente al iniciar.

### 7. Credenciales iniciales

Al ejecutar por primera vez, se crea un usuario administrador por defecto. Revisa los logs de la consola para ver las credenciales iniciales y cámbialas inmediatamente desde `/cambiar-password`.

---

## Despliegue con Docker

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    hostname: lbs.local
    ports:
      - "${APP_PORT:-5000}:${APP_PORT:-5000}"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - APP_DOMAIN=${APP_DOMAIN:-lbs.local}
      - APP_HOST=0.0.0.0
      - APP_PORT=${APP_PORT:-5000}
      - MDNS_ENABLED=false

  report_generator:
    build: .
    volumes:
      - .:/app
    command: python Reportes/generador_reporte_lbs.py
```

### Comandos

```bash
# Construir e iniciar
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build

# Ver logs
docker-compose logs -f web

# Detener
docker-compose down
```

> **Nota:** En Docker, `MDNS_ENABLED` se desactiva por defecto ya que mDNS no funciona bien dentro de contenedores.

---

## Despliegue en Producción

### Configuración recomendada

1. **Variables de entorno críticas:**

```bash
FLASK_CONFIG=production
SECRET_KEY=<clave-secreta-de-al-menos-32-caracteres>
DATABASE_URL=postgresql://usuario:contraseña@host:5432/ups_manager
```

2. **Servidor WSGI** — Usar eventlet (requerido para SocketIO):

```bash
python run.py
```

El archivo `run.py` ya está configurado para usar eventlet como servidor WSGI con soporte para WebSockets.

3. **Reverse proxy con Nginx:**

```nginx
server {
    listen 80;
    server_name lbs.local;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

4. **Servicio systemd:**

```ini
[Unit]
Description=UPS Manager LBS
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/opt/ups-manager
Environment="FLASK_CONFIG=production"
EnvironmentFile=/opt/ups-manager/.env
ExecStart=/opt/ups-manager/venv/bin/python run.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## Variables de Entorno

| Variable | Requerida | Default | Descripción |
|---|---|---|---|
| `DATABASE_URL` | Sí | `postgresql://localhost:5432/ups_manager` | URL de conexión a PostgreSQL |
| `SECRET_KEY` | Sí (prod) | Auto-generada | Clave secreta para sesiones Flask |
| `FLASK_CONFIG` | No | `development` | Perfil de configuración (`development` / `production`) |
| `APP_DOMAIN` | No | `lbs.local` | Dominio de la aplicación |
| `APP_HOST` | No | `0.0.0.0` | Host de escucha |
| `APP_PORT` | No | `5000` | Puerto de escucha |
| `MDNS_ENABLED` | No | `true` | Activar descubrimiento mDNS/Bonjour |
| `MDNS_SERVICE_NAME` | No | `UPS Manager LBS` | Nombre del servicio mDNS |
| `INFLUXDB_URL` | No | `http://localhost:8086` | URL de InfluxDB para monitoreo |
| `INFLUXDB_TOKEN` | No | `my-token` | Token de autenticación InfluxDB |
| `INFLUXDB_ORG` | No | `my-org` | Organización en InfluxDB |
| `INFLUXDB_BUCKET` | No | `ups_monitoring` | Bucket para datos de monitoreo |
| `CORS_ORIGINS` | No | Auto (basado en `APP_DOMAIN`) | Orígenes CORS separados por coma |

---

## Solución de Problemas

### La aplicación no conecta a PostgreSQL

```
psycopg.OperationalError: connection refused
```

- Verifica que PostgreSQL esté ejecutándose: `pg_isready`
- Confirma que `DATABASE_URL` en `.env` sea correcta
- Verifica que el usuario tenga permisos sobre la base de datos

### Error al ejecutar migraciones

```
relation "schema_migrations" does not exist
```

Esto es normal en la primera ejecución — la migración `001_initial_schema.sql` crea esta tabla automáticamente.

### SocketIO no conecta (monitoreo en tiempo real)

- Verifica que el navegador soporte WebSockets
- Si usas un proxy reverso, asegúrate de configurar los headers `Upgrade` y `Connection`
- Revisa que `CORS_ORIGINS` incluya el dominio desde donde accedes

### mDNS no funciona

- **Windows 10+:** Funciona nativamente con Bonjour
- **Linux:** Instala `avahi-daemon`: `sudo apt install avahi-daemon`
- **Docker:** mDNS no funciona dentro de contenedores — usa IP directa o DNS convencional

### Errores de permisos al generar PDFs

- Verifica que el directorio `Reportes/` exista y tenga permisos de escritura
- En producción, asegúrate que el usuario del servicio tenga acceso al directorio
