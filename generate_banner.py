import math
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
W, H = 1000, 150
SS = 2 # Supersampling for crisp anti-aliased text
bw, bh = W * SS, H * SS

# Fonts
font_path_bold = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
font_path_light = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf"

FONT_SIZE = 52 * SS
font_bold = ImageFont.truetype(font_path_bold, FONT_SIZE)
font_light = ImageFont.truetype(font_path_light, FONT_SIZE)

# Phrases to cycle ultra-cleanly
phrases = [
    {"main": "MFTRFERDINAND", "sub": ""},
    {"main": "ZEROLINEAR", "sub": ""},
    {"main": "ZELINE AGENTIC AI", "sub": ""},
]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

# Setup colors & measurements
BG_COLOR = (0, 0, 0, 255) # Pure black background
TEXT_MAIN = (59, 130, 246) # Crisp blue text
TEXT_SUB = (37, 99, 235) # Deeper blue muted subtitle
ACCENT_BLUE = (59, 130, 246) # Crisp minimalist accent dot / line

FRAMES_PER_PHRASE = 30
FADE_IN_FRAMES = 8
HOLD_FRAMES = 16
FADE_OUT_FRAMES = 6
TOTAL_FRAMES = len(phrases) * FRAMES_PER_PHRASE

frames = []

for gi in range(TOTAL_FRAMES):
    pi = gi // FRAMES_PER_PHRASE
    fi = gi % FRAMES_PER_PHRASE
    p = phrases[pi]
    
    # Calculate opacity curve (smooth cosine ease-in-out)
    if fi < FADE_IN_FRAMES:
        alpha = (1.0 - math.cos((fi / FADE_IN_FRAMES) * math.pi)) / 2.0
    elif fi < FADE_IN_FRAMES + HOLD_FRAMES:
        alpha = 1.0
    else:
        out_i = fi - (FADE_IN_FRAMES + HOLD_FRAMES)
        alpha = (1.0 + math.cos((out_i / FADE_OUT_FRAMES) * math.pi)) / 2.0

    canvas = Image.new("RGBA", (bw, bh), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # Calculate centered position for main text
    main_bbox = dd.textbbox((0, 0), p["main"], font=font_bold)
    main_w = main_bbox[2] - main_bbox[0]
    main_h = main_bbox[3] - main_bbox[1]

    main_x = (bw - main_w) // 2 - main_bbox[0]
    start_y = (bh - main_h) // 2 - main_bbox[1]

    # Draw Main Text (Smooth Fade)
    m_r, m_g, m_b = TEXT_MAIN
    main_color = (m_r, m_g, m_b, int(255 * alpha))
    draw.text((main_x, start_y), p["main"], font=font_bold, fill=main_color)

    # Downsample Lanczos for pristine crisp text rendering
    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(colors=32, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    )

out_file = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(
    out_file,
    save_all=True,
    append_images=frames[1:],
    duration=65,
    loop=0,
    optimize=True
)

print(f"Generated ultra-minimalist banner: {len(frames)} frames to {out_file}")
