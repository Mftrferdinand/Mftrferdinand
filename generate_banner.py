"""
Premium monochrome animated banner for Mftrferdinand-profile README.
Efek: decrypt/hacker reveal per huruf + subtle particle grid + diagonal sheen sweep.
Tema: hitam-putih premium (background pekat, teks putih, aksen abu/putih).
"""

import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1000, 200
SS = 2
bw, bh = W * SS, H * SS

font_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT = ImageFont.truetype(font_path, 56 * SS)

phrases = ["MFTRFERDINAND", "ZEROLINEAR", "ZELINE AGENTIC AI"]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)
cap_bbox = dd.textbbox((0, 0), "H", font=FONT)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]
mid_y = bh // 2
LETTER_SPACING = 6 * SS


def layout_phrase(text):
    metrics = []
    total_w = 0
    for ch in text:
        cb = dd.textbbox((0, 0), ch, font=FONT)
        cw = cb[2] - cb[0]
        metrics.append((ch, cw, cb[0]))
        total_w += cw + LETTER_SPACING
    total_w -= LETTER_SPACING
    start_x = (bw - total_w) // 2
    base_y = (mid_y - cap_h // 2) - cap_top_off
    chars = []
    x = start_x
    for ch, cw, cbx in metrics:
        chars.append({"ch": ch, "x": x - cbx, "cw": cw})
        x += cw + LETTER_SPACING
    return {
        "text": text,
        "chars": chars,
        "w": total_w,
        "start_x": start_x,
        "base_y": base_y,
    }


phrase_data = [layout_phrase(p) for p in phrases]


def ease_out_cubic(x):
    return 1 - math.pow(1 - x, 3)


def ease_in_cubic(x):
    return math.pow(x, 3)


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


# Timing: in lebih cepat, hold cukup lama, out halus
TRANS_IN = 12
HOLD = 30
TRANS_OUT = 14
FRAMES_PER_PHRASE = TRANS_IN + HOLD + TRANS_OUT
TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE

# Palet monokrom premium
BG_TOP = (10, 10, 12)
BG_MID = (18, 18, 22)
BG_BOT = (8, 8, 10)
GRID = (44, 44, 48)
ACCENT = (255, 255, 255)
GLOW = (230, 230, 235)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# Vertical gradient statis
grad = Image.new("RGBA", (bw, bh))
gpx = grad.load()
for y in range(bh):
    ty = y / bh
    col = (
        lerp(BG_TOP, BG_MID, ty / 0.5)
        if ty < 0.5
        else lerp(BG_MID, BG_BOT, (ty - 0.5) / 0.5)
    )
    for x in range(bw):
        gpx[x, y] = (*col, 255)

# Pre-render karakter acak untuk efek decrypt (glyph acak: huruf/karakter hacker)
import random

random.seed(1337)
GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+=<>{}[]|/"


def random_glyph():
    return random.choice(GLYPHS)


def make_bg(t_global):
    base = grad.copy()
    bd = ImageDraw.Draw(base)

    # 1) Grid partikel halus bergerak konstan (horizontal + vertical drift)
    gap = 30 * SS
    ox = int((t_global * 40 * SS) % gap)
    oy = int((t_global * 25 * SS) % gap)
    for gx in range(-gap + ox, bw, gap):
        for gy in range(-gap + oy, bh, gap):
            # kepadatan acak tapi deterministik per posisi
            if ((gx // gap) + (gy // gap)) % 7 == 0:
                bd.rectangle([gx, gy, gx + 2 * SS, gy + 2 * SS], fill=(52, 52, 56, 255))

    # 2) Aurora monokrom (putih halus) yang mengalir
    aur = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aur)
    cx1 = bw * (0.28 + 0.20 * math.sin(t_global * math.pi * 2 * 0.9))
    cy1 = bh * (0.30 + 0.16 * math.cos(t_global * math.pi * 2 * 0.7))
    r1 = bw * 0.32
    ad.ellipse([cx1 - r1, cy1 - r1, cx1 + r1, cy1 + r1], fill=(70, 70, 80, 75))
    cx2 = bw * (0.74 - 0.18 * math.cos(t_global * math.pi * 2 * 1.05))
    cy2 = bh * (0.62 + 0.14 * math.sin(t_global * math.pi * 2 * 0.8))
    r2 = bw * 0.28
    ad.ellipse([cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2], fill=(60, 60, 70, 70))
    aur = aur.filter(ImageFilter.GaussianBlur(80 * SS))
    base = Image.alpha_composite(base, aur)

    # 3) Diagonal sheen menyapu terus-menerus
    sweep = (t_global * 1.6) % 1.0
    cx = int(-bw * 0.35 + sweep * bw * 1.7)
    w = int(bw * 0.20)
    band = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(band).polygon(
        [(cx, 0), (cx + w, 0), (cx + w - int(bh * 0.7), bh), (cx - int(bh * 0.7), bh)],
        fill=255,
    )
    band = band.filter(ImageFilter.GaussianBlur(60 * SS))
    sheen = Image.new("RGBA", (bw, bh), (255, 255, 255, 255))
    sheen.putalpha(band.point(lambda p: int(p * 0.18)))
    base = Image.alpha_composite(base, sheen)

    # 4) Garis tepi tipis + bracket sudut
    bd = ImageDraw.Draw(base)
    bd.line([(0, 0), (bw, 0)], fill=(48, 48, 52, 255), width=2 * SS)
    bd.line([(0, bh - 2 * SS), (bw, bh - 2 * SS)], fill=(48, 48, 52, 255), width=2 * SS)
    bl = 20 * SS
    m = 10 * SS
    for ox_, oy_, dx, dy in [
        (m, m, 1, 1),
        (bw - m, m, -1, 1),
        (m, bh - m, 1, -1),
        (bw - m, bh - m, -1, -1),
    ]:
        bd.line(
            [(ox_, oy_), (ox_ + dx * bl, oy_)], fill=(88, 88, 94, 255), width=2 * SS
        )
        bd.line(
            [(ox_, oy_), (ox_, oy_ + dy * bl)], fill=(88, 88, 94, 255), width=2 * SS
        )

    return base


frames = []
for gi in range(TOTAL_FRAMES):
    pi = gi // FRAMES_PER_PHRASE
    li = gi % FRAMES_PER_PHRASE
    cp = phrase_data[pi]
    n_chars = len(cp["chars"])
    t_global = gi / float(TOTAL_FRAMES)

    canvas = make_bg(t_global)
    text_canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(text_canvas)

    if li < TRANS_IN:
        phase, pin = "in", li / float(TRANS_IN)
    elif li < TRANS_IN + HOLD:
        phase, phold = "hold", (li - TRANS_IN) / float(HOLD)
    else:
        phase, pout = "out", (li - (TRANS_IN + HOLD)) / float(TRANS_OUT)

    for ci, cinfo in enumerate(cp["chars"]):
        if phase == "in":
            # decrypt: huruf acak -> huruf benar, stagger per huruf
            stagger = ci / float(max(1, n_chars)) * 0.55
            local = max(0.0, min(1.0, (pin - stagger) / 0.45))
            e = ease_out_cubic(local)
            ca = e
            y_off = int((1.0 - e) * 18 * SS)
            # pakai glyph acak sampai huruf fix
            if e < 0.92:
                ch = random_glyph()
                ca = ca * 0.75
            else:
                ch = cinfo["ch"]
        elif phase == "hold":
            ca = 1.0
            wave = math.sin(phold * math.pi * 2 * 1.2 - ci * 0.45)
            y_off = int(wave * 2.2 * SS)
            ch = cinfo["ch"]
        else:
            e = ease_in_cubic(pout)
            ca = 1.0 - e
            y_off = -int(e * 14 * SS)
            ch = cinfo["ch"]

        if ca <= 0.02:
            continue
        t_draw.text(
            (cinfo["x"], cp["base_y"] + y_off),
            ch,
            font=FONT,
            fill=(255, 255, 255, int(ca * 255)),
        )

    # Glow putih di belakang teks
    alpha = text_canvas.split()[3]
    glow_mask = alpha.filter(ImageFilter.GaussianBlur(9 * SS))
    glow_layer = Image.new("RGBA", (bw, bh), GLOW + (0,))
    glow_layer.putalpha(glow_mask.point(lambda p: int(p * 0.45)))
    canvas = Image.alpha_composite(canvas, glow_layer)

    # Shimmer cahaya menyapu teks saat hold (lebih subtle)
    if phase == "hold":
        shimmer_pos = -0.35 + 1.7 * ease_in_out(phold)
        ray_center = cp["start_x"] + int(cp["w"] * shimmer_pos)
        ray_w = int(140 * SS)
        s_img = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(s_img).polygon(
            [
                (ray_center - ray_w + 35 * SS, 0),
                (ray_center + 35 * SS, 0),
                (ray_center + ray_w - 35 * SS, bh),
                (ray_center - 35 * SS, bh),
            ],
            fill=255,
        )
        s_blur = s_img.filter(ImageFilter.GaussianBlur(10 * SS))
        s_mask = ImageChops.multiply(alpha, s_blur)
        shimmer = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
        shimmer.putalpha(s_mask.point(lambda p: int(p * 0.85)))
        text_canvas = Image.alpha_composite(text_canvas, shimmer)

    canvas = Image.alpha_composite(canvas, text_canvas)

    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(
            colors=180, method=Image.FASTOCTREE, dither=Image.Dither.NONE
        )
    )

out_path = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    duration=42,
    loop=0,
    optimize=True,
)
print(f"Finished: {len(frames)} frames -> {out_path}")
