# ---------------------------------------------------------------------------
# COMPAT SHIM: La configuración ahora vive en database/config/config.py
# Este archivo re-exporta todo para no romper imports existentes.
# ---------------------------------------------------------------------------
from database.config.config import BaseConfig, DevelopmentConfig, ProductionConfig, config_map  # noqa: F401
