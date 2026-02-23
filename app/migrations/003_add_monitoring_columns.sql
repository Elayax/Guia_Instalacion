-- Migración 003: Agregar columnas de monitoreo SNMP avanzado
-- Requeridas por monitoring_service.py y scripts de diagnóstico

-- Columna snmp_version: 0=SNMPv1, 1=SNMPv2c (default)
ALTER TABLE monitoreo_config ADD COLUMN IF NOT EXISTS snmp_version INTEGER DEFAULT 1;

-- Columna ups_type: tipo de UPS para selección de cliente SNMP
-- Valores: 'invt_enterprise', 'invt_minimal', 'ups_mib_standard', 'hybrid'
ALTER TABLE monitoreo_config ADD COLUMN IF NOT EXISTS ups_type TEXT DEFAULT 'invt_enterprise';

-- Alias community para compatibilidad con scripts
-- (ya existe snmp_community, pero algunos scripts usan 'community')
ALTER TABLE monitoreo_config ADD COLUMN IF NOT EXISTS community TEXT DEFAULT 'public';

-- Registrar migración
INSERT INTO schema_migrations (version) VALUES ('003_add_monitoring_columns')
ON CONFLICT (version) DO NOTHING;
