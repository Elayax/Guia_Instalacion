from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Debe iniciar sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()
