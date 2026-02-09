import os
import logging
from flask import Flask

from app.config import config_map
from app.logging_config import setup_logging
from app.db_connection import ConnectionPool
from app.extensions import socketio, login_manager, csrf
from app.security import apply_security_headers
from app.models.user import User
from app.base_datos import GestorDB

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    app = Flask(__name__)

    # --- Configuración ---
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(config_map[config_name])

    # --- Logging ---
    setup_logging(app)
    logger.info("Iniciando aplicación UPS Manager (config: %s)", config_name)

    # --- Base de datos PostgreSQL ---
    pool = ConnectionPool.initialize(app.config['DATABASE_URL'])

    # Ejecutar migraciones
    from app.migrations.runner import run_migrations
    run_migrations(pool)

    # Instancia centralizada de GestorDB
    app.db = GestorDB(pool)

    # --- Extensiones de seguridad ---
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        row = app.db.obtener_usuario_por_id(int(user_id))
        return User.from_row(row)

    # Headers de seguridad
    apply_security_headers(app)

    # --- SocketIO ---
    cors_origins = app.config.get('CORS_ORIGINS', ['*'])
    socketio.init_app(app, cors_allowed_origins=cors_origins, async_mode='threading')

    # --- Blueprints ---
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.calculator import calculator_bp
    from app.routes.api import api_bp
    from app.routes.management import management_bp
    from app.routes.documents import documents_bp
    from app.routes.monitoreo_routes import monitoreo_bp
    from app.routes.test_snmp_routes import test_snmp_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(calculator_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(management_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(monitoreo_bp)
    app.register_blueprint(test_snmp_bp)

    # --- Monitoreo en segundo plano ---
    try:
        from app.services.monitoring_service import MonitoringService
        monitor_service = MonitoringService()
        monitor_service.start()
        logger.info("Servicio de monitoreo iniciado")
    except Exception as e:
        logger.warning("No se pudo iniciar el servicio de monitoreo: %s", e)

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return "Página no encontrada", 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error("Error interno del servidor: %s", e)
        return "Error interno del servidor", 500

    logger.info("Aplicación UPS Manager lista")
    return app
