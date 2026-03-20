-- Migración 007: Columnas adicionales para monitoreo avanzado con ZeroTier
-- Soporta: conexión dual-method (port-forward + ruta directa), grabación histórica,
-- inventario de red, y tracking de estado de conexión.

-- IP ZeroTier del router del sitio (para port-forward SNMP)
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS ip_zt TEXT;

-- Puerto SNMP en el port-forward ZeroTier (default: 10161)
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS snmp_port_zt INTEGER DEFAULT 10161;

-- IP local del UPS en la LAN del sitio (ej: 192.168.3.10)
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS ip_local TEXT;

-- ID del sitio (FK se agrega en migración 008)
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS site_id INTEGER;

-- Grabación histórica: activa/inactiva por dispositivo
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS recording BOOLEAN DEFAULT FALSE;

-- Intervalo de grabación en segundos (configurable por UPS)
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS recording_interval INTEGER DEFAULT 30;

-- OIDs activos descubiertos (JSON array)
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS active_oids JSONB DEFAULT '[]'::jsonb;

-- Contador de fallos consecutivos de conexión
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS fail_count INTEGER DEFAULT 0;

-- Timestamp de última conexión exitosa
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS last_seen TIMESTAMPTZ;

-- Método de conexión actual: 'port_forward' o 'direct'
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS connection_method TEXT DEFAULT 'port_forward';

-- MAC address del dispositivo
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS mac_address TEXT;

-- Marca/Modelo del UPS
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS brand TEXT;

-- Firmware version del router
ALTER TABLE monitoreo_config
ADD COLUMN IF NOT EXISTS firmware TEXT;
