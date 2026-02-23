# ---------------------------------------------------------------------------
# COMPAT SHIM: El modelo User ahora vive en database/models/user.py
# Este archivo re-exporta todo para no romper imports existentes.
# ---------------------------------------------------------------------------
from database.models.user import User  # noqa: F401
