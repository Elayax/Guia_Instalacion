# 🚀 Aplicación Standalone - Generador de Reportes LBS

## 📌 ¿Qué es esto?

Esta es una **aplicación web independiente** que muestra los avances del generador de reportes PDF para LBS. 

**IMPORTANTE:** Esta aplicación:
- ✅ **NO está conectada** al sistema principal
- ✅ Corre en un **puerto diferente** (5001 vs 5000)
- ✅ Es **completamente independiente** para desarrollo sin romper nada
- ✅ Genera **reportes PDF de muestra** con un solo click

## 🎯 Objetivo

Permitir el desarrollo y prueba del generador de reportes PDF sin interferir con el sistema principal que tiene "cosas rotas".

## 🚀 Inicio Rápido

### Windows
```bash
cd Reportes
.\iniciar_reportes.bat
```

### Linux/Mac
```bash
cd Reportes
python3 app_reportes.py
```

Luego abre tu navegador en: **http://localhost:5001**

## 📋 Estructura de Archivos

```
Reportes/
├── app_reportes.py              # 🌟 Aplicación Flask standalone
├── generador_reporte_lbs.py     # Motor de generación de PDFs
├── plantilla_datos.py           # Datos de ejemplo
├── templates/
│   └── reporte_demo.html        # 🎨 Interfaz web moderna
├── output/                      # 📁 PDFs generados (creado auto)
├── requirements.txt             # Dependencias
├── iniciar_reportes.bat         # Script de inicio Windows
└── INICIO_RAPIDO.md            # Esta guía

```

## 🎨 Características de la Interfaz

- ✅ **Diseño Glassmorphism** moderno y premium
- ✅ **Animaciones suaves** y efectos visuales
- ✅ **Responsive** - funciona en móvil y desktop
- ✅ **Un solo botón**: "Imprimir Muestra"
- ✅ **Descarga automática** del PDF

## 📄 ¿Qué genera?

El botón "Imprimir Muestra" genera un PDF que incluye:

- ✅ Encabezado con logo LBS y datos de contacto
- ✅ Información general del cliente/equipo
- ✅ Parámetros eléctricos de entrada/salida
- ✅ Operación del sistema UPS
- ✅ Condiciones de ventiladores y capacitores
- ✅ Sección de limpieza
- ✅ Área de firmas

## 🔧 Instalación de Dependencias

```bash
cd Reportes
pip install -r requirements.txt
```

O manualmente:
```bash
pip install reportlab flask
```

## 🌐 Rutas Disponibles

| Ruta | Descripción |
|------|-------------|
| `/` | Página principal con el botón |
| `/generar-muestra` | Genera y descarga el PDF |
| `/info` | Información sobre la aplicación |

## ⚙️ Configuración

El archivo `app_reportes.py` contiene la configuración:

```python
# Puerto (diferente al sistema principal)
port = 5001

# Directorio de salida
PDF_OUTPUT_DIR = './output'

# Modo debug
DEBUG = True
```

## 🐛 Solución de Problemas

### El puerto 5001 está ocupado
Edita `app_reportes.py` línea ~200:
```python
app.run(host='0.0.0.0', port=5002, debug=True)  # Cambiar 5001 a 5002
```

### Error "Template not found"
Verifica que existe:
```
Reportes/templates/reporte_demo.html
```

### Error "No module named 'reportlab'"
```bash
pip install reportlab flask
```

## 🎯 Próximos Pasos (Roadmap)

### Fase 1: ✅ COMPLETADO
- [x] Aplicación standalone funcional
- [x] Interfaz web moderna
- [x] Botón de "Imprimir Muestra"
- [x] Generación de PDF básica

### Fase 2: 🔄 EN DESARROLLO
- [ ] Agregar formulario para captura de datos
- [ ] Integrar con base de datos del sistema
- [ ] Múltiples plantillas de reportes
- [ ] Preview del PDF antes de descargar

### Fase 3: 📋 PLANEADO
- [ ] Conexión con el sistema principal
- [ ] Autenticación de usuarios
- [ ] Historial de reportes generados
- [ ] Firma digital de reportes

## 🔐 Seguridad

**NOTA**: Esta es una aplicación de desarrollo/demo. Para producción:

- ⚠️ Agregar autenticación
- ⚠️ Validar datos de entrada
- ⚠️ Implementar límites de rate
- ⚠️ Usar HTTPS en producción
- ⚠️ Configurar CORS apropiadamente

## 📞 Soporte

Para más información:
- Ver `README.md` principal del generador
- Ver `GUIA_RAPIDA.md` para documentación técnica
- Contactar al equipo de desarrollo

## 📄 Licencia

Propiedad de **LBS - Lemon Roy**  
Todos los derechos reservados © 2026

---

**Versión Actual:** 2.0 (Mejorada)  
**Última Actualización:** Febrero 2026  
**Estado:** ✅ Funcional - En Desarrollo Activo
