import logging
import asyncio
from typing import Dict, Any, List, Union

# Importación moderna para PySNMP 7.x
from pysnmp.hlapi.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, get_cmd
)

logger = logging.getLogger(__name__)

class SNMPClientError(Exception):
    pass

class SNMPClient:
    def __init__(self, ip_address: str = None, port: int = 161, community: str = 'public', timeout: int = 2, retries: int = 1):
        self.ip_address = ip_address
        self.community = community
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.engine = SnmpEngine()
        # Diccionario de OIDs específicos para tu NetAgent/Dragon Power
        self.oids_map = {
            "ups_model": "1.3.6.1.4.1.935.1.1.1.1.1.2.0",
            # Batería
            "battery_voltage": "1.3.6.1.4.1.935.1.1.1.2.2.2.0",
            "battery_capacity": "1.3.6.1.4.1.935.1.1.1.2.2.1.0",
            "battery_current": "1.3.6.1.4.1.935.1.1.1.2.2.6.0",
            "temperature": "1.3.6.1.4.1.935.1.1.1.2.2.3.0",
            # Entrada - Voltajes por fase
            "input_voltage_l1": "1.3.6.1.4.1.935.1.1.1.3.2.1.0",
            "input_voltage_l2": "1.3.6.1.4.1.935.1.1.1.3.2.2.0",
            "input_voltage_l3": "1.3.6.1.4.1.935.1.1.1.3.2.3.0",
            "input_frequency": "1.3.6.1.4.1.935.1.1.1.3.2.4.0",
            # Salida - Voltajes por fase
            "output_voltage_l1": "1.3.6.1.4.1.935.1.1.1.4.2.1.0",
            "output_voltage_l2": "1.3.6.1.4.1.935.1.1.1.4.2.2.0",
            "output_voltage_l3": "1.3.6.1.4.1.935.1.1.1.4.2.3.0",
            "output_frequency": "1.3.6.1.4.1.935.1.1.1.4.2.4.0",
            "output_current": "1.3.6.1.4.1.935.1.1.1.4.2.4.0",
            "output_load": "1.3.6.1.4.1.935.1.1.1.4.2.3.0",
        }

    async def get_ups_data(self, ip_address: str = None) -> Dict[str, Any]:
        """Consulta todos los datos del UPS y los devuelve formateados"""
        target_ip = ip_address or self.ip_address
        if not target_ip:
            return {}
            
        try:
            transport = await UdpTransportTarget.create((target_ip, self.port), timeout=self.timeout, retries=self.retries)
            objetos = [ObjectType(ObjectIdentity(oid)) for oid in self.oids_map.values()]

            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                self.engine,
                CommunityData(self.community, mpModel=1),
                transport,
                ContextData(),
                *objetos
            )

            if errorIndication or errorStatus:
                logger.error(f"Error SNMP en {target_ip}: {errorIndication or errorStatus}")
                return {}

            # Mapear y formatear resultados
            raw_data = {list(self.oids_map.keys())[i]: var[1].prettyPrint() for i, var in enumerate(varBinds)}
            
            return self._format_data(raw_data)

        except Exception as e:
            logger.exception(f"Fallo crítico consultando UPS {target_ip}: {e}")
            return {}
            
    # --- Métodos de compatibilidad para test_snmp_routes ---
    
    def test_connection(self):
        """Simula test de conexión síncrono"""
        try:
            # Probamos obtener solo el modelo, usando asyncio.run
            res = asyncio.run(self.get_oid_async(self.oids_map['ups_model']))
            if res:
                return True, "Conexión exitosa"
            else:
                return False, "No se recibió respuesta"
        except Exception as e:
            return False, str(e)

    def get_oid(self, oid):
        """Wrapper síncrono para obtener un OID"""
        return asyncio.run(self.get_oid_async(oid))

    async def get_oid_async(self, oid: str, ip_address: str = None):
        target_ip = ip_address or self.ip_address
        if not target_ip:
            raise SNMPClientError("IP no especificada")
            
        try:
            transport = await UdpTransportTarget.create((target_ip, self.port), timeout=self.timeout, retries=self.retries)
            errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                self.engine,
                CommunityData(self.community, mpModel=1),
                transport,
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            if errorIndication:
                raise SNMPClientError(f"Error SNMP: {errorIndication}")
            if errorStatus:
                raise SNMPClientError(f"Error Estado SNMP: {errorStatus.prettyPrint()}")
                
            return varBinds[0][1].prettyPrint()
        except Exception as e:
            logger.error(f"Error get_oid: {e}")
            return None

    def _format_data(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Limpia y escala los valores recibidos"""
        # Campos que vienen escalados x10 (voltajes, temperatura, frecuencia)
        scaled_fields = [
            "battery_voltage", "temperature",
            "input_voltage_l1", "input_voltage_l2", "input_voltage_l3", "input_frequency",
            "output_voltage_l1", "output_voltage_l2", "output_voltage_l3", "output_frequency",
            "output_current", "battery_current",
        ]
        formatted = {}
        for key, val in data.items():
            if val.isdigit() or (val.replace('.', '', 1).isdigit()):
                num_val = float(val)
                if key in scaled_fields:
                    formatted[key] = num_val / 10
                else:
                    formatted[key] = num_val
            else:
                formatted[key] = val
        return formatted