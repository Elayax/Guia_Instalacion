from app import create_app

# El traceback indica que se está importando un servicio de monitoreo.
# Para evitar que la aplicación se caiga si faltan dependencias de monitoreo,
# lo envolvemos en un bloque try-except.
try:
    from app.services.modbus_monitor import monitor_service
except ModuleNotFoundError:
    print("ADVERTENCIA: Dependencias de monitoreo no instaladas (ej. 'influxdb-client'). El servicio de monitoreo estará desactivado.")
    print("Para habilitarlo, instale las dependencias requeridas (ej. pip install influxdb-client).")

app = create_app()

if __name__ == '__main__':
    # Agregamos host='0.0.0.0' para que sea accesible desde fuera del contenedor
    app.run(host='0.0.0.0', port=5000, debug=True)