with open('app/migration_tools.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar caracteres Unicode problemáticos
content = content.replace('\\u2713', 'OK')
content = content.replace('\\u2717', 'X')
content = content.replace('✓', 'OK')
content = content.replace('✗', 'X')

with open('app/migration_tools.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Caracteres Unicode corregidos")
