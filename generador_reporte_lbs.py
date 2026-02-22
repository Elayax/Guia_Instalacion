import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.reporte import ReportePDF
except ImportError as e:
    print(f"Error al importar ReportePDF: {e}")
    sys.exit(1)

def generar_reporte_prueba():
    print("Iniciando generación de reporte de prueba...")

    # 1. Datos del Formulario (Simulados)
    datos = {
        'cliente_texto': 'Cliente de Prueba S.A.',
        'sucursal_texto': 'Sucursal Central',
        'nombre': 'Proyecto Demo 2024',
        'kva': '20',
        'voltaje': '220',
        'fases': '3',
        'longitud': '50',
        'tiempo_respaldo': '15'
    }

    # 2. Datos del UPS (Simulados - Estructura de BD)
    ups = {
        'Nombre_del_Producto': 'UPS Online Doble Conversión',
        'Capacidad_kVA': 20,
        'Capacidad_kW': 18,
        'Eficiencia_Modo_Bateria_pct': 0.94,
        'Bateria_Vdc': 192,
        # URLs de imágenes (pueden no existir, el reporte lo maneja)
        'imagen_url': 'ups_demo.jpg', 
        'imagen_baterias_url': 'baterias_demo.jpg',
        'imagen_instalacion_url': 'instalacion_demo.jpg',
        'imagen_layout_url': 'layout_demo.jpg',
        'tipo_ventilacion_id': 1
    }

    # 3. Datos de Batería (Simulados)
    bateria = {
        'modelo': '12V-100AH',
        'fabricante': 'Generic Bat',
        'voltaje_nominal': 12,
        'capacidad_ah': 100
    }

    # 4. Resultados de Cálculos (Simulados - Salida de CalculadoraUPS/CalculadoraBaterias)
    res = {
        'i_diseno': 65.5,
        'i_nom': 54.5,
        'breaker_sel': 80,
        'fase_sel': '4',
        'gnd_sel': '6',
        'dv_pct': 2.5,
        'i_real_cable': 85.0,
        'nota_altitud': 'Instalación a 2200msnm, se aplicó factor de corrección 0.92',
        
        # Resultados de Baterías
        'baterias_total': 32,
        'autonomia_calculada_min': 18.5,
        'autonomia_deseada_min': 15,
        'numero_strings': 2,
        'baterias_por_string': 16,
        'bat_error': None,

        # Info de Ventilación
        'tipo_ventilacion': 'Forzada por Aire',
        'tipo_ventilacion_data': {
            'nombre': 'Forzada por Aire',
            'descripcion': 'Sistema de enfriamiento mediante ventiladores internos de alto flujo.',
            'imagen_url': 'airflow_demo.jpg'
        },
        'modelo_nombre': ups['Nombre_del_Producto']
    }

    # 5. Imágenes Temporales (Simuladas - vacías para usar placeholders o defaults)
    imagenes_temp = {}

    try:
        # Instanciar reporte
        pdf = ReportePDF()
        
        # Generar contenido
        # es_publicado=False añade marcas de agua "PREVIEW"
        pdf_bytes = pdf.generar_cuerpo(
            datos=datos, 
            res=res, 
            ups=ups, 
            bateria=bateria, 
            es_publicado=False, 
            imagenes_temp=imagenes_temp
        )

        # Guardar en archivo
        nombre_archivo = "reporte_generado_lbs.pdf"
        ruta_salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
        
        with open(ruta_salida, "wb") as f:
            f.write(bytes(pdf_bytes))
            
        print(f"Reporte generado exitosamente: {ruta_salida}")
        print(f"Tamaño del archivo: {os.path.getsize(ruta_salida)} bytes")


    except Exception as e:
        print(f"Error generando el reporte: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generar_reporte_prueba()
