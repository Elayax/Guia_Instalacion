# ---------------------------------------------------------------------------
# COMPAT SHIM: El pool de conexiones ahora vive en database/connection/db_connection.py
# Este archivo re-exporta todo para no romper imports existentes.
# ---------------------------------------------------------------------------
from database.connection.db_connection import ConnectionPool  # noqa: F401
