# Guía Rápida - Aplicación Standalone de Reportes LBS

## 🚀 Inicio Rápido

### Opción 1: Usando Python directamente
```bash
cd Reportes
python app_reportes.py
```

### Opción 2: Usando el script de Windows
```bash
cd Reportes
.\iniciar_reportes.bat
```

## 📋 Acceso

Una vez iniciada la aplicación, abre tu navegador en:

- **Página Principal:** http://localhost:5001
- **Información:** http://localhost:5001/info

## ⚠️ IMPORTANTE

1. **Puerto Diferente:** Esta aplicación corre en el puerto **5001** (NO 5000)
2. **Independiente:** NO está conectada al sistema principal que corre en puerto 5000
3. **Datos de Prueba:** Los reportes generados contienen datos de ejemplo

## 🎯 ¿Qué hace esta aplicación?

- Muestra los **avances del generador de reportes PDF**
- Permite generar **reportes PDF de muestra** con un solo click
- Funciona de manera **completamente independiente** del sistema principal
- No requiere base de datos ni configuración compleja

## 📁 Archivos Generados

Los PDFs se guardan en:
```
Reportes/output/
```

Cada archivo tiene un timestamp único:
```
reporte_muestra_20260212_153045.pdf
```

## 🔧 Requisitos

Asegúrate de tener instalado:

```bash
pip install reportlab flask
```

O instala desde el archivo de requirements:
```bash
cd Reportes
pip install -r requirements.txt
```

## 🛑 Detener la Aplicación

Para detener el servidor:
- Presiona `Ctrl+C` en la terminal

## 🐛 Solución de Problemas

### Error: Puerto 5001 en uso
```bash
# Cambia el puerto en app_reportes.py línea ~200:
app.run(
    host='0.0.0.0',
    port=5002,  # Cambiar a otro puerto disponible
    debug=True
)
```

### Error: No module named 'reportlab'
```bash
pip install reportlab
```

### Error: Template not found
Verifica que existe la carpeta:
```
Reportes/
  ├── templates/
  │   └── reporte_demo.html
  └── app_reportes.py
```

## 📞 Soporte

Para más información sobre el generador de reportes, consulta:
- `README.md` - Documentación completa
- `GUIA_RAPIDA.md` - Guía de uso del generador
- `plantilla_datos.py` - Estructura de datos

## 🎨 Próximos Desarrollos

- [ ] Integración con formulario de captura
- [ ] Conexión con base de datos
- [ ] Generación dinámica basada en datos reales
- [ ] Múltiples plantillas de reportes
- [ ] Firma digital

---

**Versión:** 2.0  
**Fecha:** Febrero 2026  
**Desarrollado por:** LBS - Lemon Roy
