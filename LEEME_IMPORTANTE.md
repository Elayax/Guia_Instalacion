
# ⚠️ CAMBIOS CRITICOS APLICADOS

Hemos realizado una reingeniería completa de la detección de tu UPS Monofásico.

## 1. Problema Solucionado
Las "fases extra" (L2 y L3) seguían apareciendo porque la gráfica se inicializaba siempre como trifásica. Ahora hemos cambiado el código para que **DESTRUYA** y **RE-CREE** los gráficos en modo Monofásico (1 sola línea) cuando detecta tu dispositivo.

## 2. Pasos para ver la solución (OBLIGATORIO)

Al ser cambios en Base de Datos y Javascript, es vital seguir estos 2 pasos:

1.  **DETENER Y REINICIAR LA APP**:
    *   Ve a la terminal donde corre `python app.py`.
    *   Presiona `Ctrl + C` para detenerla.
    *   Ejecuta de nuevo: `python app.py`.
    *   *(Esto es necesario para que el sistema lea la corrección de base de datos que aplicamos: ups_type='invt_minimal')*

2.  **REFRESCAR FORZOSAMENTE EL NAVEGADOR**:
    *   En Chrome/Edge: Presiona `CTRL + SHIFT + R`.
    *   Esto cargará el nuevo código de gráficos.

## 3. Verificación
El sistema ahora detecta tu UPS como "Monofásico" (Protocolo Megatec) y solo mostrará:
*   Voltaje Entrada L1
*   Voltaje Salida L1
*   Batería
*   **GRÁFICOS:** Una sola línea (L1). L2 y L3 han sido eliminadas del código de renderizado.

Si ejecutas `python debug_minimal_client.py` verás que ya estamos leyendo los datos exitosamente.
