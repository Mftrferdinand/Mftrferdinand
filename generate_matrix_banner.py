from PIL import Image, ImageDraw, ImageFont

# Ukuran & Supersampling
W, H = 1000, 150
SS = 2
bw, bh = W * SS, H * SS

font_title_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_SIZE = 58 * SS
font_title = ImageFont.truetype(font_title_path, FONT_SIZE)

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
    phrase_data.append({"text": t, "w": w, "sx": sx, "sy": sy})

# Background: HITAM SOLID PEKAT (#000000)
BLACK = (0, 0, 0, 255)

FRAMES_PER_PHRASE = 36
TOTAL_FRAMES = len(phrase_data) * FRAMES_PER_PHRASE
frames = []

for gi in range(TOTAL_FRAMES):
    pi = gi // FRAMES_PER_PHRASE
    li = gi % FRAMES_PER_PHRASE
    cp = phrase_data[pi]

    canvas = Image.new("RGBA", (bw, bh), BLACK)

    # Smooth fade in (10 frame), solid hold (20 frame), fade out (6 frame)
    if li < 10:
        alpha = int((li / 10.0) * 255)
    elif li < 30:
        alpha = 255
    else:
        alpha = int((1.0 - (li - 30) / 6.0) * 255)

    text_canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(text_canvas)
    t_draw.text((cp["sx"], cp["sy"]), cp["text"], font=font_title, fill=(255, 255, 255, alpha))

    canvas = Image.alpha_composite(canvas, text_canvas)
    final_frame = canvas.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(
        final_frame.convert("RGB").quantize(colors=32, method=Image.FASTOCTREE, dither=Image.Dither.NONE)
    )

out_path = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    duration=55,
    loop=0,
    optimize=True,
)
print("Saved clean banner to", out_path)
