-- Migración 001: Schema inicial PostgreSQL
-- Traducido desde SQLite (app/base_datos.py)

-- ============================================
-- TABLA: schema_migrations (tracking de migraciones)
-- ============================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TABLA: users (autenticación)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TABLA: clientes
-- ============================================
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    cliente TEXT NOT NULL,
    sucursal TEXT NOT NULL,
    direccion TEXT,
    link_maps TEXT,
    lat TEXT,
    lon TEXT,
    UNIQUE(cliente, sucursal)
);

-- ============================================
-- TABLA: tipos_ventilacion
-- ============================================
CREATE TABLE IF NOT EXISTS tipos_ventilacion (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    descripcion TEXT,
    imagen_url TEXT
);

-- ============================================
-- TABLA: ups_specs (51+ columnas técnicas)
-- ============================================
CREATE TABLE IF NOT EXISTS ups_specs (
    id SERIAL PRIMARY KEY,
    "Nombre_del_Producto" TEXT,
    "Serie" TEXT,
    "Capacidad_kVA" DOUBLE PRECISION,
    "Capacidad_kW" DOUBLE PRECISION,
    "Eficiencia_Modo_AC_pct" DOUBLE PRECISION,
    "Eficiencia_Modo_Bateria_pct" DOUBLE PRECISION,
    "Eficiencia_Modo_ECO_pct" DOUBLE PRECISION,
    "FP_Salida" DOUBLE PRECISION,
    "Voltaje_Entrada_1_V" DOUBLE PRECISION,
    "Voltaje_Entrada_2_V" DOUBLE PRECISION,
    "Voltaje_Entrada_3_V" DOUBLE PRECISION,
    "Conexion_Entrada" TEXT,
    "Voltaje_Salida_1_V" DOUBLE PRECISION,
    "Voltaje_Salida_2_V" DOUBLE PRECISION,
    "Voltaje_Salida_3_V" DOUBLE PRECISION,
    "Conexion_Salida" TEXT,
    "Frecuencia_1_Hz" DOUBLE PRECISION,
    "Frecuencia_2_Hz" DOUBLE PRECISION,
    "Frecuencia_Precision_pct" DOUBLE PRECISION,
    "THDu_Lineal_pct" DOUBLE PRECISION,
    "THDu_NoLineal_pct" DOUBLE PRECISION,
    "Sobrecarga_110_pct_min" DOUBLE PRECISION,
    "Sobrecarga_125_pct_min" DOUBLE PRECISION,
    "Sobrecarga_150_pct_min" DOUBLE PRECISION,
    "Bateria_Vdc" DOUBLE PRECISION,
    "Bateria_Piezas_min" DOUBLE PRECISION,
    "Bateria_Piezas_max" DOUBLE PRECISION,
    "Bateria_Piezas_defecto" DOUBLE PRECISION,
    "Precision_Voltaje_pct" DOUBLE PRECISION,
    "TempTrabajo_min_C" DOUBLE PRECISION,
    "TempTrabajo_max_C" DOUBLE PRECISION,
    "Humedad_min_pct" DOUBLE PRECISION,
    "Humedad_max_pct" DOUBLE PRECISION,
    "Peso_Gabinete_kg" DOUBLE PRECISION,
    "Dim_Largo_mm" DOUBLE PRECISION,
    "Dim_Ancho_mm" DOUBLE PRECISION,
    "Dim_Alto_mm" DOUBLE PRECISION,
    "Nivel_Ruido_dB" DOUBLE PRECISION,
    "Cable_Entrada_mm2" DOUBLE PRECISION,
    "Cable_Entrada_conductores" DOUBLE PRECISION,
    "Cable_Salida_mm2" DOUBLE PRECISION,
    "Cable_Salida_conductores" DOUBLE PRECISION,
    "Cable_Bateria_mm2" DOUBLE PRECISION,
    "Cable_Bateria_conductores" DOUBLE PRECISION,
    "Cable_PE_mm2" DOUBLE PRECISION,
    imagen_url TEXT,
    imagen_instalacion_url TEXT,
    imagen_baterias_url TEXT,
    tipo_ventilacion_id INTEGER REFERENCES tipos_ventilacion(id),
    imagen_diagrama_ac_url TEXT,
    imagen_diagrama_dc_url TEXT,
    imagen_layout_url TEXT
);

CREATE INDEX IF NOT EXISTS idx_serie ON ups_specs("Serie");
CREATE INDEX IF NOT EXISTS idx_nombre ON ups_specs("Nombre_del_Producto");
CREATE INDEX IF NOT EXISTS idx_cap_kva ON ups_specs("Capacidad_kVA");

-- ============================================
-- TABLA: baterias_modelos (31 columnas técnicas)
-- ============================================
CREATE TABLE IF NOT EXISTS baterias_modelos (
    id SERIAL PRIMARY KEY,
    modelo TEXT UNIQUE NOT NULL,
    serie TEXT,
    voltaje_nominal DOUBLE PRECISION,
    capacidad_nominal_ah DOUBLE PRECISION,
    resistencia_interna_mohm DOUBLE PRECISION,
    max_corriente_descarga_5s_a DOUBLE PRECISION,
    largo_mm DOUBLE PRECISION,
    ancho_mm DOUBLE PRECISION,
    alto_contenedor_mm DOUBLE PRECISION,
    alto_total_mm DOUBLE PRECISION,
    peso_kg DOUBLE PRECISION,
    tipo_terminal TEXT,
    material_contenedor TEXT,
    carga_flotacion_v_min DOUBLE PRECISION,
    carga_flotacion_v_max DOUBLE PRECISION,
    coef_temp_flotacion_mv_c DOUBLE PRECISION,
    carga_ciclica_v_min DOUBLE PRECISION,
    carga_ciclica_v_max DOUBLE PRECISION,
    corriente_inicial_max_a DOUBLE PRECISION,
    coef_temp_ciclica_mv_c DOUBLE PRECISION,
    temp_descarga_min_c DOUBLE PRECISION,
    temp_descarga_max_c DOUBLE PRECISION,
    temp_carga_min_c DOUBLE PRECISION,
    temp_carga_max_c DOUBLE PRECISION,
    temp_almacenaje_min_c DOUBLE PRECISION,
    temp_almacenaje_max_c DOUBLE PRECISION,
    temp_nominal_c DOUBLE PRECISION,
    capacidad_40c_pct DOUBLE PRECISION,
    capacidad_25c_pct DOUBLE PRECISION,
    capacidad_0c_pct DOUBLE PRECISION,
    autodescarga_meses_max DOUBLE PRECISION
);

-- ============================================
-- TABLA: baterias_curvas_descarga
-- ============================================
CREATE TABLE IF NOT EXISTS baterias_curvas_descarga (
    id SERIAL PRIMARY KEY,
    bateria_id INTEGER NOT NULL REFERENCES baterias_modelos(id) ON DELETE CASCADE,
    tiempo_minutos INTEGER,
    voltaje_corte_fv DOUBLE PRECISION,
    valor DOUBLE PRECISION,
    unidad TEXT DEFAULT 'W'
);

CREATE INDEX IF NOT EXISTS idx_curva_descarga
    ON baterias_curvas_descarga(bateria_id, unidad, tiempo_minutos, voltaje_corte_fv);

-- ============================================
-- TABLA: proyectos_publicados (espina dorsal)
-- ============================================
CREATE TABLE IF NOT EXISTS proyectos_publicados (
    id SERIAL PRIMARY KEY,
    pedido TEXT UNIQUE NOT NULL,
    fecha_publicacion TEXT,

    -- Referencias
    id_ups INTEGER REFERENCES ups_specs(id),
    id_bateria INTEGER REFERENCES baterias_modelos(id),
    id_cliente INTEGER REFERENCES clientes(id),

    -- Snapshots históricos
    modelo_snap TEXT,
    potencia_snap DOUBLE PRECISION,
    cliente_snap TEXT,
    sucursal_snap TEXT,

    -- Configuración técnica
    voltaje DOUBLE PRECISION,
    fases INTEGER,
    longitud DOUBLE PRECISION,
    tiempo_respaldo DOUBLE PRECISION,
    voltaje_entrada TEXT,
    voltaje_salida TEXT,
    potencia_kva DOUBLE PRECISION,

    -- Resultados de cálculos
    calibre_fases TEXT,
    config_salida TEXT,
    calibre_tierra TEXT,

    -- Documentos generados
    pdf_guia_url TEXT,
    pdf_checklist_url TEXT
);

-- ============================================
-- TABLA: monitoreo_config
-- ============================================
CREATE TABLE IF NOT EXISTS monitoreo_config (
    id SERIAL PRIMARY KEY,
    ip TEXT NOT NULL,
    port INTEGER DEFAULT 502,
    slave_id INTEGER DEFAULT 1,
    nombre TEXT,
    protocolo TEXT DEFAULT 'modbus',
    snmp_community TEXT DEFAULT 'public',
    snmp_port INTEGER DEFAULT 161,
    estado TEXT DEFAULT 'inactivo',
    fecha_registro TIMESTAMP DEFAULT NOW(),
    UNIQUE(ip, port, slave_id)
);

-- ============================================
-- TABLA: personal
-- ============================================
CREATE TABLE IF NOT EXISTS personal (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    puesto TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT NOW()
);
