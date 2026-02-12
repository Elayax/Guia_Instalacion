@echo off
REM ==================================================================
REM  Iniciador de Aplicación Standalone - Generador de Reportes LBS
REM ==================================================================

title Generador de Reportes LBS - Standalone

echo.
echo ========================================================================
echo   GENERADOR DE REPORTES LBS - APLICACION STANDALONE
echo ========================================================================
echo.
echo   Esta aplicacion corre de manera INDEPENDIENTE del sistema principal
echo   No requiere conexion a base de datos ni configuracion compleja
echo.
echo   Puerto: 5001 (Sistema principal en puerto 5000)
echo   URL: http://localhost:5001
echo.
echo ========================================================================
echo.

REM Verificar que existe el archivo principal
if not exist "app_reportes.py" (
    echo [ERROR] No se encuentra el archivo app_reportes.py
    echo Asegurate de estar en la carpeta Reportes/
    pause
    exit /b 1
)

REM Verificar que existe la carpeta de templates
if not exist "templates\reporte_demo.html" (
    echo [ADVERTENCIA] No se encuentra templates\reporte_demo.html
    echo La aplicacion podria no funcionar correctamente
    echo.
)

REM Crear carpeta output si no existe
if not exist "output" (
    echo Creando carpeta output para PDFs...
    mkdir output
)

echo [INFO] Iniciando servidor Flask en puerto 5001...
echo.
echo ========================================================================
echo   APLICACION CORRIENDO
echo ========================================================================
echo.
echo   -> Abre tu navegador en: http://localhost:5001
echo.
echo   Para detener el servidor presiona Ctrl+C
echo.
echo ========================================================================
echo.

REM Ejecutar la aplicación
python app_reportes.py

REM Si hay error
if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un problema al ejecutar la aplicacion
    echo.
    echo Soluciones posibles:
    echo   1. Instalar dependencias: pip install reportlab flask
    echo   2. Verificar que Python esta instalado
    echo   3. Revisar que no hay otra aplicacion usando el puerto 5001
    echo.
    pause
)
