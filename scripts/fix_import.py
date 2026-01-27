with open('app/rutas.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corregir las líneas 7-14 para el import
lines[6] = 'from app.auxiliares import (\n'
lines[7] = '    obtener_datos_plantilla,\n' 
lines[8] = '    procesar_post_gestion,\n'
lines[9] = '    procesar_calculo_ups,\n'
lines[10] = '    guardar_archivo_temporal,\n'
lines[11] = '    guardar_pdf_proyecto,\n'
lines[12] = '    guardar_imagen_proyecto\n'
lines[13] = ')\n'

with open('app/rutas.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Import corregido exitosamente")
