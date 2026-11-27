"""Tạo giọng mẫu bằng VieNeu-TTS v3 Turbo (chạy CPU)."""
import sys, time
from vieneu import Vieneu

out_dir = sys.argv[1]
text = ("Nhà chật mà đồ đạc cứ bày bừa ra, nhìn là thấy mệt. "
        "Mình đã thử cái kệ này, gom gọn hết đồ trong góc bếp, nhìn thoáng hẳn. "
        "Ai đang bí chỗ để đồ giống mình thì bấm vào giỏ hàng xem thử nhé!")
voices = ["Mai Anh", "Hải Đăng", "Thùy Dung", "Adam"]

tts = Vieneu()
print("voices:", [v[0] for v in tts.list_preset_voices()])
for v in voices:
    t = time.time()
    audio = tts.infer(text, voice=v)
    name = v.replace(" ", "_")
    tts.save(audio, f"{out_dir}/{name}.wav")
    print(f"{v}: {len(audio)/48000:.1f}s audio in {time.time()-t:.1f}s")
