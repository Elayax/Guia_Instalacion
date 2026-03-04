"""Utilidades de permisos granulares por usuario."""
from functools import wraps
from flask import abort, current_app
from flask_login import current_user

SECCIONES_DISPONIBLES = ['tablero', 'calculos', 'guia_rapida', 'scada', 'datos', 'ejemplo_pdf', 'publicar_pdf', 'vales']

SECCIONES_NOMBRES = {
    'tablero': 'Tablero',
    'calculos': 'Cálculos',
    'guia_rapida': 'Guía Manual',
    'scada': 'SCADA',
    'datos': 'Datos',
    'ejemplo_pdf': 'Ejemplo PDF',
    'publicar_pdf': 'Publicar PDF',
    'vales': 'Vales Herramienta',
}


def obtener_permisos_usuario_actual():
    """Devuelve dict de permisos del usuario actual. Admins siempre tienen todo."""
    if not current_user.is_authenticated:
        return {}
    if current_user.role == 'admin':
        return {s: True for s in SECCIONES_DISPONIBLES}
    return getattr(current_user, 'permisos', {})


def tiene_permiso(seccion):
    """Retorna True si el usuario actual tiene permiso para la sección."""
    if not current_user.is_authenticated:
        return False
    if current_user.role == 'admin':
        return True
    permisos = getattr(current_user, 'permisos', {})
    return permisos.get(seccion, True)


def permiso_requerido(seccion):
    """Decorador que aborta con 403 si el usuario no tiene permiso."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not tiene_permiso(seccion):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
