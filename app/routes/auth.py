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
