<#
.SYNOPSIS
    Configura el DNS local para UPS Manager (apa.lbs.local)

.DESCRIPTION
    Este script agrega una entrada al archivo hosts de Windows para que
    el navegador resuelva el dominio del sistema sin necesidad de un
    servidor DNS externo.

    DEBE ejecutarse como Administrador.

.PARAMETER Mode
    "servidor" — Configura esta maquina como el servidor (127.0.0.1)
    "cliente"  — Configura esta maquina como cliente (apunta a la IP del servidor)

.PARAMETER ServerIP
    (Solo modo cliente) La IP del servidor en la red local.
    Ejemplo: 192.168.1.100

.PARAMETER Domain
    Dominio a configurar. Por defecto: apa.lbs.local

.PARAMETER Port
    Puerto de la aplicacion. Por defecto: 5000

.EXAMPLE
    # En la laptop/servidor:
    .\setup_dns.ps1 -Mode servidor

    # En las maquinas de los companeros:
    .\setup_dns.ps1 -Mode cliente -ServerIP 192.168.1.100

    # Con dominio personalizado:
    .\setup_dns.ps1 -Mode servidor -Domain ups.miempresa.local

.EXAMPLE
    # Desinstalar la entrada DNS:
    .\setup_dns.ps1 -Mode desinstalar
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("servidor", "cliente", "desinstalar")]
    [string]$Mode,

    [string]$ServerIP = "",

    [string]$Domain = "apa.lbs.local",

    [int]$Port = 5000
)

# --- Verificar permisos de administrador ---
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "  ERROR: Este script requiere permisos de Administrador." -ForegroundColor Red
    Write-Host "  Haz clic derecho en PowerShell -> 'Ejecutar como administrador'" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$hostsFile = "$env:SystemRoot\System32\drivers\etc\hosts"
$marker = "# UPS-Manager DNS"
$currentContent = Get-Content $hostsFile -Raw

# --- Funcion para limpiar entradas anteriores ---
function Remove-DnsEntry {
    $lines = Get-Content $hostsFile
    $cleanLines = $lines | Where-Object { $_ -notmatch "UPS-Manager DNS" -and $_ -notmatch $Domain }
    Set-Content -Path $hostsFile -Value ($cleanLines -join "`n") -NoNewline
}

# --- Modo desinstalar ---
if ($Mode -eq "desinstalar") {
    Remove-DnsEntry
    Write-Host ""
    Write-Host "  DNS eliminado. El dominio '$Domain' ya no resolvera localmente." -ForegroundColor Green
    Write-Host "  Ejecuta: ipconfig /flushdns" -ForegroundColor Yellow
    Write-Host ""
    ipconfig /flushdns | Out-Null
    exit 0
}

# --- Determinar IP ---
if ($Mode -eq "servidor") {
    $ip = "127.0.0.1"

    # Mostrar IPs de red local para que las comparta con clientes
    Write-Host ""
    Write-Host "  === Configuracion DNS - Modo SERVIDOR ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  IPs de esta maquina en la red local:" -ForegroundColor Yellow

    Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -ne "127.0.0.1" -and $_.PrefixOrigin -ne "WellKnown" } |
        ForEach-Object {
            Write-Host "    -> $($_.IPAddress)  ($($_.InterfaceAlias))" -ForegroundColor White
        }

    Write-Host ""
    Write-Host "  Comparte una de estas IPs con tus companeros para que ejecuten:" -ForegroundColor Yellow
    Write-Host "    .\setup_dns.ps1 -Mode cliente -ServerIP <TU_IP>" -ForegroundColor White
    Write-Host ""
}
elseif ($Mode -eq "cliente") {
    if ([string]::IsNullOrWhiteSpace($ServerIP)) {
        Write-Host ""
        Write-Host "  ERROR: En modo cliente necesitas indicar la IP del servidor." -ForegroundColor Red
        Write-Host "  Ejemplo: .\setup_dns.ps1 -Mode cliente -ServerIP 192.168.1.100" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    $ip = $ServerIP

    Write-Host ""
    Write-Host "  === Configuracion DNS - Modo CLIENTE ===" -ForegroundColor Cyan
    Write-Host ""
}

# --- Limpiar entradas previas y agregar nueva ---
Remove-DnsEntry

$entry = "`n$ip`t$Domain`t$marker"
Add-Content -Path $hostsFile -Value $entry

# Limpiar cache DNS de Windows
ipconfig /flushdns | Out-Null

# --- Resumen ---
Write-Host "  Dominio:  $Domain" -ForegroundColor Green
Write-Host "  Apunta a: $ip" -ForegroundColor Green
Write-Host "  URL:      http://$Domain`:$Port" -ForegroundColor Green
Write-Host ""
Write-Host "  Cache DNS limpiada." -ForegroundColor DarkGray
Write-Host ""

# --- Verificar conectividad (solo cliente) ---
if ($Mode -eq "cliente") {
    Write-Host "  Verificando conectividad con el servidor..." -ForegroundColor Yellow
    $testResult = Test-Connection -ComputerName $ServerIP -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($testResult) {
        Write-Host "  Servidor alcanzable en $ServerIP" -ForegroundColor Green
    } else {
        Write-Host "  AVISO: No se pudo alcanzar $ServerIP. Verifica que:" -ForegroundColor Red
        Write-Host "    1. El servidor este encendido y conectado a la red" -ForegroundColor Yellow
        Write-Host "    2. El firewall permita conexiones en el puerto $Port" -ForegroundColor Yellow
    }
    Write-Host ""
}

# --- Instruccion de firewall (solo servidor) ---
if ($Mode -eq "servidor") {
    Write-Host "  FIREWALL: Si tus companeros no pueden conectarse, ejecuta:" -ForegroundColor Yellow
    Write-Host "    netsh advfirewall firewall add rule name=""UPS-Manager"" dir=in action=allow protocol=TCP localport=$Port" -ForegroundColor White
    Write-Host ""
}

Write-Host "  Listo! Abre el navegador y ve a: http://$Domain`:$Port" -ForegroundColor Cyan
Write-Host ""
