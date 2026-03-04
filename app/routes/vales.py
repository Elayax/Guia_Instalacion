"""
Rutas para Vales de Entrega de Herramienta
Control de herramientas y equipos entregados a técnicos de campo
"""

from flask import Blueprint, render_template
from flask_login import login_required
from app.permisos import permiso_requerido

vales_bp = Blueprint('vales', __name__)


@vales_bp.route('/vales')
@login_required
@permiso_requerido('vales')
def vales():
    return render_template('vales.html')


@vales_bp.route('/vales/historial')
@login_required
@permiso_requerido('vales')
def vales_historial():
    return render_template('vales_historial.html')
