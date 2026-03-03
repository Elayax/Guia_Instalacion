import logging
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import bcrypt

from app.permisos import SECCIONES_DISPONIBLES, SECCIONES_NOMBRES

logger = logging.getLogger(__name__)

user_mgmt_bp = Blueprint('user_mgmt', __name__)


def admin_required(f):
    """Decorador que restringe acceso solo a administradores."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Acceso denegado. Solo administradores.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated


@user_mgmt_bp.route('/gestionar-cuentas')
@admin_required
def gestionar_cuentas():
    db = current_app.db
    usuarios = db.obtener_todos_usuarios_con_permisos()
    return render_template('gestionar_cuentas.html',
                           usuarios=usuarios,
                           secciones=SECCIONES_DISPONIBLES,
                           secciones_nombres=SECCIONES_NOMBRES)


@user_mgmt_bp.route('/gestionar-cuentas/crear', methods=['POST'])
@admin_required
def crear_usuario():
    db = current_app.db
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'user')

    if not username or not password:
        flash('Usuario y contraseña son requeridos.', 'danger')
        return redirect(url_for('user_mgmt.gestionar_cuentas'))

    if len(password) < 4:
        flash('La contraseña debe tener al menos 4 caracteres.', 'danger')
        return redirect(url_for('user_mgmt.gestionar_cuentas'))

    if role not in ('admin', 'user'):
        role = 'user'

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_id = db.crear_usuario(username, password_hash, role)

    if user_id:
        permisos = {}
        for seccion in SECCIONES_DISPONIBLES:
            permisos[seccion] = request.form.get(f'perm_{seccion}') == 'on'
        db.establecer_permisos_usuario(user_id, permisos)
        flash(f'Usuario "{username}" creado correctamente.', 'success')
    else:
        flash(f'Error al crear usuario "{username}". Puede que ya exista.', 'danger')

    return redirect(url_for('user_mgmt.gestionar_cuentas'))


@user_mgmt_bp.route('/gestionar-cuentas/reset-password', methods=['POST'])
@admin_required
def reset_password():
    db = current_app.db
    user_id = request.form.get('user_id', type=int)
    new_password = request.form.get('new_password', '').strip()

    if not user_id or not new_password:
        flash('ID de usuario y nueva contraseña son requeridos.', 'danger')
        return redirect(url_for('user_mgmt.gestionar_cuentas'))

    if len(new_password) < 4:
        flash('La contraseña debe tener al menos 4 caracteres.', 'danger')
        return redirect(url_for('user_mgmt.gestionar_cuentas'))

    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if db.actualizar_password(user_id, password_hash):
        flash('Contraseña reseteada correctamente.', 'success')
    else:
        flash('Error al resetear contraseña.', 'danger')

    return redirect(url_for('user_mgmt.gestionar_cuentas'))


@user_mgmt_bp.route('/gestionar-cuentas/permisos', methods=['POST'])
@admin_required
def actualizar_permisos():
    db = current_app.db
    user_id = request.form.get('user_id', type=int)

    if not user_id:
        flash('ID de usuario requerido.', 'danger')
        return redirect(url_for('user_mgmt.gestionar_cuentas'))

    permisos = {}
    for seccion in SECCIONES_DISPONIBLES:
        permisos[seccion] = request.form.get(f'perm_{seccion}') == 'on'

    if db.establecer_permisos_usuario(user_id, permisos):
        flash('Permisos actualizados correctamente.', 'success')
    else:
        flash('Error al actualizar permisos.', 'danger')

    return redirect(url_for('user_mgmt.gestionar_cuentas'))


@user_mgmt_bp.route('/gestionar-cuentas/eliminar', methods=['POST'])
@admin_required
def eliminar_usuario():
    db = current_app.db
    user_id = request.form.get('user_id', type=int)

    if not user_id:
        flash('ID de usuario requerido.', 'danger')
        return redirect(url_for('user_mgmt.gestionar_cuentas'))

    if user_id == current_user.id:
        flash('No puede eliminarse a sí mismo.', 'danger')
        return redirect(url_for('user_mgmt.gestionar_cuentas'))

    if db.eliminar_usuario(user_id):
        flash('Usuario eliminado correctamente.', 'success')
    else:
        flash('Error al eliminar usuario.', 'danger')

    return redirect(url_for('user_mgmt.gestionar_cuentas'))
