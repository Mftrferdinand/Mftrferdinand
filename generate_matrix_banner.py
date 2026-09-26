import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1000, 160
SS = 2
bw, bh = W * SS, H * SS

font_title_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
font_sub_path = (
    "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
)

FONT_SIZE = 54 * SS
SUB_FONT_SIZE = 14 * SS

font_title = ImageFont.truetype(font_title_path, FONT_SIZE)
font_sub = ImageFont.truetype(font_sub_path, SUB_FONT_SIZE)

phrases = [
    {"main": "MFTRFERDINAND", "tag": "SYSTEM OPERATOR // ZEROLINEAR"},
    {"main": "ZEROLINEAR", "tag": "AUTONOMOUS RESEARCH LAB"},
    {"main": "ZELINE AGENTIC AI", "tag": "HIGH-AGENCY INTELLIGENCE FRAMEWORK"},
]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

cap_bbox = dd.textbbox((0, 0), "H", font=font_title)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]
mid_y = (bh // 2) - 10 * SS

LETTER_SPACING = 4 * SS


def layout_phrase(p_dict):
    text = p_dict["main"]
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

    tag_text = p_dict["tag"]
    tb = dd.textbbox((0, 0), tag_text, font=font_sub)
    tw = tb[2] - tb[0]
    tag_x = (bw - tw) // 2
    tag_y = base_y + cap_h + 18 * SS

    return {
        "text": text,
        "tag": tag_text,
        "chars": chars,
        "w": total_w,
        "start_x": start_x,
        "base_y": base_y,
        "tag_x": tag_x,
        "tag_y": tag_y,
    }


phrase_data = [layout_phrase(p) for p in phrases]


def ease_out_cubic(x):
    return 1 - math.pow(1 - x, 3)


def ease_in_cubic(x):
    return math.pow(x, 3)


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


TRANS_IN = 14
HOLD = 24
TRANS_OUT = 12
FRAMES_PER_PHRASE = TRANS_IN + HOLD + TRANS_OUT
TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE

print(f"Generating {TOTAL_FRAMES} frames on luxury white aesthetic...")


def make_bg(t_global):
    # Pure clean white to subtle warm off-white (253, 253, 254)
    base = Image.new("RGBA", (bw, bh), (252, 252, 254, 255))
    bd = ImageDraw.Draw(base)

    # Ultra-refined subtle grid pattern (dot grid)
    grid_gap = 25 * SS
    offset_x = int((t_global * 50 * SS) % grid_gap)
    dot_color = (226, 230, 238, 255)
    for gx in range(offset_x, bw, grid_gap):
        for gy in range(0, bh, grid_gap):
            bd.point((gx, gy), fill=dot_color)
            bd.point((gx + 1, gy), fill=dot_color)
            bd.point((gx, gy + 1), fill=dot_color)
            bd.point((gx + 1, gy + 1), fill=dot_color)

    # Elegant diagonal ambient beam/sheen (very soft cool silver/blue tint)
    sweep = (t_global * 2.0) % 1.0
    cx = int(-bw * 0.3 + sweep * bw * 1.6)
    w = int(bw * 0.3)
    band = Image.new("L", (bw, bh), 0)
    band_d = ImageDraw.Draw(band)
    band_d.polygon(
        [(cx, 0), (cx + w, 0), (cx + w - bh * 0.8, bh), (cx - bh * 0.8, bh)], fill=255
    )
    band = band.filter(ImageFilter.GaussianBlur(50 * SS))
    sheen = Image.new("RGBA", (bw, bh), (235, 240, 255, 255))
    sheen.putalpha(band.point(lambda p: int(p * 0.45)))
    base = Image.alpha_composite(base, sheen)

    # Subtle border top and bottom for luxury tech frame
    line_c = (230, 233, 240, 255)
    accent_blue = (37, 99, 235, 255)  # Electric blue accent
    bd = ImageDraw.Draw(base)
    bd.line([(0, 0), (bw, 0)], fill=line_c, width=2 * SS)
    bd.line([(0, bh - 2 * SS), (bw, bh - 2 * SS)], fill=line_c, width=2 * SS)

    # Subtle corner bracket accents
    bracket_len = 16 * SS
    # Top-left
    bd.line(
        [(8 * SS, 8 * SS), (8 * SS + bracket_len, 8 * SS)],
        fill=accent_blue,
        width=2 * SS,
    )
    bd.line(
        [(8 * SS, 8 * SS), (8 * SS, 8 * SS + bracket_len)],
        fill=accent_blue,
        width=2 * SS,
    )
    # Top-right
    bd.line(
        [(bw - 8 * SS - bracket_len, 8 * SS), (bw - 8 * SS, 8 * SS)],
        fill=accent_blue,
        width=2 * SS,
    )
    bd.line(
        [(bw - 8 * SS, 8 * SS), (bw - 8 * SS, 8 * SS + bracket_len)],
        fill=accent_blue,
        width=2 * SS,
    )
    # Bottom-left
    bd.line(
        [(8 * SS, bh - 8 * SS), (8 * SS + bracket_len, bh - 8 * SS)],
        fill=accent_blue,
        width=2 * SS,
    )
    bd.line(
        [(8 * SS, bh - 8 * SS), (8 * SS, bh - 8 * SS - bracket_len)],
        fill=accent_blue,
        width=2 * SS,
    )
    # Bottom-right
    bd.line(
        [(bw - 8 * SS - bracket_len, bh - 8 * SS), (bw - 8 * SS, bh - 8 * SS)],
        fill=accent_blue,
        width=2 * SS,
    )
    bd.line(
        [(bw - 8 * SS, bh - 8 * SS), (bw - 8 * SS, bh - 8 * SS - bracket_len)],
        fill=accent_blue,
        width=2 * SS,
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

    # Render Main Text (Pitch Black with smooth float + optical weight)
    for ci, cinfo in enumerate(cp["chars"]):
        if phase == "in":
            stagger = ci / float(max(1, n_chars)) * 0.5
            local = max(0.0, min(1.0, (pin - stagger) / (1.0 - 0.5)))
            e = ease_out_cubic(local)
            ca = e
            y_off = int((1.0 - e) * (18 * SS))
            # Blur dissipation
            blur = (1.0 - e) * 4.0 * SS
        elif phase == "hold":
            ca = 1.0
            wave = math.sin(phold * math.pi * 2 * 1.5 - ci * 0.55)
            y_off = int(wave * 2.2 * SS)
            blur = 0.0
        else:
            e = ease_in_cubic(pout)
            ca = 1.0 - e
            y_off = -int(e * 14 * SS)
            blur = e * 3.0 * SS

        if ca <= 0.02:
            continue

        # Crisp deep obsidian / dark slate (#09090b)
        text_color = (10, 10, 15, int(ca * 255))
        t_draw.text(
            (cinfo["x"], cp["base_y"] + y_off),
            cinfo["ch"],
            font=font_title,
            fill=text_color,
        )

    # Soft ambient drop shadow underneath text for 3D premium elevation
    shadow_mask = text_canvas.split()[3].filter(ImageFilter.GaussianBlur(6 * SS))
    shadow_layer = Image.new("RGBA", (bw, bh), (30, 40, 60, 0))
    shadow_layer.putalpha(shadow_mask.point(lambda p: int(p * 0.22)))
    # Shift shadow down slightly
    shadow_shifted = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    shadow_shifted.paste(shadow_layer, (0, int(4 * SS)))
    canvas = Image.alpha_composite(canvas, shadow_shifted)

    # Shimmer gleam across text during hold
    if phase == "hold":
        shimmer_pos = -0.3 + 1.6 * ease_in_out(phold)
        ray_center = cp["start_x"] + int(cp["w"] * shimmer_pos)
        ray_width = int(140 * SS)
        s_img = Image.new("L", (bw, bh), 0)
        s_draw = ImageDraw.Draw(s_img)
        s_draw.polygon(
            [
                (ray_center - ray_width + 40 * SS, 0),
                (ray_center + 40 * SS, 0),
                (ray_center + ray_width - 40 * SS, bh),
                (ray_center - 40 * SS, bh),
            ],
            fill=255,
        )
        s_blur = s_img.filter(ImageFilter.GaussianBlur(8 * SS))
        s_mask = ImageChops.multiply(text_canvas.split()[3], s_blur)

        # Electric royal blue / cyan light pass (#2563eb)
        shimmer_color = Image.new("RGBA", (bw, bh), (37, 99, 235, 0))
        shimmer_color.putalpha(s_mask.point(lambda p: int(p * 0.9)))
        text_canvas = Image.alpha_composite(text_canvas, shimmer_color)

    # Render Subtitle / Tagline
    tag_canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    tag_draw = ImageDraw.Draw(tag_canvas)

    if phase == "in":
        tag_alpha = max(0.0, min(1.0, (pin - 0.4) / 0.6))
        tag_y_shift = int((1.0 - tag_alpha) * (6 * SS))
    elif phase == "hold":
        tag_alpha = 1.0
        tag_y_shift = 0
    else:
        tag_alpha = 1.0 - pout
        tag_y_shift = -int(pout * (6 * SS))

    if tag_alpha > 0.02:
        # Subtle slate gray (#64748b) for secondary typography
        tag_color = (100, 116, 139, int(tag_alpha * 255))
        tag_draw.text(
            (cp["tag_x"], cp["tag_y"] + tag_y_shift),
            cp["tag"],
            font=font_sub,
            fill=tag_color,
        )

    canvas = Image.alpha_composite(canvas, text_canvas)
    canvas = Image.alpha_composite(canvas, tag_canvas)

    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(
            colors=128, method=Image.FASTOCTREE, dither=Image.Dither.NONE
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
