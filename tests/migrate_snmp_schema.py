"""
Script de migración para agregar soporte SNMP a la base de datos.

Este script actualiza el esquema de base de datos existente agregando
las tablas necesarias para dispositivos SNMP y sus lecturas.

Uso:
    python tests/migrate_snmp_schema.py

Autor: Sistema de Monitoreo UPS
Fecha: 2026-01-26
"""

import sqlite3
import os
import sys
from datetime import datetime

# Path a la base de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'app', 'Equipos.db')


def print_header(message):
    """Imprime encabezado de sección."""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70)


def create_snmp_tables(conn):
    """Crea las tablas para SNMP."""
    cursor = conn.cursor()
    
    print_header("Creando Tablas SNMP")
    
    # ========================================================================
    # TABLA: snmp_devices
    # ========================================================================
    print("\n📦 Creando tabla 'snmp_devices'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snmp_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            ip_address TEXT NOT NULL,
            port INTEGER DEFAULT 8161,
            community TEXT DEFAULT 'public',
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP,
            
            -- Información estática del dispositivo (se lee una vez)
            model TEXT,
            serial_number TEXT,
            manufacturer TEXT,
            monitor_version TEXT,
            battery_count INTEGER,
            battery_ah INTEGER,
            battery_rated_voltage INTEGER,
            battery_type INTEGER,
            rated_power INTEGER,
            rated_input_voltage INTEGER,
            rated_output_voltage INTEGER,
            input_phases INTEGER,
            output_phases INTEGER
        )
    ''')
    conn.commit()
    print("  ✓ Tabla 'snmp_devices' creada")
    
    # ========================================================================
    # TABLA: snmp_readings
    # ========================================================================
    print("\n📊 Creando tabla 'snmp_readings'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snmp_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Estado general
            connection_status INTEGER,
            power_supply_mode INTEGER,  -- 0=none, 1=UPS, 2=bypass
            battery_status INTEGER,      -- 0-4 (ver ups_oids.py)
            maintain_breaker INTEGER,
            battery_test_result INTEGER,
            
            -- Batería (CRÍTICO)
            battery_voltage REAL,
            battery_current REAL,
            battery_charge_percent INTEGER,
            battery_runtime_remaining INTEGER,  -- minutos
            battery_temperature REAL,
            battery_cycles INTEGER,
            
            -- Entrada (Input) - Fase A principalmente
            input_voltage_a REAL,
            input_voltage_b REAL,
            input_voltage_c REAL,
            input_current_a REAL,
            input_current_b REAL,
            input_current_c REAL,
            input_frequency_a REAL,
            input_active_power_a REAL,
            input_reactive_power_a REAL,
            input_apparent_power_a REAL,
            
            -- Salida (Output) - Fase A principalmente
            output_voltage_a REAL,
            output_voltage_b REAL,
            output_voltage_c REAL,
            output_current_a REAL,
            output_current_b REAL,
            output_current_c REAL,
            output_frequency_a REAL,
            output_active_power_a REAL,
            output_reactive_power_a REAL,
            output_apparent_power_a REAL,
            output_power_factor_a REAL,
            output_active_power_total REAL,
            output_apparent_power_total REAL,
            
            -- Carga (Load)
            load_percent_a INTEGER,
            load_percent_b INTEGER,
            load_percent_c INTEGER,
            
            -- Bypass
            bypass_voltage_a REAL,
            bypass_voltage_b REAL,
            bypass_voltage_c REAL,
            bypass_current_a REAL,
            bypass_frequency_a REAL,
            
            FOREIGN KEY (device_id) REFERENCES snmp_devices(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    print("  ✓ Tabla 'snmp_readings' creada")
    
    # ========================================================================
    # ÍNDICES para snmp_readings
    # ========================================================================
    print("\n🔍 Creando índices para 'snmp_readings'...")
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_snmp_readings_device_timestamp 
        ON snmp_readings(device_id, timestamp DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_snmp_readings_timestamp 
        ON snmp_readings(timestamp DESC)
    ''')
    
    conn.commit()
    print("  ✓ Índices creados")
    
    # ========================================================================
    # TABLA: snmp_alarms
    # ========================================================================
    print("\n🚨 Creando tabla 'snmp_alarms'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snmp_alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            alarm_type TEXT NOT NULL,  
            -- 'LOW_BATTERY', 'ON_BATTERY', 'HIGH_TEMP', 'BYPASS_MODE', 
            -- 'OVERLOAD', 'INPUT_FAIL', 'VOLTAGE_OUT_OF_RANGE'
            severity TEXT NOT NULL,     -- 'INFO', 'WARNING', 'CRITICAL'
            message TEXT NOT NULL,
            value REAL,                 -- Valor que disparó la alarma
            threshold REAL,             -- Umbral configurado
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT 0,
            acknowledged_at TIMESTAMP,
            acknowledged_by TEXT,
            cleared BOOLEAN DEFAULT 0,
            cleared_at TIMESTAMP,
            
            FOREIGN KEY (device_id) REFERENCES snmp_devices(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    print("  ✓ Tabla 'snmp_alarms' creada")
    
    # Índices para alarmas
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_snmp_alarms_device 
        ON snmp_alarms(device_id, triggered_at DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_snmp_alarms_active 
        ON snmp_alarms(cleared, acknowledged, triggered_at DESC)
    ''')
    
    conn.commit()
    print("  ✓ Índices de alarmas creados")
    
    # ========================================================================
    # TABLA: snmp_events
    # ========================================================================
    print("\n📝 Creando tabla 'snmp_events'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snmp_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,  
            -- 'STATUS_CHANGE', 'POWER_FAIL', 'POWER_RESTORE', 
            -- 'BATTERY_TEST', 'CONNECTION_LOST', 'CONNECTION_RESTORED'
            description TEXT,
            old_value TEXT,
            new_value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (device_id) REFERENCES snmp_devices(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    print("  ✓ Tabla 'snmp_events' creada")
    
    # Índice para eventos
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_snmp_events_device_timestamp 
        ON snmp_events(device_id, timestamp DESC)
    ''')
    
    conn.commit()
    print("  ✓ Índices de eventos creados")
    
    # ========================================================================
    # VISTA: unified_device_status
    # ========================================================================
    print("\n🔗 Creando vista unificada 'unified_device_status'...")
    
    # Primero borrar si existe
    cursor.execute('DROP VIEW IF EXISTS unified_device_status')
    
    cursor.execute('''
        CREATE VIEW unified_device_status AS
        SELECT 
            'modbus' as protocol,
            m.id,
            m.nombre as name,
            m.ip,
            m.port,
            NULL as battery_charge_percent,
            NULL as battery_temperature,
            NULL as power_source,
            NULL as last_seen,
            m.estado as enabled
        FROM monitoreo_config m
        
        UNION ALL
        
        SELECT 
            'snmp' as protocol,
            s.id,
            s.name,
            s.ip_address as ip,
            s.port,
            sr.battery_charge_percent,
            sr.battery_temperature,
            sr.power_supply_mode as power_source,
            s.last_seen,
            s.enabled
        FROM snmp_devices s
        LEFT JOIN snmp_readings sr ON s.id = sr.device_id 
        WHERE sr.id = (
            SELECT id FROM snmp_readings 
            WHERE device_id = s.id 
            ORDER BY timestamp DESC 
            LIMIT 1
        )
    ''')
    
    conn.commit()
    print("  ✓ Vista 'unified_device_status' creada")


def verify_tables(conn):
    """Verifica que las tablas se hayan creado correctamente."""
    cursor = conn.cursor()
    
    print_header("Verificando Tablas Creadas")
    
    # Verificar tablas existentes
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'snmp%'
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        print("\n✓ Tablas SNMP encontradas:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("\n✗ No se encontraron tablas SNMP")
        return False
    
    # Verificar vista
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND name='unified_device_status'
    """)
    
    view = cursor.fetchone()
    if view:
        print(f"\n✓ Vista encontrada: {view[0]}")
    else:
        print("\n✗ Vista 'unified_device_status' no encontrada")
    
    return True


def show_schema_info(conn):
    """Muestra información del esquema de cada tabla."""
    cursor = conn.cursor()
    
    print_header("Esquema de Tablas SNMP")
    
    tables = ['snmp_devices', 'snmp_readings', 'snmp_alarms', 'snmp_events']
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        print(f"\n📋 Tabla: {table}")
        print(f"  Columnas: {len(columns)}")
        for col in columns[:5]:  # Mostrar solo primeras 5 columnas
            print(f"    - {col[1]} ({col[2]})")
        if len(columns) > 5:
            print(f"    ... y {len(columns) - 5} más")


def main():
    """Función principal de migración."""
    print("\n🔧 SCRIPT DE MIGRACIÓN SNMP - SISTEMA DE MONITOREO UPS")
    print("=" * 70)
    print(f"  Base de datos: {DB_PATH}")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que existe la BD
    if not os.path.exists(DB_PATH):
        print(f"\n❌ ERROR: No se encontró la base de datos en {DB_PATH}")
        print("   Asegúrate de que la aplicación Flask se haya ejecutado al menos una vez.")
        sys.exit(1)
    
    try:
        # Conectar a la BD
        print("\n📡 Conectando a base de datos...")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        print("  ✓ Conexión establecida")
        
        # Crear tablas
        create_snmp_tables(conn)
        
        # Verificar
        if verify_tables(conn):
            print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        else:
            print("\n⚠️  MIGRACIÓN COMPLETADA CON ADVERTENCIAS")
        
        # Mostrar info del esquema
        show_schema_info(conn)
        
        # Cerrar conexión
        conn.close()
        print("\n" + "=" * 70)
        print("  Puedes proceder a ejecutar el script de testing:")
        print("  python tests/test_snmp_connection.py")
        print("=" * 70 + "\n")
        
        sys.exit(0)
    
    except sqlite3.Error as e:
        print(f"\n❌ ERROR DE BASE DE DATOS: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
