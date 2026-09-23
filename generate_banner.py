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
    {"main": "MFTRFERDINAND", "sub": "AI & WEB3 ARCHITECT"},
    {"main": "ZEROLINEAR", "sub": "AUTONOMOUS AGENTIC AI"},
    {"main": "ZELINE", "sub": "MODEL-AGNOSTIC AI FRAMEWORK"},
]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)

# Setup colors & measurements
BG_COLOR = (10, 11, 14, 255) # Deep sleek graphite background
TEXT_MAIN = (240, 243, 248) # Off-white crisp text
TEXT_SUB = (120, 130, 145) # Subtle slate muted subtitle
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
    
    sub_bbox = dd.textbbox((0, 0), p["sub"], font=font_light)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    
    spacing = 14 * SS
    total_h = main_h + spacing + sub_h
    start_y = (bh - total_h) // 2 - main_bbox[1]

    main_x = (bw - main_w) // 2 - main_bbox[0]
    sub_x = (bw - sub_w) // 2 - sub_bbox[0]
    sub_y = start_y + main_h + spacing

    # Draw Main Text (Smooth Fade)
    m_r, m_g, m_b = TEXT_MAIN
    main_color = (m_r, m_g, m_b, int(255 * alpha))
    draw.text((main_x, start_y), p["main"], font=font_bold, fill=main_color)

    # Accent Dot next to Main text
    dot_size = 6 * SS
    dot_x = main_x + main_w + (12 * SS)
    dot_y = start_y + (main_h // 2) - (dot_size // 2)
    acc_r, acc_g, acc_b = ACCENT_BLUE
    draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], fill=(acc_r, acc_g, acc_b, int(255 * alpha)))

    # Draw Subtitle
    s_r, s_g, s_b = TEXT_SUB
    sub_color = (s_r, s_g, s_b, int(180 * alpha))
    draw.text((sub_x, sub_y), p["sub"], font=font_light, fill=sub_color)

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
