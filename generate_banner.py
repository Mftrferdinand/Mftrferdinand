#!/usr/bin/env python3
"""
Generate zerolinear-banner.gif
Background: pure black (#000000)
Text: all blue shades — bright blue for MFTRFERDINAND,
      sky-blue for ZEROLINEAR, deep-electric for ZELINE AGENTIC AI.
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

W, H = 1000, 150
SS   = 3                  # super-sample factor for crisp AA
bw, bh = W * SS, H * SS

font_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_SIZE = 62 * SS

# ── colour palette (all blue) ──────────────────────────────────────────────
# MFTRFERDINAND : bright electric blue  #3b82f6
# ZEROLINEAR    : lighter cyan-blue     #60a5fa
# ZELINE AGENTIC AI : deeper royal blue #1d4ed8
phrase_configs = [
    {"text": "MFTRFERDINAND",    "color": (59,  130, 246)},   # #3b82f6  electric blue
    {"text": "ZEROLINEAR",       "color": (96,  165, 250)},   # #60a5fa  sky blue
    {"text": "ZELINE AGENTIC AI","color": (29,   78, 216)},   # #1d4ed8  royal blue
]

# ── measure text ───────────────────────────────────────────────────────────
dummy = Image.new("RGBA", (1, 1))
dd    = ImageDraw.Draw(dummy)
font  = ImageFont.truetype(font_path, FONT_SIZE)

cap_bbox   = dd.textbbox((0, 0), "H", font=font)
cap_h      = cap_bbox[3] - cap_bbox[1]
cap_top_off= cap_bbox[1]
mid_y      = bh // 2

phrase_data = []
for p in phrase_configs:
    t    = p["text"]
    bbox = dd.textbbox((0, 0), t, font=font)
    w    = bbox[2] - bbox[0]
    sx   = (bw - w) // 2 - bbox[0]
    sy   = (mid_y - cap_h // 2) - cap_top_off
    phrase_data.append({"text": t, "color": p["color"], "w": w, "sx": sx, "sy": sy})

max_w = int(bw * 0.94)
for p in phrase_data:
    assert p["w"] <= max_w, f"'{p['text']}' too wide ({p['w']} > {max_w})"

# ── background: pure black ─────────────────────────────────────────────────
BG_COLOR = (0, 0, 0, 255)
bg_layer = Image.new("RGBA", (bw, bh), BG_COLOR)

# ── easing helpers ─────────────────────────────────────────────────────────
def ease_in_out(t):
    return 0.5 * (1.0 - math.cos(math.pi * max(0.0, min(1.0, t))))

def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)

# ── animation params ───────────────────────────────────────────────────────
FRAMES_PER = 45
TRANS_IN   = 12
HOLD       = 23
TRANS_OUT  = 10

frames = []

for pi, cp in enumerate(phrase_data):
    color_rgb = cp["color"]

    for li in range(FRAMES_PER):
        if li < TRANS_IN:
            prog     = li / TRANS_IN
            alpha_f  = ease_out_cubic(prog)
            y_offset = int((1.0 - ease_out_cubic(prog)) * (18 * SS))
        elif li < TRANS_IN + HOLD:
            prog     = (li - TRANS_IN) / HOLD
            alpha_f  = 1.0
            y_offset = 0
        else:
            prog     = (li - TRANS_IN - HOLD) / TRANS_OUT
            alpha_f  = 1.0 - ease_in_out(prog)
            y_offset = -int(ease_in_out(prog) * (18 * SS))

        cur_sy = cp["sy"] + y_offset

        # crisp text mask
        cur_mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(cur_mask).text(
            (cp["sx"], cur_sy), cp["text"], font=font, fill=int(255 * alpha_f)
        )

        # subtle blue glow (more intense for blue text to make it pop on black)
        glow_pulse = 0.5 + 0.5 * math.sin(li * (2 * math.pi / FRAMES_PER))
        glow_alpha = int((50 + 55 * glow_pulse) * alpha_f)

        glow_layer = Image.new("RGBA", (bw, bh), (*color_rgb, glow_alpha))
        glow_mask  = cur_mask.filter(ImageFilter.GaussianBlur(14 * SS))
        glow_layer.putalpha(
            ImageChops.multiply(glow_mask, Image.new("L", (bw, bh), glow_alpha))
        )

        # crisp text layer
        text_layer = Image.new("RGBA", (bw, bh), (*color_rgb, 255))
        text_layer.putalpha(cur_mask)

        # composite over black background
        frame = Image.alpha_composite(bg_layer, glow_layer)
        frame = Image.alpha_composite(frame, text_layer)

        # downsample with LANCZOS for sharp AA
        final = frame.resize((W, H), Image.Resampling.LANCZOS)
        frames.append(
            final.convert("RGB").quantize(colors=128, method=Image.Quantize.MAXCOVERAGE)
        )

out = "/data/data/com.termux/files/home/_gh_mftr/assets/zerolinear-banner.gif"
frames[0].save(
    out, save_all=True, append_images=frames[1:],
    duration=50, loop=0, optimize=True
)
print(f"Done: {len(frames)} frames → {out}")
