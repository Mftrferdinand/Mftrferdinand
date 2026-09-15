import math
import random
from PIL import Image, ImageDraw, ImageFont

# Ukuran & Supersampling
W, H = 1000, 150
SS = 2
bw, bh = W * SS, H * SS

font_title_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
font_code_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"

# Ukuran font: Besar, tegas, optical center konsisten
FONT_SIZE = 58 * SS
CODE_SIZE = 13 * SS

font_title = ImageFont.truetype(font_title_path, FONT_SIZE)
font_code = ImageFont.truetype(font_code_path, CODE_SIZE)

phrases = ["MFTRFERDINAND", "ZEROLINEAR", "ZELINE AGENTIC AI"]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

# Hitung optical center huruf kapital
cap_bbox = dd.textbbox((0, 0), "H", font=font_title)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]
mid_y = bh // 2

phrase_data = []
for t in phrases:
    bbox = dd.textbbox((0, 0), t, font=font_title)
    w = bbox[2] - bbox[0]
    sx = (bw - w) // 2 - bbox[0]
    sy = (mid_y - cap_h // 2) - cap_top_off
    
    # Hitung posisi x tiap huruf agar animasi decode per karakter presisi
    char_positions = []
    curr_x = sx
    for char in t:
        c_box = dd.textbbox((0, 0), char, font=font_title)
        cw = c_box[2] - c_box[0]
        adv_box = dd.textbbox((0, 0), char + "A", font=font_title)
        a_box = dd.textbbox((0, 0), "A", font=font_title)
        adv = (adv_box[2] - adv_box[0]) - (a_box[2] - a_box[0])
        char_positions.append({"char": char, "x": curr_x, "w": cw})
        curr_x += max(adv, cw)
    
    phrase_data.append({"text": t, "w": w, "sx": sx, "sy": sy, "chars": char_positions})

# Warna dasar: 100% BIRU SOLID MURNI (#2563eb)
BLUE = (37, 99, 235, 255)

# Karakter untuk background matrix / CLI rain
CODE_CHARS = list("0123456789ABCDEF010101<>{}[]/*+=-~$#@!_?%&|:;")
SCRAMBLE_CHARS = list("0123456789ABCDEF!@#$%&*<>[]{}01")

# Kolom Matrix Rain
random.seed(42)
NUM_COLS = 50
col_spacing = bw / NUM_COLS
rain_columns = []
for i in range(NUM_COLS):
    speed = random.uniform(5.5 * SS, 9.0 * SS)
    length = random.randint(7, 14)
    offset_y = random.uniform(-bh, bh)
    chars = [random.choice(CODE_CHARS) for _ in range(35)]
    rain_columns.append({
        "x": int(i * col_spacing + col_spacing * 0.1),
        "speed": speed,
        "length": length,
        "y": offset_y,
        "chars": chars
    })

# Timing:
# 3 frasa x 36 frame = 108 frame total
# - DECRYPTING (karakter teracak lalu ngunci per huruf): 14 frame
# - SOLID HOLD (teks putih murni, matrix rain tetap ngalir): 16 frame
# - QUICK DISSOLVE: 6 frame
FRAMES_PER_PHRASE = 36
TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE
frames = []

row_h = int(14 * SS)

print(f"Generating {TOTAL_FRAMES} clean frames (zero shadow, zero vignette)...")

for gi in range(TOTAL_FRAMES):
    pi = gi // FRAMES_PER_PHRASE
    li = gi % FRAMES_PER_PHRASE
    cp = phrase_data[pi]
    
    # 1. Base canvas: 100% BIRU SOLID FLAT (tanpa gradasi, tanpa vignette)
    canvas = Image.new("RGBA", (bw, bh), BLUE)
    
    # 2. Render Matrix Rain (warna cyan & putih jernih langsung di atas biru)
    rain_draw = ImageDraw.Draw(canvas)
    for col in rain_columns:
        head_y = (col["y"] + gi * col["speed"]) % (bh + col["length"] * row_h) - (col["length"] * row_h)
        for ci in range(col["length"]):
            char_y = head_y - ci * row_h
            if -row_h <= char_y < bh + row_h:
                char = col["chars"][(gi + ci) % len(col["chars"])]
                if ci == 0:
                    # Head: Putih bersih tajam
                    c_color = (255, 255, 255, 220)
                elif ci < 3:
                    # Upper trail: Cyan terang
                    c_color = (180, 220, 255, 170)
                else:
                    # Lower trail: Biru muda transparan
                    fade = 1.0 - (ci / col["length"])
                    alpha = int(120 * fade)
                    c_color = (120, 180, 255, alpha)
                
                if c_color[3] > 20:
                    rain_draw.text((col["x"], int(char_y)), char, font=font_code, fill=c_color)
    
    # 3. Main Text (CRISP FLAT WHITE - TANPA SHADOW, TANPA BLUR GLOW)
    n_chars = len(cp["chars"])
    
    if li < 14:
        prog = li / 14.0
        locked_count = int(n_chars * prog)
        text_alpha = min(255, int(prog * 260) + 70)
    elif li < 30:
        locked_count = n_chars
        text_alpha = 255
    else:
        prog_out = (li - 30) / 6.0
        locked_count = int(n_chars * (1.0 - prog_out * 0.5))
        text_alpha = max(0, int(255 * (1.0 - prog_out)))
        
    text_canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(text_canvas)
    
    for idx, cinfo in enumerate(cp["chars"]):
        if idx < locked_count:
            char_to_draw = cinfo["char"]
            char_color = (255, 255, 255, text_alpha)
        else:
            char_to_draw = random.choice(SCRAMBLE_CHARS) if text_alpha > 40 else ""
            char_color = (180, 225, 255, int(text_alpha * 0.8))
            
        if char_to_draw:
            t_draw.text((cinfo["x"], cp["sy"]), char_to_draw, font=font_title, fill=char_color)
            
    canvas = Image.alpha_composite(canvas, text_canvas)
    
    # Downscale supersample Lanczos
    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    # Quantize dengan dither=NONE untuk memastikan warna flat bersih tanpa bintik/noise
    frames.append(final_frame.convert("RGB").quantize(colors=64, method=Image.FASTOCTREE, dither=Image.Dither.NONE))

out_path = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=55, loop=0, optimize=False)
print("Saved cleanly to", out_path)
