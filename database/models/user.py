from flask_login import UserMixin


class User(UserMixin):
    """Modelo de usuario para autenticación con Flask-Login."""

    def __init__(self, id, username, password_hash, role='user', created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        """Crea un User desde un diccionario de fila de BD."""
        if row is None:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            role=row.get('role', 'user'),
            created_at=row.get('created_at')
        )
