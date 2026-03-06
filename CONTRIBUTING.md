# Guía de Contribución

> UPS Manager LBS — Cómo colaborar en el proyecto

[← Volver al README](README.md)

---

## Configurar Entorno de Desarrollo

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_ORG/Guia_Instalacion.git
cd Guia_Instalacion

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores locales

# 5. Ejecutar
python run.py
```

Para más detalle, consulta [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Estrategia de Ramas Git

| Rama | Propósito |
|---|---|
| `main` | Rama principal estable |
| `produccion` | Rama de producción desplegada |
| `nombre_Dev` | Rama de desarrollo personal (ej: `Samuel_Dev`) |
| `feature/descripcion` | Nueva funcionalidad |
| `fix/descripcion` | Corrección de bug |

### Flujo de trabajo

1. Crea tu rama desde `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/mi-nueva-funcionalidad
   ```
2. Desarrolla y haz commits descriptivos
3. Abre un Pull Request hacia `main`
4. Espera revisión antes de hacer merge

---

## Estilo de Código

- **Idioma:** Todo el código, variables, comentarios y documentación en **español**, excepto palabras reservadas de Python/Flask
- **Formato:** Seguir [PEP 8](https://peps.python.org/pep-0008/)
- **Indentación:** 4 espacios (nunca tabs)
- **Nombrado:**
  - Variables y funciones: `snake_case` — ej: `obtener_usuario_por_id`
  - Clases: `PascalCase` — ej: `GestorDB`, `ReportePDF`
  - Constantes: `UPPER_SNAKE_CASE` — ej: `SECCIONES_DISPONIBLES`
- **Imports:** Agrupar en orden: stdlib, terceros, locales

---

## Cómo Agregar un Nuevo Blueprint

1. Crea el archivo en `app/routes/mi_modulo.py`:

```python
from flask import Blueprint, render_template
from flask_login import login_required
from app.permisos import permiso_requerido

mi_modulo_bp = Blueprint('mi_modulo', __name__)

@mi_modulo_bp.route('/mi-ruta')
@login_required
@permiso_requerido('seccion_correspondiente')
def mi_vista():
    return render_template('mi_modulo/index.html')
```

2. Registra el blueprint en `app/__init__.py`:

```python
from app.routes.mi_modulo import mi_modulo_bp
app.register_blueprint(mi_modulo_bp)
```

3. Si necesitas un nuevo permiso, agrégalo a `SECCIONES_DISPONIBLES` en `app/permisos.py` y crea una migración SQL.

---

## Cómo Agregar una Migración

1. Crea un archivo SQL en `database/migrations/` siguiendo la convención `NNN_nombre.sql`:

```sql
-- database/migrations/009_mi_cambio.sql
ALTER TABLE mi_tabla ADD COLUMN nuevo_campo TEXT;
```

2. Las migraciones se ejecutan automáticamente al iniciar la aplicación
3. Usa `IF NOT EXISTS` para hacerlas idempotentes
4. Nunca modifiques una migración ya aplicada — crea una nueva

---

## Cómo Agregar un Permiso

1. Agrega la sección a `SECCIONES_DISPONIBLES` en `app/permisos.py`
2. Crea una migración para asignar el permiso a usuarios existentes:

```sql
-- database/migrations/010_permiso_nuevo.sql
INSERT INTO user_permissions (user_id, seccion, permitido)
SELECT id, 'mi_nuevo_permiso', TRUE FROM users
ON CONFLICT (user_id, seccion) DO NOTHING;
```

3. Usa el decorador `@permiso_requerido('mi_nuevo_permiso')` en las rutas correspondientes

---

## Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app

# Un archivo específico
pytest tests/test_calculos.py -v
```

---

## Pull Requests

- Título corto y descriptivo (< 70 caracteres)
- Descripción con:
  - Qué cambia y por qué
  - Cómo probarlo
  - Capturas de pantalla si hay cambios visuales
- Asegúrate de que los tests pasen antes de solicitar revisión
- Un PR por funcionalidad o corrección — evita PRs gigantes
