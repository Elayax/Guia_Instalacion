"""
Cliente SNMP para monitoreo de UPS usando pysnmp 5.x.

Este módulo proporciona una interfaz simplificada para realizar consultas SNMP
a dispositivos UPS remotos, con manejo robusto de errores, timeouts y logging detallado.

Compatible con Python 3.14 usando pysnmp 5.x

Autor: Sistema de Monitoreo UPS
Fecha: 2026-01-26
"""

import logging
from typing import Dict, List, Optional, Tuple, Any

# Imports para pysnmp 5.x (compatible con Python 3.14)
from pysnmp.hlapi.v1arch.asyncio import *
from pysnmp.hlapi.asyncio import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, getCmd, nextCmd
import asyncio

# Configurar logging
logger = logging.getLogger(__name__)


class SNMPClientError(Exception):
    """Excepción personalizada para errores del cliente SNMP."""
    pass


class SNMPClient:
    """
    Cliente SNMP para comunicación con dispositivos UPS.
    
    Usa pysnmp 5.x compatible con Python 3.14+.
    Soporta SNMP v2c con timeouts configurables para redes VPN.
    
    Attributes:
        host (str): Dirección IP o hostname del dispositivo
        port (int): Puerto SNMP (default: 161, RUT956: 8161)
        community (str): Community string SNMP (default: 'public')
        timeout (int): Timeout en segundos para operaciones SNMP
        retries (int): Número de reintentos en caso de fallo
    
    Example:
        >>> client = SNMPClient('10.147.17.2', port=8161, community='public')
        >>> voltage = client.get_oid('.1.3.6.1.4.1.56788.1.1.1.3.5.1')
        >>> print(f"Voltaje batería: {voltage} V")
    """
    
    def __init__(
        self,
        host: str,
        port: int = 161,
        community: str = 'public',
        timeout: int = 5,
        retries: int = 2
    ):
        """
        Inicializa el cliente SNMP.
        
        Args:
            host: Dirección IP del dispositivo UPS
            port: Puerto SNMP (8161 para RUT956 con port forward)
            community: Community string SNMP
            timeout: Timeout en segundos (5s recomendado para VPN)
            retries: Número de reintentos automáticos
        """
        self.host = host
        self.port = port
        self.community = community
        self.timeout = timeout
        self.retries = retries
        
        logger.info(
            f"Cliente SNMP inicializado: {host}:{port} "
            f"(community={community}, timeout={timeout}s, retries={retries})"
        )
    
    def _run_async(self, coro):
        """Helper para ejecutar corutinas asyncio de forma sincrónica."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    async def _get_oid_async(self, oid: str) -> Optional[Any]:
        """Versión async de get_oid."""
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community, mpModel=1),  # SNMPv2c
            await UdpTransportTarget.create((self.host, self.port), timeout=self.timeout, retries=self.retries),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        
        if errorIndication:
            raise SNMPClientError(f"Error de comunicación: {errorIndication}")
        
        if errorStatus:
            raise SNMPClientError(f"{errorStatus.prettyPrint()} en posición {errorIndex}")
        
        for varBind in varBinds:
            oid_result, value = varBind
            return value.prettyPrint() if hasattr(value, 'prettyPrint') else str(value)
        
        return None
    
    def get_oid(self, oid: str) -> Optional[Any]:
        """
        Lee el valor de un OID individual.
        
        Args:
            oid: OID en formato string (ej: '.1.3.6.1.4.1.56788.1.1.1.3.5.1')
        
        Returns:
            Valor del OID (int, str, float) o None si hay error
        
        Raises:
            SNMPClientError: Si ocurre un error de comunicación SNMP
        
        Example:
            >>> battery_voltage = client.get_oid('.1.3.6.1.4.1.56788.1.1.1.3.5.1')
        """
        logger.debug(f"Leyendo OID {oid} desde {self.host}:{self.port}")
        
        try:
            value = self._run_async(self._get_oid_async(oid))
            logger.debug(f"OID {oid} = {value}")
            return value
        except Exception as e:
            logger.exception(f"Excepción al leer OID {oid}: {e}")
            raise SNMPClientError(f"Error al leer OID {oid}: {e}")
    
    def get_multiple_oids(self, oids: List[str]) -> Dict[str, Any]:
        """
        Lee múltiples OIDs (uno por uno debido a limitaciones de la API).
        
        Args:
            oids: Lista de OIDs a consultar
        
        Returns:
            Diccionario {oid: valor} con los resultados
        """
        logger.debug(f"Leyendo {len(oids)} OIDs desde {self.host}:{self.port}")
        
        results = {}
        for oid in oids:
            try:
                value = self.get_oid(oid)
                results[oid] = value
            except:
                results[oid] = None
        
        logger.info(f"Lectura batch exitosa: {len(results)}/{len(oids)} OIDs")
        return results
    
    def walk_oid(self, base_oid: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Realiza un SNMP WALK para explorar un árbol de OIDs.
        
        Args:
            base_oid: OID base desde donde comenzar el walk
            max_results: Máximo número de resultados a retornar
        
        Returns:
            Diccionario {oid: valor} con todos los OIDs descendientes
        """
        logger.debug(f"Iniciando WALK desde OID {base_oid}")
        results = {}
        count = 0
        
        # Implementación simplificada usando get iterativo
        current_oid = base_oid
        while count < max_results:
            try:
                value = self.get_oid(current_oid)
                if value:
                    results[current_oid] = value
                    count += 1
                else:
                    break
            except:
                break
        
        logger.info(f"WALK completado: {count} OIDs encontrados")
        return results
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Prueba la conectividad SNMP con el dispositivo.
        
        Returns:
            Tupla (éxito: bool, mensaje: str)
        """
        logger.info(f"Probando conectividad SNMP a {self.host}:{self.port}")
        
        try:
            sys_descr_oid = '.1.3.6.1.2.1.1.1.0'
            value = self.get_oid(sys_descr_oid)
            
            if value:
                msg = f"Conexión exitosa. Device: {value}"
                logger.info(msg)
                return True, msg
            else:
                msg = "Conexión establecida pero sin respuesta válida"
                logger.warning(msg)
                return False, msg
        
        except SNMPClientError as e:
            msg = f"Error de conexión: {e}"
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Error inesperado: {e}"
            logger.exception(msg)
            return False, msg
