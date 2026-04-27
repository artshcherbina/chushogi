#!/usr/bin/env python3
"""
Чу сёги — листы фигур (ryoko_1kanji)
• Ячейка 20×20мм (2×2 см), фигура кадрируется вплотную к полю
• 9 столбцов × 13 строк = 117 слотов: 92 игровых + 25 запасных
• Минимальный текст, узкие поля
• Стр.1 ЛИЦО / Стр.2 СПИНА (зеркало)
"""
import io, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import cairosvg
from PIL import Image

import os
SVG   = "lishogi/ui/@build/pieces/assets/chushogi/ryoko_1kanji"
BLANK = f"{SVG}/blank/big.svg"

pdfmetrics.registerFont(TTFont("JP",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))

# ── Маппинг фигур (front, back=None → пустая деревяшка) ──────────────────────
PIECES = [
    ("Пешка",        "0_PAWN",          "0_PROMOTEDPAWN",     12),
    ("Посредник",    "0_GOBETWEEN",      "0_ELEPHANT",          2),
    ("Медный",       "0_COPPER",         "0_SIDEMOVER",         2),
    ("Серебряный",   "0_SILVER",         "0_VERTICALMOVER",     2),
    ("Золотой",      "0_GOLD",           "0_ROOK",              2),
    ("Свир.барс",    "0_LEOPARD",        "0_BISHOP",            2),
    ("Слеп.тигр",    "0_TIGER",          "0_QUEEN",             2),
    ("Пьян.слон",    "0_ELEPHANT",       "0_PRINCE",            1),
    ("Кирин",        "0_KIRIN",          "0_LIONPROMOTED",      1),
    ("Феникс",       "0_PHOENIX",        "0_QUEENPROMOTED",     1),
    ("Копьё",        "0_LANCE",          "0_WHITEHORSE",        2),
    ("Колесница↑",   "0_CHARIOT",        "0_BISHOPPROMOTED",    2),
    ("Боков.ходок",  "0_SIDEMOVER",      "0_BOAR",              2),
    ("Верт.ходок",   "0_VERTICALMOVER",  "0_OX",                2),
    ("Слон",         "0_BISHOP",         "0_HORSE",             2),
    ("Ладья",        "0_ROOK",           "0_DRAGON",            2),
    ("Дракон-конь",  "0_HORSE",          "0_HORSEPROMOTED",     2),
    ("Дракон-кор.",  "0_DRAGON",         "0_DRAGONPROMOTED",    2),
    ("Своб.кор.",    "0_QUEEN",          None,                  1),
    ("Лев",          "0_LION",           None,                  1),
    ("Король 王",    "0_KING",           None,                  1),
    ("Король 玉",    "0_TAMA",           None,                  1),
]

# ── 92 игровых фигуры ─────────────────────────────────────────────────────────
GAME: list[tuple] = []
for row in PIECES:
    name, front, back, cnt = row
    if name.startswith("Король"):
        GAME.append(row)
    else:
        for _ in range(cnt * 2):
            GAME.append(row)

assert len(GAME) == 92, f"Expected 92, got {len(GAME)}"

# ── 25 запасных фигур пропорционально ────────────────────────────────────────
# Всего на игрока 46. Пешек 12, двухместных ×10 типов, одиночных ×5.
SPARE_N = 25
counts_1p = [(r[0], r[3]) for r in PIECES if not r[0].startswith("Король")]
counts_1p.append(("Король", 1))          # 1 король на игрока
total_1p  = sum(c for _, c in counts_1p) # 46

raw = {name: SPARE_N * cnt / total_1p for name, cnt in counts_1p}
# Округляем по убыванию остатка
floored = {n: int(v) for n, v in raw.items()}
remainder = SPARE_N - sum(floored.values())
by_frac = sorted(raw.items(), key=lambda x: -(x[1] - int(x[1])))
for name, _ in by_frac[:remainder]:
    floored[name] += 1

print(f"Запасных: {sum(floored.values())} (цель {SPARE_N})")
assert sum(floored.values()) == SPARE_N

# Строим список запасных — берём из PIECES по имени
piece_by_name = {r[0]: r for r in PIECES}
piece_by_name["Король"] = ("Король", "0_KING", None, 1)  # запасной король = 王

SPARE: list[tuple] = []
for name, cnt in floored.items():
    if cnt == 0:
        continue
    row = piece_by_name.get(name)
    if row:
        for _ in range(cnt):
            SPARE.append(row)

print(f"Запасные фигуры ({len(SPARE)}):")
from collections import Counter
sc = Counter(r[0] for r in SPARE)
for k, v in sorted(sc.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

ALL = GAME + SPARE   # 92 + 25 = 117

# ── Параметры страницы ────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
PIECE_SZ  = 20.0 * mm   # ячейка разрезки = ровно 2×2 см
GAP       = 1.2  * mm
COLS      = 9
HEADER_H  = 6   * mm    # высота под заголовок
MARGIN_B  = 2   * mm
ROWS      = int((PAGE_H - HEADER_H - MARGIN_B) / (PIECE_SZ + GAP))
GRID_W    = COLS * (PIECE_SZ + GAP) - GAP
OFFSET_X  = (PAGE_W - GRID_W) / 2
TOP_Y     = PAGE_H - HEADER_H - PIECE_SZ / 2

print(f"\nСетка: {COLS}×{ROWS} = {COLS*ROWS} слотов  (игровых {len(GAME)}, запасных {len(SPARE)})")

# ── SVG → PNG с кадрированием паддинга ───────────────────────────────────────
PX = 160   # рендер-разрешение (внутренний буфер)
_cache: dict[str, bytes] = {}

def svg_fitted(path: str) -> bytes:
    if path in _cache:
        return _cache[path]
    # Рендер в 2× для качества
    raw = cairosvg.svg2png(url=path, output_width=PX*2, output_height=PX*2)
    img = Image.open(io.BytesIO(raw)).convert("RGBA")
    bbox = img.getbbox()
    if bbox is None:
        # пустая фигура
        buf = io.BytesIO(); img.resize((PX,PX), Image.LANCZOS).save(buf,"PNG")
        _cache[path] = buf.getvalue(); return _cache[path]
    # Добавим 3% поля вокруг bbox
    pad = int(PX * 2 * 0.03)
    x0 = max(0,          bbox[0] - pad)
    y0 = max(0,          bbox[1] - pad)
    x1 = min(img.width,  bbox[2] + pad)
    y1 = min(img.height, bbox[3] + pad)
    crop = img.crop((x0, y0, x1, y1))
    # Вписываем в квадрат PX×PX, сохраняя пропорции
    cw, ch = crop.size
    scale  = min(PX/cw, PX/ch)
    nw, nh = int(cw*scale), int(ch*scale)
    resized = crop.resize((nw, nh), Image.LANCZOS)
    final = Image.new("RGBA", (PX, PX), (255,255,255,0))
    final.paste(resized, ((PX-nw)//2, (PX-nh)//2))
    buf = io.BytesIO(); final.save(buf, "PNG")
    _cache[path] = buf.getvalue()
    return _cache[path]

def draw_piece(c: canvas.Canvas, cx, cy, path: str):
    data = svg_fitted(path)
    img  = ImageReader(io.BytesIO(data))
    x = cx - PIECE_SZ/2; y = cy - PIECE_SZ/2
    c.drawImage(img, x, y, width=PIECE_SZ, height=PIECE_SZ,
                mask='auto', preserveAspectRatio=True)

# ── Вспомогательное: позиции на странице ──────────────────────────────────────
def page_positions(back=False):
    pos = []
    for r in range(ROWS):
        for col in range(COLS):
            cx = OFFSET_X + col*(PIECE_SZ+GAP) + PIECE_SZ/2
            cy = TOP_Y    - r  *(PIECE_SZ+GAP)
            pos.append((cx, cy))
    if back:
        mirrored = []
        for r in range(ROWS):
            chunk = pos[r*COLS:(r+1)*COLS]
            mirrored.extend(reversed(chunk))
        return mirrored
    return pos

def draw_guides(c: canvas.Canvas, pos):
    c.setStrokeColor(HexColor("#BBBBBB"))
    c.setLineWidth(0.2); c.setDash([1,3])
    for cx,cy in pos:
        hw = PIECE_SZ/2 + GAP/2
        c.rect(cx-hw, cy-hw, hw*2, hw*2, fill=0, stroke=1)
    c.setDash()

def draw_page(c: canvas.Canvas, pieces, back: bool):
    pos = page_positions(back)
    n   = len(pieces)
    draw_guides(c, pos[:n])
    for i,(cx,cy) in enumerate(pos):
        if i >= n: break
        _, front_f, back_f, _ = pieces[i]
        path = (f"{SVG}/{back_f}.svg" if back_f else BLANK) if back \
               else f"{SVG}/{front_f}.svg"
        draw_piece(c, cx, cy, path)
    # Маркер «ЗАПАС» над первым запасным (только лицо)
    if not back and n > 92:
        spare_i = 92
        if spare_i < len(pos):
            cx, cy = pos[spare_i]
            c.setFont("JP", 5); c.setFillColor(HexColor("#999999"))
            c.drawCentredString(cx, cy + PIECE_SZ/2 + 1.5*mm, "запас ↓")

def header(c: canvas.Canvas, title: str, warn: str = ""):
    c.setFont("JP", 9); c.setFillColor(HexColor("#1F1F1F"))
    y = PAGE_H - 4.5*mm
    if warn:
        c.drawString(10*mm, y, title)
        c.setFont("JP", 7); c.setFillColor(HexColor("#CC4400"))
        c.drawRightString(PAGE_W-10*mm, y, warn)
    else:
        c.drawCentredString(PAGE_W/2, y, title)

# ── Генерация PDF ─────────────────────────────────────────────────────────────
print("\nРендеринг...")
os.makedirs("pieces", exist_ok=True)
OUT = "pieces/chu_shogi_pieces.pdf"
c   = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("Чу сёги — фигуры")

draw_page(c, ALL, back=False)
c.showPage()

draw_page(c, ALL, back=True)
c.showPage()
c.save()

# ── Отчёт о размерах ──────────────────────────────────────────────────────────
print(f"\nСохранено: {OUT}")
print(f"\n=== РАЗМЕРЫ ===")
# Замер реального размера фигуры в ячейке
test = cairosvg.svg2png(url=f"{SVG}/0_PAWN.svg", output_width=400, output_height=400)
img  = Image.open(io.BytesIO(test)).convert("RGBA")
bbox = img.getbbox()
pad  = int(400*0.03)
x0   = max(0, bbox[0]-pad); y0 = max(0, bbox[1]-pad)
x1   = min(400, bbox[2]+pad); y1 = min(400, bbox[3]+pad)
cw   = x1-x0; ch = y1-y0
scale_to_cell = min(PX/cw, PX/ch)
# В реальных мм при PIECE_SZ=20мм
cell_mm = 20.0
piece_w_mm = cell_mm * (scale_to_cell * cw / PX)
piece_h_mm = cell_mm * (scale_to_cell * ch / PX)
print(f"Ячейка разрезки:   {cell_mm:.0f} × {cell_mm:.0f} мм  (ровно 2×2 см ✓)")
print(f"Фигура в ячейке:   {piece_w_mm:.1f} × {piece_h_mm:.1f} мм")
print(f"Поля:              {OFFSET_X/mm:.1f} мм слева/справа")
