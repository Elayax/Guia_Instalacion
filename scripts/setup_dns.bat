@echo off
REM ============================================================
REM  Configurar DNS local para UPS Manager
REM  Ejecutar como Administrador
REM ============================================================

echo.
echo  UPS Manager - Configuracion DNS
echo  ================================
echo.
echo  1) Configurar como SERVIDOR (esta es la maquina que corre la app)
echo  2) Configurar como CLIENTE  (esta maquina accede a la app)
echo  3) DESINSTALAR DNS
echo.

set /p opcion="  Selecciona una opcion (1/2/3): "

if "%opcion%"=="1" (
    powershell -ExecutionPolicy Bypass -File "%~dp0setup_dns.ps1" -Mode servidor
) else if "%opcion%"=="2" (
    set /p serverip="  Ingresa la IP del servidor (ej: 192.168.1.100): "
    powershell -ExecutionPolicy Bypass -File "%~dp0setup_dns.ps1" -Mode cliente -ServerIP %serverip%
) else if "%opcion%"=="3" (
    powershell -ExecutionPolicy Bypass -File "%~dp0setup_dns.ps1" -Mode desinstalar
) else (
    echo  Opcion no valida.
)

echo.
pause
