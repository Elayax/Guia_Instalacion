# 🗄️ database/

Carpeta central de todo lo relacionado a la base de datos del proyecto **UPS Manager**.

---

## 📁 Estructura

```
database/
├── config/
│   └── config.py              ← Configuración de la app (DATABASE_URL, SECRET_KEY, etc.)
├── connection/
│   └── db_connection.py       ← Pool de conexiones thread-safe para PostgreSQL (psycopg3)
├── migrations/
│   ├── 001_initial_schema.sql ← Esquema inicial: tablas users, equipos, etc.
│   ├── 002_seed_data.sql      ← Datos iniciales / seeds
│   ├── 003_add_monitoring_columns.sql ← Columnas para monitoreo SNMP
│   └── runner.py              ← Ejecutor automático de migraciones al iniciar la app
└── models/
    └── user.py                ← Modelo User para Flask-Login
```

---

## ⚙️ Configuración de conexión

La cadena de conexión se define en `config/config.py` y se puede sobreescribir con la variable de entorno:

```bash
# Ejemplo .env o variable de entorno
DATABASE_URL=postgresql://postgres:Lemonroy%231@localhost:5432/ups_manager
```

**Motor:** PostgreSQL 18  
**Librería:** `psycopg` (psycopg3) + `psycopg_pool`

---

## 🚀 Migraciones

Las migraciones se ejecutan **automáticamente** al iniciar la aplicación (`app/__init__.py`).  
Se trackean en la tabla `schema_migrations` para no aplicarse dos veces.

Para agregar una nueva migración:
1. Crear un archivo `004_nombre_descriptivo.sql` en esta carpeta
2. Reiniciar la aplicación — se aplicará sola

---

## 🔗 Pool de conexiones

El pool se inicializa en `app/__init__.py`:

```python
from database.connection.db_connection import ConnectionPool
pool = ConnectionPool.initialize(DATABASE_URL)
```

Y se usa en cualquier parte del código:

```python
pool = ConnectionPool.get_instance()
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipos")
```

---

## 📝 Notas

- Los archivos en `app/config.py`, `app/db_connection.py` y `app/models/user.py` son **shims de compatibilidad** que re-exportan desde aquí.  
- Si en el futuro se refactorizan los imports del proyecto, se pueden eliminar esos shims.
