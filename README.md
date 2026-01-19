# Sistema de Gestión y Cálculo para Instalaciones UPS

Este proyecto es una aplicación web desarrollada en **Python** y **Flask** diseñada para automatizar el cálculo de calibres de cables, protecciones eléctricas y la generación de guías de instalación para sistemas UPS (Sistemas de Alimentación Ininterrumpida).

El sistema facilita el cumplimiento de la normativa **NOM-001-SEDE-2012** y gestiona bases de datos de clientes y equipos.

## 🚀 Características Principales

* **Gestión de Clientes:** Base de datos para registrar clientes, sucursales, direcciones y geolocalización.
* **Catálogo de UPS:** Registro de equipos con especificaciones técnicas (Fabricante, Modelo, Potencia, Voltajes de Entrada/Salida).
* **Cálculos Automáticos:**
    * Selección de calibre de conductor (basado en corriente y factor de temperatura).
    * Cálculo de protecciones eléctricas requeridas.
* **Generación de Reportes:** Creación automática de guías de instalación en PDF.
* **Interfaz Web:** Panel de administración amigable para gestionar los datos y realizar los cálculos.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3, Flask.
* **Frontend:** HTML5, CSS3, JavaScript (Jinja2 Templates).
* **Base de Datos:** SQLite.
* **Librerías Clave:**
    * `fpdf` (Generación de PDFs).

## 📋 Requisitos Previos

Necesitas tener instalado **Python 3.8+** y **Git**.

## 🔧 Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/Guia_Instalacion.git](https://github.com/TU_USUARIO/Guia_Instalacion.git)
    cd Guia_Instalacion
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    python run.py
    ```

5.  **Abrir en el navegador:**
    Visita `http://127.0.0.1:5000`

## 📂 Estructura del Proyecto

```text
Guia_Instalacion/
├── app/
│   ├── static/          # Archivos CSS, JS e imágenes
│   ├── templates/       # Plantillas HTML
│   ├── calculos.py      # Lógica de ingeniería eléctrica
│   ├── base_datos.py    # Gestión de SQLite
│   ├── rutas.py         # Controladores de la web
├── run.py               # Punto de entrada de la app
├── requirements.txt     # Lista de dependencias
└── README.md            # Documentación

## 📦 Control de Versiones de la Base de Datos

El archivo de base de datos es `app/sistema_ups_master.db`. Por lo general, Git ignora los archivos `.db`.

Si deseas **compartir los datos** (Clientes/UPS) a través de Git:
1. Edita el archivo `.gitignore` y agrega la línea: `!app/sistema_ups_master.db`
2. O usa el comando: `git add -f app/sistema_ups_master.db`

> **Nota:** Se recomienda usar la función de "Carga Masiva" con archivos CSV para compartir datos iniciales, ya que los archivos binarios `.db` pueden causar conflictos en Git si varias personas los editan al mismo tiempo.
