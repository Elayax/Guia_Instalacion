-- Migración 005: Tabla de permisos por usuario
CREATE TABLE IF NOT EXISTS user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seccion VARCHAR(50) NOT NULL,
    permitido BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_user_seccion UNIQUE (user_id, seccion)
);

-- Seed: permisos por defecto para usuarios existentes
-- Admins: todo habilitado
INSERT INTO user_permissions (user_id, seccion, permitido)
SELECT u.id, s.seccion, TRUE
FROM users u
CROSS JOIN (VALUES ('tablero'), ('calculos'), ('guia_rapida'), ('scada'), ('datos')) AS s(seccion)
WHERE u.role = 'admin'
ON CONFLICT (user_id, seccion) DO NOTHING;

-- Users: todo habilitado excepto SCADA
INSERT INTO user_permissions (user_id, seccion, permitido)
SELECT u.id, s.seccion,
    CASE WHEN s.seccion = 'scada' THEN FALSE ELSE TRUE END
FROM users u
CROSS JOIN (VALUES ('tablero'), ('calculos'), ('guia_rapida'), ('scada'), ('datos')) AS s(seccion)
WHERE u.role = 'user'
ON CONFLICT (user_id, seccion) DO NOTHING;
