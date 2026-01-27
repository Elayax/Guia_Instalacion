with open('app/rutas.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Eliminar línea 310 específicamente que contiene "import json" fuera de lugar
if lines[309].strip() == 'import json':
    del lines[309]
    print(f"Eliminada línea 310: {lines[309] if len(lines) > 309 else 'N/A'}")
else:
    print(f"Línea 310 actual: {lines[309]}")
    # Buscar cualquier "import json" que esté mal ubicado
    for i, line in enumerate(lines):
        if line.strip() == 'import json' and i > 20:  # Después de los imports iniciales
            print(f"Encontrado import json duplicado en línea {i+1}")
            del lines[i]
            break

with open('app/rutas.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Archivo corregido")
