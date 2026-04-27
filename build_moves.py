#!/usr/bin/env python3
"""
Chu Shogi — move diagrams for all 21 piece types.
Moves verified against Wikipedia. Range pieces go to grid edge.
Usage: python3 build_moves.py [lang]   (default: en)
Supported: en de fr es ja ru
"""
import io, math, os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import cairosvg
from PIL import Image as PILImage

pdfmetrics.registerFont(TTFont("JPb", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))
pdfmetrics.registerFont(TTFont("LAT", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))

LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
if LANG not in ("en", "de", "fr", "es", "ja", "ru"):
    print(f"Unknown lang '{LANG}', defaulting to 'en'"); LANG = "en"
FONT = "JPb" if LANG == "ja" else "LAT"

SVG = "lishogi/ui/@build/pieces/assets/chushogi/ryoko_1kanji"
os.makedirs(LANG, exist_ok=True)
OUT = f"{LANG}/chu_shogi_moves.pdf"

C_GRID     = HexColor("#CCBFA8")
C_CENTER   = HexColor("#EDE0C4")
C_STEP     = HexColor("#CC2200")
C_LION2    = HexColor("#FF8800")
C_BG       = HexColor("#FDF8F0")
C_PROMO_BG = HexColor("#FFF0F0")
C_BLACK    = HexColor("#1A1A1A")
C_RED      = HexColor("#AA1100")

NO_PROMO = "NO_PROMO"

TRANSLATIONS = {
    "en": {
        "pawn":         "Pawn",
        "tokin":        "Tokin\n(Gold)",
        "gobetween":    "Go-Between",
        "drunk_el_p":   "Drunk\nElephant",
        "copper":       "Copper\nGeneral",
        "sidemover_p":  "Side Mover",
        "silver":       "Silver\nGeneral",
        "vertmover_p":  "Vertical\nMover",
        "gold":         "Gold\nGeneral",
        "rook_p":       "Rook",
        "leopard":      "Fierce\nLeopard",
        "bishop_p":     "Bishop",
        "tiger":        "Blind Tiger",
        "flying_stag":  "Flying Stag",
        "elephant":     "Drunk\nElephant",
        "crown_prince": "Crown\nPrince",
        "kirin":        "Kirin",
        "lion_k":       "Lion\n(Kirin)",
        "phoenix":      "Phoenix",
        "freeking_p":   "Free King",
        "lance":        "Lance",
        "white_horse":  "White Horse",
        "chariot":      "Reverse\nChariot",
        "whale":        "Whale",
        "sidemover":    "Side Mover",
        "boar":         "Running Boar",
        "vertmover":    "Vertical\nMover",
        "flying_ox":    "Flying Ox",
        "bishop":       "Bishop",
        "dhorse_p":     "Dragon\nHorse",
        "rook":         "Rook",
        "dking_p":      "Dragon\nKing",
        "dhorse":       "Dragon\nHorse",
        "horned_falcon":"Horned\nFalcon",
        "dking":        "Dragon\nKing",
        "soaring_eagle":"Soaring\nEagle",
        "freeking":     "Free King",
        "lion":         "Lion",
        "king":         "King",
    },
    "de": {
        "pawn":         "Bauer",
        "tokin":        "Tokin\n(Gold)",
        "gobetween":    "Vermittler",
        "drunk_el_p":   "Trunkener\nElefant",
        "copper":       "Kupfer-\nGeneral",
        "sidemover_p":  "Seitläufer",
        "silver":       "Silber-\nGeneral",
        "vertmover_p":  "Vertikaler\nLäufer",
        "gold":         "Gold-\nGeneral",
        "rook_p":       "Turm",
        "leopard":      "Heftiger\nLeopard",
        "bishop_p":     "Läufer",
        "tiger":        "Blinder\nTiger",
        "flying_stag":  "Fliegender\nHirsch",
        "elephant":     "Trunkener\nElefant",
        "crown_prince": "Kronprinz",
        "kirin":        "Kirin",
        "lion_k":       "Löwe\n(Kirin)",
        "phoenix":      "Phönix",
        "freeking_p":   "Freier\nKönig",
        "lance":        "Lanze",
        "white_horse":  "Weißes\nPferd",
        "chariot":      "Rückwärts-\nWagen",
        "whale":        "Wal",
        "sidemover":    "Seitläufer",
        "boar":         "Laufender\nEber",
        "vertmover":    "Vertikaler\nLäufer",
        "flying_ox":    "Fliegender\nOchse",
        "bishop":       "Läufer",
        "dhorse_p":     "Drachen-\nPferd",
        "rook":         "Turm",
        "dking_p":      "Drachen-\nKönig",
        "dhorse":       "Drachen-\nPferd",
        "horned_falcon":"Gehörnter\nFalke",
        "dking":        "Drachen-\nKönig",
        "soaring_eagle":"Schwebender\nAdler",
        "freeking":     "Freier\nKönig",
        "lion":         "Löwe",
        "king":         "König",
    },
    "fr": {
        "pawn":         "Pion",
        "tokin":        "Tokin\n(Or)",
        "gobetween":    "Intermédiaire",
        "drunk_el_p":   "Éléphant\nivre",
        "copper":       "Général de\nCuivre",
        "sidemover_p":  "Coulisseur\nLatéral",
        "silver":       "Général\nd'Argent",
        "vertmover_p":  "Coulisseur\nVertical",
        "gold":         "Général\nd'Or",
        "rook_p":       "Tour",
        "leopard":      "Léopard\nFéroce",
        "bishop_p":     "Fou",
        "tiger":        "Tigre\nAveugle",
        "flying_stag":  "Cerf\nVolant",
        "elephant":     "Éléphant\nivre",
        "crown_prince": "Prince\nHéritier",
        "kirin":        "Kirin",
        "lion_k":       "Lion\n(Kirin)",
        "phoenix":      "Phénix",
        "freeking_p":   "Roi Libre",
        "lance":        "Lance",
        "white_horse":  "Cheval\nBlanc",
        "chariot":      "Char\nInversé",
        "whale":        "Baleine",
        "sidemover":    "Coulisseur\nLatéral",
        "boar":         "Sanglier\nCourant",
        "vertmover":    "Coulisseur\nVertical",
        "flying_ox":    "Bœuf\nVolant",
        "bishop":       "Fou",
        "dhorse_p":     "Cheval\nDragon",
        "rook":         "Tour",
        "dking_p":      "Roi\nDragon",
        "dhorse":       "Cheval\nDragon",
        "horned_falcon":"Faucon\nCornu",
        "dking":        "Roi\nDragon",
        "soaring_eagle":"Aigle\nPlanant",
        "freeking":     "Roi Libre",
        "lion":         "Lion",
        "king":         "Roi",
    },
    "es": {
        "pawn":         "Peón",
        "tokin":        "Tokin\n(Oro)",
        "gobetween":    "Intermediario",
        "drunk_el_p":   "Elefante\nEbrio",
        "copper":       "General\nde Cobre",
        "sidemover_p":  "Deslizador\nLateral",
        "silver":       "General\nde Plata",
        "vertmover_p":  "Deslizador\nVertical",
        "gold":         "General\nde Oro",
        "rook_p":       "Torre",
        "leopard":      "Leopardo\nFeroz",
        "bishop_p":     "Alfil",
        "tiger":        "Tigre\nCiego",
        "flying_stag":  "Ciervo\nVolador",
        "elephant":     "Elefante\nEbrio",
        "crown_prince": "Príncipe\nHeredero",
        "kirin":        "Kirin",
        "lion_k":       "León\n(Kirin)",
        "phoenix":      "Fénix",
        "freeking_p":   "Rey Libre",
        "lance":        "Lanza",
        "white_horse":  "Caballo\nBlanco",
        "chariot":      "Carro\nInverso",
        "whale":        "Ballena",
        "sidemover":    "Deslizador\nLateral",
        "boar":         "Jabalí\nCorredor",
        "vertmover":    "Deslizador\nVertical",
        "flying_ox":    "Buey\nVolador",
        "bishop":       "Alfil",
        "dhorse_p":     "Caballo\nDragón",
        "rook":         "Torre",
        "dking_p":      "Rey\nDragón",
        "dhorse":       "Caballo\nDragón",
        "horned_falcon":"Halcón\nCornudo",
        "dking":        "Rey\nDragón",
        "soaring_eagle":"Águila\nAlta",
        "freeking":     "Rey Libre",
        "lion":         "León",
        "king":         "Rey",
    },
    "ru": {
        "pawn":         "Пешка",
        "tokin":        "Золотой\n(то-кин)",
        "gobetween":    "Посредник",
        "drunk_el_p":   "Пьяный\nслон",
        "copper":       "Медный\nгенерал",
        "sidemover_p":  "Боковой\nходок",
        "silver":       "Серебряный\nгенерал",
        "vertmover_p":  "Вертикальный\nходок",
        "gold":         "Золотой\nгенерал",
        "rook_p":       "Ладья",
        "leopard":      "Свирепый\nбарс",
        "bishop_p":     "Слон",
        "tiger":        "Слепой\nтигр",
        "flying_stag":  "Летящий\nолень",
        "elephant":     "Пьяный\nслон",
        "crown_prince": "Кронпринц",
        "kirin":        "Кирин",
        "lion_k":       "Лев\n(Кирин)",
        "phoenix":      "Феникс",
        "freeking_p":   "Свободный\nкороль",
        "lance":        "Копьё",
        "white_horse":  "Белая\nлошадь",
        "chariot":      "Колесница\nназад",
        "whale":        "Кит",
        "sidemover":    "Боковой\nходок",
        "boar":         "Бегущий\nкабан",
        "vertmover":    "Вертикальный\nходок",
        "flying_ox":    "Летящий\nбык",
        "bishop":       "Слон",
        "dhorse_p":     "Дракон-\nконь",
        "rook":         "Ладья",
        "dking_p":      "Дракон-\nкороль",
        "dhorse":       "Дракон-\nконь",
        "horned_falcon":"Рогатый\nсокол",
        "dking":        "Дракон-\nкороль",
        "soaring_eagle":"Парящий\nорёл",
        "freeking":     "Свободный\nкороль",
        "lion":         "Лев",
        "king":         "Король",
    },
    "ja": {
        "pawn":         "歩兵",
        "tokin":        "と金",
        "gobetween":    "仲人",
        "drunk_el_p":   "酔象",
        "copper":       "銅将",
        "sidemover_p":  "横行",
        "silver":       "銀将",
        "vertmover_p":  "竪行",
        "gold":         "金将",
        "rook_p":       "飛車",
        "leopard":      "猛豹",
        "bishop_p":     "角行",
        "tiger":        "盲虎",
        "flying_stag":  "飛鹿",
        "elephant":     "酔象",
        "crown_prince": "太子",
        "kirin":        "麒麟",
        "lion_k":       "獅子\n(麒麟)",
        "phoenix":      "鳳凰",
        "freeking_p":   "奔王",
        "lance":        "香車",
        "white_horse":  "白駒",
        "chariot":      "反車",
        "whale":        "鯨鯢",
        "sidemover":    "横行",
        "boar":         "奔猪",
        "vertmover":    "竪行",
        "flying_ox":    "飛牛",
        "bishop":       "角行",
        "dhorse_p":     "龍馬",
        "rook":         "飛車",
        "dking_p":      "龍王",
        "dhorse":       "龍馬",
        "horned_falcon":"角鷹",
        "dking":        "龍王",
        "soaring_eagle":"飛鷲",
        "freeking":     "奔王",
        "lion":         "獅子",
        "king":         "王将",
    },
}

# drow += forward (top of diagram), dcol += right
PAIRS = [
  ("pawn","0_PAWN",
   {'steps':[(1,0)]},
   "tokin","0_PROMOTEDPAWN",
   {'steps':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,0)]}),

  ("gobetween","0_GOBETWEEN",
   {'steps':[(1,0),(-1,0)]},
   "drunk_el_p","0_ELEPHANTPROMOTED",
   {'steps':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,1),(-1,-1)]}),

  ("copper","0_COPPER",
   {'steps':[(1,0),(1,1),(1,-1),(-1,0)]},
   "sidemover_p","0_SIDEMOVERPROMOTED",
   {'range':[(0,1),(0,-1)],'steps':[(1,0),(-1,0)]}),

  ("silver","0_SILVER",
   {'steps':[(1,0),(1,1),(1,-1),(-1,1),(-1,-1)]},
   "vertmover_p","0_VERTICALMOVERPROMOTED",
   {'range':[(1,0),(-1,0)],'steps':[(0,1),(0,-1)]}),

  ("gold","0_GOLD",
   {'steps':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,0)]},
   "rook_p","0_ROOKPROMOTED",
   {'range':[(1,0),(0,1),(0,-1),(-1,0)]}),

  ("leopard","0_LEOPARD",
   {'steps':[(1,0),(1,1),(1,-1),(-1,0),(-1,1),(-1,-1)]},
   "bishop_p","0_BISHOPPROMOTED",
   {'range':[(1,1),(1,-1),(-1,1),(-1,-1)]}),

  ("tiger","0_TIGER",
   {'steps':[(1,1),(1,-1),(0,1),(0,-1),(-1,0),(-1,1),(-1,-1)]},
   "flying_stag","0_STAG",
   {'range':[(1,0),(-1,0)],'steps':[(1,1),(1,-1),(0,1),(0,-1),(-1,1),(-1,-1)]}),

  ("elephant","0_ELEPHANT",
   {'steps':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,1),(-1,-1)]},
   "crown_prince","0_PRINCE",
   {'steps':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,0),(-1,1),(-1,-1)]}),

  ("kirin","0_KIRIN",
   {'steps':[(1,1),(1,-1),(-1,1),(-1,-1)],'jump2':[(2,0),(-2,0),(0,2),(0,-2)]},
   "lion_k","0_LIONPROMOTED",
   {'lion':True}),

  ("phoenix","0_PHOENIX",
   {'steps':[(1,0),(-1,0),(0,1),(0,-1)],'jump2':[(2,2),(2,-2),(-2,2),(-2,-2)]},
   "freeking_p","0_QUEENPROMOTED",
   {'range':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,0),(-1,1),(-1,-1)]}),

  ("lance","0_LANCE",
   {'range':[(1,0)]},
   "white_horse","0_WHITEHORSE",
   {'range':[(1,0),(1,1),(1,-1),(-1,0)]}),

  ("chariot","0_CHARIOT",
   {'range':[(1,0),(-1,0)]},
   "whale","0_WHALE",
   {'range':[(1,0),(-1,0),(-1,1),(-1,-1)]}),

  ("sidemover","0_SIDEMOVER",
   {'range':[(0,1),(0,-1)],'steps':[(1,0),(-1,0)]},
   "boar","0_BOAR",
   {'range':[(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]}),

  ("vertmover","0_VERTICALMOVER",
   {'range':[(1,0),(-1,0)],'steps':[(0,1),(0,-1)]},
   "flying_ox","0_OX",
   {'range':[(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]}),

  ("bishop","0_BISHOP",
   {'range':[(1,1),(1,-1),(-1,1),(-1,-1)]},
   "dhorse_p","0_HORSEPROMOTED",
   {'range':[(1,1),(1,-1),(-1,1),(-1,-1)],'steps':[(1,0),(0,1),(0,-1),(-1,0)]}),

  ("rook","0_ROOK",
   {'range':[(1,0),(0,1),(0,-1),(-1,0)]},
   "dking_p","0_DRAGONPROMOTED",
   {'range':[(1,0),(0,1),(0,-1),(-1,0)],'steps':[(1,1),(1,-1),(-1,1),(-1,-1)]}),

  ("dhorse","0_HORSE",
   {'range':[(1,1),(1,-1),(-1,1),(-1,-1)],'steps':[(1,0),(0,1),(0,-1),(-1,0)]},
   "horned_falcon","0_FALCON",
   {'range':[(1,1),(1,-1),(-1,1),(-1,-1)],'steps':[(1,0),(0,1),(0,-1),(-1,0)],'jump2':[(2,0)]}),

  ("dking","0_DRAGON",
   {'range':[(1,0),(0,1),(0,-1),(-1,0)],'steps':[(1,1),(1,-1),(-1,1),(-1,-1)]},
   "soaring_eagle","0_EAGLE",
   {'range':[(1,0),(0,1),(0,-1),(-1,0)],'steps':[(1,1),(1,-1),(-1,1),(-1,-1)],'jump2':[(2,2),(2,-2)]}),

  ("freeking","0_QUEEN",
   {'range':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,0),(-1,1),(-1,-1)]},
   NO_PROMO,None,None),

  ("lion","0_LION",
   {'lion':True},
   NO_PROMO,None,None),

  ("king","0_KING",
   {'steps':[(1,0),(1,1),(1,-1),(0,1),(0,-1),(-1,0),(-1,1),(-1,-1)]},
   NO_PROMO,None,None),
]

# ── Layout ────────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
COLS         = 4
MARGIN_X     = 6*mm
MARGIN_Y_TOP = 10*mm
MARGIN_Y_BOT = 3*mm
LABEL_H      = 11*mm

AVAIL_W  = PAGE_W - 2*MARGIN_X
AVAIL_H  = PAGE_H - MARGIN_Y_TOP - MARGIN_Y_BOT
DIAG_W   = AVAIL_W / COLS

GRID_N   = 5
CELL     = (DIAG_W * 0.86) / GRID_N
GRID_SZ  = GRID_N * CELL
ROW_GAP  = 2*mm
DIAG_H   = GRID_SZ + LABEL_H + ROW_GAP

ROWS_PP  = int(AVAIL_H / DIAG_H)
PER_PAGE = COLS * ROWS_PP

print(f"Cell={CELL/mm:.1f}mm  Grid={GRID_SZ/mm:.1f}mm  Rows={ROWS_PP}  Slots={PER_PAGE}")

# ── SVG → PNG ─────────────────────────────────────────────────────────────────
_cache = {}
def piece_png(name):
    if name in _cache: return _cache[name]
    raw = cairosvg.svg2png(url=f"{SVG}/{name}.svg", output_width=200, output_height=200)
    img = PILImage.open(io.BytesIO(raw)).convert("RGBA")
    bb  = img.getbbox()
    if bb:
        p = int(200*0.025)
        img = img.crop((max(0,bb[0]-p),max(0,bb[1]-p),
                        min(200,bb[2]+p),min(200,bb[3]+p)))
    sz = max(img.size)
    sq = PILImage.new("RGBA",(sz,sz),(0,0,0,0))
    sq.paste(img,((sz-img.width)//2,(sz-img.height)//2))
    sq = sq.resize((150,150), PILImage.LANCZOS)
    buf = io.BytesIO(); sq.save(buf,"PNG")
    _cache[name] = buf.getvalue()
    return _cache[name]

def cc(gx,gy,row,col):
    return gx+col*CELL+CELL/2, gy+(GRID_N-1-row)*CELL+CELL/2

def tg(drow,dcol): return 2-drow, 2+dcol

def range_edge(gx, gy, drow, dcol):
    ex = gx + GRID_SZ if dcol > 0 else (gx if dcol < 0 else gx+2*CELL+CELL/2)
    ey = gy + GRID_SZ if drow > 0 else (gy if drow < 0 else gy+2*CELL+CELL/2)
    return ex, ey

def arrowhead(c, x0, y0, x1, y1, sz):
    a = math.atan2(y1-y0, x1-x0)
    tip_x = x1 - sz*0.3*math.cos(a)
    tip_y = y1 - sz*0.3*math.sin(a)
    p = c.beginPath()
    p.moveTo(tip_x, tip_y)
    p.lineTo(tip_x-sz*math.cos(a-0.45), tip_y-sz*math.sin(a-0.45))
    p.lineTo(tip_x-sz*math.cos(a+0.45), tip_y-sz*math.sin(a+0.45))
    p.close()
    c.setFillColor(C_STEP); c.drawPath(p, fill=1, stroke=0)

def draw_slot(c, gx, gy, svg_name, moves, label, is_promo):
    bg = C_PROMO_BG if is_promo else C_BG

    c.setFillColor(bg); c.rect(gx,gy,GRID_SZ,GRID_SZ,fill=1,stroke=0)
    c.setFillColor(C_CENTER); c.rect(gx+2*CELL,gy+2*CELL,CELL,CELL,fill=1,stroke=0)

    if moves and moves.get('lion'):
        c.setFillColor(HexColor("#FFE8C0"))
        for dr in range(-2,3):
            for dc in range(-2,3):
                if dr==0 and dc==0: continue
                r,col_ = tg(dr,dc)
                if 0<=r<GRID_N and 0<=col_<GRID_N:
                    c.rect(gx+col_*CELL, gy+(GRID_N-1-r)*CELL, CELL, CELL, fill=1, stroke=0)

    c.setStrokeColor(C_GRID); c.setLineWidth(0.4)
    for i in range(GRID_N+1):
        c.line(gx+i*CELL, gy, gx+i*CELL, gy+GRID_SZ)
        c.line(gx, gy+i*CELL, gx+GRID_SZ, gy+i*CELL)

    if moves:
        cx0, cy0 = cc(gx,gy,2,2)

        if 'range' in moves:
            c.setStrokeColor(C_STEP); c.setLineWidth(1.1)
            for drow,dcol in moves['range']:
                ex, ey = range_edge(gx, gy, drow, dcol)
                c.line(cx0, cy0, ex, ey)
                arrowhead(c, cx0, cy0, ex, ey, CELL*0.22)
                c.setFillColor(C_STEP)
                for dist in range(1, GRID_N):
                    r,col_ = tg(drow*dist, dcol*dist)
                    if not (0<=r<GRID_N and 0<=col_<GRID_N): break
                    bx,by = cc(gx,gy,r,col_)
                    c.circle(bx,by, CELL*0.14, fill=1, stroke=0)

        if 'steps' in moves:
            c.setFillColor(C_STEP)
            for drow,dcol in moves['steps']:
                r,col_ = tg(drow,dcol)
                if 0<=r<GRID_N and 0<=col_<GRID_N:
                    bx,by = cc(gx,gy,r,col_)
                    c.circle(bx,by, CELL*0.26, fill=1, stroke=0)

        if 'jump2' in moves:
            for drow,dcol in moves['jump2']:
                r,col_ = tg(drow,dcol)
                if 0<=r<GRID_N and 0<=col_<GRID_N:
                    bx,by = cc(gx,gy,r,col_)
                    c.setFillColor(bg); c.setStrokeColor(C_STEP); c.setLineWidth(1.0)
                    c.circle(bx,by, CELL*0.26, fill=1, stroke=1)
                    c.setFillColor(C_STEP)
                    c.circle(bx,by, CELL*0.10, fill=1, stroke=0)

        if moves.get('lion'):
            for dr in range(-2,3):
                for dc in range(-2,3):
                    if dr==0 and dc==0: continue
                    r,col_ = tg(dr,dc)
                    bx,by = cc(gx,gy,r,col_)
                    c.setFillColor(C_STEP if max(abs(dr),abs(dc))==1 else C_LION2)
                    c.circle(bx,by, CELL*0.26, fill=1, stroke=0)

    png = piece_png(svg_name)
    img = ImageReader(io.BytesIO(png))
    sz  = CELL*0.97
    c.drawImage(img, gx+2*CELL+CELL/2-sz/2, gy+2*CELL+CELL/2-sz/2,
                width=sz, height=sz, mask='auto', preserveAspectRatio=True)

    color = C_RED if is_promo else C_BLACK
    lines = label.split('\n')
    max_w = GRID_SZ * 0.94
    fs = 4.0*mm
    for line in lines:
        while pdfmetrics.stringWidth(line, FONT, fs) > max_w and fs > 2.0*mm:
            fs -= 0.15*mm
    c.setFont(FONT, fs)
    line_gap = fs * 1.25
    if len(lines) == 1:
        c.setFillColor(color)
        c.drawCentredString(gx+GRID_SZ/2, gy - LABEL_H/2 - 0.5*mm, lines[0])
    else:
        c.setFillColor(color)
        c.drawCentredString(gx+GRID_SZ/2, gy - LABEL_H/2 + line_gap/2, lines[0])
        c.drawCentredString(gx+GRID_SZ/2, gy - LABEL_H/2 - line_gap/2, lines[1])

def slot_pos(idx):
    row = idx // COLS
    col = idx  % COLS
    gx  = MARGIN_X + col*DIAG_W + (DIAG_W-GRID_SZ)/2
    gy  = PAGE_H - MARGIN_Y_TOP - (row+1)*DIAG_H + LABEL_H
    return gx, gy

# ── Build slot list ───────────────────────────────────────────────────────────
labels = TRANSLATIONS[LANG]
SLOTS = []
for pid_n, svg_n, mov_n, pid_p, svg_p, mov_p in PAIRS:
    SLOTS.append((svg_n, mov_n, labels[pid_n], False))
    if pid_p is not NO_PROMO:
        SLOTS.append((svg_p, mov_p, labels[pid_p], True))

total_pages = math.ceil(len(SLOTS)/PER_PAGE)
print(f"Slots: {len(SLOTS)}  Pages: {total_pages}")

# ── Generate PDF ──────────────────────────────────────────────────────────────
c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("Chu Shogi — Piece Moves")

for i, slot in enumerate(SLOTS):
    if i % PER_PAGE == 0 and i > 0:
        c.showPage()
    gx, gy = slot_pos(i % PER_PAGE)
    svg_name, moves, label, is_promo = slot
    draw_slot(c, gx, gy, svg_name, moves, label, is_promo)
    print(f"  {'▲ ' if is_promo else '  '}{label.replace(chr(10),' ')}")

c.showPage()
c.save()
print(f"\nDone: {OUT}")

import subprocess
subprocess.run(["pdftoppm", "-r", "400", "-png", OUT, f"{LANG}/moves"], check=True)
print(f"PNG: {LANG}/moves-1.png ...")
