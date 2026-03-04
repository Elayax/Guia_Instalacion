-- Migración 007: Agregar permisos granulares para PDFs (ejemplo_pdf, publicar_pdf)

-- Admins: habilitar ambos permisos
INSERT INTO user_permissions (user_id, seccion, permitido)
SELECT u.id, s.seccion, TRUE
FROM users u
CROSS JOIN (VALUES ('ejemplo_pdf'), ('publicar_pdf')) AS s(seccion)
WHERE u.role = 'admin'
ON CONFLICT (user_id, seccion) DO NOTHING;

-- Users: ejemplo_pdf habilitado, publicar_pdf deshabilitado
INSERT INTO user_permissions (user_id, seccion, permitido)
SELECT u.id, s.seccion,
    CASE WHEN s.seccion = 'publicar_pdf' THEN FALSE ELSE TRUE END
FROM users u
CROSS JOIN (VALUES ('ejemplo_pdf'), ('publicar_pdf')) AS s(seccion)
WHERE u.role = 'user'
ON CONFLICT (user_id, seccion) DO NOTHING;
