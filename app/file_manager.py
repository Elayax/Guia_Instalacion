# -*- coding: utf-8 -*-
"""
FileManager - Gestión centralizada de archivos del sistema
Maneja PDFs, imágenes y archivos temporales de forma consistente.
"""
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

class FileManager:
    """Gestor centralizado de archivos para el sistema UPS"""
    
    def __init__(self, base_dir=None):
        """
        Inicializa el FileManager
        
        Args:
            base_dir: Directorio base de la aplicación (por defecto usa __file__)
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_dir = base_dir
        self.static_dir = os.path.join(base_dir, 'app', 'static')
        self.temp_dir = os.path.join(self.static_dir, 'temp')
        self.pdf_dir = os.path.join(self.static_dir, 'pdf', 'proyectos')
        self.img_dir = os.path.join(self.static_dir, 'img', 'proyectos')
        
        # Crear directorios si no existen
        for directory in [self.temp_dir, self.pdf_dir, self.img_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def _get_safe_filename(self, filename):
        """Retorna un nombre de archivo seguro"""
        return secure_filename(filename)
    
    def validar_formato_imagen(self, file):
        """
        Valida que el archivo sea una imagen válida
        
        Args:
            file: FileStorage object de Flask
        
        Returns:
            tuple: (es_valido, mensaje_error)
        """
        if not file or not file.filename:
            return False, "No se proporcionó ningún archivo"
        
        extensiones_permitidas = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}
        _, ext = os.path.splitext(file.filename.lower())
        
        if ext not in extensiones_permitidas:
            return False, f"Formato no permitido. Use: {', '.join(extensiones_permitidas)}"
        
        # Verificar tamaño (max 10MB)
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Regresar al inicio
        
        max_size = 10 * 1024 * 1024  # 10MB
        if size > max_size:
            return False, f"El archivo es demasiado grande ({size/1024/1024:.1f}MB). Máximo: 10MB"
        
        return True, "OK"
    
    def obtener_ruta_proyecto(self, pedido, tipo='pdf'):
        """
        Obtiene o crea la ruta del directorio de un proyecto
        
        Args:
            pedido: Número de pedido
            tipo: 'pdf' o 'img'
        
        Returns:
            str: Ruta absoluta al directorio del proyecto
        """
        base = self.pdf_dir if tipo == 'pdf' else self.img_dir
        ruta_proyecto = os.path.join(base, str(pedido))
        os.makedirs(ruta_proyecto, exist_ok=True)
        return ruta_proyecto
    
    def guardar_pdf_proyecto(self, pdf_bytes, pedido, tipo='guia'):
        """
        Guarda un PDF en el directorio del proyecto
        
        Args:
            pdf_bytes: Bytes del PDF
            pedido: Número de pedido
            tipo: 'guia' o 'checklist'
        
        Returns:
            str: Ruta relativa al PDF guardado (para guardar en BD)
        """
        ruta_proyecto = self.obtener_ruta_proyecto(pedido, tipo='pdf')
        
        # Nombre del archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if tipo == 'guia':
            filename = f'Guia_Instalacion_{pedido}_{timestamp}.pdf'
        else:
            filename = f'Checklist_{pedido}_{timestamp}.pdf'
        
        ruta_completa = os.path.join(ruta_proyecto, filename)
        
        # Guardar archivo
        with open(ruta_completa, 'wb') as f:
            f.write(pdf_bytes)
        
        # Retornar ruta relativa
        ruta_relativa = os.path.join('pdf', 'proyectos', str(pedido), filename)
        return ruta_relativa.replace('\\', '/')  # Normalizar para web
    
    def guardar_imagen_proyecto(self, file, pedido, tipo=None):
        """
        Guarda una imagen en el directorio del proyecto
        
        Args:
            file: FileStorage object de Flask
            pedido: Número de pedido
            tipo: Tipo de imagen (opcional, para el nombre)
        
        Returns:
            str: Nombre del archivo guardado
        """
        # Validar formato
        valido, mensaje = self.validar_formato_imagen(file)
        if not valido:
            raise ValueError(mensaje)
        
        ruta_proyecto = self.obtener_ruta_proyecto(pedido, tipo='img')
        
        # Generar nombre seguro
        nombre_original = self._get_safe_filename(file.filename)
        nombre_base, extension = os.path.splitext(nombre_original)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if tipo:
            filename = f'{tipo}_{timestamp}{extension}'
        else:
            filename = f'{nombre_base}_{timestamp}{extension}'
        
        ruta_completa = os.path.join(ruta_proyecto, filename)
        
        # Guardar archivo
        file.save(ruta_completa)
        
        return filename
    
    def guardar_temporal(self, file):
        """
        Guarda un archivo en el directorio temporal
        
        Args:
            file: FileStorage object de Flask
        
        Returns:
            str: Ruta absoluta al archivo temporal
        """
        nombre_seguro = self._get_safe_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_base, extension = os.path.splitext(nombre_seguro)
        filename = f'temp_{nombre_base}_{timestamp}{extension}'
        
        ruta_completa = os.path.join(self.temp_dir, filename)
        file.save(ruta_completa)
        
        return ruta_completa
    
    def limpiar_archivos_temporales(self, dias_antiguedad=7):
        """
        Elimina archivos temporales antiguos
        
        Args:
            dias_antiguedad: Eliminar archivos más antiguos que estos días
        
        Returns:
            tuple: (archivos_eliminados, espacio_liberado_mb)
        """
        if not os.path.exists(self.temp_dir):
            return 0, 0
        
        limite = datetime.now() - timedelta(days=dias_antiguedad)
        archivos_eliminados = 0
        espacio_liberado = 0
        
        for filename in os.listdir(self.temp_dir):
            filepath = os.path.join(self.temp_dir, filename)
            
            if os.path.isfile(filepath):
                # Verificar fecha de modificación
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if mtime < limite:
                    try:
                        size = os.path.getsize(filepath)
                        os.remove(filepath)
                        archivos_eliminados += 1
                        espacio_liberado += size
                    except Exception as e:
                        print(f"Error eliminando {filename}: {e}")
        
        espacio_mb = espacio_liberado / (1024 * 1024)
        return archivos_eliminados, espacio_mb
    
    def crear_backup_db(self, db_path=None):
        """
        Crea un backup de la base de datos PostgreSQL usando pg_dump.

        Returns:
            str: Ruta al archivo de backup creado
        """
        import subprocess
        from app.config import BaseConfig

        backup_dir = os.path.join(self.base_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'ups_manager_backup_{timestamp}.sql'
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            result = subprocess.run(
                ['pg_dump', BaseConfig.DATABASE_URL, '-f', backup_path],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                raise RuntimeError(f"pg_dump failed: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError("pg_dump no encontrado. Instalar PostgreSQL client tools.")

        return backup_path
    
    def obtener_ruta_completa_imagen(self, pedido, nombre_archivo):
        """
        Obtiene la ruta completa de una imagen de proyecto
        
        Args:
            pedido: Número de pedido
            nombre_archivo: Nombre del archivo de imagen
        
        Returns:
            str: Ruta absoluta a la imagen
        """
        return os.path.join(self.obtener_ruta_proyecto(pedido, tipo='img'), nombre_archivo)
    
    def obtener_ruta_completa_pdf(self, ruta_relativa):
        """
        Convierte una ruta relativa de PDF a ruta absoluta
        
        Args:
            ruta_relativa: Ruta relativa (ej: 'pdf/proyectos/123/Guia_123.pdf')
        
        Returns:
            str: Ruta absoluta al PDF
        """
        return os.path.join(self.static_dir, ruta_relativa.replace('/', os.sep))
