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

phrase_data = []
for t in phrases:
    bbox = dd.textbbox((0, 0), t, font=font_title)
    w = bbox[2] - bbox[0]
    sx = (bw - w) // 2 - bbox[0]
    sy = (mid_y - cap_h // 2) - cap_top_off
    phrase_data.append({"text": t, "w": w, "sx": sx, "sy": sy})

BLACK = (0, 0, 0, 255)

def ease_out_cubic(x):
    return 1 - math.pow(1 - x, 3)

def ease_in_cubic(x):
    return math.pow(x, 3)

FRAMES_PER_PHRASE = 38
TRANS_IN = 10
HOLD = 20
TRANS_OUT = 8

TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE
frames = []

print(f"Rendering {TOTAL_FRAMES} frames...")

for gi in range(TOTAL_FRAMES):
    pi = gi // FRAMES_PER_PHRASE
    li = gi % FRAMES_PER_PHRASE
    cp = phrase_data[pi]

    canvas = Image.new("RGBA", (bw, bh), BLACK)

    # State timing:
    if li < TRANS_IN:
        progress = li / float(TRANS_IN)
        alpha = ease_out_cubic(progress)
        # Meluncur naik lembut dari +14px ke 0
        y_offset = int((1.0 - ease_out_cubic(progress)) * (14 * SS))
        shimmer_pos = -0.5
    elif li < TRANS_IN + HOLD:
        alpha = 1.0
        y_offset = 0
        hold_prog = (li - TRANS_IN) / float(HOLD)
        # Shimmer melintasi teks dari kiri ke kanan secara smooth
        shimmer_pos = -0.2 + 1.4 * hold_prog
    else:
        out_prog = (li - (TRANS_IN + HOLD)) / float(TRANS_OUT)
        alpha = 1.0 - ease_in_cubic(out_prog)
        # Meluncur naik tipis saat keluar (0 ke -10px)
        y_offset = -int(ease_in_cubic(out_prog) * (10 * SS))
        shimmer_pos = 1.5

    cur_sy = cp["sy"] + y_offset

    # Layer teks dasar putih tajam
    text_canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(text_canvas)
    fill_alpha = int(alpha * 255)
    t_draw.text((cp["sx"], cur_sy), cp["text"], font=font_title, fill=(255, 255, 255, fill_alpha))

    # Glow layer halus di belakang teks saat hold
    if alpha > 0.3:
        glow_mask = text_canvas.split()[3].filter(ImageFilter.GaussianBlur(8 * SS))
        glow_layer = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
        # Ambient subtle white glow
        glow_intensity = int(alpha * 38)
        glow_alpha_channel = glow_mask.point(lambda p: int(p * (glow_intensity / 255.0)))
        glow_layer.putalpha(glow_alpha_channel)
        canvas = Image.alpha_composite(canvas, glow_layer)

    # Shimmer ray effect (cahaya perak bergerak di atas teks)
    if -0.2 <= shimmer_pos <= 1.2 and fill_alpha > 100:
        ray_center = cp["sx"] + int(cp["w"] * shimmer_pos)
        ray_width = int(140 * SS)
        
        # Mask shimmer
        shimmer_img = Image.new("L", (bw, bh), 0)
        s_draw = ImageDraw.Draw(shimmer_img)
        # Gambar pita miring (sheared beam)
        poly = [
            (ray_center - ray_width + 40 * SS, 0),
            (ray_center + 40 * SS, 0),
            (ray_center + ray_width - 40 * SS, bh),
            (ray_center - 40 * SS, bh)
        ]
        s_draw.polygon(poly, fill=255)
        shimmer_blurred = shimmer_img.filter(ImageFilter.GaussianBlur(12 * SS))
        
        # Kali dengan alpha channel teks agar shimmer hanya muncul di dalam badan teks
        shimmer_text_mask = ImageChops.multiply(text_canvas.split()[3], shimmer_blurred)
        
        # Tambahkan shimmer layer (putih ekstra terang 100%)
        shimmer_layer = Image.new("RGBA", (bw, bh), (255, 255, 255, 0))
        shimmer_layer.putalpha(shimmer_text_mask)
        text_canvas = Image.alpha_composite(text_canvas, shimmer_layer)

    canvas = Image.alpha_composite(canvas, text_canvas)

    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(colors=48, method=Image.FASTOCTREE, dither=Image.Dither.NONE)
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
print("Finished saving:", out_path)
