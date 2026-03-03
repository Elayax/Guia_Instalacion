from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    host = app.config.get('APP_HOST', '0.0.0.0')
    port = app.config.get('APP_PORT', 5000)
    domain = app.config.get('APP_DOMAIN', 'localhost')
    debug = app.config.get('DEBUG', False)

    print(f"  * UPS Manager escuchando en http://{host}:{port}")
    print(f"  * DNS configurado: http://{domain}:{port}")
    print(f"  * Modo: {'desarrollo' if debug else 'producción'}")

    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
