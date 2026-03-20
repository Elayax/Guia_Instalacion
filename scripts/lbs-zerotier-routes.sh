#!/bin/bash
# Rutas ZeroTier persistentes para LBS Monitor
# Agrega rutas estáticas para cada subnet de sitio a través del router ZT correspondiente.
# Ejecutar después de que ZeroTier esté activo.
#
# Uso: sudo bash lbs-zerotier-routes.sh
# O instalar como servicio: lbs-zerotier-routes.service

set -euo pipefail

ZT_IFACE=$(ip link show | grep -oP 'zt\w+' | head -1)

if [ -z "$ZT_IFACE" ]; then
    echo "ERROR: No se encontró interfaz ZeroTier activa"
    exit 1
fi

echo "Interfaz ZeroTier: $ZT_IFACE"

# Sitio 03: 192.168.3.0/24 via router 10.216.124.130
ip route replace 192.168.3.0/24 via 10.216.124.130 dev "$ZT_IFACE" 2>/dev/null && \
    echo "  Ruta agregada: 192.168.3.0/24 -> 10.216.124.130" || \
    echo "  WARN: No se pudo agregar ruta para Sitio 03"

# Sitio 04: 192.168.4.0/24 via router 10.216.124.204
ip route replace 192.168.4.0/24 via 10.216.124.204 dev "$ZT_IFACE" 2>/dev/null && \
    echo "  Ruta agregada: 192.168.4.0/24 -> 10.216.124.204" || \
    echo "  WARN: No se pudo agregar ruta para Sitio 04"

# Agregar más sitios aquí conforme se desplieguen:
# ip route replace 192.168.X.0/24 via 10.216.124.XXX dev "$ZT_IFACE"

echo "Rutas ZeroTier configuradas correctamente."
