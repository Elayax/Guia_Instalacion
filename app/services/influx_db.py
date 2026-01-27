import os
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDBService:
    def __init__(self):
        # Configuration - should preferably come from env vars
        self.url = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
        self.token = os.environ.get('INFLUXDB_TOKEN', 'my-token')
        self.org = os.environ.get('INFLUXDB_ORG', 'my-org')
        self.bucket = os.environ.get('INFLUXDB_BUCKET', 'ups_monitoring')
        self.client = None
        self.write_api = None

    def connect(self):
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            print("Conectado a InfluxDB")
            return True
        except Exception as e:
            print(f"Error conectando a InfluxDB: {e}")
            return False

    def write_ups_data(self, ups_name, ip, data_dict):
        """
        Escribe datos de un UPS a InfluxDB.
        data_dict: Diccionario con métricas { 'voltaje_in': 220, 'bateria_pct': 100, ... }
        """
        if not self.write_api:
            if not self.connect():
                return False

        try:
            point = Point("ups_status") \
                .tag("device_name", ups_name) \
                .tag("ip", ip) \
                .time(datetime.utcnow())

            for key, value in data_dict.items():
                if isinstance(value, (int, float)):
                    point = point.field(key, float(value))
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True
        except Exception as e:
            print(f"Error escribiendo a InfluxDB: {e}")
            return False

    def close(self):
        if self.client:
            self.client.close()

# Singleton instance
influx_service = InfluxDBService()
