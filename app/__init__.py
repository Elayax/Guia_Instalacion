from flask import Flask

def create_app():
    app = Flask(__name__)

    # Importar y registrar Blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.calculator import calculator_bp
    from app.routes.api import api_bp
    from app.routes.management import management_bp
    from app.routes.documents import documents_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(calculator_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(management_bp)
    app.register_blueprint(documents_bp)

    from app.routes.monitoreo_routes import monitoreo_bp
    app.register_blueprint(monitoreo_bp)

    from app.extensions import socketio
    socketio.init_app(app, async_mode='threading')

    return app