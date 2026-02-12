# Generador de Reportes de Servicio LBS

Sistema automatizado para generar reportes de servicio en formato PDF siguiendo el estándar LBS.

## 📋 Características

- ✅ Replica fielmente el diseño oficial de reportes LBS
- ✅ Colores corporativos (rojo #C00000 para bordes y encabezados)
- ✅ Estructura modular y fácilmente extensible
- ✅ Basado en especificación técnica del formulario v3.1
- ✅ Soporte para múltiples tipos de servicio (Preventivo, Correctivo, Diagnóstico, etc.)
- ✅ Generación de PDFs de 5 páginas con toda la información técnica

## 🚀 Instalación

```bash
pip install reportlab --break-system-packages
```

## 💻 Uso Básico

### Generar un reporte simple

```python
from generador_reporte_lbs import ReporteServicioLBS

# Datos mínimos requeridos
datos = {
    'folio_ticket': '20105',
    'fecha_servicio': '06/02/2026',
    'nombre_cliente': 'Radio Movil DYPSA',
    'marca_equipo': 'OPA FXD',
    'modelo_equipo': 'OPA FXD',
    'capacidad': '400 kVA'
}

# Generar PDF
generador = ReporteServicioLBS(datos)
generador.generar_pdf('mi_reporte.pdf')
```

### Generar con datos completos

```python
from plantilla_datos import obtener_plantilla_completa

# Obtener plantilla con todos los campos
datos = obtener_plantilla_completa()

# Personalizar campos específicos
datos['nombre_cliente'] = 'Mi Cliente'
datos['modelo_equipo'] = 'UPS-5000'

# Generar
generador = ReporteServicioLBS(datos)
generador.generar_pdf('reporte_completo.pdf')
```

## 📊 Estructura de Datos

El generador acepta un diccionario con la siguiente estructura:

### Bloque 1: Encabezado y Metadatos
```python
{
    'folio_ticket': str,           # Número de folio (ej: "20105")
    'fecha_servicio': str,         # Fecha en formato DD/MM/YYYY
    'nombre_cliente': str,         # Nombre del cliente
    'sucursal_sitio': str,         # Ubicación/Sucursal
    'tipo_de_servicio': str,       # Preventivo, Correctivo, etc.
    'marca_equipo': str,           # Marca del UPS
    'modelo_equipo': str,          # Modelo del UPS
    'arquitectura_ups': str,       # Monolítico o Modular
    'es_equipo_ge': bool,          # True si es equipo GE
}
```

### Bloque 2: Lecturas Entrada/Salida
```python
{
    'configuracion_fases': str,    # Monofásico, Bifásico, Trifásico
    'punto_medicion': list,        # ['UPS', 'Transformador', etc.]
    'parametros_entrada': {
        'l1_l2': float,
        'l2_l3': float,
        'frecuencia_hz': float,
    },
    'parametros_salida': {
        'estado': str,             # Inversor Encendido, Bypass, etc.
        'l1_l2': float,
    }
}
```

### Bloques 3-13: Ver `plantilla_datos.py` para estructura completa

## 🎨 Personalización

### Cambiar colores corporativos

```python
class ReporteServicioLBS:
    COLOR_ROJO_LBS = colors.HexColor('#FF0000')  # Cambiar rojo
    COLOR_ROJO_CLARO = colors.HexColor('#FFE0E0')
```

### Modificar secciones

Cada sección tiene su método `_dibujar_*`:
- `_dibujar_encabezado()` - Encabezado con logo
- `_dibujar_info_cliente()` - Datos del cliente
- `_dibujar_parametros_entrada_salida()` - Mediciones eléctricas
- `_dibujar_operacion_sistema()` - Estado del UPS
- etc.

### Agregar nueva sección

```python
def _dibujar_mi_seccion(self, c, y_pos):
    """Dibuja una nueva sección personalizada"""
    x_start = self.margin_left
    width = self.width - self.margin_left - self.margin_right
    
    # Título
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_start, y_pos, "MI NUEVA SECCIÓN:")
    
    y_pos -= 5*mm
    
    # Rectángulo con borde rojo
    c.setStrokeColor(self.COLOR_ROJO_LBS)
    c.setLineWidth(1.5)
    c.rect(x_start, y_pos - 30*mm, width, 30*mm)
    
    # Contenido
    c.setFont("Helvetica", 7)
    # ... agregar contenido ...
    
    return y_pos - 30*mm
```

## 📁 Archivos del Proyecto

```
├── generador_reporte_lbs.py    # Clase principal del generador
├── plantilla_datos.py          # Plantillas de datos pre-configuradas
├── README.md                   # Este archivo
└── ejemplos/                   # Ejemplos de uso
    ├── ejemplo_basico.py
    ├── ejemplo_diagnostico.py
    └── ejemplo_preventivo.py
```

## 🔧 Arquitectura

### Flujo de generación

1. **Inicialización**: Se crea instancia con datos del reporte
2. **Generación página por página**: 
   - Página 1: Encabezado, cliente, parámetros eléctricos
   - Página 2: Revisión de cableado, refacciones
   - Página 3: Baterías, transformadores, pruebas
   - Página 4: Condiciones del sitio, observaciones
   - Página 5: Criterios de cumplimiento, firmas
3. **Guardado**: Se genera el archivo PDF

### Principios de diseño

- **Modularidad**: Cada sección es un método independiente
- **Extensibilidad**: Fácil agregar nuevas secciones o modificar existentes
- **Datos estructurados**: Basado en especificación del formulario v3.1
- **Validación**: Los datos pueden validarse antes de generar

## 📝 Reglas de Negocio Implementadas

Según FormularioV1:

- ✅ **[A]** Equipos GE habilitan Bloque 12 de servicios especiales
- ✅ **[C]** Capacitación visible solo en "Arranque/Puesta en Marcha"
- ✅ **[E]** Arquitectura Modular requiere seriales de módulos
- ✅ **[G]** Configuración de fases controla campos visibles
- ✅ **[I]** Capacidad de interruptores condicional a su existencia
- ✅ **[N, P]** Daños y piezas condicionados a sustitución
- ✅ **[Q, R]** Motivos y ubicaciones se habilitan según detección

## 🔄 Roadmap Futuro

### Versión 1.1
- [ ] Validación automática de datos
- [ ] Generación de múltiples reportes en lote
- [ ] Exportar a JSON/Excel desde PDF

### Versión 1.2
- [ ] Interfaz web para captura de datos
- [ ] Generación de gráficas de voltajes
- [ ] Historial de servicios por cliente

### Versión 2.0
- [ ] Sistema completo con base de datos
- [ ] Dashboard de análisis de reportes
- [ ] Integración con sistema ERP
- [ ] Firma electrónica avanzada

## 📞 Soporte

Para dudas o problemas:
1. Revisar este README
2. Ver ejemplos en carpeta `ejemplos/`
3. Consultar `plantilla_datos.py` para estructura completa

## 📄 Licencia

Propiedad de LBS - Lemon Roy
Todos los derechos reservados © 2026
