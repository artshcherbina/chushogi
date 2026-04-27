#!/usr/bin/env python3
"""Chu Shogi — 12x12 board (A3). Promotion zones lightly shaded."""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("LAT", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("JPb", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))

os.makedirs("pieces", exist_ok=True)
OUT = "pieces/chu_shogi_board.pdf"

PAGE_W, PAGE_H = A3  # 297 x 420 mm in points

N       = 12
MARGIN  = 15*mm
CELL    = (PAGE_W - 2*MARGIN) / N   # ≈ 22.25 mm
BOARD_W = CELL * N
BOARD_H = CELL * N
BX      = MARGIN
BY      = (PAGE_H - BOARD_H) / 2   # vertically centered

C_WOOD   = HexColor("#F2DFA8")
C_PROMO  = HexColor("#E8C87A")
C_LINE   = HexColor("#7A5400")
C_BORDER = HexColor("#4A3200")
C_LABEL  = HexColor("#4A3200")
C_ARROW  = HexColor("#7A5400")
C_PLAYER = HexColor("#3A2800")

c = canvas.Canvas(OUT, pagesize=A3)
c.setTitle("Chu Shogi — 12×12 Board")

# ── Background ────────────────────────────────────────────────────────────────
c.setFillColor(C_WOOD)
c.rect(BX, BY, BOARD_W, BOARD_H, fill=1, stroke=0)

# ── Grid ──────────────────────────────────────────────────────────────────────
c.setStrokeColor(C_LINE); c.setLineWidth(2.5)
for i in range(N + 1):
    c.line(BX + i*CELL, BY, BX + i*CELL, BY + BOARD_H)
    c.line(BX, BY + i*CELL, BX + BOARD_W, BY + i*CELL)

# ── Border ────────────────────────────────────────────────────────────────────
c.setStrokeColor(C_BORDER); c.setLineWidth(7.0)
c.rect(BX, BY, BOARD_W, BOARD_H, fill=0, stroke=1)

# ── Column numbers (1–12, left to right) ──────────────────────────────────────
fs = 3.8*mm
c.setFont("LAT", fs); c.setFillColor(C_LABEL)
for i in range(N):
    cx = BX + (i + 0.5) * CELL
    c.drawCentredString(cx, BY + BOARD_H + 3*mm, str(i + 1))
    c.drawCentredString(cx, BY - 6*mm, str(i + 1))

# ── Row numbers (1–12, top to bottom) ────────────────────────────────────────
for j in range(N):
    cy = BY + BOARD_H - (j + 0.5) * CELL - fs*0.35
    c.drawRightString(BX - 2*mm, cy, str(j + 1))
    c.drawString(BX + BOARD_W + 2*mm, cy, str(j + 1))


c.showPage()
c.save()
print(f"Done: {OUT}  (cell={CELL/mm:.1f} mm)")

import subprocess
subprocess.run(["pdftoppm", "-r", "300", "-png", OUT, "pieces/board"], check=True)
print("PNG: pieces/board-1.png")
