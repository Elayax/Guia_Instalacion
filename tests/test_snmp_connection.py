"""
Script de testing para verificar conectividad SNMP con dispositivo UPS.

Este script prueba la comunicación SNMP con el UPS conectado via RUT956,
lee OIDs críticos y valida los valores recibidos.

Uso:
    python tests/test_snmp_connection.py

Autor: Sistema de Monitoreo UPS
Fecha: 2026-01-26
"""

import sys
import os
import logging
from datetime import datetime

# Agregar directorio raíz al path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.protocols.snmp_client import SNMPClient, SNMPClientError
from app.utils.ups_oids import UPS_OIDS, SCALE_FACTORS, DECODERS, CRITICAL_OIDS

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UPSSNMPTester:
    """Clase para testing de conectividad SNMP con UPS."""
    
    def __init__(self, host: str, port: int = 8161, community: str = 'public'):
        """
        Inicializa el tester.
        
        Args:
            host: IP del RUT956 con ZeroTier (ej: 10.147.17.2)
            port: Puerto con port forward al UPS (default: 8161)
            community: Community string SNMP
        """
        self.host = host
        self.port = port
        self.community = community
        self.client = SNMPClient(host, port, community, timeout=5, retries=2)
        self.results = {}
    
    def print_header(self, message: str):
        """Imprime encabezado de sección."""
        print("\n" + "=" * 70)
        print(f"  {message}")
        print("=" * 70)
    
    def print_result(self, label: str, value: any, unit: str = "", status: str = "✓"):
        """Imprime resultado formateado."""
        print(f"  {status} {label:30s}: {value} {unit}")
    
    def apply_scale_factor(self, oid: str, raw_value: str) -> float:
        """Aplica factor de escala si existe para el OID."""
        try:
            numeric_value = float(raw_value)
            scale = SCALE_FACTORS.get(oid, 1.0)
            return numeric_value * scale
        except (ValueError, TypeError):
            return raw_value
    
    def decode_enum_value(self, decoder_name: str, raw_value: str) -> str:
        """Decodifica valor enum usando diccionario."""
        try:
            int_value = int(raw_value)
            decoder = DECODERS.get(decoder_name, {})
            return decoder.get(int_value, f"Desconocido ({int_value})")
        except (ValueError, TypeError):
            return raw_value
    
    def test_connection(self) -> bool:
        """Test 1: Verificar conectividad básica."""
        self.print_header("TEST 1: Conectividad SNMP")
        
        try:
            success, message = self.client.test_connection()
            if success:
                self.print_result("Estado de conexión", message, status="✓")
                return True
            else:
                self.print_result("Estado de conexión", message, status="✗")
                return False
        except Exception as e:
            self.print_result("Estado de conexión", f"ERROR: {e}", status="✗")
            return False
    
    def test_device_info(self) -> bool:
        """Test 2: Leer información del dispositivo."""
        self.print_header("TEST 2: Información del Dispositivo")
        
        try:
            info_oids = UPS_OIDS['info']
            
            # Leer información básica
            model = self.client.get_oid(info_oids['model'])
            serial = self.client.get_oid(info_oids['serial_number'])
            manufacturer = self.client.get_oid(info_oids['company_name'])
            rated_power = self.client.get_oid(info_oids['rated_power'])
            
            self.print_result("Fabricante", manufacturer or "N/A")
            self.print_result("Modelo", model or "N/A")
            self.print_result("Número de Serie", serial or "N/A")
            self.print_result("Potencia Nominal", rated_power or "N/A", "VA")
            
            # Guardar para reporte final
            self.results['device_info'] = {
                'model': model,
                'serial': serial,
                'manufacturer': manufacturer,
                'rated_power': rated_power
            }
            
            return True
        
        except SNMPClientError as e:
            self.print_result("Lectura de info", f"ERROR: {e}", status="✗")
            return False
    
    def test_critical_oids(self) -> bool:
        """Test 3: Leer OIDs críticos del UPS."""
        self.print_header("TEST 3: Parámetros Críticos")
        
        try:
            # Leer OIDs críticos en batch
            values = self.client.get_multiple_oids(CRITICAL_OIDS)
            
            # Procesar y mostrar valores críticos
            battery_oids = UPS_OIDS['battery']
            status_oids = UPS_OIDS['status']
            input_oids = UPS_OIDS['input']
            output_oids = UPS_OIDS['output']
            load_oids = UPS_OIDS['load']
            
            # === BATERÍA (MÁS CRÍTICO) ===
            print("\n  📊 BATERÍA:")
            battery_voltage_raw = values.get(battery_oids['voltage'])
            battery_voltage = self.apply_scale_factor(battery_oids['voltage'], battery_voltage_raw) if battery_voltage_raw else None
            self.print_result("  Voltaje", f"{battery_voltage:.1f}" if battery_voltage else "N/A", "V")
            
            battery_current_raw = values.get(battery_oids['current'])
            battery_current = self.apply_scale_factor(battery_oids['current'], battery_current_raw) if battery_current_raw else None
            self.print_result("  Corriente", f"{battery_current:.1f}" if battery_current else "N/A", "A")
            
            battery_charge = values.get(battery_oids['charge_percent'])
            self.print_result("  Carga", battery_charge or "N/A", "%")
            
            battery_runtime = values.get(battery_oids['runtime_remaining'])
            self.print_result("  Autonomía", battery_runtime or "N/A", "min")
            
            battery_temp = values.get(battery_oids['temperature'])
            self.print_result("  Temperatura", battery_temp or "N/A", "°C")
            
            # === ESTADO ===
            print("\n  ⚙️ ESTADO:")
            power_source_raw = values.get(status_oids['power_source'])
            power_source = self.decode_enum_value('power_source', power_source_raw) if power_source_raw else "N/A"
            self.print_result("  Fuente de Alimentación", power_source)
            
            battery_status_raw = values.get(status_oids['battery_status'])
            battery_status = self.decode_enum_value('battery_status', battery_status_raw) if battery_status_raw else "N/A"
            self.print_result("  Estado de Batería", battery_status)
            
            # === ENTRADA ===
            print("\n  ⚡ ENTRADA:")
            input_voltage = values.get(input_oids['voltage_a'])
            self.print_result("  Voltaje Fase A", input_voltage or "N/A", "V")
            
            input_freq_raw = values.get(input_oids['frequency_a'])
            input_freq = self.apply_scale_factor(input_oids['frequency_a'], input_freq_raw) if input_freq_raw else None
            self.print_result("  Frecuencia", f"{input_freq:.1f}" if input_freq else "N/A", "Hz")
            
            # === SALIDA ===
            print("\n  🔌 SALIDA:")
            output_voltage = values.get(output_oids['voltage_a'])
            self.print_result("  Voltaje Fase A", output_voltage or "N/A", "V")
            
            output_current_raw = values.get(output_oids['current_a'])
            output_current = self.apply_scale_factor(output_oids['current_a'], output_current_raw) if output_current_raw else None
            self.print_result("  Corriente Fase A", f"{output_current:.1f}" if output_current else "N/A", "A")
            
            output_power_raw = values.get(output_oids['active_power_total'])
            output_power = self.apply_scale_factor(output_oids['active_power_total'], output_power_raw) if output_power_raw else None
            self.print_result("  Potencia Activa Total", f"{output_power:.1f}" if output_power else "N/A", "kW")
            
            # === CARGA ===
            print("\n  📈 CARGA:")
            load_percent = values.get(load_oids['percent_a'])
            self.print_result("  Carga Fase A", load_percent or "N/A", "%")
            
            # Guardar para reporte
            self.results['critical_data'] = {
                'battery_voltage': battery_voltage,
                'battery_charge': battery_charge,
                'battery_temp': battery_temp,
                'power_source': power_source,
                'battery_status': battery_status,
                'output_power': output_power,
                'load_percent': load_percent
            }
            
            return True
        
        except SNMPClientError as e:
            self.print_result("Lectura de OIDs críticos", f"ERROR: {e}", status="✗")
            return False
    
    def test_value_validation(self) -> bool:
        """Test 4: Validar que los valores estén en rangos esperados."""
        self.print_header("TEST 4: Validación de Valores")
        
        if 'critical_data' not in self.results:
            self.print_result("Validación", "No hay datos para validar", status="⚠")
            return False
        
        data = self.results['critical_data']
        all_valid = True
        
        # Validar voltaje de batería (esperado: 300-400V para 384V nominal)
        if data.get('battery_voltage'):
            if 300 <= data['battery_voltage'] <= 450:
                self.print_result("Voltaje Batería (300-450V)", f"{data['battery_voltage']:.1f}V válido")
            else:
                self.print_result("Voltaje Batería", f"{data['battery_voltage']:.1f}V FUERA DE RANGO", status="✗")
                all_valid = False
        
        # Validar carga de batería (0-100%)
        if data.get('battery_charge'):
            charge = int(data['battery_charge'])
            if 0 <= charge <= 100:
                self.print_result("Carga Batería (0-100%)", f"{charge}% válido")
            else:
                self.print_result("Carga Batería", f"{charge}% FUERA DE RANGO", status="✗")
                all_valid = False
        
        # Validar temperatura (<60°C)
        if data.get('battery_temp'):
            temp = int(data['battery_temp'])
            if temp < 60:
                self.print_result("Temperatura (<60°C)", f"{temp}°C válido")
            else:
                self.print_result("Temperatura", f"{temp}°C ALTA", status="⚠")
        
        # Validar carga del UPS (0-100%)
        if data.get('load_percent'):
            load = int(data['load_percent'])
            if 0 <= load <= 100:
                self.print_result("Carga UPS (0-100%)", f"{load}% válido")
            else:
                self.print_result("Carga UPS", f"{load}% FUERA DE RANGO", status="✗")
                all_valid = False
        
        return all_valid
    
    def generate_report(self):
        """Genera reporte final del testing."""
        self.print_header("REPORTE FINAL")
        
        print(f"\n  Fecha de Test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Dispositivo: {self.host}:{self.port}")
        print(f"  Community: {self.community}")
        
        if 'device_info' in self.results:
            info = self.results['device_info']
            print(f"\n  📦 Dispositivo: {info.get('manufacturer')} {info.get('model')}")
            print(f"  🔢 S/N: {info.get('serial')}")
            print(f"  ⚡ Potencia: {info.get('rated_power')} VA")
        
        if 'critical_data' in self.results:
            data = self.results['critical_data']
            print(f"\n  🔋 Batería: {data.get('battery_charge')}% | {data.get('battery_voltage'):.1f}V | {data.get('battery_temp')}°C")
            print(f"  📊 Estado: {data.get('power_source')} | {data.get('battery_status')}")
            print(f"  🔌 Salida: {data.get('output_power'):.1f}kW | Carga {data.get('load_percent')}%")
        
        print("\n" + "=" * 70)


def main():
    """Función principal de testing."""
    print("\n🔍 SCRIPT DE TESTING SNMP - SISTEMA DE MONITOREO UPS")
    print("=" * 70)
    
    # Configuración del test (ajustar según tu entorno)
    HOST = '10.147.17.2'  # IP ZeroTier del RUT956
    PORT = 8161           # Puerto con port forward
    COMMUNITY = 'public'  # Community string
    
    print(f"\n📡 Objetivo: {HOST}:{PORT}")
    print(f"🔑 Community: {COMMUNITY}")
    
    # Crear tester
    tester = UPSSNMPTester(HOST, PORT, COMMUNITY)
    
    # Ejecutar tests
    test_results = []
    
    test_results.append(("Conectividad", tester.test_connection()))
    test_results.append(("Información de Dispositivo", tester.test_device_info()))
    test_results.append(("OIDs Críticos", tester.test_critical_oids()))
    test_results.append(("Validación de Valores", tester.test_value_validation()))
    
    # Generar reporte
    tester.generate_report()
    
    # Resumen de tests
    print("\n📋 RESUMEN DE TESTS:")
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    # Exit code
    all_passed = all(result for _, result in test_results)
    if all_passed:
        print("\n✅ TODOS LOS TESTS PASARON\n")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
