#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Independiente de Generador de Reportes LBS
======================================================

Esta es una aplicación STANDALONE que NO se conecta al sistema principal.
Propósito: Mostrar los avances del generador de reportes PDF.

IMPORTANTE: Esta aplicación corre en un puerto diferente (5001) para no 
interferir con el sistema principal que corre en el puerto 5000.
"""

from flask import Flask, render_template, send_file, url_for
import os
from datetime import datetime
from generador_reporte_lbs import ReporteLBSMejorado

# ============================================================================
#                        CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configuración básica
app.config['SECRET_KEY'] = 'reportes-lbs-standalone-2026'
app.config['DEBUG'] = True

# Directorio para guardar PDFs generados
PDF_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# ============================================================================
#                              RUTAS
# ============================================================================

@app.route('/')
def index():
    """
    Página principal con el botón de Imprimir Muestra
    """
    return render_template('reporte_demo.html')


@app.route('/generar-muestra')
def generar_muestra():
    """
    Genera un PDF de muestra con los avances del reporte
    
    Returns:
        PDF file: Archivo PDF generado como descarga
    """
    try:
        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f'reporte_muestra_{timestamp}.pdf'
        ruta_completa = os.path.join(PDF_OUTPUT_DIR, nombre_archivo)
        
        # Generar el reporte usando la clase mejorada
        generador = ReporteLBSMejorado()
        generador.generar_reporte(ruta_completa)
        
        # Enviar el archivo como descarga
        return send_file(
            ruta_completa,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return f"""
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    color: white;
                }}
                .error-box {{
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 600px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }}
                h1 {{
                    margin: 0 0 20px 0;
                    color: #ff6b6b;
                }}
                .error-details {{
                    background: rgba(0, 0, 0, 0.3);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-family: monospace;
                    font-size: 14px;
                }}
                a {{
                    color: #4ecdc4;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>❌ Error al Generar Reporte</h1>
                <p>Ocurrió un error durante la generación del PDF:</p>
                <div class="error-details">{str(e)}</div>
                <p><a href="/">← Volver al inicio</a></p>
            </div>
        </body>
        </html>
        """


@app.route('/info')
def info():
    """
    Información sobre la aplicación standalone
    """
    return """
    <html>
    <head>
        <title>Información - Generador de Reportes LBS</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 40px;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                margin: 0 0 30px 0;
                border-bottom: 2px solid rgba(255, 255, 255, 0.3);
                padding-bottom: 20px;
            }
            .info-section {
                background: rgba(0, 0, 0, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .badge {
                display: inline-block;
                background: #4ecdc4;
                color: #1a1a1a;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                margin: 5px;
            }
            a {
                color: #4ecdc4;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            ul {
                line-height: 1.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Generador de Reportes LBS - Standalone</h1>
            
            <div class="info-section">
                <h2>ℹ️ Información General</h2>
                <p><strong>Versión:</strong> 2.0 (Mejorada)</p>
                <p><strong>Puerto:</strong> 5001 (Independiente del sistema principal)</p>
                <p><strong>Estado:</strong> <span class="badge">INDEPENDIENTE</span> <span class="badge">NO CONECTADO AL SISTEMA</span></p>
            </div>
            
            <div class="info-section">
                <h2>🎯 Propósito</h2>
                <p>Esta aplicación es una versión standalone del generador de reportes LBS. 
                No se conecta al sistema principal y está diseñada para:</p>
                <ul>
                    <li>Mostrar los avances en el desarrollo del generador de reportes PDF</li>
                    <li>Generar muestras de reportes en formato PDF</li>
                    <li>Desarrollo y pruebas independientes sin afectar el sistema principal</li>
                </ul>
            </div>
            
            <div class="info-section">
                <h2>📋 Características Implementadas</h2>
                <ul>
                    <li>✅ Diseño fiel al reporte oficial LBS</li>
                    <li>✅ Colores corporativos (#C00000)</li>
                    <li>✅ Módulo de encabezado con logo y datos de contacto</li>
                    <li>✅ Módulo de información general del cliente</li>
                    <li>✅ Módulo de parámetros eléctricos (entrada/salida)</li>
                    <li>✅ Módulo de operación del sistema UPS</li>
                    <li>✅ Módulo de ventiladores y capacitores</li>
                    <li>✅ Módulo de limpieza</li>
                    <li>✅ Módulo de firmas</li>
                </ul>
            </div>
            
            <div class="info-section">
                <h2>🚀 Próximos Pasos</h2>
                <ul>
                    <li>⏳ Integración con formulario de captura de datos</li>
                    <li>⏳ Conexión con base de datos del sistema</li>
                    <li>⏳ Generación dinámica basada en datos reales</li>
                    <li>⏳ Firma digital de reportes</li>
                </ul>
            </div>
            
            <p style="text-align: center; margin-top: 40px;">
                <a href="/">← Volver a la página principal</a>
            </p>
        </div>
    </body>
    </html>
    """


# ============================================================================
#                          PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  GENERADOR DE REPORTES LBS - APLICACIÓN STANDALONE")
    print("="*70)
    print(f"\n  📄 Aplicación corriendo en: http://localhost:5001")
    print(f"  ⚠️  NOTA: Esta aplicación NO está conectada al sistema principal")
    print(f"  ℹ️  Sistema principal corre en: http://localhost:5000")
    print(f"  📁 PDFs se guardan en: {PDF_OUTPUT_DIR}")
    print("\n" + "="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5001,  # Puerto diferente para no interferir con el sistema principal
        debug=True
    )
