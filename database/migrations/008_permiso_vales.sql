-- Migración 008: Agregar permiso 'vales' para todos los usuarios existentes

INSERT INTO user_permissions (user_id, seccion, permitido)
SELECT u.id, 'vales', TRUE FROM users u
ON CONFLICT (user_id, seccion) DO NOTHING;
