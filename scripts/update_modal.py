with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Cambiar el action del modal
old_action = '''                <form method="POST" action="{{ url_for('main.calculadora') }}" enctype="multipart/form-data"
                    id="formVistaPrevia">'''

new_action = '''                <form method="POST" action="{{ url_for('main.generar_pdf_calculadora') }}" enctype="multipart/form-data"
                    id="formVistaPrevia">'''

content = content.replace(old_action, new_action)

# 2. Eliminar la función abrirModalVistaPrevia que ya no se usa y el script de auto-descarga
# Primero, eliminar el script de auto-descarga (líneas 1081-1101 en el original)
old_auto_download = '''    <!-- Auto-descarga del PDF si está disponible -->
    {% if pdf_trigger %}
    <script>
        (function() {
            console.log('PDF generado, iniciando descarga automática...');
            const link = document.createElement('a');
            link.href = '{{ pdf_trigger.path }}';
            link.download = '{{ pdf_trigger.filename }}';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Scroll suave a los resultados
            setTimeout(() => {
                const resultsSection = document.querySelector('.tech-matrix');
                if(resultsSection) {
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 500);
        })();
    </script>
    {% endif %}'''

content = content.replace(old_auto_download, '')

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modal y scripts actualizados exitosamente")
