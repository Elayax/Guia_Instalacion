-- Migración 008: Tabla de sitios para inventario de red
-- Cada sitio representa una ubicación física con su router y UPS.

CREATE TABLE IF NOT EXISTS sites (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    numero INTEGER UNIQUE NOT NULL,
    ip_zt_router TEXT,
    subnet TEXT,
    gateway TEXT,
    router_node_id TEXT,
    firmware TEXT,
    descripcion TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agregar FK de monitoreo_config a sites
-- Usar DO block para evitar error si la constraint ya existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_monitoreo_site'
        AND table_name = 'monitoreo_config'
    ) THEN
        ALTER TABLE monitoreo_config
        ADD CONSTRAINT fk_monitoreo_site
        FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE SET NULL;
    END IF;
END $$;
