#!/bin/bash
# Script de Instalación - Generador de Reportes LBS
# ==================================================

echo "======================================================"
echo "  INSTALADOR - Generador de Reportes LBS v1.0"
echo "======================================================"
echo ""

# Verificar Python
echo "1. Verificando instalación de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "   Por favor instala Python 3.8 o superior"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION encontrado"
echo ""

# Verificar pip
echo "2. Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip no está instalado"
    echo "   Instalando pip..."
    python3 -m ensurepip --default-pip
fi
echo "✓ pip encontrado"
echo ""

# Instalar dependencias
echo "3. Instalando dependencias..."
echo "   Esto puede tomar unos momentos..."
pip3 install -r requirements.txt --break-system-packages

if [ $? -eq 0 ]; then
    echo "✓ Dependencias instaladas correctamente"
else
    echo "❌ Error al instalar dependencias"
    exit 1
fi
echo ""

# Verificar instalación
echo "4. Verificando instalación..."
python3 -c "import reportlab; print('✓ ReportLab versión:', reportlab.Version)"
echo ""

# Generar reporte de prueba
echo "5. Generando reporte de prueba..."
python3 generador_reporte_lbs.py

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================"
    echo "  ✓ INSTALACIÓN COMPLETADA EXITOSAMENTE"
    echo "======================================================"
    echo ""
    echo "Archivos generados:"
    echo "  - reporte_servicio_lbs_20105.pdf (reporte de ejemplo)"
    echo ""
    echo "Para generar tu propio reporte:"
    echo "  1. Edita los datos en generador_reporte_lbs.py"
    echo "  2. Ejecuta: python3 generador_reporte_lbs.py"
    echo ""
    echo "Para ver ejemplos:"
    echo "  - cd ejemplos/"
    echo "  - python3 ejemplo_basico.py"
    echo "  - python3 ejemplo_plantillas.py"
    echo ""
    echo "Consulta README.md para más información"
    echo "======================================================"
else
    echo ""
    echo "❌ Error al generar reporte de prueba"
    echo "   Revisa los errores anteriores"
    exit 1
fi
