import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

# Banner canvas — lebar penuh README, super-sampled 2x biar tajam.
W, H = 1000, 200
SS = 2
bw, bh = W * SS, H * SS

font_title_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
font_title = ImageFont.truetype(font_title_path, 58 * SS)

# HANYA 3 frase, TANPA tagline.
phrases = ["MFTRFERDINAND", "ZEROLINEAR", "ZELINE AGENTIC AI"]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

cap_bbox = dd.textbbox((0, 0), "H", font=font_title)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]
mid_y = bh // 2

LETTER_SPACING = 5 * SS


def layout_phrase(text):
    metrics = []
    total_w = 0
    for ch in text:
        cb = dd.textbbox((0, 0), ch, font=font_title)
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
    return {"text": text, "chars": chars, "w": total_w, "start_x": start_x, "base_y": base_y}


phrase_data = [layout_phrase(p) for p in phrases]


def ease_out_cubic(x):
    return 1 - math.pow(1 - x, 3)


def ease_in_cubic(x):
    return math.pow(x, 3)


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


TRANS_IN = 14
HOLD = 26
TRANS_OUT = 12
FRAMES_PER_PHRASE = TRANS_IN + HOLD + TRANS_OUT
TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE

print(f"Generating {TOTAL_FRAMES} frames — blue animated bg, white text...")

# ── Palet biru ──
BLUE_TOP = (7, 18, 48)       # navy pekat
BLUE_MID = (16, 42, 96)      # biru royal gelap
BLUE_BOT = (9, 24, 60)       # navy
ACCENT = (56, 132, 255)      # electric blue
GLOW = (120, 180, 255)       # cyan-biru terang


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# Precompute vertical gradient sekali (statis) — animasi lewat overlay.
grad = Image.new("RGBA", (bw, bh))
gpx = grad.load()
for y in range(bh):
    ty = y / bh
    if ty < 0.5:
        col = lerp(BLUE_TOP, BLUE_MID, ty / 0.5)
    else:
        col = lerp(BLUE_MID, BLUE_BOT, (ty - 0.5) / 0.5)
    for x in range(bw):
        gpx[x, y] = (col[0], col[1], col[2], 255)


def make_bg(t_global):
    base = grad.copy()

    # 1) Grid titik halus yang bergeser pelan (efek gerak konstan)
    bd = ImageDraw.Draw(base)
    grid_gap = 28 * SS
    off = int((t_global * 60 * SS) % grid_gap)
    dot = (70, 120, 210, 255)
    for gx in range(off, bw, grid_gap):
        for gy in range(0, bh, grid_gap):
            bd.point((gx, gy), fill=dot)
            bd.point((gx + 1, gy), fill=dot)

    # 2) Dua "aurora" biru yang mengalir (radial glow bergerak sinus)
    aur = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aur)
    cx1 = bw * (0.30 + 0.18 * math.sin(t_global * math.pi * 2))
    cy1 = bh * (0.35 + 0.15 * math.cos(t_global * math.pi * 2 * 0.8))
    r1 = bw * 0.34
    ad.ellipse([cx1 - r1, cy1 - r1, cx1 + r1, cy1 + r1], fill=(40, 100, 220, 90))
    cx2 = bw * (0.72 - 0.16 * math.cos(t_global * math.pi * 2 * 1.1))
    cy2 = bh * (0.6 + 0.18 * math.sin(t_global * math.pi * 2 * 0.7))
    r2 = bw * 0.30
    ad.ellipse([cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2], fill=(30, 150, 235, 80))
    aur = aur.filter(ImageFilter.GaussianBlur(70 * SS))
    base = Image.alpha_composite(base, aur)

    # 3) Diagonal sheen menyapu (light beam)
    sweep = (t_global * 2.0) % 1.0
    cx = int(-bw * 0.3 + sweep * bw * 1.6)
    w = int(bw * 0.22)
    band = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(band).polygon(
        [(cx, 0), (cx + w, 0), (cx + w - bh * 0.8, bh), (cx - bh * 0.8, bh)], fill=255
    )
    band = band.filter(ImageFilter.GaussianBlur(55 * SS))
    sheen = Image.new("RGBA", (bw, bh), (150, 195, 255, 255))
    sheen.putalpha(band.point(lambda p: int(p * 0.30)))
    base = Image.alpha_composite(base, sheen)

    # 4) Frame tepi + corner bracket accent (electric blue)
    bd = ImageDraw.Draw(base)
    line_c = (60, 110, 200, 255)
    bd.line([(0, 0), (bw, 0)], fill=line_c, width=2 * SS)
    bd.line([(0, bh - 2 * SS), (bw, bh - 2 * SS)], fill=line_c, width=2 * SS)
    bl = 18 * SS
    m = 9 * SS
    for (ox, oy, dx, dy) in [
        (m, m, 1, 1), (bw - m, m, -1, 1),
        (m, bh - m, 1, -1), (bw - m, bh - m, -1, -1),
    ]:
        bd.line([(ox, oy), (ox + dx * bl, oy)], fill=ACCENT + (255,), width=2 * SS)
        bd.line([(ox, oy), (ox, oy + dy * bl)], fill=ACCENT + (255,), width=2 * SS)

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

    # Teks PUTIH dengan float + fade
    for ci, cinfo in enumerate(cp["chars"]):
        if phase == "in":
            stagger = ci / float(max(1, n_chars)) * 0.5
            local = max(0.0, min(1.0, (pin - stagger) / 0.5))
            e = ease_out_cubic(local)
            ca = e
            y_off = int((1.0 - e) * (20 * SS))
        elif phase == "hold":
            ca = 1.0
            wave = math.sin(phold * math.pi * 2 * 1.4 - ci * 0.5)
            y_off = int(wave * 2.4 * SS)
        else:
            e = ease_in_cubic(pout)
            ca = 1.0 - e
            y_off = -int(e * 16 * SS)

        if ca <= 0.02:
            continue
        # PUTIH bersih
        t_draw.text(
            (cinfo["x"], cp["base_y"] + y_off),
            cinfo["ch"],
            font=font_title,
            fill=(255, 255, 255, int(ca * 255)),
        )

    # Glow biru di belakang teks (bikin putih "menyala")
    glow_mask = text_canvas.split()[3].filter(ImageFilter.GaussianBlur(7 * SS))
    glow_layer = Image.new("RGBA", (bw, bh), GLOW + (0,))
    glow_layer.putalpha(glow_mask.point(lambda p: int(p * 0.55)))
    canvas = Image.alpha_composite(canvas, glow_layer)

    # Shimmer cahaya menyapu teks saat hold
    if phase == "hold":
        shimmer_pos = -0.3 + 1.6 * ease_in_out(phold)
        ray_center = cp["start_x"] + int(cp["w"] * shimmer_pos)
        ray_w = int(150 * SS)
        s_img = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(s_img).polygon(
            [
                (ray_center - ray_w + 40 * SS, 0),
                (ray_center + 40 * SS, 0),
                (ray_center + ray_w - 40 * SS, bh),
                (ray_center - 40 * SS, bh),
            ],
            fill=255,
        )
        s_blur = s_img.filter(ImageFilter.GaussianBlur(9 * SS))
        s_mask = ImageChops.multiply(text_canvas.split()[3], s_blur)
        shimmer = Image.new("RGBA", (bw, bh), (190, 220, 255, 0))
        shimmer.putalpha(s_mask.point(lambda p: int(p * 0.95)))
        text_canvas = Image.alpha_composite(text_canvas, shimmer)

    canvas = Image.alpha_composite(canvas, text_canvas)

    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(
            colors=200, method=Image.FASTOCTREE, dither=Image.Dither.NONE
        )
    )

out_path = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    duration=45,
    loop=0,
    optimize=True,
)
print("Finished saving GIF:", out_path)
