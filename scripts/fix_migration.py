with open('app/migration_tools.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar y corregir la línea 47
for i, line in enumerate(lines):
    if 'modelo_snap = proyecto.get' in line and '.strip()' in line:
        lines[i] = "        modelo_snap = proyecto.get('modelo_snap') or ''\n"
        print(f"Corregida línea {i+1}")
        break

with open('app/migration_tools.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Archivo corregido exitosamente")
