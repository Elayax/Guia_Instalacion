import logging
import threading
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Pool de conexiones thread-safe para PostgreSQL."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self, database_url, minconn=2, maxconn=10):
        self.database_url = database_url
        self._pool = pool.ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=database_url
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
        """Context manager que provee una conexión con auto-commit/rollback."""
        conn = self._pool.getconn()
        conn.autocommit = False
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def get_cursor_factory(self):
        """Retorna el cursor factory para obtener diccionarios."""
        return RealDictCursor

    def close(self):
        """Cierra todas las conexiones del pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Pool de conexiones cerrado")
