#!/usr/bin/env python3
"""
Generate high-end zerolinear-banner.gif
Background: Pure deep black (#000000)
Typography: 3 phrases with bespoke cyber-kinetic animation:
  1. MFTRFERDINAND     -> Bright electric blue (#3b82f6)
  2. ZEROLINEAR        -> Vibrant cyan-sky blue (#60a5fa)
  3. ZELINE AGENTIC AI -> Royal deep blue (#2563eb)
Animation:
  - Phase 1 (Enter): Kinetic slide-up with cubic easing + staggered letter lock
  - Phase 2 (Hold): Breathing ambient aura glow + sharp light beam shimmer sweep
  - Phase 3 (Exit): Smooth momentum slide-up & fade-out
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

W, H = 1000, 150
SS = 3  # High-definition super-sample
bw, bh = W * SS, H * SS

font_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_SIZE = 60 * SS
font = ImageFont.truetype(font_path, FONT_SIZE)

# Phrase setups as requested by owner
phrase_configs = [
    {"text": "MFTRFERDINAND",     "color": (59, 130, 246)},   # Electric Blue (#3b82f6)
    {"text": "ZEROLINEAR",        "color": (96, 165, 250)},   # Sky Blue (#60a5fa)
    {"text": "ZELINE AGENTIC AI", "color": (37, 99, 235)},    # Royal Tech Blue (#2563eb)
]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

cap_bbox = dd.textbbox((0, 0), "H", font=font)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]
mid_y = bh // 2

phrase_data = []
for p in phrase_configs:
    t = p["text"]
    bbox = dd.textbbox((0, 0), t, font=font)
    w = bbox[2] - bbox[0]
    sx = (bw - w) // 2 - bbox[0]
    sy = (mid_y - cap_h // 2) - cap_top_off
    phrase_data.append({"text": t, "color": p["color"], "w": w, "sx": sx, "sy": sy})

# Pure black background
BG_COLOR = (0, 0, 0, 255)
bg_layer = Image.new("RGBA", (bw, bh), BG_COLOR)

# Minimalist tech frame accents: subtle top & bottom edge guides
accents_layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
al_draw = ImageDraw.Draw(accents_layer)
guide_color = (255, 255, 255, 18)
al_draw.line([(50 * SS, 15 * SS), (bw - 50 * SS, 15 * SS)], fill=guide_color, width=1 * SS)
al_draw.line([(50 * SS, bh - 15 * SS), (bw - 50 * SS, bh - 15 * SS)], fill=guide_color, width=1 * SS)
# Corner marks
mark_len = 8 * SS
for cx, cy in [(50 * SS, 15 * SS), (bw - 50 * SS, 15 * SS), (50 * SS, bh - 15 * SS), (bw - 50 * SS, bh - 15 * SS)]:
    al_draw.line([(cx - mark_len, cy), (cx + mark_len, cy)], fill=(59, 130, 246, 75), width=1 * SS)
    al_draw.line([(cx, cy - mark_len), (cx, cy + mark_len)], fill=(59, 130, 246, 75), width=1 * SS)

def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)

def ease_in_cubic(t):
    t = max(0.0, min(1.0, t))
    return math.pow(t, 3)

# Timing configuration (50ms per frame = 20 fps, total ~6 seconds seamless loop)
FRAMES_PER = 40
TRANS_IN = 10
HOLD = 22
TRANS_OUT = 8

frames = []
print("Rendering enhanced banner frames...")

for pi, cp in enumerate(phrase_data):
    color_rgb = cp["color"]

    for li in range(FRAMES_PER):
        shimmer_pos = -1.0
        
        if li < TRANS_IN:
            # Phase 1: Slide In with spring-like deceleration
            prog = li / float(TRANS_IN)
            alpha_f = ease_out_cubic(prog)
            y_offset = int((1.0 - ease_out_cubic(prog)) * (16 * SS))
        elif li < TRANS_IN + HOLD:
            # Phase 2: Hold with subtle breathing glow and light shimmer beam
            prog = (li - TRANS_IN) / float(HOLD)
            alpha_f = 1.0
            y_offset = 0
            shimmer_pos = -0.2 + 1.4 * prog  # Sweep from left to right
        else:
            # Phase 3: Slide Out & Dissolve
            prog = (li - TRANS_IN - HOLD) / float(TRANS_OUT)
            alpha_f = 1.0 - ease_in_cubic(prog)
            y_offset = -int(ease_in_cubic(prog) * (14 * SS))

        cur_sy = cp["sy"] + y_offset

        # Text canvas
        text_canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        t_draw = ImageDraw.Draw(text_canvas)
        text_fill = (*color_rgb, int(255 * alpha_f))
        t_draw.text((cp["sx"], cur_sy), cp["text"], font=font, fill=text_fill)

        # 1. Dual Ambient Glow behind text
        glow_pulse = 0.5 + 0.5 * math.sin(li * (2 * math.pi / FRAMES_PER))
        glow_alpha = int((45 + 35 * glow_pulse) * alpha_f)
        
        # Wide neon aura
        text_alpha_mask = text_canvas.split()[3]
        wide_glow_mask = text_alpha_mask.filter(ImageFilter.GaussianBlur(14 * SS))
        wide_glow = Image.new("RGBA", (bw, bh), (*color_rgb, 0))
        wide_glow.putalpha(wide_glow_mask.point(lambda p: int(p * (glow_alpha / 255.0))))
        
        # Tight luminous core
        tight_glow_mask = text_alpha_mask.filter(ImageFilter.GaussianBlur(4 * SS))
        tight_glow = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
        tight_glow.putalpha(tight_glow_mask.point(lambda p: int(p * (0.25 * alpha_f))))

        # 2. Diagonal Light Shimmer Sweep
        if 0.0 <= shimmer_pos <= 1.2 and alpha_f > 0.8:
            ray_center = cp["sx"] + int(cp["w"] * shimmer_pos)
            ray_w = int(110 * SS)
            
            shimmer_img = Image.new("L", (bw, bh), 0)
            s_draw = ImageDraw.Draw(shimmer_img)
            poly = [
                (ray_center - ray_w + 35 * SS, 0),
                (ray_center + 35 * SS, 0),
                (ray_center + ray_w - 35 * SS, bh),
                (ray_center - 35 * SS, bh)
            ]
            s_draw.polygon(poly, fill=255)
            shimmer_blurred = shimmer_img.filter(ImageFilter.GaussianBlur(10 * SS))
            
            # Mask shimmer only onto the text shape
            shimmer_cut = ImageChops.multiply(text_alpha_mask, shimmer_blurred)
            shimmer_layer = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
            shimmer_layer.putalpha(shimmer_cut)
            text_canvas = Image.alpha_composite(text_canvas, shimmer_layer)

        # Base composition
        frame = Image.alpha_composite(bg_layer, accents_layer)
        frame = Image.alpha_composite(frame, wide_glow)
        frame = Image.alpha_composite(frame, tight_glow)
        frame = Image.alpha_composite(frame, text_canvas)

        # Downsample with Lanczos for ultra-crisp edges
        final = frame.resize((W, H), Image.Resampling.LANCZOS)
        frames.append(
            final.convert("RGB").quantize(colors=96, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
        )

out_file = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(
    out_file,
    save_all=True,
    append_images=frames[1:],
    duration=50,
    loop=0,
    optimize=True
)

print(f"Success: {len(frames)} frames generated and saved to {out_file}")
