import os
import secrets


class BaseConfig:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True

    # Base de datos PostgreSQL
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'postgresql://localhost:5432/ups_manager'
    )

    # Archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    ALLOWED_IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/gif'}

    # --- DNS / Red ---
    APP_DOMAIN = os.environ.get('APP_DOMAIN', 'lbs.local')
    APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.environ.get('APP_PORT', '5000'))

    # --- mDNS (Bonjour / Zeroconf) ---
    MDNS_ENABLED = os.environ.get('MDNS_ENABLED', 'true').lower() in ('true', '1', 'yes')
    MDNS_SERVICE_NAME = os.environ.get('MDNS_SERVICE_NAME', 'UPS Manager LBS')

    # SocketIO CORS (red local + dominio)
    _cors_env = os.environ.get('CORS_ORIGINS', '')
    _domain = os.environ.get('APP_DOMAIN', 'lbs.local')
    _port = os.environ.get('APP_PORT', '5000')
    CORS_ORIGINS = (
        _cors_env.split(',') if _cors_env
        else [
            '*',
            f'http://{_domain}',
            f'http://{_domain}:{_port}',
            f'https://{_domain}',
            f'https://{_domain}:{_port}',
        ]
    )

    # InfluxDB (monitoreo)
    INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
    INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN', 'my-token')
    INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG', 'my-org')
    INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET', 'ups_monitoring')


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = False  # Cambiar a True si se usa HTTPS en la intranet


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
