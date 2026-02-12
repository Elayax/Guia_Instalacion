# Guía de Referencia Rápida - Generador de Reportes LBS

## 🎯 Inicio Rápido en 3 Pasos

### 1. Importar y crear datos
```python
from generador_reporte_lbs import ReporteServicioLBS

datos = {
    'folio_ticket': '20105',
    'nombre_cliente': 'Mi Cliente',
    'marca_equipo': 'APC',
    'modelo_equipo': 'Smart-UPS',
    # ... más datos
}
```

### 2. Crear generador
```python
generador = ReporteServicioLBS(datos)
```

### 3. Generar PDF
```python
generador.generar_pdf('mi_reporte.pdf')
```

---

## 🔧 Personalización Común

### Cambiar colores del reporte

Editar en `generador_reporte_lbs.py`:

```python
class ReporteServicioLBS:
    # Cambiar estos valores
    COLOR_ROJO_LBS = colors.HexColor('#C00000')      # Rojo de bordes
    COLOR_ROJO_CLARO = colors.HexColor('#FFC7CE')    # Fondos claros
    COLOR_GRIS_OSCURO = colors.HexColor('#404040')   # Texto gris
```

### Cambiar márgenes de página

```python
def __init__(self, datos_reporte):
    self.margin_left = 20 * mm    # Margen izquierdo
    self.margin_right = 20 * mm   # Margen derecho
    self.margin_top = 15 * mm     # Margen superior
    self.margin_bottom = 15 * mm  # Margen inferior
```

### Cambiar tamaño de página

```python
from reportlab.lib.pagesizes import letter, A4

# En __init__:
self.width, self.height = A4  # Cambiar a A4
# o
self.width, self.height = letter  # Mantener carta
```

---

## 📝 Agregar Nueva Sección

### Paso 1: Crear método de dibujo

```python
def _dibujar_mi_nueva_seccion(self, c, y_pos):
    """Dibuja una nueva sección personalizada"""
    x_start = self.margin_left
    width = self.width - self.margin_left - self.margin_right
    height_section = 40*mm  # Altura de la sección
    
    # Título de la sección
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_start, y_pos, "MI NUEVA SECCIÓN:")
    
    y_pos -= 5*mm
    
    # Rectángulo con borde rojo
    c.setStrokeColor(self.COLOR_ROJO_LBS)
    c.setLineWidth(1.5)
    c.rect(x_start, y_pos - height_section, width, height_section)
    
    # Contenido de la sección
    c.setFont("Helvetica", 7)
    y_text = y_pos - 5*mm
    
    # Extraer datos
    mi_dato = self.datos.get('mi_campo', 'Valor por defecto')
    c.drawString(x_start + 3, y_text, f"Mi campo: {mi_dato}")
    
    # Retornar nueva posición Y para siguiente sección
    return y_pos - height_section
```

### Paso 2: Llamar el método desde una página

Editar `_generar_pagina_X`:

```python
def _generar_pagina_2(self, c):
    y_pos = self.height - self.margin_top
    
    # ... secciones existentes ...
    
    # Agregar nueva sección
    y_pos = self._dibujar_mi_nueva_seccion(c, y_pos - 5*mm)
    
    # ... más secciones ...
```

### Paso 3: Agregar campo a plantilla de datos

En `plantilla_datos.py`:

```python
def obtener_plantilla_vacia():
    return {
        # ... campos existentes ...
        
        # Mi nueva sección
        'mi_campo': '',
        'otro_campo': False,
    }
```

---

## 🎨 Elementos de Diseño Comunes

### Dibujar checkbox

```python
# Checkbox marcado
c.drawString(x, y, "☑ Opción marcada")

# Checkbox sin marcar
c.drawString(x, y, "☐ Opción sin marcar")

# Dinámico
marcado = '☑' if condicion else '☐'
c.drawString(x, y, f"{marcado} Mi opción")
```

### Dibujar línea horizontal

```python
c.setStrokeColor(colors.black)
c.setLineWidth(1)
c.line(x_inicio, y, x_fin, y)
```

### Dibujar tabla simple

```python
# Encabezados de tabla
c.setFont("Helvetica-Bold", 7)
c.drawString(x, y, "Columna 1")
c.drawString(x + 50*mm, y, "Columna 2")

# Datos
c.setFont("Helvetica", 7)
y -= 4*mm
c.drawString(x, y, "Valor 1")
c.drawString(x + 50*mm, y, "Valor 2")
```

### Dibujar rectángulo con fondo de color

```python
# Fondo de color
c.setFillColor(self.COLOR_ROJO_CLARO)
c.rect(x, y, width, height, fill=1, stroke=0)

# Borde rojo sin fondo
c.setStrokeColor(self.COLOR_ROJO_LBS)
c.setLineWidth(1.5)
c.rect(x, y, width, height, fill=0, stroke=1)
```

---

## 📐 Unidades de Medida

```python
from reportlab.lib.units import inch, mm, cm

# Conversiones comunes
1 * inch  # 1 pulgada = 72 puntos
1 * mm    # 1 milímetro
1 * cm    # 1 centímetro

# Ejemplos de uso
ancho = 50 * mm
alto = 2 * inch
margen = 1.5 * cm
```

---

## 🔍 Debugging y Tips

### Ver posición actual

```python
# Agregar temporalmente para ver dónde estás dibujando
c.setFont("Helvetica", 6)
c.setFillColor(colors.red)
c.drawString(x, y, f"y={y}")
c.setFillColor(colors.black)
```

### Verificar que no te salgas de página

```python
if y_pos < self.margin_bottom + 20*mm:
    print(f"⚠️ Advertencia: y_pos muy bajo: {y_pos}")
    # Agregar nueva página o ajustar diseño
```

### Dibujar líneas guía (desarrollo)

```python
# Líneas guía para ver márgenes (remover en producción)
c.setStrokeColor(colors.red)
c.setLineWidth(0.5)
c.line(self.margin_left, 0, self.margin_left, self.height)  # Izquierda
c.line(self.width - self.margin_right, 0, 
       self.width - self.margin_right, self.height)  # Derecha
```

---

## 🔄 Validación de Datos

### Crear función de validación

```python
def validar_datos_reporte(datos):
    """
    Valida que los datos mínimos estén presentes.
    """
    campos_requeridos = [
        'folio_ticket',
        'nombre_cliente',
        'marca_equipo',
        'modelo_equipo'
    ]
    
    errores = []
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo]:
            errores.append(f"Campo requerido faltante: {campo}")
    
    if errores:
        raise ValueError("Errores de validación:\n" + "\n".join(errores))
    
    return True
```

### Usar antes de generar

```python
validar_datos_reporte(datos)
generador = ReporteServicioLBS(datos)
generador.generar_pdf('reporte.pdf')
```

---

## 📊 Agregar Campos Calculados

### En la clase ReporteServicioLBS

```python
def _calcular_autonomia_estimada(self):
    """Calcula autonomía basada en baterías y carga"""
    num_baterias = self.datos.get('baterias', {}).get('numero_baterias', 0)
    capacidad_kva = float(self.datos.get('capacidad', '0').replace('kVA', '').strip())
    
    # Fórmula simplificada
    if num_baterias > 0 and capacidad_kva > 0:
        autonomia_min = (num_baterias * 12 * 65) / (capacidad_kva * 1000) * 60
        return round(autonomia_min, 1)
    return 0

def _dibujar_analisis_autonomia(self, c, y_pos):
    """Dibuja análisis de autonomía calculado"""
    autonomia = self._calcular_autonomia_estimada()
    c.drawString(x, y, f"Autonomía estimada: {autonomia} minutos")
```

---

## 🎯 Mejores Prácticas

1. **Siempre retornar `y_pos`** desde métodos `_dibujar_*`
2. **Usar constantes de clase** para colores y medidas repetidas
3. **Validar datos** antes de generar PDF
4. **Comentar secciones complejas** para facilitar mantenimiento
5. **Mantener métodos cortos** (max 50 líneas cada uno)
6. **Usar plantillas** en lugar de hardcodear datos
7. **Probar con datos vacíos** para evitar crashes

---

## 📞 Solución de Problemas

### El PDF sale en blanco
- Verificar que `c.save()` se llame al final
- Asegurarse que `y_pos` no sea negativo

### Texto cortado o fuera de página
- Reducir tamaño de fuente
- Ajustar altura de secciones
- Verificar márgenes

### Caracteres especiales no se ven
- Usar encoding UTF-8 en archivos Python
- Para símbolos especiales, usar códigos unicode

### Colores no aparecen
- Llamar `c.setFillColor()` antes de dibujar texto
- Llamar `c.setStrokeColor()` antes de dibujar líneas/bordes

---

## 📚 Recursos Adicionales

- [Documentación ReportLab](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- Ver `ejemplos/` para casos de uso completos
- Ver `plantilla_datos.py` para estructura de datos completa
- Consultar PDF original para referencia de diseño
