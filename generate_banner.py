import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1000, 150
SS = 2
bw, bh = W * SS, H * SS

font_title_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
font_code_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"

FONT_SIZE = 58 * SS
font_title = ImageFont.truetype(font_title_path, FONT_SIZE)
font_code = ImageFont.truetype(font_code_path, FONT_SIZE)

# 3 Frasa:
# 1. MFTRFERDINAND -> Bright Electric Blue (#3b82f6)
# 2. ZEROLINEAR -> Sky Blue (#60a5fa)
# 3. ZELINE AGENTIC AI -> Royal / Cyber Deep Blue (#2563eb)
phrase_configs = [
    {"text": "MFTRFERDINAND", "color": (59, 130, 246)},
    {"text": "ZEROLINEAR", "color": (96, 165, 250)},
    {"text": "ZELINE AGENTIC AI", "color": (37, 99, 235)},
]

SCRAMBLE_POOL = list("0123456789ABCDEF!@#$%&*<>[]{}~+/=")

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

cap_bbox = dd.textbbox((0, 0), "H", font=font_title)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]
mid_y = bh // 2

phrase_data = []
for p in phrase_configs:
    t = p["text"]
    bbox = dd.textbbox((0, 0), t, font=font_title)
    w = bbox[2] - bbox[0]
    sx = (bw - w) // 2 - bbox[0]
    sy = (mid_y - cap_h // 2) - cap_top_off
    
    chars = []
    curr_x = sx
    for c in t:
        cw = dd.textlength(c, font=font_title)
        chars.append({"char": c, "x": curr_x, "w": cw})
        curr_x += cw
        
    phrase_data.append({
        "text": t,
        "color": p["color"],
        "w": w,
        "sx": sx,
        "sy": sy,
        "chars": chars,
        "len": len(chars)
    })

BLACK = (0, 0, 0, 255)

# Frame timings (FPS: 20 -> 50ms per frame)
# Total per phrase: 38 frames (~1.9s per phrase, total ~5.7s loop)
FRAMES_PER_PHRASE = 38
DECRYPT_FRAMES = 14  # Karakter me-lock satu per satu dari kiri ke kanan
HOLD_FRAMES = 18     # Teks solid + shimmer beam + breathing glow
EXIT_FRAMES = 6      # Glitch flash + dissolve out

TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE
frames = []

random.seed(1337)

print(f"Generating {TOTAL_FRAMES} frames of High-Tech Decrypt & Shimmer...")

for gi in range(TOTAL_FRAMES):
    pi = gi // FRAMES_PER_PHRASE
    li = gi % FRAMES_PER_PHRASE
    cp = phrase_data[pi]
    color_rgb = cp["color"]

    # Base: Pure deep black
    canvas = Image.new("RGBA", (bw, bh), BLACK)

    # 1. Text Canvas
    text_canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(text_canvas)

    n_chars = cp["len"]
    shimmer_progress = -1.0
    text_alpha = 255

    if li < DECRYPT_FRAMES:
        # Phase 1: DECRYPT LOCK-IN
        prog = li / float(DECRYPT_FRAMES)
        # Staggered lock index
        locked_chars = int(prog * (n_chars + 2))
        
        for idx, cinfo in enumerate(cp["chars"]):
            char_real = cinfo["char"]
            if char_real == " ":
                continue
                
            if idx < locked_chars:
                # Sudah locked: warna teks asli solid
                t_draw.text((cinfo["x"], cp["sy"]), char_real, font=font_title, fill=(*color_rgb, 255))
            elif idx == locked_chars:
                # Sedang decrypting (head focus): White luminous glyph
                scramble_c = random.choice(SCRAMBLE_POOL)
                t_draw.text((cinfo["x"], cp["sy"]), scramble_c, font=font_code, fill=(255, 255, 255, 255))
            else:
                # Belum locked: Scramble glyph warna biru elektrik transparan
                scramble_c = random.choice(SCRAMBLE_POOL)
                t_draw.text((cinfo["x"], cp["sy"]), scramble_c, font=font_code, fill=(*color_rgb, 150))
                
    elif li < DECRYPT_FRAMES + HOLD_FRAMES:
        # Phase 2: HOLD + SHIMMER BEAM + BREATHING GLOW
        hold_prog = (li - DECRYPT_FRAMES) / float(HOLD_FRAMES)
        # Gambar semua teks locked
        for cinfo in cp["chars"]:
            if cinfo["char"] != " ":
                t_draw.text((cinfo["x"], cp["sy"]), cinfo["char"], font=font_title, fill=(*color_rgb, 255))
        
        # Shimmer ray sweeps across
        shimmer_progress = -0.2 + 1.4 * hold_prog

    else:
        # Phase 3: SMOOTH DISSOLVE EXIT
        out_prog = (li - DECRYPT_FRAMES - HOLD_FRAMES) / float(EXIT_FRAMES)
        text_alpha = int((1.0 - out_prog) * 255)
        for cinfo in cp["chars"]:
            if cinfo["char"] != " ":
                t_draw.text((cinfo["x"], cp["sy"]), cinfo["char"], font=font_title, fill=(*color_rgb, text_alpha))

    # 2. Ambient Aura Glow behind Text
    alpha_mask = text_canvas.split()[3]
    if text_alpha > 30:
        pulse = 0.5 + 0.5 * math.sin(li * (2 * math.pi / FRAMES_PER_PHRASE))
        glow_val = int((40 + 35 * pulse) * (text_alpha / 255.0))
        
        glow_mask = alpha_mask.filter(ImageFilter.GaussianBlur(10 * SS))
        glow_layer = Image.new("RGBA", (bw, bh), (*color_rgb, 0))
        glow_layer.putalpha(glow_mask.point(lambda p: int(p * (glow_val / 255.0))))
        canvas = Image.alpha_composite(canvas, glow_layer)

    # 3. Shimmer Ray Highlight (Sinar kilap diagonal terang)
    if 0.0 <= shimmer_progress <= 1.2:
        ray_center = cp["sx"] + int(cp["w"] * shimmer_progress)
        ray_w = int(120 * SS)
        
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
        
        shimmer_cut = ImageChops.multiply(alpha_mask, shimmer_blurred)
        shimmer_layer = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
        shimmer_layer.putalpha(shimmer_cut)
        text_canvas = Image.alpha_composite(text_canvas, shimmer_layer)

    canvas = Image.alpha_composite(canvas, text_canvas)

    # Downscale supersample Lanczos
    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(colors=64, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
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

print(f"Successfully generated high-end banner: {len(frames)} frames to {out_file}")
