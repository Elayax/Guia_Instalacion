import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt

from app.models.user import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Usuario y contraseña son requeridos.', 'danger')
            return render_template('login.html')

        db = current_app.db
        user_row = db.obtener_usuario_por_username(username)

        if user_row and bcrypt.checkpw(
            password.encode('utf-8'),
            user_row['password_hash'].encode('utf-8')
        ):
            user = User.from_row(user_row)
            login_user(user, remember=True)
            logger.info("Usuario '%s' inició sesión", username)

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.dashboard'))
        else:
            logger.warning("Intento de login fallido para usuario: %s", username)
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logger.info("Usuario '%s' cerró sesión", current_user.username)
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    if request.method == 'POST':
        actual = request.form.get('password_actual', '').strip()
        nueva = request.form.get('password_nueva', '').strip()
        confirmar = request.form.get('password_confirmar', '').strip()

        if not all([actual, nueva, confirmar]):
            flash('Todos los campos son requeridos.', 'danger')
        elif nueva != confirmar:
            flash('La nueva contraseña no coincide con la confirmación.', 'danger')
        elif len(nueva) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', 'danger')
        else:
            db = current_app.db
            user_row = db.obtener_usuario_por_id(current_user.id)
            if user_row and bcrypt.checkpw(actual.encode('utf-8'), user_row['password_hash'].encode('utf-8')):
                new_hash = bcrypt.hashpw(nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                if db.actualizar_password(current_user.id, new_hash):
                    logger.info("Usuario '%s' cambió su contraseña", current_user.username)
                    flash('Contraseña actualizada correctamente.', 'success')
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    flash('Error al actualizar la contraseña. Intente de nuevo.', 'danger')
            else:
                flash('Contraseña actual incorrecta.', 'danger')

    return render_template('cambiar_password.html')
