import logging
import asyncio
from typing import Dict, Any, List

from pysnmp.hlapi.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, get_cmd
)

from app.utils.ups_oids import (
    UPS_OIDS, SCALE_FACTORS, UPS_INTERNAL_TEMP_OID,
    FAST_POLL_GROUPS, SLOW_POLL_GROUPS
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 25


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
        # OIDs legacy para compatibilidad con NetAgent/Dragon Power
        self._legacy_oids_map = {
            "ups_model": "1.3.6.1.4.1.935.1.1.1.1.1.2.0",
            "battery_voltage": "1.3.6.1.4.1.935.1.1.1.2.2.2.0",
            "battery_capacity": "1.3.6.1.4.1.935.1.1.1.2.2.1.0",
            "input_voltage": "1.3.6.1.4.1.935.1.1.1.3.2.1.0",
            "output_voltage": "1.3.6.1.4.1.935.1.1.1.4.2.1.0",
            "output_load": "1.3.6.1.4.1.935.1.1.1.4.2.3.0",
            "temperature": "1.3.6.1.4.1.935.1.1.1.2.2.3.0"
        }

    async def get_ups_data_full(self, ip_address: str = None, groups: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Consulta múltiples grupos de OIDs del UPS INVT y retorna datos organizados por grupo.

        Args:
            ip_address: IP del dispositivo (o usa self.ip_address)
            groups: Lista de nombres de grupo a consultar. Si None, usa FAST_POLL_GROUPS.

        Returns:
            Dict anidado: {group_name: {field_name: scaled_value}}
        """
        target_ip = ip_address or self.ip_address
        if not target_ip:
            return {}

        if groups is None:
            groups = list(FAST_POLL_GROUPS)

        # Construir mapeo plano: oid_string -> (group_name, field_name)
        oid_to_group = {}
        for group_name in groups:
            group = UPS_OIDS.get(group_name, {})
            for field_name, oid in group.items():
                oid_to_group[oid] = (group_name, field_name)

        # Agregar OID de temperatura interna (no pertenece a un grupo dict)
        if any(g in groups for g in ['data_battery', 'data_input', 'data_output']):
            oid_to_group[UPS_INTERNAL_TEMP_OID] = ('internal', 'temperature')

        all_oids = list(oid_to_group.keys())
        if not all_oids:
            return {}

        # Consultar en lotes
        raw_results = await self._batch_get(target_ip, all_oids)

        # Organizar resultados por grupo y aplicar escala
        result = {}
        for oid, raw_val in raw_results.items():
            if oid not in oid_to_group:
                continue
            group_name, field_name = oid_to_group[oid]
            if group_name not in result:
                result[group_name] = {}

            # Aplicar escala
            try:
                num_val = float(raw_val)
                scale = SCALE_FACTORS.get(oid, 1.0)
                result[group_name][field_name] = round(num_val * scale, 2)
            except (ValueError, TypeError):
                result[group_name][field_name] = raw_val

        return result

    async def _batch_get(self, ip: str, oids: List[str]) -> Dict[str, str]:
        """Ejecuta get_cmd en lotes de BATCH_SIZE OIDs."""
        all_results = {}

        try:
            transport = await UdpTransportTarget.create(
                (ip, self.port), timeout=self.timeout, retries=self.retries
            )
        except Exception as e:
            logger.error(f"Error creando transporte UDP a {ip}:{self.port}: {e}")
            return {}

        for i in range(0, len(oids), BATCH_SIZE):
            batch_oids = oids[i:i + BATCH_SIZE]
            objetos = [ObjectType(ObjectIdentity(oid)) for oid in batch_oids]

            try:
                errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
                    self.engine,
                    CommunityData(self.community, mpModel=1),
                    transport,
                    ContextData(),
                    *objetos
                )

                if errorIndication:
                    logger.warning(f"SNMP error (batch {i // BATCH_SIZE}) en {ip}: {errorIndication}")
                    continue
                if errorStatus:
                    logger.warning(f"SNMP status error (batch {i // BATCH_SIZE}) en {ip}: {errorStatus}")
                    continue

                for idx, var in enumerate(varBinds):
                    oid_str = batch_oids[idx]
                    val_str = var[1].prettyPrint()
                    # Ignorar valores tipo noSuchInstance o noSuchObject
                    if 'noSuch' not in val_str:
                        all_results[oid_str] = val_str

            except Exception as e:
                logger.error(f"Error en batch SNMP {i // BATCH_SIZE} para {ip}: {e}")
                continue

        return all_results

    # --- Método legacy para compatibilidad ---

    async def get_ups_data(self, ip_address: str = None) -> Dict[str, Any]:
        """Consulta los 7 OIDs legacy del UPS (NetAgent/Dragon Power)."""
        target_ip = ip_address or self.ip_address
        if not target_ip:
            return {}

        try:
            transport = await UdpTransportTarget.create(
                (target_ip, self.port), timeout=self.timeout, retries=self.retries
            )
            objetos = [ObjectType(ObjectIdentity(oid)) for oid in self._legacy_oids_map.values()]

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

            raw_data = {
                list(self._legacy_oids_map.keys())[i]: var[1].prettyPrint()
                for i, var in enumerate(varBinds)
            }
            return self._format_data_legacy(raw_data)

        except Exception as e:
            logger.exception(f"Fallo crítico consultando UPS {target_ip}: {e}")
            return {}

    # --- Métodos de compatibilidad para test_snmp_routes ---

    def test_connection(self):
        """Simula test de conexión síncrono."""
        try:
            res = asyncio.run(self.get_oid_async(UPS_OIDS['info']['model']))
            if res:
                return True, "Conexión exitosa"
            else:
                return False, "No se recibió respuesta"
        except Exception as e:
            return False, str(e)

    def get_oid(self, oid):
        """Wrapper síncrono para obtener un OID."""
        return asyncio.run(self.get_oid_async(oid))

    async def get_oid_async(self, oid: str, ip_address: str = None):
        target_ip = ip_address or self.ip_address
        if not target_ip:
            raise SNMPClientError("IP no especificada")

        try:
            transport = await UdpTransportTarget.create(
                (target_ip, self.port), timeout=self.timeout, retries=self.retries
            )
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
        except SNMPClientError:
            raise
        except Exception as e:
            logger.error(f"Error get_oid: {e}")
            return None

    def _format_data_legacy(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Limpia y escala los valores recibidos (formato legacy)."""
        formatted = {}
        for key, val in data.items():
            if val.isdigit() or (val.replace('.', '', 1).isdigit()):
                num_val = float(val)
                if key in ["battery_voltage", "input_voltage", "output_voltage", "temperature"]:
                    formatted[key] = num_val / 10
                else:
                    formatted[key] = num_val
            else:
                formatted[key] = val
        return formatted
