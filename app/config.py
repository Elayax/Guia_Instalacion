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
        'postgresql://ups_admin:ups_secure_2024@localhost:5432/ups_manager'
    )

    # Archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    ALLOWED_IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/gif'}

    # SocketIO CORS (red local)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

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
