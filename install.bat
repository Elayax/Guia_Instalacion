@echo off
echo ===================================================
echo   Instalador Automatico para GuiaInstalacion
echo ===================================================
echo.

REM Verificando Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Por favor instala Python 3.10+ desde python.org
    pause
    exit /b
)

echo [OK] Python detectado.
echo.

REM Verificando/Creando Entorno Virtual
if not exist ".venv" (
    echo [INFO] Creando entorno virtual .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Fallo al crear el entorno virtual.
        pause
        exit /b
    )
    echo [OK] Entorno virtual creado.
) else (
    echo [INFO] El entorno virtual .venv ya existe.
)

REM Activando y actualizando pip
echo [INFO] Activando entorno y actualizando pip...
call .venv\Scripts\activate.bat
python.exe -m pip install --upgrade pip

REM Instalando dependencias
echo.
echo [INFO] Instalando dependencias desde requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema instalando las dependencias. Revisa los errores arriba.
    pause
    exit /b
)

echo.
echo ===================================================
echo   INSTALACION COMPLETADA CON EXITO
echo ===================================================
echo.
echo Para iniciar la aplicacion, ejecuta:
echo    .venv\Scripts\activate
echo    python run.py
echo.
pause
