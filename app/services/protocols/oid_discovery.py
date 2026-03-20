"""
Servicio de auto-discovery de OIDs.
Wrapper sobre SNMPScanner para uso desde la API REST.
"""

import asyncio
import logging
from app.services.protocols.snmp_scanner import SNMPScanner

logger = logging.getLogger(__name__)


class OIDDiscoveryService:
    def __init__(self):
        pass

    async def discover(self, ip: str, port: int = 161, community: str = 'public') -> dict:
        """
        Ejecuta auto-detección SNMP completa.
        Retorna dict con OIDs encontrados y tipo recomendado.
        """
        scanner = SNMPScanner(ip=ip, port=port, timeout=3)

        # Si se proporcionó community específica, usarla primero
        if community != 'public':
            scanner.COMMON_COMMUNITIES = [community] + scanner.COMMON_COMMUNITIES

        config = await scanner.auto_detect()

        # Mapear ups_type a nuestro formato interno
        recommended = 'invt_enterprise'
        caps = config.get('capabilities', [])
        if 'ups_mib' in caps and 'invt_oids' in caps:
            recommended = 'hybrid'
        elif 'ups_mib' in caps:
            recommended = 'ups_mib_standard'
        elif 'invt_oids' in caps:
            recommended = 'invt_enterprise'

        oids_found = []
        for oid in config.get('oids_working', []):
            oids_found.append({
                'oid': oid,
                'value': config.get('device_info', {}).get(oid, '')
            })

        return {
            'success': config.get('success', False),
            'ip': ip,
            'port': port,
            'community': config.get('community', community),
            'snmp_version': config.get('version', 'Unknown'),
            'recommended_type': recommended,
            'ups_type_detected': config.get('ups_type', 'Unknown'),
            'device_info': config.get('device_info', {}),
            'oids_found': oids_found,
            'capabilities': caps,
            'log': config.get('results', scanner.results) if hasattr(scanner, 'results') else [],
        }
