import math
import random
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Canvas settings
W, H = 1000, 200
SS = 2
bw, bh = W * SS, H * SS

font_mono_path = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
font_regular_mono = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansMono.ttf"

font_title = ImageFont.truetype(font_mono_path, 44 * SS)
font_sub = ImageFont.truetype(font_mono_path, 13 * SS)
font_matrix = ImageFont.truetype(font_regular_mono, 11 * SS)
font_badge = ImageFont.truetype(font_mono_path, 11 * SS)

# Phrases that cycle
phrases = [
    ("MFTRFERDINAND", "TARGET: IN-SCOPE // BOUNTY HUNTER", "[ STATUS: EXPLOIT LOADED ]", "0x01"),
    ("SECURITY RESEARCH", "RECON // REVERSE ENG // SYSTEM PWN", "[ SEVERITY: CRITICAL P1 ]", "0x02"),
    ("ZELINE AGENTIC AI", "AUTONOMOUS AGENT // ETHICAL HACKING", "[ SUBMISSION: VALIDATED ]", "0x03"),
]

# Matrix / Hex stream setup
random.seed(1337)
NUM_COLS = 50
col_chars = []
hex_alphabet = "0123456789ABCDEF!@#$%&*<>/{}:~_[]"

for _ in range(NUM_COLS):
    col_chars.append([random.choice(hex_alphabet) for _ in range(16)])

col_speeds = [random.uniform(0.6, 1.4) for _ in range(NUM_COLS)]
col_offsets = [random.uniform(0, 20) for _ in range(NUM_COLS)]

# Glitch snippets
GLITCH_SNIPPETS = [
    "CVE-2026-9041", "RCE_VERIFIED", "SQLi_DUMP", "PAYLOAD_INJECT", "BYPASS_AUTH", "SCOPE_MATCH"
]

def render_frame(phrase_idx, t_in_phrase, global_frame, total_frames):
    # Base background: deep cyber black/slate
    # Color palette: Terminal Green + Electric Cyan Cyberpunk
    im = Image.new("RGBA", (bw, bh), (7, 11, 14, 255))
    draw = ImageDraw.Draw(im)

    t_global = global_frame / total_frames
    p_title, p_sub, p_badge, p_code = phrases[phrase_idx]

    # 1. Subtle Cyber Grid
    grid_sz = 30 * SS
    for x in range(0, bw, grid_sz):
        draw.line([(x, 0), (x, bh)], fill=(12, 24, 25, 180), width=1)
    for y in range(0, bh, grid_sz):
        draw.line([(0, y), (bw, y)], fill=(12, 24, 25, 180), width=1)

    # 2. Matrix Digital Rain (Falling hex streams in background)
    col_w = bw / NUM_COLS
    for i in range(NUM_COLS):
        cx = int(i * col_w + col_w / 2)
        speed = col_speeds[i]
        offset = (col_offsets[i] + global_frame * speed * 0.4) % 18
        
        for j in range(14):
            char_y = int(j * 16 * SS + (offset * 12 * SS)) % bh
            char = col_chars[i][(j + int(offset)) % len(col_chars[i])]
            
            # Distance from head gives alpha / color brightness
            fade = 1.0 - (j / 14.0)
            if j == 0:
                # Head: bright white-cyan
                color = (180, 255, 220, 160)
            else:
                # Tail: cyber matrix green/emerald
                color = (0, int(180 * fade) + 30, int(110 * fade) + 20, int(120 * fade) + 15)
            
            draw.text((cx, char_y), char, font=font_matrix, fill=color)

    # 3. Ambient Cyber Glow / Vignette
    glow = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    # Green pulse center
    center_pulse = 0.5 + 0.5 * math.sin(global_frame * 0.15)
    gr = int(bw * 0.35)
    gx = bw // 2
    gy = bh // 2
    gd.ellipse([gx - gr, gy - int(gr*0.4), gx + gr, gy + int(gr*0.4)], fill=(0, 220, 130, int(25 + 15 * center_pulse)))
    glow = glow.filter(ImageFilter.GaussianBlur(50 * SS))
    im = Image.alpha_composite(im, glow)
    draw = ImageDraw.Draw(im)

    # 4. HUD Hacker UI Elements (Corner brackets, scope markers, target crosshair)
    # HUD Borders
    pad = 14 * SS
    corner_len = 22 * SS
    c_green = (0, 255, 136, 230)
    c_dim = (0, 180, 100, 140)

    # Top-Left Bracket
    draw.line([(pad, pad), (pad + corner_len, pad)], fill=c_green, width=2*SS)
    draw.line([(pad, pad), (pad, pad + corner_len)], fill=c_green, width=2*SS)
    # Top-Right Bracket
    draw.line([(bw - pad, pad), (bw - pad - corner_len, pad)], fill=c_green, width=2*SS)
    draw.line([(bw - pad, pad), (bw - pad, pad + corner_len)], fill=c_green, width=2*SS)
    # Bottom-Left Bracket
    draw.line([(pad, bh - pad), (pad + corner_len, bh - pad)], fill=c_green, width=2*SS)
    draw.line([(pad, bh - pad), (pad, bh - pad - corner_len)], fill=c_green, width=2*SS)
    # Bottom-Right Bracket
    draw.line([(bw - pad, bh - pad), (bw - pad - corner_len, bh - pad)], fill=c_green, width=2*SS)
    draw.line([(bw - pad, bh - pad), (bw - pad, bh - pad - corner_len)], fill=c_green, width=2*SS)

    # Top Status Bar
    draw.text((pad + 28 * SS, pad - 2 * SS), f"[SYS.INT: 0x{phrase_idx+1:02X}] VULN_LAB // SCOPE: LIVE", font=font_badge, fill=c_dim)
    draw.text((bw - pad - 190 * SS, pad - 2 * SS), f"LATENCY: {18 + (global_frame % 7)*2}ms // PORT: 443", font=font_badge, fill=c_dim)

    # Bottom Status Bar
    draw.text((pad + 28 * SS, bh - pad - 12 * SS), f"HASH: SHA256:{hash((p_title, global_frame)) & 0xFFFFFFFFFFFF:012x}", font=font_badge, fill=c_dim)
    
    # Blinking RED REC or GREEN EXPLOIT indicator
    blink = (global_frame // 8) % 2 == 0
    if blink:
        draw.ellipse([(bw - pad - 14 * SS, bh - pad - 10 * SS), (bw - pad - 6 * SS, bh - pad - 2 * SS)], fill=(255, 60, 60, 255))
        draw.text((bw - pad - 60 * SS, bh - pad - 12 * SS), "HUNTING", font=font_badge, fill=(255, 80, 80, 255))
    else:
        draw.ellipse([(bw - pad - 14 * SS, bh - pad - 10 * SS), (bw - pad - 6 * SS, bh - pad - 2 * SS)], fill=(0, 255, 136, 255))
        draw.text((bw - pad - 60 * SS, bh - pad - 12 * SS), "ONLINE", font=font_badge, fill=(0, 255, 136, 255))

    # 5. Typewriter & Decrypt effect for Main Title
    # t_in_phrase goes from 0.0 to 1.0
    # Decrypt in 0.0 -> 0.35, hold 0.35 -> 0.85, glitch out 0.85 -> 1.0
    display_title = ""
    title_len = len(p_title)
    
    if t_in_phrase < 0.35:
        # Decrypting
        progress = t_in_phrase / 0.35
        revealed = int(progress * title_len)
        for idx in range(title_len):
            if idx < revealed:
                display_title += p_title[idx]
            elif idx == revealed:
                display_title += random.choice("0123456789_#@!<>{}?")
            else:
                display_title += random.choice("·:/*%")
    elif t_in_phrase <= 0.85:
        # Full display with subtle cursor or glitch
        display_title = p_title
        if (global_frame // 4) % 2 == 0:
            cursor = "█"
        else:
            cursor = " "
    else:
        # Glitch out
        progress = (t_in_phrase - 0.85) / 0.15
        scramble_prob = progress * 0.8
        for idx in range(title_len):
            if random.random() < scramble_prob:
                display_title += random.choice("!#$01_<>?")
            else:
                display_title += p_title[idx]

    # Measure Title Width
    tb = draw.textbbox((0, 0), display_title, font=font_title)
    tw = tb[2] - tb[0]
    tx = (bw - tw) // 2
    ty = (bh // 2) - (28 * SS)

    # Glitch chromatic aberration (horizontal split on glitch)
    is_glitch_frame = (t_in_phrase > 0.86) or (random.random() < 0.05 and t_in_phrase < 0.3)
    
    if is_glitch_frame:
        glitch_shift = random.randint(3 * SS, 8 * SS)
        # Red layer
        draw.text((tx - glitch_shift, ty), display_title, font=font_title, fill=(255, 40, 70, 200))
        # Cyan layer
        draw.text((tx + glitch_shift, ty), display_title, font=font_title, fill=(0, 255, 230, 200))
        # Draw slice line
        slice_y = ty + random.randint(0, 30 * SS)
        draw.line([(0, slice_y), (bw, slice_y)], fill=(0, 255, 180, 160), width=1*SS)

    # Core Title Text (Bright Crisp Terminal Green-White)
    draw.text((tx, ty), display_title, font=font_title, fill=(240, 255, 245, 255))

    # 6. Subtitle / Terminal Command line
    sub_bbox = draw.textbbox((0, 0), p_sub, font=font_sub)
    sw = sub_bbox[2] - sub_bbox[0]
    sx = (bw - sw) // 2
    sy = ty + (48 * SS)

    draw.text((sx, sy), p_sub, font=font_sub, fill=(0, 255, 170, 230))

    # 7. Target Pill / Badge above or below
    # Pill box for severity/status
    badge_bbox = draw.textbbox((0, 0), p_badge, font=font_badge)
    bw_w = badge_bbox[2] - badge_bbox[0]
    bx = (bw - bw_w) // 2
    by = ty - (22 * SS)

    # Pill background
    pad_h = 3 * SS
    pad_w = 8 * SS
    draw.rectangle([bx - pad_w, by - pad_h, bx + bw_w + pad_w, by + (12 * SS) + pad_h], 
                   fill=(10, 35, 25, 220), outline=(0, 255, 136, 180), width=1*SS)
    draw.text((bx, by), p_badge, font=font_badge, fill=(100, 255, 180, 255))

    # 8. CRT Scanline Overlay
    for y in range(0, bh, 3 * SS):
        draw.line([(0, y), (bw, y)], fill=(0, 0, 0, 70), width=1)

    # 9. Moving horizontal sweep beam (radar / laser line)
    sweep_y = int((global_frame * 5 * SS) % bh)
    draw.line([(0, sweep_y), (bw, sweep_y)], fill=(0, 255, 180, 90), width=2*SS)

    # Downsample back to W, H for sharp antialiased look
    frame_final = im.resize((W, H), Image.Resampling.LANCZOS)
    return frame_final

# Frame timing settings
FRAMES_PER_PHRASE = 36  # ~3.6s per phrase at 100ms
TOTAL_FRAMES = len(phrases) * FRAMES_PER_PHRASE

print(f"Generating {TOTAL_FRAMES} frames for Bug Bounty Hacker Banner...")

frames = []
for i in range(TOTAL_FRAMES):
    phrase_idx = i // FRAMES_PER_PHRASE
    t_in_phrase = (i % FRAMES_PER_PHRASE) / FRAMES_PER_PHRASE
    f = render_frame(phrase_idx, t_in_phrase, i, TOTAL_FRAMES)
    frames.append(f)
    if (i + 1) % 18 == 0:
        print(f"Rendered {i + 1}/{TOTAL_FRAMES} frames...")

# Motion check to ensure high dynamics
diffs = []
for i in range(1, len(frames)):
    d = np.abs(np.array(frames[i].convert("RGB"), dtype=float) - np.array(frames[i-1].convert("RGB"), dtype=float)).mean()
    diffs.append(d)

avg_diff = sum(diffs) / len(diffs)
min_diff = min(diffs)
print(f"Motion Verification: Avg Diff = {avg_diff:.2f}, Min Diff = {min_diff:.2f}")

output_path = "/data/data/com.termux/files/home/Mftrferdinand-profile/assets/zerolinear-banner.gif"

# Save optimized GIF
print("Quantizing and saving GIF...")
quantized_frames = [
    f.convert("RGB").quantize(colors=128, method=Image.FASTOCTREE, dither=Image.Dither.NONE)
    for f in frames
]

quantized_frames[0].save(
    output_path,
    save_all=True,
    append_images=quantized_frames[1:],
    duration=90,  # 90ms per frame = ~11 fps smooth
    loop=0,
    optimize=True
)

file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"Saved to {output_path} ({file_size_mb:.2f} MB)")
