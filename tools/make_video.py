#!/usr/bin/env python3
"""Dựng video sản phẩm 9:16 từ ảnh thật — không dùng credit AI.

Cách dùng:
    python3 tools/make_video.py <thư mục>/video.json

Cấu hình (video.json), đường dẫn ảnh tính từ thư mục chứa file json:
{
  "output": "out.mp4",
  "fps": 30,
  "style": "sale",                # sale (kênh affiliate, mặc định) | minimal (chữ mảnh, tông trầm)
  "grade": "true",                # true: giữ màu thật, tăng tương phản nhẹ | soft | none
  "audio": "voice.mp3",           # tùy chọn: giọng đọc
  "script": "Lời đọc đầy đủ...",  # dùng để chạy phụ đề theo giọng (không có audio thì ước lượng)
  "hook": {"text": "Câu hook to ở giây đầu", "duration": 2.2},
  "scenes": [
    {"image": "1.jpg", "duration": 1.0, "motion": "zoom_in", "fit": "auto"},
    {"image": "1.jpg", "focus": [0.5, 0.35, 1.3], "duration": 0.8}   # cận chi tiết
  ],
  "end_card": {"image": "1.jpg", "text": "Xem ở giỏ hàng", "duration": 1.8}
}

motion: zoom_in | zoom_out | pan_left | pan_right | pan_up | pan_down | still
fit:    auto | cover | contain | blur
        (auto: nền trắng -> contain; ảnh vuông/ngang -> blur; ảnh dọc -> cover)
focus:  [cx, cy, zoom] — cắt cận một vùng của ảnh (tọa độ 0..1), zoom 1.0–1.6.
        Ảnh shop thường chỉ 800px: zoom > 1.6 sẽ vỡ.
Phụ đề: có "script" thì tự chia câu, căn thời gian theo độ dài và khoảng lặng của giọng.
        Khi có phụ đề, trường "text" của từng cảnh bị bỏ qua.
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
    "bold": os.path.join(HERE, "fonts", "BeVietnamPro-ExtraBold.ttf"),
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
    if mode == "true":  # giữ màu thật của hàng, chỉ làm rõ và nét hơn
        img = ImageEnhance.Contrast(img).enhance(1.05)
        return img.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    # Nhẹ tay để màu sản phẩm vẫn đúng hàng thật
    img = ImageEnhance.Color(img).enhance(0.85)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    lut = [max(0, min(255, int((i - 8) * 255 / 247))) for i in range(256)] * 3
    return img.point(lut)


def build_base(path, fit, backdrop, grade_mode, focus=None, style="sale"):
    """Trả về ảnh nền kích thước (W*OVERSCAN, H*OVERSCAN)."""
    bw, bh = int(W * OVERSCAN), int(H * OVERSCAN)
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if focus:  # cận chi tiết: cắt khung 9:16 quanh (cx, cy)
        cx, cy, z = focus
        maxw = min(img.width, img.height * 9 / 16)
        cw = maxw / max(1.0, z)
        ch = cw * 16 / 9
        x0 = min(max(0, cx * img.width - cw / 2), img.width - cw)
        y0 = min(max(0, cy * img.height - ch / 2), img.height - ch)
        img = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
        fit = "cover"
    if fit == "auto":
        if is_white_background(img):
            fit = "contain"
        elif img.height / img.width < 1.4:
            # sale: lấp kín khung (cắt hai bên) cho sống động; minimal: giữ trọn ảnh trên nền mờ
            fit = "cover" if style == "sale" else "blur"
        else:
            fit = "cover"
    if fit == "cover":
        base = ImageOps.fit(img, (bw, bh), Image.LANCZOS)
    elif fit == "blur":
        # nền: chính ảnh đó phủ kín khung, làm mờ và tối nhẹ
        base = ImageOps.fit(img, (bw, bh), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
        base = ImageEnhance.Brightness(base).enhance(0.72)
        # ảnh gốc giữ trọn, rộng bằng khung hiển thị, đặt hơi cao hơn tâm (chừa chỗ cho chữ)
        scale = min(W / img.width, (H * 0.62) / img.height)
        full = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        x = (bw - full.width) // 2
        y = int(bh * 0.45) - full.height // 2
        base.paste(full, (x, y))
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
    out = grade(base, grade_mode)
    out.info["fit"] = fit
    return out


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


# ---------- Phong cách bán hàng: hook to, phụ đề, thẻ cuối ----------

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def bold_block(text, size, cy, maxw, boxed=False, stroke=7):
    """Chữ đậm, căn giữa, tối đa 3 dòng. boxed: chữ tối trên khối trắng bo góc (kiểu chữ TikTok)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    font = ImageFont.truetype(FONTS["bold"], size)
    lines = wrap(d, text, font, maxw)
    while len(lines) > 3 and font.size > 40:
        font = ImageFont.truetype(FONTS["bold"], font.size - 4)
        lines = wrap(d, text, font, maxw)
    lh = int(font.size * 1.28)
    top = int(cy - lh * len(lines) / 2)
    for k, ln in enumerate(lines):
        tw = d.textlength(ln, font=font)
        x, y = (W - tw) / 2, top + k * lh
        if boxed:
            pad = int(font.size * 0.32)
            d.rounded_rectangle((x - pad, y - pad * 0.55, x + tw + pad, y + font.size + pad * 0.95),
                                radius=int(font.size * 0.28), fill=(255, 255, 255, 245))
    for k, ln in enumerate(lines):
        tw = d.textlength(ln, font=font)
        x, y = (W - tw) / 2, top + k * lh
        if boxed:
            d.text((x, y), ln, font=font, fill=(20, 20, 20, 255))
        else:
            d.text((x, y), ln, font=font, fill=(255, 255, 255, 255),
                   stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return layer


def end_card_layer(text):
    layer = bold_block(text, 76, H * 0.60, W * 0.80, boxed=True)
    d = ImageDraw.Draw(layer)
    cx, y = W / 2, H * 0.60 + 90  # mũi tên chỉ xuống giỏ hàng
    d.polygon([(cx - 38, y), (cx + 38, y), (cx, y + 44)], fill=(255, 255, 255, 245))
    return layer


def split_script(script, max_words=7):
    """Chia lời đọc thành các cụm phụ đề ngắn. Trả về [(cụm, trọng số thời gian, cuối câu?)]."""
    import re
    out = []
    for sent in re.split(r"(?<=[.!?…])\s+", script.strip()):
        parts = [p.strip() for p in re.split(r"(?<=[,:;])\s+", sent) if p.strip()]
        for pi, part in enumerate(parts):
            words = part.split()
            n = max(1, math.ceil(len(words) / max_words))
            size = math.ceil(len(words) / n)
            chunks = [" ".join(words[a:a + size]) for a in range(0, len(words), size)]
            for ci, ch in enumerate(chunks):
                last_in_part = ci == len(chunks) - 1
                end_sent = last_in_part and pi == len(parts) - 1
                pause = (1.2 if end_sent else 0.5) if last_in_part else 0
                out.append((ch.rstrip(",;:."), len(ch.split()) + pause, end_sent))
    return out


def silences(audio):
    """Các khoảng lặng (giữa) trong file giọng, để căn ranh giới câu."""
    import re
    r = subprocess.run(["ffmpeg", "-i", audio, "-af", "silencedetect=noise=-35dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [(a + b) / 2 for a, b in zip(st, en)]


def subtitle_track(script, total, audio=None):
    chunks = split_script(script)
    wsum = sum(w for _, w, _ in chunks)
    t, track = 0.0, []
    for txt, w, end in chunks:
        track.append([txt, t, t + total * w / wsum, end])
        t += total * w / wsum
    if audio:  # kéo ranh giới cuối câu về khoảng lặng gần nhất trong giọng thật
        sil = silences(audio)
        for k, item in enumerate(track[:-1]):
            if item[3] and sil:
                near = min(sil, key=lambda s_: abs(s_ - item[2]))
                if abs(near - item[2]) < 0.8:
                    item[2] = near
                    track[k + 1][1] = near
        # dàn đều lại các cụm trong cùng câu sau khi dời ranh giới
        start = 0
        for k, item in enumerate(track):
            if item[3] or k == len(track) - 1:
                seg = track[start:k + 1]
                a, b = seg[0][1], seg[-1][2]
                ws = [len(x[0].split()) for x in seg]
                acc = a
                for x, ww in zip(seg, ws):
                    x[1], x[2] = acc, acc + (b - a) * ww / sum(ws)
                    acc = x[2]
                start = k + 1
    return [(a, b, txt) for txt, a, b, _ in track]


def audio_duration(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode().strip())


def render(cfg_path):
    root = os.path.dirname(os.path.abspath(cfg_path))
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    fps = cfg.get("fps", 30)
    style = cfg.get("style", "sale")
    backdrop = cfg.get("backdrop", "#F2EFEA")
    grade_mode = cfg.get("grade", "true" if style == "sale" else "soft")
    out = os.path.join(root, cfg.get("output", "out.mp4"))
    scenes = list(cfg["scenes"])
    ec = cfg.get("end_card")
    if ec:
        scenes.append({"image": ec.get("image", scenes[0]["image"]), "text": ec.get("text", ""),
                       "duration": ec.get("duration", 1.8), "motion": "zoom_out",
                       "fit": ec.get("fit", "auto"), "focus": ec.get("focus"),
                       "end": True})

    audio = cfg.get("audio")
    audio_path = os.path.join(root, audio) if audio else None
    script = cfg.get("script", "").strip()
    subs_on = bool(script) and cfg.get("subtitles", True)

    # Tổng thời lượng: theo giọng thật, hoặc ước lượng từ lời đọc (khoảng 4,3 tiếng/giây)
    if audio_path:
        speech = audio_duration(audio_path)
    elif script:
        speech = len(script.split()) / cfg.get("syllables_per_sec", 4.3) + 0.4
    else:
        speech = None
    if speech and cfg.get("fit_to_audio", True):
        planned = sum(sc.get("duration", 1.0) for sc in scenes)
        k = (speech + 0.5) / planned
        for sc in scenes:
            sc["duration"] = max(0.6, sc.get("duration", 1.0) * k)

    subs = subtitle_track(script, speech, audio_path) if subs_on else []
    sub_cache = {}
    hook = cfg.get("hook")
    hook_layer = bold_block(hook["text"], 84, H * 0.25, W * 0.82, boxed=True) if hook else None
    hook_dur = hook.get("duration", 2.2) if hook else 0

    silent = out + ".silent.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent],
        stdin=subprocess.PIPE)

    punch = 4  # số khung "zoom punch" cuối mỗi cảnh = chuyển cảnh bằng chuyển động
    gframe = 0
    for i, sc in enumerate(scenes):
        base = build_base(os.path.join(root, sc["image"]), sc.get("fit", "auto"), backdrop, grade_mode,
                          sc.get("focus"), style)
        motion = sc.get("motion", "zoom_in" if i % 2 == 0 else "zoom_out")
        if base.info.get("fit") == "blur" and motion.startswith("pan"):
            motion = "zoom_in" if motion in ("pan_up", "pan_left") else "zoom_out"
        if sc.get("end"):
            txt = end_card_layer(sc["text"]) if style == "sale" else text_layer(sc["text"], "caption", None)
        elif subs_on:
            txt = None
        else:
            txt = text_layer(sc.get("text", ""), sc.get("text_style", "title" if i == 0 else "caption"),
                             under=frame_at(base, motion, 0.5))
        n = max(1, round(sc.get("duration", 1.0) * fps))
        last = i == len(scenes) - 1
        for f in range(n):
            t = f / max(1, n - 1)
            now = gframe / fps
            fr = frame_at(base, motion, t)
            if not last and f >= n - punch:
                kk = (f - (n - punch) + 1) / punch
                z = 1 + 0.10 * kk * kk
                cw, ch = W / z, H / z
                fr = fr.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
            fr = fr.convert("RGBA")
            if txt is not None:
                a = min(1.0, f / 5)
                tl = txt
                if a < 1:
                    tl = txt.copy()
                    tl.putalpha(tl.getchannel("A").point(lambda v: int(v * a)))
                fr = Image.alpha_composite(fr, tl)
            if subs_on and not sc.get("end"):
                cur = next((s_ for s_ in subs if s_[0] <= now < s_[1]), None)
                if cur:
                    if cur[2] not in sub_cache:
                        sub_cache[cur[2]] = bold_block(cur[2], 66, H * 0.66, W * 0.78)
                    fr = Image.alpha_composite(fr, sub_cache[cur[2]])
            if hook_layer is not None and now < hook_dur:
                # bật ra: phóng từ 85% lên 100% trong 5 khung đầu
                p_ = min(1.0, gframe / 5)
                if p_ < 1:
                    sz = 0.85 + 0.15 * p_
                    hl = hook_layer.resize((int(W * sz), int(H * sz)), Image.BICUBIC)
                    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    tmp.paste(hl, ((W - hl.width) // 2, int(H * 0.25 - H * 0.25 * sz)))
                    fr = Image.alpha_composite(fr, tmp)
                else:
                    fr = Image.alpha_composite(fr, hook_layer)
            ff.stdin.write(fr.convert("RGB").tobytes())
            gframe += 1
    ff.stdin.close()
    ff.wait()

    if audio_path:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio_path,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
        os.remove(silent)
    else:
        os.replace(silent, out)
    print(f"Đã xuất: {out} ({gframe / fps:.1f}s, {len(scenes)} cảnh, {len(subs)} dòng phụ đề)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    render(sys.argv[1])
