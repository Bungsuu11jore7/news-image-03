#!/usr/bin/env python3
"""Corkboard news image for make.fun news-image-01.

Draws a 1024x1024 PNG: an editor's corkboard with six pinned
clippings summing up Friday 13 November 2026. Pure standard
library: the PNG is encoded by hand (zlib) and all text is set
in a small 5x7 bitmap font defined below. Deterministic: the
same input always writes the same bytes (fixed speckle seed,
no timestamps, no network).
"""

import os
import random
import struct
import zlib

W = 1024
H = 1024

# ---- palette ----
CORK = (176, 138, 88)
CORK_DARK = (148, 112, 66)
CORK_LIGHT = (200, 162, 110)
WOOD = (104, 66, 38)
WOOD_DARK = (82, 50, 26)
PAPER = (247, 239, 220)
PAPER_B = (244, 232, 206)
PAPER_C = (250, 243, 226)
INK = (28, 34, 48)
BODY = (58, 58, 58)
GREY = (110, 110, 104)
RED = (178, 34, 34)
BLUE = (31, 78, 121)
TEAL = (15, 107, 92)
GREEN = (30, 107, 52)
GOLD = (138, 109, 0)
STEEL = (46, 95, 122)
MAROON = (139, 30, 30)
WHITE = (255, 255, 255)
BLACK = (22, 22, 22)
SHADOW = (96, 64, 32)
PANEL = (235, 229, 210)
PANEL_LINE = (190, 178, 150)
PIN_RED = (200, 40, 40)
PIN_BLUE = (40, 90, 180)
PIN_GREEN = (40, 140, 70)
PIN_GOLD = (220, 160, 30)

# ---- 5x7 bitmap font ('#' = ink, '.' = empty) ----
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}


class Canvas:
    def __init__(self):
        self.px = bytearray(W * H * 3)

    def fill(self, color):
        r, g, b = color
        row = bytes((r, g, b)) * W
        self.px[:] = row * H

    def rect(self, x, y, w, h, color):
        r, g, b = color
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        span = bytes((r, g, b)) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * W + x0) * 3
            self.px[off:off + len(span)] = span

    def outline(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def circle(self, cx, cy, rad, color):
        r, g, b = color
        for dy in range(-rad, rad + 1):
            dx = int((rad * rad - dy * dy) ** 0.5)
            yy = cy + dy
            if 0 <= yy < H:
                x0 = max(0, cx - dx)
                x1 = min(W - 1, cx + dx)
                off = (yy * W + x0) * 3
                span = bytes((r, g, b)) * (x1 - x0 + 1)
                self.px[off:off + len(span)] = span

    def ring(self, cx, cy, rad, color, t=3):
        for k in range(t):
            self.circle_outline(cx, cy, rad - k, color)

    def circle_outline(self, cx, cy, rad, color):
        r, g, b = color
        steps = max(8, rad * 8)
        import math
        for i in range(steps):
            a = 2 * math.pi * i / steps
            x = int(cx + rad * math.cos(a))
            y = int(cy + rad * math.sin(a))
            if 0 <= x < W and 0 <= y < H:
                off = (y * W + x) * 3
                self.px[off:off + 3] = bytes((r, g, b))

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0, y0, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # scanline fill of a triangle
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        def interp(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = interp(ax, ay, bx, by, y)
                xb = interp(ax, ay, cx, cy, y)
            else:
                xa = interp(bx, by, cx, cy, y)
                xb = interp(ax, ay, cx, cy, y)
            x0i, x1i = int(min(xa, xb)), int(max(xa, xb))
            self.rect(x0i, y, x1i - x0i + 1, 1, color)


def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, color):
    for i, ch in enumerate(s):
        g = FONT.get(ch)
        if g is None:
            continue
        ox = x + i * 6 * scale
        for row_i, row in enumerate(g):
            for col_i, bit in enumerate(row):
                if bit == "#":
                    cv.rect(ox + col_i * scale, y + row_i * scale,
                            scale, scale, color)


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap(text, scale, maxw):
    lines = []
    cur = ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---- pictograms, drawn in a 130x150 panel at (x, y) ----
def draw_icon(cv, x, y, kind):
    cv.rect(x, y, 130, 150, PANEL)
    cv.outline(x, y, 130, 150, PANEL_LINE, 2)
    if kind == "capitol":
        # dome + columns + steps
        cv.circle(x + 65, y + 42, 20, STEEL)
        cv.rect(x + 45, y + 42, 40, 8, STEEL)
        for cx in (x + 28, x + 50, x + 72, x + 94):
            cv.rect(cx, y + 58, 10, 52, STEEL)
        cv.rect(x + 20, y + 110, 90, 8, STEEL)
        cv.rect(x + 14, y + 118, 102, 8, STEEL)
        cv.rect(x + 8, y + 126, 114, 8, STEEL)
    elif kind == "warship":
        # sea
        cv.rect(x + 8, y + 104, 114, 12, (70, 130, 170))
        cv.rect(x + 8, y + 122, 114, 10, (50, 110, 150))
        # hull with pointed bow
        cv.rect(x + 16, y + 84, 80, 16, (52, 62, 74))
        cv.triangle(x + 96, y + 84, x + 96, y + 100, x + 114, y + 100,
                    (52, 62, 74))
        # superstructure + mast + smoke
        cv.rect(x + 38, y + 66, 32, 18, (52, 62, 74))
        cv.rect(x + 52, y + 46, 4, 20, (52, 62, 74))
        cv.circle(x + 42, y + 38, 7, (150, 150, 150))
        cv.circle(x + 58, y + 30, 9, (170, 170, 170))
        cv.circle(x + 76, y + 24, 7, (190, 190, 190))
        # drone overhead
        cv.rect(x + 94, y + 50, 14, 4, BLACK)
        cv.circle(x + 101, y + 52, 3, BLACK)
    elif kind == "laptop":
        # screen + base
        cv.rect(x + 22, y + 34, 86, 58, (30, 42, 60))
        cv.rect(x + 28, y + 40, 74, 46, (90, 160, 200))
        cv.rect(x + 14, y + 92, 102, 10, (30, 42, 60))
        # coins
        for cx, cy in ((x + 34, y + 122), (x + 62, y + 122), (x + 90, y + 122)):
            cv.circle(cx, cy, 11, (212, 175, 55))
            cv.circle(cx, cy, 7, (240, 205, 90))
    elif kind == "monitor":
        # cracked screen
        cv.rect(x + 20, y + 30, 90, 66, (30, 42, 60))
        cv.rect(x + 26, y + 36, 78, 54, (120, 130, 140))
        cv.line(x + 40, y + 36, x + 62, y + 62, RED, 3)
        cv.line(x + 62, y + 62, x + 52, y + 90, RED, 3)
        cv.line(x + 62, y + 62, x + 88, y + 48, RED, 3)
        cv.rect(x + 58, y + 96, 14, 22, (30, 42, 60))
        cv.rect(x + 40, y + 118, 50, 8, (30, 42, 60))
    elif kind == "flags":
        # two poles, flags hanging inward
        cv.rect(x + 24, y + 28, 4, 92, (90, 70, 40))
        cv.rect(x + 102, y + 28, 4, 92, (90, 70, 40))
        # Qatar flag (maroon, white hoist strip)
        cv.rect(x + 28, y + 30, 32, 28, MAROON)
        cv.rect(x + 28, y + 30, 8, 28, WHITE)
        # Turkey flag (red, white crescent)
        cv.rect(x + 70, y + 30, 32, 28, RED)
        cv.circle(x + 82, y + 44, 7, WHITE)
        cv.circle(x + 85, y + 44, 6, RED)
        # deal band
        cv.rect(x + 22, y + 96, 86, 20, GOLD)
        draw_text_centered(cv, x + 65, y + 101, "DEAL", 2, WHITE)
    elif kind == "football":
        cv.circle(x + 65, y + 62, 44, BLACK)
        cv.circle(x + 65, y + 62, 40, WHITE)
        cv.circle(x + 65, y + 62, 9, BLACK)
        for dx, dy in ((-24, -16), (24, -16), (-28, 16), (28, 16), (0, 30)):
            cv.circle(x + 65 + dx, y + 62 + dy, 5, BLACK)
        draw_text_centered(cv, x + 65, y + 118, "126", 3, INK)


STORIES = [
    dict(tag="USA - SENATE", band=BLUE, pin=PIN_RED, paper=PAPER,
         headline="SENATE SUMMONS HUANG",
         summary="SENATE BANKING PANEL CALLS NVIDIA CHIEF AND COMMERCE SECRETARY TO TESTIFY ON CHIP EXPORTS.",
         icon="capitol"),
    dict(tag="UKRAINE - BALTIC", band=STEEL, pin=PIN_BLUE, paper=PAPER_B,
         headline="DRONE HITS RUSSIAN WARSHIP",
         summary="KYIV SAYS A DRONE STRUCK A RUSSIAN WARSHIP IN THE GULF OF FINLAND.",
         icon="warship"),
    dict(tag="CYBER - FBI", band=MAROON, pin=PIN_GOLD, paper=PAPER_C,
         headline="FBI: $400M FACE-STEALER HACK",
         summary="NORTH KOREAN HACKERS USED FAKE VIDEO CALLS TO STEAL $400M IN CRYPTO, THE FBI SAYS.",
         icon="laptop"),
    dict(tag="TECH - OUTAGE", band=TEAL, pin=PIN_GREEN, paper=PAPER,
         headline="MICROSOFT OUTAGE DAY TWO",
         summary="GLOBAL MICROSOFT 365 OUTAGE DISRUPTS OUTLOOK, TEAMS AND COURTS FOR A SECOND DAY.",
         icon="monitor"),
    dict(tag="MIDDLE EAST", band=GOLD, pin=PIN_RED, paper=PAPER_B,
         headline="QATAR-TURKEY DEFENCE PACT",
         summary="DOHA AND ANKARA SIGN A MUTUAL DEFENCE DEAL IN ISTANBUL.",
         icon="flags"),
    dict(tag="SPORT - ENGLAND", band=GREEN, pin=PIN_BLUE, paper=PAPER_C,
         headline="KANE BREAKS CAPS RECORD",
         summary="KANE WINS A RECORD 126TH ENGLAND CAP AS ENGLAND BEAT CROATIA 2-1 AT WEMBLEY.",
         icon="football"),
]


def draw_card(cv, x, y, st):
    cv.rect(x + 6, y + 7, 452, 252, SHADOW)
    cv.rect(x, y, 452, 252, st["paper"])
    cv.outline(x, y, 452, 252, (120, 100, 70), 2)
    cv.rect(x, y, 452, 34, st["band"])
    draw_text(cv, x + 16, y + 10, st["tag"], 2, WHITE)
    # pushpin
    px, py = x + 226, y + 8
    cv.circle(px, py, 13, st["pin"])
    cv.circle(px - 4, py - 4, 4, (255, 255, 255))
    # pictogram panel
    draw_icon(cv, x + 16, y + 50, st["icon"])
    # text column
    tx = x + 16 + 130 + 14
    tw = 452 - 16 - 130 - 14 - 16
    hy = y + 52
    for ln in wrap(st["headline"], 3, tw):
        draw_text(cv, tx, hy, ln, 3, INK)
        hy += 27
    hy += 4
    for ln in wrap(st["summary"], 2, tw):
        draw_text(cv, tx, hy, ln, 2, BODY)
        hy += 18


def png_bytes(cv):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += cv.px[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def build():
    cv = Canvas()
    cv.fill(CORK)
    rng = random.Random(20261113)
    for _ in range(5200):
        sx = int(rng.random() * W)
        sy = int(rng.random() * H)
        c = CORK_DARK if rng.random() < 0.5 else CORK_LIGHT
        cv.rect(sx, sy, 2, 2, c)
    for _ in range(260):
        sx = int(rng.random() * W)
        sy = int(rng.random() * H)
        c = CORK_DARK if rng.random() < 0.5 else CORK_LIGHT
        cv.rect(sx, sy, 4, 2, c)
    # wood frame
    cv.rect(0, 0, W, 20, WOOD)
    cv.rect(0, H - 20, W, 20, WOOD)
    cv.rect(0, 0, 20, H, WOOD)
    cv.rect(W - 20, 0, 20, H, WOOD)
    cv.rect(20, 20, W - 40, 3, WOOD_DARK)
    cv.rect(20, H - 23, W - 40, 3, WOOD_DARK)
    # header strip
    cv.rect(40, 36, 944, 112, PAPER)
    cv.outline(40, 36, 944, 112, RED, 3)
    draw_text_centered(cv, 512, 54, "FRIDAY 13 NOVEMBER 2026", 4, INK)
    draw_text_centered(cv, 512, 104, "SIX STORIES PINNED TO THE BOARD", 2, GREY)
    # six pinned clippings
    xs = (40, 532)
    ys = (168, 440, 712)
    for i, st in enumerate(STORIES):
        draw_card(cv, xs[i % 2], ys[i // 2], st)
    # footer
    draw_text_centered(
        cv, 512, 978,
        "EVERY STORY HAPPENED OR WAS FIRST REPORTED ON FRIDAY 13 NOVEMBER 2026",
        2, (70, 48, 24))
    return png_bytes(cv)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(outdir, exist_ok=True)
    data = build()
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
