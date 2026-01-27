from app import create_app
from app.extensions import socketio
from app.services.modbus_monitor import monitor_service

app = create_app()

if __name__ == '__main__':
    monitor_service.start_background_task()
    socketio.run(app, debug=True)