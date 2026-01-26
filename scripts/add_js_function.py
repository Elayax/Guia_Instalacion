with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar nueva función abrirModalImprimir después de cerrarModalDespuesDeSubmit
new_function = '''

        // --- 1.1 Nueva función para abrir modal de impresión con valores editados ---
        function abrirModalImprimir(esPublicar = false) {
            console.log('=== ABRIENDO MODAL DE IMPRESIÓN ===');
            console.log('Es publicar:', esPublicar);

            // Obtener formularios
            const mainForm = document.getElementById('mainForm');
            const previewForm = document.getElementById('formVistaPrevia');

            if (!mainForm || !previewForm) {
                alert('ERROR: No se encontraron los formularios.');
                return;
            }

            // Limpiar campos clonados anteriores
            const existingClones = previewForm.querySelectorAll('input[type="hidden"]:not([name="accion"])');
            existingClones.forEach(input => input.remove());

            // Cambiar el valor de accion según si es publicar o preview
            const accionInput = previewForm.querySelector('input[name="accion"]');
            if (accionInput) {
                accionInput.value = esPublicar ? 'publicar' : 'preview';
                console.log('Acción configurada:', accionInput.value);
            }

            // Actualizar título del modal
            const modalTitle = document.getElementById('modalTituloPreview');
            if (modalTitle) {
                if (esPublicar) {
                    modalTitle.innerHTML = '<i class="bi bi-check-circle me-2"></i> PUBLICAR - Cargar Imágenes';
                    modalTitle.classList.remove('text-danger');
                    modalTitle.classList.add('text-success');
                } else {
                    modalTitle.innerHTML = '<i class="bi bi-file-earmark-pdf me-2"></i> Vista Previa - Cargar Imágenes';
                    modalTitle.classList.remove('text-success');
                    modalTitle.classList.add('text-danger');
                }
            }

            // Actualizar texto del botón submit
            const submitBtn = document.getElementById('btnSubmitPreview');
            if (submitBtn) {
                if (esPublicar) {
                    submitBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>PUBLICAR PROYECTO';
                    submitBtn.classList.remove('btn-primary');
                    submitBtn.classList.add('btn-success');
                } else {
                    submitBtn.innerHTML = '<i class="bi bi-file-earmark-arrow-down me-2"></i>Generar Vista Previa';
                    submitBtn.classList.remove('btn-success');
                    submitBtn.classList.add('btn-primary');
                }
            }

            // Copiar todos los campos del formulario principal
            const mainInputs = mainForm.querySelectorAll('input, select, textarea');
            mainInputs.forEach(input => {
                if (input.name && input.value) {
                    const clonedInput = document.createElement('input');
                    clonedInput.type = 'hidden';
                    clonedInput.name = input.name;
                    clonedInput.value = input.value;
                    previewForm.appendChild(clonedInput);
                }
            });

            // COPIAR VALORES EDITADOS DE LOS INPUTS
            const editInputs = {
                'i_diseno': document.getElementById('edit_i_diseno'),
                'voltaje': document.getElementById('edit_voltaje'),
                'dv_pct': document.getElementById('edit_dv_pct'),
                'fase_sel': document.getElementById('edit_fase_sel'),
                'breaker_sel': document.getElementById('edit_breaker_sel'),
                'bat_series': document.getElementById('edit_bat_series'),
                'bat_strings': document.getElementById('edit_bat_strings'),
                'bat_total': document.getElementById('edit_bat_total')
            };

            Object.keys(editInputs).forEach(key => {
                const input = editInputs[key];
                if (input && input.value) {
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = key;
                    hiddenInput.value = input.value;
                    previewForm.appendChild(hiddenInput);
                    console.log(`Valor copiado: ${key} = ${input.value}`);
                }
            });

            // ABRIR MODAL
            const modalElement = document.getElementById('vistaPreviewModal');
            if (!modalElement) {
                alert('ERROR: Modal no encontrado.');
                return;
            }

            try {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                console.log('Modal abierto exitosamente');
            } catch (error) {
                console.error('Error al abrir modal:', error);
                alert('ERROR al abrir modal: ' + error.message);
            }
        }
'''

# Buscar donde insertar la nueva función (después de cerrarModalDespuesDeSubmit)
insert_marker = '            return true; // Permitir que el formulario se envíe\r\n        }'
content = content.replace(insert_marker, insert_marker + new_function)

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Función JavaScript abrirModalImprimir agregada exitosamente")
