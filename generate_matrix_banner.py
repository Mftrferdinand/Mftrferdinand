import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1000, 150
SS = 2
bw, bh = W * SS, H * SS

font_title_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_SIZE = 58 * SS
font_title = ImageFont.truetype(font_title_path, FONT_SIZE)

phrases = ["MFTRFERDINAND", "ZEROLINEAR", "ZELINE AGENTIC AI"]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

cap_bbox = dd.textbbox((0, 0), "H", font=font_title)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]
mid_y = bh // 2

LETTER_SPACING = 3 * SS


def layout_phrase(text):
    total_w = 0
    metrics = []
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
    return {
        "text": text,
        "chars": chars,
        "w": total_w,
        "start_x": start_x,
        "base_y": base_y,
    }


phrase_data = [layout_phrase(t) for t in phrases]


def ease_out_cubic(x):
    return 1 - math.pow(1 - x, 3)


def ease_in_cubic(x):
    return math.pow(x, 3)


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


TRANS_IN = 12
HOLD = 22
TRANS_OUT = 10
FRAMES_PER_PHRASE = TRANS_IN + HOLD + TRANS_OUT
TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE
frames = []

print(f"Rendering {TOTAL_FRAMES} frames...")


# ---- Animated background: a diagonal light band that ALWAYS sweeps across ----
def make_bg(t_global):
    """t_global in [0,1) over whole loop -> moving diagonal sheen on blue."""
    base = Image.new("RGBA", (bw, bh), (30, 80, 205, 255))
    # moving diagonal bright band
    band = Image.new("L", (bw, bh), 0)
    bd = ImageDraw.Draw(band)
    sweep = t_global * 2.0 % 1.0  # two sweeps per loop -> continuous motion
    cx = int(-bw * 0.4 + sweep * bw * 1.8)
    w = int(bw * 0.35)
    bd.polygon(
        [(cx, 0), (cx + w, 0), (cx + w - bh, bh), (cx - bh, bh)],
        fill=255,
    )
    band = band.filter(ImageFilter.GaussianBlur(60))
    sheen = Image.new("RGBA", (bw, bh), (70, 130, 255, 255))
    sheen.putalpha(band.point(lambda p: int(p * 0.55)))
    base = Image.alpha_composite(base, sheen)
    return base


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

    blur_needed = 0.0
    for ci, cinfo in enumerate(cp["chars"]):
        if phase == "in":
            stagger = ci / float(max(1, n_chars)) * 0.6
            local = max(0.0, min(1.0, (pin - stagger) / (1.0 - 0.6)))
            e = ease_out_cubic(local)
            ca = e
            y_off = int((1.0 - e) * (22 * SS))
            blur_needed = max(blur_needed, (1.0 - e) * 7.0 * SS)
        elif phase == "hold":
            ca = 1.0
            # continuous wave: each letter bobs on a travelling sine -> always moving
            wave = math.sin(phold * math.pi * 2 * 1.5 - ci * 0.6)
            y_off = int(wave * 3.0 * SS)
        else:
            e = ease_in_cubic(pout)
            ca = 1.0 - e
            y_off = -int(e * 16 * SS)
        if ca <= 0.01:
            continue
        t_draw.text(
            (cinfo["x"], cp["base_y"] + y_off),
            cinfo["ch"],
            font=font_title,
            fill=(255, 255, 255, int(ca * 255)),
        )

    if blur_needed > 0.4:
        text_canvas = text_canvas.filter(ImageFilter.GaussianBlur(blur_needed))

    # Always-on soft glow that pulses noticeably
    glow_amt = 0.35 + 0.35 * math.sin(t_global * math.pi * 2 * 3)
    if phase == "in":
        glow_amt *= pin
    elif phase == "out":
        glow_amt *= 1.0 - pout
    if glow_amt > 0.05:
        glow_mask = text_canvas.split()[3].filter(ImageFilter.GaussianBlur(11 * SS))
        glow_layer = Image.new("RGBA", (bw, bh), (150, 200, 255, 0))
        glow_layer.putalpha(
            glow_mask.point(lambda p, g=glow_amt: int(p * (int(g * 80) / 255.0)))
        )
        canvas = Image.alpha_composite(canvas, glow_layer)

    # Bright shimmer ray sweeping the letters — runs during hold, clearly visible
    if phase == "hold":
        shimmer_pos = -0.3 + 1.6 * ease_in_out(phold)
        ray_center = cp["start_x"] + int(cp["w"] * shimmer_pos)
        ray_width = int(120 * SS)
        shimmer_img = Image.new("L", (bw, bh), 0)
        s_draw = ImageDraw.Draw(shimmer_img)
        s_draw.polygon(
            [
                (ray_center - ray_width + 40 * SS, 0),
                (ray_center + 40 * SS, 0),
                (ray_center + ray_width - 40 * SS, bh),
                (ray_center - 40 * SS, bh),
            ],
            fill=255,
        )
        shimmer_blurred = shimmer_img.filter(ImageFilter.GaussianBlur(10 * SS))
        shimmer_text_mask = ImageChops.multiply(text_canvas.split()[3], shimmer_blurred)
        shimmer_layer = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
        shimmer_layer.putalpha(shimmer_text_mask)  # full bright sweep
        text_canvas = Image.alpha_composite(text_canvas, shimmer_layer)

    canvas = Image.alpha_composite(canvas, text_canvas)
    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(
            colors=64, method=Image.FASTOCTREE, dither=Image.Dither.NONE
        )
    )

out_path = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    duration=50,
    loop=0,
    optimize=True,
)
print("Finished. Frames:", len(frames))
