-- Migración 009: Tablas de lecturas históricas y alertas persistentes
-- ups_readings: almacena datos de telemetría cuando recording=TRUE
-- ups_alerts: almacena alertas con ciclo de vida (activa → resuelta)

CREATE TABLE IF NOT EXISTS ups_readings (
    id BIGSERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES monitoreo_config(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Voltajes de entrada por fase (V RMS)
    voltaje_in_l1 REAL,
    voltaje_in_l2 REAL,
    voltaje_in_l3 REAL,
    frecuencia_in REAL,

    -- Voltajes de salida por fase (V RMS)
    voltaje_out_l1 REAL,
    voltaje_out_l2 REAL,
    voltaje_out_l3 REAL,
    frecuencia_out REAL,

    -- Corrientes de salida por fase (A)
    corriente_out_l1 REAL,
    corriente_out_l2 REAL,
    corriente_out_l3 REAL,

    -- Carga y potencia
    carga_pct REAL,
    power_factor REAL,
    active_power REAL,
    apparent_power REAL,

    -- Batería
    bateria_pct REAL,
    voltaje_bateria REAL,
    corriente_bateria REAL,
    temperatura REAL,
    battery_remain_time REAL,

    -- Estado
    power_mode TEXT,
    battery_status TEXT
);

-- Índice principal: consultas por dispositivo ordenadas por tiempo
CREATE INDEX IF NOT EXISTS idx_readings_device_time
ON ups_readings(device_id, timestamp DESC);

-- Índice para limpieza por antigüedad
CREATE INDEX IF NOT EXISTS idx_readings_timestamp
ON ups_readings(timestamp);


CREATE TABLE IF NOT EXISTS ups_alerts (
    id BIGSERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES monitoreo_config(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level TEXT NOT NULL,          -- 'info', 'warning', 'critical'
    code TEXT NOT NULL,           -- 'BAT_LOW', 'DEVICE_OFFLINE', 'OVERLOAD', etc.
    message TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ
);

-- Índice para alertas por dispositivo
CREATE INDEX IF NOT EXISTS idx_alerts_device_time
ON ups_alerts(device_id, timestamp DESC);

-- Índice para alertas no resueltas (consulta frecuente del dashboard)
CREATE INDEX IF NOT EXISTS idx_alerts_unresolved
ON ups_alerts(resolved, timestamp DESC)
WHERE resolved = FALSE;
