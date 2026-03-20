#!/bin/bash
# Setup de Cloudflare Tunnel para LBS Monitor
# Permite acceso externo seguro sin abrir puertos.
#
# Requisitos: cuenta Cloudflare con dominio configurado
# Uso: bash setup-cloudflare-tunnel.sh

set -euo pipefail

TUNNEL_NAME="lbs-monitor"
LOCAL_PORT=5000

echo "=== Setup de Cloudflare Tunnel ==="

# 1. Instalar cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "Instalando cloudflared..."
    if command -v yay &> /dev/null; then
        yay -S --noconfirm cloudflared
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm cloudflared
    else
        echo "Descargando binario de cloudflared..."
        curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
        chmod +x /tmp/cloudflared
        sudo mv /tmp/cloudflared /usr/local/bin/cloudflared
    fi
    echo "cloudflared instalado: $(cloudflared --version)"
else
    echo "cloudflared ya instalado: $(cloudflared --version)"
fi

# 2. Autenticar (abre navegador)
echo ""
echo "Autenticando con Cloudflare..."
echo "(Se abrirá tu navegador para autorizar)"
cloudflared tunnel login

# 3. Crear tunnel
echo ""
echo "Creando tunnel '$TUNNEL_NAME'..."
cloudflared tunnel create "$TUNNEL_NAME"

# 4. Obtener ID del tunnel
TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
echo "Tunnel ID: $TUNNEL_ID"

# 5. Crear configuración
CONFIG_DIR="$HOME/.cloudflared"
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_DIR/config.yml" << EOF
tunnel: $TUNNEL_ID
credentials-file: $CONFIG_DIR/${TUNNEL_ID}.json

ingress:
  - hostname: lbs-monitor.example.com
    service: http://localhost:$LOCAL_PORT
  - service: http_status:404
EOF

echo ""
echo "Configuración creada en $CONFIG_DIR/config.yml"
echo ""
echo "IMPORTANTE: Edita $CONFIG_DIR/config.yml y cambia 'lbs-monitor.example.com' por tu dominio real."
echo ""
echo "Después ejecuta:"
echo "  cloudflared tunnel route dns $TUNNEL_NAME tu-subdominio.tu-dominio.com"
echo "  sudo cloudflared service install"
echo "  sudo systemctl enable --now cloudflared"
echo ""
echo "Para probar manualmente:"
echo "  cloudflared tunnel run $TUNNEL_NAME"
