-- Migración 004: Agregar usuario GustavoV
INSERT INTO users (username, password_hash, role)
VALUES ('GustavoV', '$2b$12$jnilJ3h3rJHboVwDPoBU2.0OBYG9/bAM4RLykjX.m/GbAoYOflq8C', 'user')
ON CONFLICT (username) DO NOTHING;
