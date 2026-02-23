import logging
import os
import threading
from contextlib import contextmanager
from urllib.parse import urlparse, unquote

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool as Psycopg3Pool

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Pool de conexiones thread-safe para PostgreSQL usando psycopg3."""

    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def _parse_db_url(database_url):
        """Parsea la DATABASE_URL en conninfo string para psycopg3."""
        parsed = urlparse(database_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        dbname = unquote(parsed.path.lstrip('/')) if parsed.path else ''
        user = unquote(parsed.username) if parsed.username else ''
        password = unquote(parsed.password) if parsed.password else ''
        return f"host={host} port={port} dbname={dbname} user={user} password={password}"

    def __init__(self, database_url, minconn=2, maxconn=10):
        self.database_url = database_url
        conninfo = self._parse_db_url(database_url)
        self._pool = Psycopg3Pool(
            conninfo,
            min_size=minconn,
            max_size=maxconn,
            open=True,
        )
        logger.info("Pool de conexiones PostgreSQL inicializado (min=%d, max=%d)", minconn, maxconn)

    @classmethod
    def initialize(cls, database_url, minconn=2, maxconn=10):
        """Inicializa el singleton del pool."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
            cls._instance = cls(database_url, minconn, maxconn)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Obtiene la instancia singleton del pool."""
        if cls._instance is None:
            raise RuntimeError(
                "ConnectionPool no inicializado. Llamar initialize() primero."
            )
        return cls._instance

    @contextmanager
    def get_connection(self):
        """Context manager que provee una conexion con auto-commit/rollback."""
        with self._pool.connection() as conn:
            conn.autocommit = False
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def get_row_factory(self):
        """Retorna el row factory para obtener diccionarios."""
        return dict_row

    def close(self):
        """Cierra todas las conexiones del pool."""
        if self._pool:
            self._pool.close()
            logger.info("Pool de conexiones cerrado")
