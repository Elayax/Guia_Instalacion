with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_button = '''                <button type="button" onclick="descargarPDF()" class="btn btn-primary btn-lg px-5 fw-bold shadow">
                    <i class="bi bi-file-earmark-pdf-fill"></i> DESCARGAR PDF
                </button>'''

new_buttons = '''                <div class="d-flex gap-3">
                    <button type="button" onclick="abrirModalImprimir(false)" class="btn btn-warning btn-lg px-4 fw-bold shadow">
                        <i class="bi bi-eye me-2"></i>VISTA PREVIA PDF
                    </button>
                    <button type="button" onclick="abrirModalImprimir(true)" class="btn btn-primary btn-lg px-4 fw-bold shadow">
                        <i class="bi bi-printer-fill me-2"></i>PUBLICAR PDF
                    </button>
                </div>'''

content = content.replace(old_button, new_buttons)

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Botones reemplazados exitosamente")
