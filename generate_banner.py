import math
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

W, H = 1000, 150
SS = 3
bw, bh = W * SS, H * SS
font_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"

FONT_SIZE = 62 * SS
phrases = ["MFTRFERDINAND", "ZEROLINEAR", "ZELINE AGENTIC AI"]

dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)
font = ImageFont.truetype(font_path, FONT_SIZE)

cap_bbox = dd.textbbox((0, 0), "H", font=font)
cap_h = cap_bbox[3] - cap_bbox[1]
cap_top_off = cap_bbox[1]

mid_y = bh // 2

phrase_data = []
for t in phrases:
    bbox = dd.textbbox((0, 0), t, font=font)
    w = bbox[2] - bbox[0]
    sx = (bw - w) // 2 - bbox[0]
    sy = (mid_y - cap_h // 2) - cap_top_off
    phrase_data.append({"text": t, "w": w, "sx": sx, "sy": sy})

max_w = int(bw * 0.94)
for p in phrase_data:
    assert p["w"] <= max_w, f"'{p['text']}' terlalu lebar ({p['w']} > {max_w})"

BLUE = (37, 99, 235, 255)
bubble = Image.new("RGBA", (bw, bh), BLUE)

# Render base masks per phrase
base_masks = []
for cp in phrase_data:
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).text((cp["sx"], cp["sy"]), cp["text"], font=font, fill=255)
    base_masks.append(mask)

def ease_in_out(t):
    return 0.5 * (1.0 - math.cos(math.pi * max(0.0, min(1.0, t))))

def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)

# Timing budget per phrase:
# Total 45 frames per phrase (~2.25s per phrase, total 6.75s loop)
# 1) Slide up + Smooth Fade-in: 12 frames
# 2) Elegant breathing / subtle glow pulse: 23 frames
# 3) Smooth Slide up + Fade-out exit: 10 frames
FRAMES_PER = 45
TRANS_IN = 12
HOLD = 23
TRANS_OUT = 10

frames = []

for pi in range(len(phrase_data)):
    cp = phrase_data[pi]
    base_m = base_masks[pi]
    
    for li in range(FRAMES_PER):
        if li < TRANS_IN:
            # Masuk: slide naik perlahan dari +18px ke 0px + fade in
            prog = li / TRANS_IN
            alpha_f = ease_out_cubic(prog)
            y_offset = int((1.0 - ease_out_cubic(prog)) * (18 * SS))
        elif li < TRANS_IN + HOLD:
            # Hold: tenang, ada breathing pulse lembut
            prog = (li - TRANS_IN) / HOLD
            alpha_f = 1.0
            y_offset = 0
        else:
            # Keluar: slide naik lagi dari 0px ke -18px + fade out
            prog = (li - TRANS_IN - HOLD) / TRANS_OUT
            alpha_f = 1.0 - ease_in_out(prog)
            y_offset = -int(ease_in_out(prog) * (18 * SS))
            
        # Posisi vertikal dinamis
        cur_sy = cp["sy"] + y_offset
        
        # Buat mask teks bergeser
        cur_mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(cur_mask).text((cp["sx"], cur_sy), cp["text"], font=font, fill=int(255 * alpha_f))
        
        # Ambient subtle glow di belakang teks
        glow_pulse = 0.5 + 0.5 * math.sin(li * (2 * math.pi / FRAMES_PER))
        glow_alpha = int((30 + 40 * glow_pulse) * alpha_f)
        
        glow_layer = Image.new("RGBA", (bw, bh), (255, 255, 255, glow_alpha))
        # Mask glow dengan teks yang di-blur
        glow_mask = cur_mask.filter(ImageFilter.GaussianBlur(8 * SS))
        glow_layer.putalpha(ImageChops.multiply(glow_mask, Image.new("L", (bw, bh), glow_alpha)))
        
        # Crisp white text layer
        text_layer = Image.new("RGBA", (bw, bh), (255, 255, 255, 255))
        text_layer.putalpha(cur_mask)
        
        # Composite di atas background biru solid
        frame = Image.alpha_composite(bubble, glow_layer)
        frame = Image.alpha_composite(frame, text_layer)
        
        # Downscale supersample untuk ultra-smooth anti-aliasing
        final = frame.resize((W, H), Image.Resampling.LANCZOS)
        frames.append(final.convert("RGB").quantize(colors=64, method=Image.FASTOCTREE))

out = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=50, loop=0, optimize=False)

print(f"Selesai: {len(frames)} frames disimpan ke {out}")
