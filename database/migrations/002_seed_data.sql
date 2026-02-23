-- Migración 002: Datos semilla
-- Tipos de ventilación y baterías de ejemplo

-- ============================================
-- DATOS SEMILLA: tipos_ventilacion
-- ============================================
INSERT INTO tipos_ventilacion (nombre, descripcion) VALUES
    ('Aire Forzado', 'Ventilación mediante ventiladores que impulsan el aire a través del equipo'),
    ('Convección Natural', 'Ventilación pasiva mediante circulación natural del aire'),
    ('Flujo Cruzado', 'Entrada y salida de aire en lados opuestos del equipo'),
    ('Flujo Frontal', 'Entrada y salida de aire en la parte frontal del equipo')
ON CONFLICT (nombre) DO NOTHING;

-- ============================================
-- DATOS SEMILLA: baterias_modelos
-- ============================================
INSERT INTO baterias_modelos (
    modelo, serie, voltaje_nominal, capacidad_nominal_ah,
    resistencia_interna_mohm, max_corriente_descarga_5s_a,
    largo_mm, ancho_mm, alto_contenedor_mm, alto_total_mm, peso_kg,
    tipo_terminal, material_contenedor,
    carga_flotacion_v_min, carga_flotacion_v_max, coef_temp_flotacion_mv_c,
    carga_ciclica_v_min, carga_ciclica_v_max, corriente_inicial_max_a, coef_temp_ciclica_mv_c,
    temp_descarga_min_c, temp_descarga_max_c, temp_carga_min_c, temp_carga_max_c,
    temp_almacenaje_min_c, temp_almacenaje_max_c, temp_nominal_c,
    capacidad_40c_pct, capacidad_25c_pct, capacidad_0c_pct, autodescarga_meses_max
) VALUES
    ('LBS12-7.2','General Purpose',12,7.2,18.0,108.0,151,65,93.5,99,2.35,'T2','ABS',13.5,13.8,-20,14.4,15.0,2.16,-30,-15,50,0,40,-15,40,25,103,100,86,6),
    ('LBS12-9.0','General Purpose',12,8.6,19.0,129.0,151,65,93.5,99,2.66,'T2','ABS',13.5,13.8,-20,14.4,15.0,2.58,-30,-15,50,0,40,-15,40,25,103,100,86,6),
    ('LBS12-10','General Purpose',12,10.0,22.0,150.0,151,65,111,117,3.20,'T2','ABS',13.5,13.8,-20,14.4,15.0,3.00,-30,-15,50,0,40,-15,40,25,103,100,86,6),
    ('LBS12-55','General Purpose',12,55.0,7.5,660.0,229,138,205,211,16.2,'T6','ABS',13.5,13.8,-20,14.4,15.0,16.5,-30,-15,50,0,40,-15,40,25,103,100,86,6),
    ('LBS12-75','General Purpose',12,75.0,6.6,900.0,260,168,208,214,22.3,'T6','ABS',13.5,13.8,-20,14.4,15.0,22.5,-30,-15,50,0,40,-15,40,25,103,100,86,6),
    ('LBS12-100','General Purpose',12,100.0,4.9,1200.0,330,173,212,220,30.6,'T11','ABS',13.5,13.8,-20,14.4,15.0,30.0,-30,-15,50,0,40,-15,40,25,103,100,86,6)
ON CONFLICT (modelo) DO NOTHING;
