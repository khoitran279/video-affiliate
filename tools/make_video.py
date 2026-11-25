#!/usr/bin/env python3
"""Dựng video sản phẩm 9:16 từ ảnh thật — không dùng credit AI.

Cách dùng:
    python3 tools/make_video.py projects/<ten-video>/video.json

Cấu hình (video.json), đường dẫn ảnh tính từ thư mục chứa file json:
{
  "output": "out.mp4",
  "fps": 30,
  "grade": "soft",                # soft | none   (soft: giảm bão hòa nhẹ, đẩy đen nhẹ)
  "backdrop": "#E9E4DC",          # nền cho ảnh sản phẩm nền trắng
  "audio": "voice.mp3",           # tùy chọn: giọng đọc hoặc nhạc
  "scenes": [
    {"image": "1.jpg", "text": "Tết tối giản", "duration": 1.5,
     "motion": "zoom_in", "fit": "auto", "text_style": "title"}
  ],
  "end_card": {"text": "Link sản phẩm ở giỏ hàng", "duration": 2.0}
}

motion: zoom_in | zoom_out | pan_left | pan_right | pan_up | pan_down | still
fit:    auto | cover | contain   (auto: ảnh nền trắng -> contain trên backdrop)
text_style: title (serif, lớn vừa) | caption (sans mảnh, nhỏ) | price (sans, góc dưới)
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {
    "title": os.path.join(HERE, "fonts", "PlayfairDisplay-Regular.ttf"),
    "caption": os.path.join(HERE, "fonts", "BeVietnamPro-Light.ttf"),
    "price": os.path.join(HERE, "fonts", "BeVietnamPro-Regular.ttf"),
}
SIZES = {"title": 66, "caption": 48, "price": 50}
OVERSCAN = 1.18  # ảnh lớn hơn khung để còn chỗ zoom/pan


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def is_white_background(img):
    """Ảnh sản phẩm kiểu sàn TMĐT: viền gần như trắng."""
    g = img.convert("L").resize((200, 200))
    px = g.load()
    border = [px[x, y] for x in range(200) for y in (0, 1, 198, 199)]
    border += [px[x, y] for y in range(200) for x in (0, 1, 198, 199)]
    return sum(1 for v in border if v > 235) / len(border) > 0.85


def background_mask(prod):
    """Chỉ xóa vùng nền trắng NỐI VỚI MÉP ảnh, nên sản phẩm màu trắng không bị ăn mất."""
    sentinel = (255, 0, 255)
    work = prod.copy()
    pw, ph = work.size
    seeds = [(0, 0), (pw - 1, 0), (0, ph - 1), (pw - 1, ph - 1)]
    seeds += [(int(pw * f), 0) for f in (0.25, 0.5, 0.75)] + [(int(pw * f), ph - 1) for f in (0.25, 0.5, 0.75)]
    seeds += [(0, int(ph * f)) for f in (0.25, 0.5, 0.75)] + [(pw - 1, int(ph * f)) for f in (0.25, 0.5, 0.75)]
    for s in seeds:
        if min(work.getpixel(s)) > 230:
            ImageDraw.floodfill(work, s, sentinel, thresh=22)
    px = work.load()
    mask = Image.new("L", work.size, 255)
    mp = mask.load()
    for yy in range(ph):
        for xx in range(pw):
            if px[xx, yy] == sentinel:
                mp[xx, yy] = 0
    return mask.filter(ImageFilter.GaussianBlur(1.2))


def grade(img, mode):
    if mode == "none":
        return img
    # Nhẹ tay để màu sản phẩm vẫn đúng hàng thật
    img = ImageEnhance.Color(img).enhance(0.85)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    lut = [max(0, min(255, int((i - 8) * 255 / 247))) for i in range(256)] * 3
    return img.point(lut)


def build_base(path, fit, backdrop, grade_mode):
    """Trả về ảnh nền kích thước (W*OVERSCAN, H*OVERSCAN)."""
    bw, bh = int(W * OVERSCAN), int(H * OVERSCAN)
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if fit == "auto":
        fit = "contain" if is_white_background(img) else "cover"
    if fit == "cover":
        base = ImageOps.fit(img, (bw, bh), Image.LANCZOS)
    else:
        base = Image.new("RGB", (bw, bh), hex_rgb(backdrop))
        # sản phẩm chiếm ~72% chiều ngang khung hiển thị, đặt hơi cao hơn tâm
        target_w = int(W * 0.78)
        scale = min(target_w / img.width, (H * 0.55) / img.height)
        prod = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        mask = background_mask(prod)
        x = (bw - prod.width) // 2
        y = int(bh * 0.44) - prod.height // 2
        # bóng đổ theo đúng hình sản phẩm, lệch xuống dưới, rất mềm
        pad = 60
        sh = Image.new("L", (prod.width + pad * 2, prod.height + pad * 2), 0)
        sh.paste(mask.point(lambda v: v * 0.35), (pad, pad + 24))
        sh = sh.filter(ImageFilter.GaussianBlur(28))
        base.paste(Image.new("RGB", sh.size, (70, 62, 55)), (x - pad, y - pad), sh)
        base.paste(prod, (x, y), mask)
    return grade(base, grade_mode)


def text_layer(text, style, under=None):
    """under: khung hình ở giữa cảnh, để chọn chữ sáng hay tối theo nền."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not text:
        return layer
    bright = False
    if under is not None:
        region = under.crop((0, int(H * 0.72), W, int(H * 0.86))).convert("L").resize((64, 16))
        bright = ImageStat.Stat(region).mean[0] > 165
    font = ImageFont.truetype(FONTS[style], SIZES[style])
    d = ImageDraw.Draw(layer)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # tự thu nhỏ nếu dài hơn 86% khung (luôn 1 dòng)
    while tw > W * 0.86 and font.size > 28:
        font = ImageFont.truetype(FONTS[style], font.size - 2)
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) // 2 - bbox[0]
    y = int(H * (0.80 if style != "title" else 0.76)) - bbox[1]
    if bright:  # nền sáng: chữ tối, không cần dải nền
        ImageDraw.Draw(layer).text((x, y), text, font=font, fill=(38, 35, 32, 255))
        return layer
    # nền tối/rối: chữ sáng trên dải tối mờ
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    top = y + bbox[1] - 60
    for i in range(240):
        a = int(110 * math.sin(math.pi * i / 240))
        bd.line([(0, top + i - 60), (W, top + i - 60)], fill=(10, 10, 10, a))
    layer = Image.alpha_composite(layer, band.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(layer)
    d.text((x, y), text, font=font, fill=(245, 242, 236, 255))
    return layer


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def frame_at(base, motion, t):
    """t: 0..1 trong cảnh. Cắt cửa sổ W x H từ ảnh overscan."""
    bw, bh = base.size
    e = ease(t)
    if motion in ("zoom_in", "zoom_out"):
        z = 1.0 + 0.12 * (e if motion == "zoom_in" else 1 - e)
        cw, ch = bw / z, bh / z
        cx, cy = bw / 2, bh / 2
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    else:
        mx, my = bw - W, bh - H
        dx = dy = 0.5
        if motion == "pan_left":
            dx = 1 - e
        elif motion == "pan_right":
            dx = e
        elif motion == "pan_up":
            dy = 1 - e
        elif motion == "pan_down":
            dy = e
        x0, y0 = mx * dx, my * dy
        box = (x0, y0, x0 + W, y0 + H)
    return base.resize((W, H), Image.BICUBIC, box=box)


def render(cfg_path):
    root = os.path.dirname(os.path.abspath(cfg_path))
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    fps = cfg.get("fps", 30)
    backdrop = cfg.get("backdrop", "#E9E4DC")
    grade_mode = cfg.get("grade", "soft")
    out = os.path.join(root, cfg.get("output", "out.mp4"))
    scenes = list(cfg["scenes"])
    if cfg.get("end_card"):
        ec = cfg["end_card"]
        scenes.append({"image": ec.get("image", scenes[0]["image"]), "text": ec["text"],
                       "duration": ec.get("duration", 2.0), "motion": "zoom_out",
                       "fit": ec.get("fit", scenes[0].get("fit", "auto")),
                       "text_style": "caption"})

    # Kéo giãn thời lượng các cảnh cho khớp giọng đọc (mặc định bật khi có audio)
    audio = cfg.get("audio")
    if audio and cfg.get("fit_to_audio", True):
        dur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
             os.path.join(root, audio)]).decode().strip())
        planned = sum(sc.get("duration", 1.5) for sc in scenes)
        k = (dur + 0.6) / planned
        for sc in scenes:
            sc["duration"] = max(0.9, sc.get("duration", 1.5) * k)

    silent = out + ".silent.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent],
        stdin=subprocess.PIPE)

    punch = 4  # số khung "zoom punch" ở cuối mỗi cảnh = chuyển cảnh bằng chuyển động
    total = 0.0
    for i, sc in enumerate(scenes):
        base = build_base(os.path.join(root, sc["image"]), sc.get("fit", "auto"), backdrop, grade_mode)
        txt = text_layer(sc.get("text", ""), sc.get("text_style", "title" if i == 0 else "caption"),
                         under=frame_at(base, sc.get("motion", "zoom_in"), 0.5))
        n = max(1, round(sc.get("duration", 1.5) * fps))
        last = i == len(scenes) - 1
        for f in range(n):
            t = f / max(1, n - 1)
            fr = frame_at(base, sc.get("motion", "zoom_in"), t)
            if not last and f >= n - punch:  # đẩy zoom nhanh sang cảnh sau
                k = (f - (n - punch) + 1) / punch
                z = 1 + 0.10 * k * k
                cw, ch = W / z, H / z
                fr = fr.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
            fr = fr.convert("RGBA")
            # chữ hiện dần trong 6 khung đầu
            a = min(1.0, f / 6)
            if a < 1:
                tl = txt.copy()
                tl.putalpha(tl.getchannel("A").point(lambda v: int(v * a)))
                fr = Image.alpha_composite(fr, tl)
            else:
                fr = Image.alpha_composite(fr, txt)
            ff.stdin.write(fr.convert("RGB").tobytes())
        total += n / fps
    ff.stdin.close()
    ff.wait()

    if audio:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(root, audio),
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
        os.remove(silent)
    else:
        os.replace(silent, out)
    print(f"Đã xuất: {out} ({total:.1f}s)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    render(sys.argv[1])
