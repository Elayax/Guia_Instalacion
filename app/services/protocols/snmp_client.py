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
        
        # OIDs Comunes (Batería, Info, etc)
        self.oids_common = {
            "ups_model": "1.3.6.1.4.1.935.1.1.1.1.1.2.0",
            "battery_voltage": "1.3.6.1.4.1.935.1.1.1.2.2.2.0",
            "battery_capacity": "1.3.6.1.4.1.935.1.1.1.2.2.1.0",
            "battery_current": "1.3.6.1.4.1.935.1.1.1.2.2.6.0",
            "temperature": "1.3.6.1.4.1.935.1.1.1.2.2.3.0",
        }

        # --- MAPAS DE ENTRADA ---
        self.oids_input_1ph = {
            "input_voltage_l1": "1.3.6.1.4.1.935.1.1.1.3.2.1.0",
            "input_frequency": "1.3.6.1.4.1.935.1.1.1.3.2.2.0",
        }
        self.oids_input_3ph = {
            "input_voltage_l1": "1.3.6.1.4.1.935.1.1.1.3.2.1.0",
            "input_voltage_l2": "1.3.6.1.4.1.935.1.1.1.3.2.2.0",
            "input_voltage_l3": "1.3.6.1.4.1.935.1.1.1.3.2.3.0",
            "input_frequency": "1.3.6.1.4.1.935.1.1.1.3.2.4.0",
        }

        # --- MAPAS DE SALIDA ---
        self.oids_output_1ph = {
            "output_voltage_l1": "1.3.6.1.4.1.935.1.1.1.4.2.1.0",
            "output_frequency": "1.3.6.1.4.1.935.1.1.1.4.2.2.0",
            "output_load": "1.3.6.1.4.1.935.1.1.1.4.2.3.0",
             # En 1Ph, corriente suele ser el siguiente. Si falla, asumimos 0.
            "output_current": "1.3.6.1.4.1.935.1.1.1.4.2.4.0", 
        }
        self.oids_output_3ph = {
            "output_voltage_l1": "1.3.6.1.4.1.935.1.1.1.4.2.1.0",
            "output_voltage_l2": "1.3.6.1.4.1.935.1.1.1.4.2.2.0",
            "output_voltage_l3": "1.3.6.1.4.1.935.1.1.1.4.2.3.0",
            "output_frequency": "1.3.6.1.4.1.935.1.1.1.4.2.4.0",
            
            # Corrientes Salida
            "output_current_l1": "1.3.6.1.4.1.935.1.1.1.4.2.5.0",
            "output_current_l2": "1.3.6.1.4.1.935.1.1.1.4.2.6.0",
            "output_current_l3": "1.3.6.1.4.1.935.1.1.1.4.2.7.0",
            
            # Potencia
            "output_load": "1.3.6.1.4.1.935.1.1.1.4.2.12.0",    
            "active_power": "1.3.6.1.4.1.935.1.1.1.4.2.13.0",   
            "apparent_power": "1.3.6.1.4.1.935.1.1.1.4.2.14.0", 
            "power_factor": "1.3.6.1.4.1.935.1.1.1.4.2.15.0",   
        }

    async def _detect_phase_mode(self, ip_address: str, oid_check: str) -> int:
        """Helper para heurística: >800 -> 3Ph, <=800 -> 1Ph"""
        try:
            val_str = await self.get_oid_async(oid_check, ip_address)
            if val_str and val_str.isdigit():
                val = float(val_str)
                if val > 800: return 3
                return 1
        except Exception:
            pass
        return 1

    async def get_ups_data(self, ip_address: str = None) -> Dict[str, Any]:
        """Consulta datos detectando Entry/Exit phases independientemente"""
        target_ip = ip_address or self.ip_address
        if not target_ip: return {}
            
        try:
            # 1. Detectar Fases Independientes
            # Input: Checar 3.2.2.0 (L2 vs Freq)
            in_phases = await self._detect_phase_mode(target_ip, "1.3.6.1.4.1.935.1.1.1.3.2.2.0")
            
            # Output: Checar 4.2.2.0 (L2 vs Freq)
            out_phases = await self._detect_phase_mode(target_ip, "1.3.6.1.4.1.935.1.1.1.4.2.2.0")
            
            # 2. Construir Mapa Dinámico
            oids_map = self.oids_common.copy()
            
            # INPUT
            if in_phases == 3:
                oids_map.update(self.oids_input_3ph)
            else:
                oids_map.update(self.oids_input_1ph)
                
            # OUTPUT
            if out_phases == 3:
                oids_map.update(self.oids_output_3ph)
            else:
                oids_map.update(self.oids_output_1ph)

            # 3. Consulta SNMP Standard
            transport = await UdpTransportTarget.create((target_ip, self.port), timeout=self.timeout, retries=self.retries)
            objetos = [ObjectType(ObjectIdentity(oid)) for oid in oids_map.values()]

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

            keys = list(oids_map.keys())
            raw_data = {keys[i]: var[1].prettyPrint() for i, var in enumerate(varBinds)}
            
            # Agregar metadatos
            data = self._format_data(raw_data)
            data['_phases_in'] = in_phases
            data['_phases_out'] = out_phases
            data['_phases'] = out_phases # Legacy compatibility
            
            return data

        except Exception as e:
            logger.exception(f"Fallo crítico {target_ip}: {e}")
            return {}
            
    # --- Métodos de compatibilidad para test_snmp_routes ---
    
    def test_connection(self):
        """Simula test de conexión síncrono"""
        try:
            # Probamos obtener solo el modelo, usando asyncio.run
            res = asyncio.run(self.get_oid_async(self.oids_common['ups_model']))
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
        # Campos que vienen escalados x10 (voltajes, temperatura, frecuencia, corrientes, potencias)
        scaled_fields_x10 = [
            "battery_voltage", "temperature",
            "input_voltage_l1", "input_voltage_l2", "input_voltage_l3", "input_frequency",
            "output_voltage_l1", "output_voltage_l2", "output_voltage_l3", "output_frequency",
            "output_current", "output_current_l1", "output_current_l2", "output_current_l3", 
            "battery_current",
            "active_power", "apparent_power"
        ]
        
        # Campos escalados x100 (Factor de potencia)
        scaled_fields_x100 = ["power_factor"]

        formatted = {}
        for key, val in data.items():
            if val.isdigit() or (val.replace('.', '', 1).isdigit()):
                num_val = float(val)
                if key in scaled_fields_x10:
                    formatted[key] = num_val / 10
                elif key in scaled_fields_x100:
                    formatted[key] = num_val / 100
                else:
                    formatted[key] = num_val
            else:
                formatted[key] = val
        return formatted