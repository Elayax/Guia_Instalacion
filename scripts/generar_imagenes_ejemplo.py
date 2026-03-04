"""Genera imágenes de muestra para el PDF de ejemplo.
Las imágenes tienen aspect ratio alto (portrait-friendly) para llenar páginas A4.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'app', 'static', 'img', 'ejemplo'
)
os.makedirs(OUT_DIR, exist_ok=True)

# Colores corporativos
FONDO = (245, 245, 245)
BORDE = (180, 180, 180)
ROJO = (200, 40, 50)
AZUL = (40, 80, 160)
VERDE = (40, 140, 70)
GRIS = (100, 100, 100)
NEGRO = (30, 30, 30)
BLANCO = (255, 255, 255)
AMARILLO = (230, 180, 40)
GRIS_CLARO = (200, 200, 200)


def _font(size=16):
    """Intenta cargar Arial, fallback a default."""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()


def _centrar_texto(draw, text, y, w, font, fill=NEGRO):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) / 2, y), text, font=font, fill=fill)


def _degradado_vertical(draw, x1, y1, x2, y2, color_top, color_bot):
    """Dibuja un degradado vertical entre dos colores."""
    h = y2 - y1
    for i in range(int(h)):
        ratio = i / max(h, 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * ratio)
        draw.line([(x1, y1 + i), (x2, y1 + i)], fill=(r, g, b))


# ============================================================
# 1. PORTADA — UPS estilizada (ratio ~4:3 para portrait)
# ============================================================
def generar_portada():
    w, h = 800, 900
    img = Image.new('RGB', (w, h), BLANCO)
    d = ImageDraw.Draw(img)

    # Fondo degradado
    _degradado_vertical(d, 0, 0, w, h, (235, 235, 245), (210, 210, 225))

    # Gabinete UPS
    gx, gy, gw, gh = 220, 50, 360, 520
    d.rectangle([gx, gy, gx + gw, gy + gh], fill=(45, 45, 55), outline=(25, 25, 35), width=4)

    # Panel frontal
    px, py, pw, ph = gx + 25, gy + 25, gw - 50, gh - 70
    d.rectangle([px, py, px + pw, py + ph], fill=(35, 35, 45), outline=(65, 65, 75), width=2)

    # Display LCD
    lx, ly = px + 40, py + 25
    lw, lh = pw - 80, 100
    d.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=5, fill=(15, 50, 15), outline=(50, 50, 50))
    _centrar_texto(d, "UPS ONLINE", ly + 15, w, _font(22), fill=(0, 200, 0))
    _centrar_texto(d, "60 kVA / 54 kW", ly + 50, w, _font(26), fill=(0, 255, 0))

    # LEDs de estado
    led_y = ly + lh + 40
    colores_led = [(0, 200, 0), (0, 200, 0), (0, 200, 0), AMARILLO, ROJO]
    labels_led = ["AC IN", "INV", "BAT", "TEMP", "ALARM"]
    for i, (c, lbl) in enumerate(zip(colores_led, labels_led)):
        cx = px + 30 + i * 55
        d.ellipse([cx, led_y, cx + 18, led_y + 18], fill=c, outline=(80, 80, 80))
        d.text((cx - 5, led_y + 24), lbl, font=_font(9), fill=(160, 160, 160))

    # Controles
    ctrl_y = led_y + 60
    for i, lbl in enumerate(["ON", "OFF", "BYPASS", "TEST"]):
        bx = px + 20 + i * 70
        d.rounded_rectangle([bx, ctrl_y, bx + 55, ctrl_y + 28], radius=4, fill=(60, 60, 70), outline=(100, 100, 110))
        d.text((bx + 8, ctrl_y + 5), lbl, font=_font(11), fill=(180, 180, 180))

    # Ventilaciones inferiores
    for i in range(6):
        vx = gx + 40 + i * 50
        vy = gy + gh - 45
        for j in range(4):
            d.rectangle([vx, vy + j * 9, vx + 35, vy + j * 9 + 5], fill=(30, 30, 40))

    # Etiquetas
    _centrar_texto(d, "DRAGON POWER PLUS 60", gy + gh + 25, w, _font(24), fill=ROJO)
    _centrar_texto(d, "UPS Online Doble Conversión", gy + gh + 60, w, _font(16), fill=GRIS)
    _centrar_texto(d, "60 kVA / 54 kW / 220V / 3 Fases", gy + gh + 85, w, _font(14), fill=GRIS)

    # Tabla de specs
    sy = gy + gh + 120
    specs = [
        ("Entrada:", "220V 3F+N+T"),
        ("Salida:", "220V 3F+N"),
        ("Baterías:", "240 VDC"),
        ("Peso:", "180 kg"),
        ("Dimensiones:", "659 × 442 × 1740 mm"),
    ]
    d.rectangle([180, sy - 5, 620, sy + len(specs) * 28 + 10], fill=(250, 250, 255), outline=BORDE, width=1)
    for i, (lbl, val) in enumerate(specs):
        d.text((200, sy + 5 + i * 28), lbl, font=_font(13), fill=GRIS)
        d.text((360, sy + 5 + i * 28), val, font=_font(14), fill=NEGRO)

    _centrar_texto(d, "IMAGEN DE EJEMPLO", h - 30, w, _font(11), fill=GRIS_CLARO)

    img.save(os.path.join(OUT_DIR, 'ejemplo_portada.png'), 'PNG')
    print("  [OK] ejemplo_portada.png")


# ============================================================
# 2. DIAGRAMA UNIFILAR AC (ratio ~4:5 para portrait)
# ============================================================
def generar_unifilar():
    w, h = 1000, 1150  # Reducido de 1300 — menos whitespace interno
    img = Image.new('RGB', (w, h), BLANCO)
    d = ImageDraw.Draw(img)

    # Marco y título
    d.rectangle([8, 8, w - 8, h - 8], outline=BORDE, width=2)
    d.rectangle([8, 8, w - 8, 60], fill=(40, 40, 60))
    _centrar_texto(d, "DIAGRAMA UNIFILAR AC", 15, w, _font(24), fill=BLANCO)

    margin = 60
    cx = w // 2  # centro horizontal

    # === ACOMETIDA CFE ===
    by = 90
    bw, bh = 300, 70
    bx = cx - bw // 2
    d.rectangle([bx, by, bx + bw, by + bh], fill=(200, 220, 255), outline=AZUL, width=3)
    _centrar_texto(d, "ACOMETIDA CFE", by + 10, w, _font(18), fill=AZUL)
    _centrar_texto(d, "220V 3F + N + Tierra", by + 38, w, _font(14), fill=GRIS)

    # Línea vertical CFE → Medidor
    d.line([(cx, by + bh), (cx, by + bh + 50)], fill=ROJO, width=4)

    # === MEDIDOR ===
    my = by + bh + 50
    mw, mh = 200, 50
    mx = cx - mw // 2
    d.rectangle([mx, my, mx + mw, my + mh], fill=(255, 250, 235), outline=AMARILLO, width=2)
    _centrar_texto(d, "MEDIDOR CFE", my + 12, w, _font(14), fill=NEGRO)

    d.line([(cx, my + mh), (cx, my + mh + 50)], fill=ROJO, width=4)

    # === INTERRUPTOR GENERAL ===
    iy = my + mh + 50
    iw, ih = 240, 65
    ix = cx - iw // 2
    d.rectangle([ix, iy, ix + iw, iy + ih], fill=(255, 235, 235), outline=ROJO, width=3)
    _centrar_texto(d, "INTERRUPTOR PRINCIPAL", iy + 8, w, _font(14), fill=ROJO)
    _centrar_texto(d, "BREAKER 3P — 200A", iy + 32, w, _font(16), fill=NEGRO)

    d.line([(cx, iy + ih), (cx, iy + ih + 50)], fill=ROJO, width=4)

    # === UPS ===
    uy = iy + ih + 50
    uw, uh = 320, 130
    ux = cx - uw // 2
    d.rectangle([ux, uy, ux + uw, uy + uh], fill=(45, 45, 60), outline=NEGRO, width=4)
    _centrar_texto(d, "UPS", uy + 15, w, _font(28), fill=BLANCO)
    _centrar_texto(d, "60 kVA — DOBLE CONVERSIÓN", uy + 55, w, _font(16), fill=(0, 200, 0))
    _centrar_texto(d, "Entrada: 220V 3F | Salida: 220V 3F", uy + 85, w, _font(12), fill=(160, 160, 160))

    # Etiquetas INPUT/OUTPUT
    d.text((ux - 70, uy + 50), "INPUT", font=_font(12), fill=ROJO)
    d.line([(ux - 10, uy + 60), (ux, uy + 60)], fill=ROJO, width=2)
    d.text((ux + uw + 15, uy + 50), "OUTPUT", font=_font(12), fill=VERDE)
    d.line([(ux + uw, uy + 60), (ux + uw + 10, uy + 60)], fill=VERDE, width=2)

    # === BYPASS (derecha) ===
    bypass_x = ux + uw + 80
    d.line([(cx, iy + ih), (bypass_x, iy + ih)], fill=AMARILLO, width=2)
    d.line([(bypass_x, iy + ih), (bypass_x, uy + uh + 100)], fill=AMARILLO, width=2)
    d.line([(bypass_x, uy + uh + 100), (cx, uy + uh + 100)], fill=AMARILLO, width=2)
    bpx = bypass_x - 50
    bpy = uy + 20
    d.rectangle([bpx, bpy, bpx + 100, bpy + 40], fill=(255, 250, 230), outline=AMARILLO, width=2)
    d.text((bpx + 10, bpy + 8), "BYPASS", font=_font(14), fill=AMARILLO)

    # === BANCO BATERÍAS (izquierda) ===
    bbx, bby = ux - 230, uy + 20
    bbw, bbh = 170, 90
    d.rectangle([bbx, bby, bbx + bbw, bby + bbh], fill=(255, 245, 230), outline=AMARILLO, width=2)
    _centrar_texto(d, "BANCO BATERÍAS", bby + 10, bbx * 2 + bbw, _font(13), fill=NEGRO)
    _centrar_texto(d, "240 VDC", bby + 35, bbx * 2 + bbw, _font(16), fill=ROJO)
    _centrar_texto(d, "2 Strings × 20 uds", bby + 60, bbx * 2 + bbw, _font(11), fill=GRIS)
    d.line([(bbx + bbw, bby + bbh // 2), (ux, uy + uh // 2)], fill=AMARILLO, width=3)
    d.text((bbx + bbw + 5, bby + 30), "DC", font=_font(11), fill=AMARILLO)

    # Salida UPS
    d.line([(cx, uy + uh), (cx, uy + uh + 50)], fill=VERDE, width=4)

    # === BREAKER SALIDA ===
    oby = uy + uh + 50
    obw, obh = 240, 55
    obx = cx - obw // 2
    d.rectangle([obx, oby, obx + obw, oby + obh], fill=(230, 255, 230), outline=VERDE, width=2)
    _centrar_texto(d, "BREAKER SALIDA", oby + 5, w, _font(13), fill=VERDE)
    _centrar_texto(d, "3P — 200A", oby + 28, w, _font(14), fill=NEGRO)

    d.line([(cx, oby + obh), (cx, oby + obh + 50)], fill=VERDE, width=4)

    # === TABLERO DISTRIBUCIÓN ===
    ty = oby + obh + 50
    tw, th = 360, 100
    tx = cx - tw // 2
    d.rectangle([tx, ty, tx + tw, ty + th], fill=(230, 255, 230), outline=VERDE, width=3)
    _centrar_texto(d, "TABLERO DE DISTRIBUCIÓN", ty + 15, w, _font(18), fill=VERDE)
    _centrar_texto(d, "CARGA CRÍTICA", ty + 48, w, _font(20), fill=NEGRO)
    _centrar_texto(d, "Circuitos protegidos por UPS", ty + 75, w, _font(12), fill=GRIS)

    # === INFO CONDUCTORES ===
    iy2 = ty + th + 30
    d.rectangle([40, iy2, w - 40, iy2 + 120], fill=(248, 248, 255), outline=BORDE, width=1)
    d.text((60, iy2 + 8), "CONDUCTORES (NOM-001-SEDE-2012):", font=_font(14), fill=ROJO)
    info_items = [
        "Fases: 3 × 1/0 AWG THHN/THWN-2 Cobre",
        "Neutro: 1 × 1/0 AWG THHN/THWN-2 Cobre (No reducir)",
        "Tierra Física: 1 × 6 AWG Cobre Desnudo / Verde",
        "Canalización: Tubería EMT o Charola tipo escalera",
    ]
    for i, txt in enumerate(info_items):
        d.text((80, iy2 + 35 + i * 20), f"- {txt}", font=_font(12), fill=NEGRO)

    _centrar_texto(d, "DIAGRAMA DE EJEMPLO — NO PARA CONSTRUCCIÓN", h - 30, w, _font(12), fill=GRIS_CLARO)

    img.save(os.path.join(OUT_DIR, 'ejemplo_unifilar.png'), 'PNG')
    print("  [OK] ejemplo_unifilar.png")


# ============================================================
# 3. DIAGRAMA BATERÍAS DC (ratio ~4:5 para portrait)
# ============================================================
def generar_baterias():
    w, h = 1000, 1050  # Reducido de 1250 — menos whitespace interno
    img = Image.new('RGB', (w, h), BLANCO)
    d = ImageDraw.Draw(img)

    d.rectangle([8, 8, w - 8, h - 8], outline=BORDE, width=2)
    d.rectangle([8, 8, w - 8, 60], fill=(40, 40, 60))
    _centrar_texto(d, "CONEXIÓN BANCO DE BATERÍAS DC — 240 VDC", 15, w, _font(22), fill=BLANCO)

    bw, bh = 80, 45  # tamaño de cada batería

    # === STRING 1 ===
    sy1 = 85
    d.text((30, sy1), "STRING 1  —  20 baterías × 12V = 240 VDC", font=_font(16), fill=ROJO)
    d.line([(30, sy1 + 22), (w - 30, sy1 + 22)], fill=(230, 200, 200), width=1)

    # Fila superior (baterías 1-10)
    for i in range(10):
        bx = 30 + i * 96
        by = sy1 + 35
        d.rectangle([bx, by, bx + bw, by + bh], fill=(255, 240, 230), outline=ROJO, width=2)
        d.text((bx + 8, by + 5), f"B{i+1:02d}", font=_font(11), fill=NEGRO)
        d.text((bx + 8, by + 24), "12V", font=_font(10), fill=GRIS)
        # Terminales
        d.rectangle([bx + 15, by - 6, bx + 25, by], fill=ROJO)
        d.rectangle([bx + 55, by - 6, bx + 65, by], fill=AZUL)
        if i > 0:
            d.line([(bx - 16, by + bh // 2), (bx, by + bh // 2)], fill=NEGRO, width=2)

    # Fila inferior (baterías 11-20)
    for i in range(10):
        bx = 30 + i * 96
        by = sy1 + 95
        d.rectangle([bx, by, bx + bw, by + bh], fill=(255, 240, 230), outline=ROJO, width=2)
        d.text((bx + 8, by + 5), f"B{i+11:02d}", font=_font(11), fill=NEGRO)
        d.text((bx + 8, by + 24), "12V", font=_font(10), fill=GRIS)
        if i > 0:
            d.line([(bx - 16, by + bh // 2), (bx, by + bh // 2)], fill=NEGRO, width=2)

    # Conexión entre filas string 1
    last_x = 30 + 9 * 96 + bw
    d.line([(last_x, sy1 + 35 + bh // 2), (last_x + 20, sy1 + 35 + bh // 2)], fill=ROJO, width=3)
    d.line([(last_x + 20, sy1 + 35 + bh // 2), (last_x + 20, sy1 + 95 + bh // 2)], fill=ROJO, width=3)
    d.line([(last_x + 20, sy1 + 95 + bh // 2), (last_x, sy1 + 95 + bh // 2)], fill=ROJO, width=3)

    # === STRING 2 ===
    sy2 = 290
    d.text((30, sy2), "STRING 2  —  20 baterías × 12V = 240 VDC", font=_font(16), fill=AZUL)
    d.line([(30, sy2 + 22), (w - 30, sy2 + 22)], fill=(200, 200, 230), width=1)

    for i in range(10):
        bx = 30 + i * 96
        by = sy2 + 35
        d.rectangle([bx, by, bx + bw, by + bh], fill=(230, 240, 255), outline=AZUL, width=2)
        d.text((bx + 8, by + 5), f"B{i+21:02d}", font=_font(11), fill=NEGRO)
        d.text((bx + 8, by + 24), "12V", font=_font(10), fill=GRIS)
        d.rectangle([bx + 15, by - 6, bx + 25, by], fill=ROJO)
        d.rectangle([bx + 55, by - 6, bx + 65, by], fill=AZUL)
        if i > 0:
            d.line([(bx - 16, by + bh // 2), (bx, by + bh // 2)], fill=NEGRO, width=2)

    for i in range(10):
        bx = 30 + i * 96
        by = sy2 + 95
        d.rectangle([bx, by, bx + bw, by + bh], fill=(230, 240, 255), outline=AZUL, width=2)
        d.text((bx + 8, by + 5), f"B{i+31:02d}", font=_font(11), fill=NEGRO)
        d.text((bx + 8, by + 24), "12V", font=_font(10), fill=GRIS)
        if i > 0:
            d.line([(bx - 16, by + bh // 2), (bx, by + bh // 2)], fill=NEGRO, width=2)

    d.line([(last_x, sy2 + 35 + bh // 2), (last_x + 20, sy2 + 35 + bh // 2)], fill=AZUL, width=3)
    d.line([(last_x + 20, sy2 + 35 + bh // 2), (last_x + 20, sy2 + 95 + bh // 2)], fill=AZUL, width=3)
    d.line([(last_x + 20, sy2 + 95 + bh // 2), (last_x, sy2 + 95 + bh // 2)], fill=AZUL, width=3)

    # === INTERRUPTOR DC ===
    idy = 520
    d.line([(w // 2, sy1 + 160), (w // 2, idy)], fill=ROJO, width=3)
    d.line([(w // 2, sy2 + 160), (w // 2 + 100, sy2 + 160)], fill=AZUL, width=3)
    d.line([(w // 2 + 100, sy2 + 160), (w // 2 + 100, idy + 30)], fill=AZUL, width=3)
    d.line([(w // 2 + 100, idy + 30), (w // 2, idy + 30)], fill=AZUL, width=2)

    diw = 200
    d.rectangle([w // 2 - diw // 2, idy, w // 2 + diw // 2, idy + 60], fill=(255, 250, 235), outline=AMARILLO, width=3)
    _centrar_texto(d, "INTERRUPTOR DC", idy + 8, w, _font(14), fill=NEGRO)
    _centrar_texto(d, "PROTECCIÓN", idy + 30, w, _font(12), fill=AMARILLO)

    # Línea al UPS
    d.line([(w // 2, idy + 60), (w // 2, idy + 120)], fill=ROJO, width=4)

    # === UPS ===
    upy = idy + 120
    upw, uph = 280, 100
    upx = w // 2 - upw // 2
    d.rectangle([upx, upy, upx + upw, upy + uph], fill=(45, 45, 60), outline=NEGRO, width=4)
    _centrar_texto(d, "UPS  60 kVA", upy + 20, w, _font(24), fill=BLANCO)
    _centrar_texto(d, "Conexión DC Baterías", upy + 60, w, _font(14), fill=(0, 200, 0))

    # === TABLA DE ESPECIFICACIONES ===
    ty = upy + uph + 40
    d.rectangle([50, ty, w - 50, ty + 160], fill=(248, 248, 255), outline=BORDE, width=1)
    d.text((70, ty + 10), "ESPECIFICACIONES DEL BANCO DC:", font=_font(16), fill=ROJO)

    specs = [
        ("Modelo Batería:", "LBS12-100 (100Ah 12V VRLA)"),
        ("Configuración:", "2 Strings en paralelo"),
        ("Baterías por String:", "20 unidades en serie"),
        ("Total Baterías:", "40 unidades"),
        ("Voltaje del Banco:", "240 VDC nominal"),
        ("Cable DC:", "Calibre según fabricante — verificar torque"),
    ]
    for i, (lbl, val) in enumerate(specs):
        yy = ty + 40 + i * 20
        d.text((80, yy), lbl, font=_font(12), fill=GRIS)
        d.text((340, yy), val, font=_font(13), fill=NEGRO)

    _centrar_texto(d, "DIAGRAMA DE EJEMPLO — NO PARA CONSTRUCCIÓN", h - 30, w, _font(12), fill=GRIS_CLARO)

    img.save(os.path.join(OUT_DIR, 'ejemplo_baterias.png'), 'PNG')
    print("  [OK] ejemplo_baterias.png")


# ============================================================
# 4. DISPOSICIÓN DE EQUIPOS (ratio ~4:5 para portrait)
# ============================================================
def generar_layout():
    w, h = 900, 970  # Reducido de 1150 — menos whitespace interno
    img = Image.new('RGB', (w, h), BLANCO)
    d = ImageDraw.Draw(img)

    d.rectangle([8, 8, w - 8, h - 8], outline=BORDE, width=2)
    d.rectangle([8, 8, w - 8, 60], fill=(40, 40, 60))
    _centrar_texto(d, "DISPOSICIÓN DE EQUIPOS — VISTA PLANTA", 15, w, _font(22), fill=BLANCO)

    # Sala eléctrica
    rx, ry, rw, rh = 50, 85, 800, 700
    d.rectangle([rx, ry, rx + rw, ry + rh], fill=(248, 248, 248), outline=GRIS, width=3)
    d.text((rx + 15, ry + 8), "SALA ELÉCTRICA / CUARTO UPS", font=_font(14), fill=GRIS)

    # Achurado de piso
    for i in range(rx, rx + rw, 40):
        d.line([(i, ry), (i, ry + rh)], fill=(238, 238, 238), width=1)
    for j in range(ry, ry + rh, 40):
        d.line([(rx, j), (rx + rw, j)], fill=(238, 238, 238), width=1)

    # Puerta
    d.rectangle([rx + rw - 120, ry + rh - 6, rx + rw - 20, ry + rh + 6], fill=BLANCO, outline=NEGRO, width=2)
    d.text((rx + rw - 110, ry + rh - 22), "PUERTA", font=_font(11), fill=GRIS)

    # UPS (centro-izquierda)
    ux, uy = 150, 250
    uww, uhh = 160, 300
    d.rectangle([ux, uy, ux + uww, uy + uhh], fill=(55, 55, 70), outline=NEGRO, width=4)
    _centrar_texto(d, "UPS", uy + 100, (ux + uww // 2) * 2, _font(32), fill=BLANCO)
    _centrar_texto(d, "60 kVA", uy + 150, (ux + uww // 2) * 2, _font(20), fill=(0, 200, 0))
    _centrar_texto(d, "659×442", uy + 190, (ux + uww // 2) * 2, _font(12), fill=(150, 150, 150))
    _centrar_texto(d, "×1740mm", uy + 208, (ux + uww // 2) * 2, _font(12), fill=(150, 150, 150))

    # Cotas UPS
    d.line([(ux, uy - 20), (ux + uww, uy - 20)], fill=ROJO, width=1)
    d.line([(ux, uy - 25), (ux, uy - 15)], fill=ROJO, width=1)
    d.line([(ux + uww, uy - 25), (ux + uww, uy - 15)], fill=ROJO, width=1)
    d.text((ux + 50, uy - 38), "659 mm", font=_font(11), fill=ROJO)

    d.line([(ux - 25, uy), (ux - 25, uy + uhh)], fill=ROJO, width=1)
    d.line([(ux - 30, uy), (ux - 20, uy)], fill=ROJO, width=1)
    d.line([(ux - 30, uy + uhh), (ux - 20, uy + uhh)], fill=ROJO, width=1)
    d.text((ux - 70, uy + 140), "442", font=_font(11), fill=ROJO)

    # Espacio libre frente (abajo del UPS)
    zone_y = uy + uhh + 5
    zone_h = 80
    d.rectangle([ux - 10, zone_y, ux + uww + 10, zone_y + zone_h], outline=VERDE, width=2)
    for i in range(ux - 10, ux + uww + 10, 20):
        d.line([(i, zone_y), (i - 15, zone_y + zone_h)], fill=(210, 240, 210), width=1)
    _centrar_texto(d, "800 mm LIBRE", zone_y + 25, (ux + uww // 2) * 2, _font(13), fill=VERDE)
    _centrar_texto(d, "(FRENTE)", zone_y + 45, (ux + uww // 2) * 2, _font(11), fill=VERDE)

    # Espacio libre atrás (arriba del UPS)
    zone_y2 = uy - 85
    d.rectangle([ux - 10, zone_y2, ux + uww + 10, zone_y2 + zone_h], outline=VERDE, width=2)
    for i in range(ux - 10, ux + uww + 10, 20):
        d.line([(i, zone_y2), (i - 15, zone_y2 + zone_h)], fill=(210, 240, 210), width=1)
    _centrar_texto(d, "800 mm LIBRE", zone_y2 + 25, (ux + uww // 2) * 2, _font(13), fill=VERDE)
    _centrar_texto(d, "(POSTERIOR)", zone_y2 + 45, (ux + uww // 2) * 2, _font(11), fill=VERDE)

    # Rack de baterías (derecha)
    bbx, bby = 450, 200
    bbww, bbhh = 330, 200
    d.rectangle([bbx, bby, bbx + bbww, bby + bbhh], fill=(90, 75, 55), outline=NEGRO, width=3)
    _centrar_texto(d, "RACK DE BATERÍAS", bby + 35, (bbx + bbww // 2) * 2, _font(18), fill=BLANCO)
    _centrar_texto(d, "String 1: 20 × LBS12-100", bby + 70, (bbx + bbww // 2) * 2, _font(13), fill=(220, 200, 180))
    _centrar_texto(d, "String 2: 20 × LBS12-100", bby + 95, (bbx + bbww // 2) * 2, _font(13), fill=(220, 200, 180))
    _centrar_texto(d, "Total: 40 baterías", bby + 130, (bbx + bbww // 2) * 2, _font(14), fill=(255, 230, 200))
    _centrar_texto(d, "240 VDC", bby + 158, (bbx + bbww // 2) * 2, _font(16), fill=AMARILLO)

    # Tablero distribución
    tx, ty = 450, 480
    tww, thh = 330, 130
    d.rectangle([tx, ty, tx + tww, ty + thh], fill=(50, 110, 50), outline=NEGRO, width=3)
    _centrar_texto(d, "TABLERO", ty + 25, (tx + tww // 2) * 2, _font(18), fill=BLANCO)
    _centrar_texto(d, "DISTRIBUCIÓN", ty + 55, (tx + tww // 2) * 2, _font(16), fill=BLANCO)
    _centrar_texto(d, "CARGA CRÍTICA", ty + 85, (tx + tww // 2) * 2, _font(14), fill=(200, 255, 200))

    # Líneas de conexión
    d.line([(ux + uww, uy + 100), (bbx, bby + 100)], fill=AMARILLO, width=3)
    d.text((ux + uww + 10, uy + 80), "DC", font=_font(14), fill=AMARILLO)
    d.line([(ux + uww, uy + 250), (tx, ty + 65)], fill=VERDE, width=3)
    d.text((ux + uww + 10, uy + 255), "AC OUT", font=_font(14), fill=VERDE)
    d.line([(ux + uww // 2, uy), (ux + uww // 2, uy - 5)], fill=ROJO, width=3)
    d.text((ux + uww // 2 + 10, uy - 20), "AC IN", font=_font(12), fill=ROJO)

    # Norte
    nx, ny = w - 70, 90
    d.regular_polygon((nx, ny, 22), 3, rotation=0, fill=GRIS)
    d.text((nx - 5, ny + 25), "N", font=_font(14), fill=NEGRO)

    # Leyenda
    ly = ry + rh + 30
    d.rectangle([50, ly, w - 50, ly + 100], fill=(250, 250, 255), outline=BORDE, width=1)
    d.text((70, ly + 8), "LEYENDA:", font=_font(14), fill=ROJO)

    items = [
        ((55, 55, 70), "UPS 60 kVA"),
        ((90, 75, 55), "Rack de Baterías (40 uds)"),
        ((50, 110, 50), "Tablero Distribución"),
    ]
    for i, (color, lbl) in enumerate(items):
        bx = 80 + i * 250
        d.rectangle([bx, ly + 35, bx + 20, ly + 50], fill=color, outline=NEGRO)
        d.text((bx + 28, ly + 34), lbl, font=_font(12), fill=NEGRO)

    d.rectangle([80, ly + 65, 100, ly + 80], outline=VERDE, width=2)
    d.text((108, ly + 64), "Espacio libre requerido (800mm frente/atrás, 300mm laterales)", font=_font(11), fill=VERDE)

    _centrar_texto(d, "LAYOUT DE EJEMPLO — NO PARA CONSTRUCCIÓN", h - 30, w, _font(12), fill=GRIS_CLARO)

    img.save(os.path.join(OUT_DIR, 'ejemplo_layout.png'), 'PNG')
    print("  [OK] ejemplo_layout.png")


if __name__ == '__main__':
    print("Generando imágenes de ejemplo (portrait-friendly)...")
    generar_portada()
    generar_unifilar()
    generar_baterias()
    generar_layout()
    print(f"\nImágenes guardadas en: {OUT_DIR}")
