#!/usr/bin/env python3
"""Tạo giọng đọc bằng Google Cloud Text-to-Speech.

Khóa API KHÔNG nằm trong code hay trong repo: nó được lưu ở cài đặt môi trường
(network secret) và proxy tự gắn vào header X-Goog-Api-Key cho host
texttospeech.googleapis.com. Script chỉ gửi một giá trị giả để có header.

Cách dùng:
    python3 tools/tts_google.py voices                      # liệt kê giọng vi-VN
    python3 tools/tts_google.py say <giọng> <file.mp3> "Lời đọc..." [--rate 1.0]
    python3 tools/tts_google.py say <giọng> <file.mp3> --text-file loi_doc.txt

Ví dụ giọng: vi-VN-Neural2-A, vi-VN-Wavenet-A, vi-VN-Chirp3-HD-<Tên>
"""
import base64
import json
import os
import sys
import urllib.request

API = "https://texttospeech.googleapis.com/v1"
KEY = os.environ.get("GOOGLE_TTS_KEY", "dummy-key-replaced-by-proxy")


def call(path, body=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"X-Goog-Api-Key": KEY, "Content-Type": "application/json; charset=utf-8"},
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Lỗi Google TTS {e.code}: {e.read().decode(errors='replace')[:500]}")


def voices():
    data = call("/voices?languageCode=vi-VN")
    for v in sorted(data.get("voices", []), key=lambda v: v["name"]):
        print(f'{v["name"]:32} {v["ssmlGender"]:7} {v.get("naturalSampleRateHertz", "")}')


def say(voice, out, text, rate=1.0):
    body = {
        "input": {"text": text},
        "voice": {"languageCode": "vi-VN", "name": voice},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": rate, "sampleRateHertz": 44100},
    }
    if "Chirp" in voice:  # giọng Chirp HD không nhận speakingRate ở mọi phiên bản
        body["audioConfig"].pop("speakingRate")
    data = call("/text:synthesize", body)
    with open(out, "wb") as f:
        f.write(base64.b64decode(data["audioContent"]))
    print(f"Đã lưu {out} ({len(text)} ký tự)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "voices":
        voices()
    elif a[0] == "say" and len(a) >= 4:
        voice, out = a[1], a[2]
        rate = float(a[a.index("--rate") + 1]) if "--rate" in a else 1.0
        if "--text-file" in a:
            text = open(a[a.index("--text-file") + 1], encoding="utf-8").read().strip()
        else:
            text = a[3]
        say(voice, out, text, rate)
    else:
        sys.exit(__doc__)
