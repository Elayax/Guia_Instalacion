#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación del Sistema Standalone
==============================================

Este script verifica que todos los componentes necesarios
estén instalados y configurados correctamente.
"""

import sys
import os

def verificar_archivo(ruta, descripcion):
    """Verifica que existe un archivo"""
    if os.path.exists(ruta):
        print(f"  ✅ {descripcion}")
        return True
    else:
        print(f"  ❌ {descripcion} - NO ENCONTRADO")
        return False

def verificar_modulo(nombre_modulo, descripcion):
    """Verifica que un módulo de Python está instalado"""
    try:
        __import__(nombre_modulo)
        print(f"  ✅ {descripcion}")
        return True
    except ImportError:
        print(f"  ❌ {descripcion} - NO INSTALADO")
        print(f"     Instalar con: pip install {nombre_modulo}")
        return False

def main():
    print("\n" + "="*70)
    print("  VERIFICACIÓN DEL SISTEMA STANDALONE - GENERADOR DE REPORTES LBS")
    print("="*70 + "\n")
    
    errores = 0
    
    # 1. Verificar archivos principales
    print("1️⃣  Verificando archivos principales...")
    archivos = [
        ("app_reportes.py", "Aplicación Flask"),
        ("generador_reporte_lbs.py", "Motor de generación de PDFs"),
        ("templates/reporte_demo.html", "Template HTML"),
        ("requirements.txt", "Archivo de dependencias"),
        ("iniciar_reportes.bat", "Script de inicio Windows"),
    ]
    
    for archivo, desc in archivos:
        if not verificar_archivo(archivo, desc):
            errores += 1
    
    print()
    
    # 2. Verificar módulos de Python
    print("2️⃣  Verificando módulos de Python...")
    modulos = [
        ("flask", "Flask (Framework web)"),
        ("reportlab", "ReportLab (Generador de PDFs)"),
    ]
    
    for modulo, desc in modulos:
        if not verificar_modulo(modulo, desc):
            errores += 1
    
    print()
    
    # 3. Verificar estructura de directorios
    print("3️⃣  Verificando estructura de directorios...")
    
    # Crear output si no existe
    if not os.path.exists("output"):
        os.makedirs("output")
        print("  ✅ Carpeta 'output' creada")
    else:
        print("  ✅ Carpeta 'output' existe")
    
    if not os.path.exists("templates"):
        print("  ❌ Carpeta 'templates' NO existe")
        errores += 1
    else:
        print("  ✅ Carpeta 'templates' existe")
    
    print()
    
    # 4. Resultado final
    print("="*70)
    if errores == 0:
        print("  ✅ ✅ ✅  SISTEMA LISTO PARA USAR  ✅ ✅ ✅")
        print()
        print("  Para iniciar la aplicación:")
        print("    Windows: .\\iniciar_reportes.bat")
        print("    Linux/Mac: python3 app_reportes.py")
        print()
        print("  Acceso: http://localhost:5001")
    else:
        print(f"  ❌ Se encontraron {errores} problema(s)")
        print()
        print("  Soluciones:")
        print("    1. Instalar dependencias: pip install -r requirements.txt")
        print("    2. Verificar que estás en la carpeta 'Reportes/'")
        print("    3. Revisar que todos los archivos se crearon correctamente")
    
    print("="*70 + "\n")
    
    return errores

if __name__ == "__main__":
    errores = main()
    sys.exit(0 if errores == 0 else 1)
