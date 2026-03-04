from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    host = app.config.get('APP_HOST', '0.0.0.0')
    port = app.config.get('APP_PORT', 5000)
    domain = app.config.get('APP_DOMAIN', 'localhost')
    debug = app.config.get('DEBUG', False)

    mdns_enabled = app.config.get('MDNS_ENABLED', True)

    print(f"  * UPS Manager escuchando en http://{host}:{port}")
    print(f"  * Dominio: http://{domain}:{port}")
    print(f"  * Modo: {'desarrollo' if debug else 'produccion'}")
    if mdns_enabled:
        print(f"  * mDNS activo: cualquier dispositivo en la red puede acceder a http://{domain}:{port}")

    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
