# Guía de Instalación para PC de Trabajo

Esta guía te ayudará a configurar el entorno de desarrollo en tu PC del trabajo para ejecutar el proyecto **GuiaInstalacion**.

## Prerrequisitos

1.  **Python 3.10 o superior**: Asegúrate de tener Python instalado. Puedes verificarlo abriendo una terminal (PowerShell o CMD) y escribiendo:
    ```powershell
    python --version
    ```
    Si no está instalado, descárgalo de [python.org](https://www.python.org/downloads/).

## Instalación Rápida (Recomendado)

Hemos creado un script automático para facilitar la instalación.

1.  Abre la carpeta del proyecto en el Explorador de Archivos.
2.  Haz doble clic en el archivo `install.bat`.
3.  El script verificará Python, creará el entorno virtual `.venv` y descargará todas las dependencias necesarias.

## Instalación Manual

Si prefieres hacerlo manualmente o el script falla, sigue estos pasos:

1.  **Abrir Terminal**: Abre PowerShell en la carpeta del proyecto.
2.  **Crear Entorno Virtual**:
    ```powershell
    python -m venv .venv
    ```
3.  **Activar Entorno Virtual**:
    ```powershell
    .\.venv\Scripts\activate
    ```
    *(Deberías ver `(.venv)` al principio de tu línea de comandos)*
4.  **Instalar Dependencias**:
    ```powershell
    pip install -r requirements.txt
    ```

## Ejecutar la Aplicación

Una vez instalado todo:

1.  Asegúrate de que el entorno virtual esté activado.
2.  Ejecuta:
    ```powershell
    python run.py
    ```
3.  Abre tu navegador en `http://127.0.0.1:5000`.

## Solución de Problemas Comunes

-   **Error de permisos en PowerShell**: Si al activar el entorno te da un error de scripts, ejecuta este comando en PowerShell como Administrador:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
-   **Dependencias faltantes**: Si `run.py` se queja de módulos faltantes, asegúrate de haber ejecutado el paso 4 de la instalación manual y que no hubo errores rojos en la terminal.
