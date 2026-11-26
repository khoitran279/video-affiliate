---
name: dung-video
description: Quy trình 2 giai đoạn cho Google Sheet affiliate. Giai đoạn A viết lời đọc cho dòng "Đã chọn" và chuyển sang "Chờ giọng". Giai đoạn B, khi chủ dự án đã bỏ file âm thanh vào thư mục ảnh, dựng video 9:16 khớp giọng bằng tools/make_video.py, tải lên Drive, cập nhật Sheet. Dùng trong lần chạy hằng ngày hoặc khi được yêu cầu "viết lời đọc", "dựng video".
---

# Dựng video

Đọc `CLAUDE.md` ở gốc repo trước (ID, cột A–S, gu hình ảnh, quy tắc pháp lý). Làm việc trong thư mục tạm của phiên, không ghi ảnh, âm thanh hay video vào repo.

Đọc `'<tab>'!A1:S` của 3 tab (dải mở). Tối đa 3 video mỗi kênh mỗi lần chạy.

## Cách lấy file trong thư mục Drive (dùng cho cả A và B)

- ID thư mục lấy từ link cột O (`.../folders/<ID>`).
- `search_files` với `parentId = '<ID>'`, `excludeContentSnippets: true`.
- `download_file_content(fileId)`: file được lưu sẵn trên máy, kết quả ghi đường dẫn (`[Image: source: <path>]` với ảnh, `Binary content ... saved to <path>` với âm thanh, video). Copy file đó vào thư mục tạm.

---

## Giai đoạn A: viết lời đọc (dòng `Đã chọn`)

1. Dòng thiếu cột O: ghi R = "Cần thư mục ảnh", bỏ qua.
2. Tải và xem ảnh (tối đa 6). Ảnh nền trắng thì sau này dùng `fit: "contain"`, ảnh lifestyle dùng `fit: "cover"`. Bỏ ảnh mờ, ảnh có chữ quảng cáo to, ảnh có mặt người lạ.
3. Chọn format và viết **lời đọc** (xem mục "Kịch bản" bên dưới).
4. Ghi vào Sheet:
   - S = lời đọc (chỉ chữ, không ký hiệu, không emoji, để dán thẳng vào CapCut).
   - M = `Chờ giọng`.
   - R = `Chờ giọng từ dd/mm. Format: <tên format>.`
5. Nếu trong thư mục **đã có sẵn** file âm thanh hoặc video, làm luôn giai đoạn B cho dòng đó.

## Giai đoạn B: dựng video (dòng `Chờ giọng`)

1. Tìm file âm thanh trong thư mục cột O: `mimeType contains 'audio/'` hoặc `mimeType contains 'video/'`. Nếu nhiều file, lấy file mới nhất.
2. **Chưa có file:**
   - Nếu R ghi "Chờ giọng từ dd/mm" và đã quá 2 ngày: dùng giọng dự phòng (mục "Giọng dự phòng"), ghi R thêm "Dùng giọng dự phòng HoaiMy".
   - Nếu chưa quá 2 ngày: bỏ qua, nhắc trong báo cáo.
3. **Có file:** tải về, chuẩn hóa thành `voice.mp3`:
   ```
   ffmpeg -y -i <file tải về> -vn -ac 1 -ar 44100 -b:a 160k voice.mp3
   ```
   (Lệnh này dùng được cho cả file video: chỉ lấy tiếng.) Bỏ khoảng lặng dài đầu và cuối nếu có:
   ```
   ffmpeg -y -i voice.mp3 -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" voice_trim.mp3 && mv voice_trim.mp3 voice.mp3
   ```
4. Tải ảnh, viết `video.json` theo mục "Kịch bản" bên dưới: các cảnh đi theo thứ tự ý của lời đọc, `"audio": "voice.mp3"`, `"script"` = cột S, `"hook"` = câu trong R. Thời lượng cảnh và phụ đề tự khớp giọng (phụ đề căn theo khoảng lặng). Nếu chủ dự án đọc lệch kịch bản nhiều, ghi R để chủ dự án sửa cột S rồi dựng lại.
5. Render và kiểm tra:
   ```
   python3 <repo>/tools/make_video.py <thư mục tạm>/video.json
   ```
   `ffprobe` phải có cả video và audio. Trích 3 khung hình (đầu, giữa, cuối), ghép lại và xem: chữ không tràn, sản phẩm rõ.
6. Tải lên Drive **file `<output>_drive.mp4`** (720p, dưới 3 MB, do công cụ tự xuất; connector giới hạn khoảng 3 MB). Nếu bản này vẫn trên 3 MB, chạy lại với `"drive_max_mb": 2.6`.
   `sha256sum <output>_drive.mp4`, rồi `create_file` với `parentId: "1tPGwiNV9KwqkO9Rg777NwdrELaLc2Z0C"`, `contentMimeType: "video/mp4"`, `disableConversionToGoogleType: true`, `base64Content: "sha256:<hash>:<đường dẫn tuyệt đối>"`, `title: "<Kênh> - <Tên ngắn> - <dd.mm>.mp4"`.
7. Ghi Sheet: P = link `viewUrl`, Q = caption, M = `Đã dựng`, R = "Đã dựng dd/mm, giọng: <file của chủ dự án | HoaiMy dự phòng>".

---

## Kịch bản

Hai format đã được duyệt (xem `CLAUDE.md`, mục "Phong cách kênh affiliate"):

| Format | Cấu trúc | Ví dụ mở đầu |
|---|---|---|
| **A – Nỗi đau** (mặc định) | Tình huống khó chịu cụ thể → sản phẩm giải quyết, nêu chi tiết thấy được → size/dịp dùng → CTA | "Trời lạnh mà cho con gái mặc áo phao thì tròn như cục bông, chụp ảnh chẳng thấy dáng đâu." |
| **C – Gấp theo mùa** (khi còn ≥ 5 ngày tới Noel, Tết, 14/02…) | Mốc thời gian + câu hỏi → một sản phẩm dùng được cho dịp → CTA | "Còn chưa đầy một tháng nữa là Noel, đồ cho con gái đã có chưa các mẹ?" |
| Sách: 1 ý tưởng | Câu hỏi đời thường → ý tưởng diễn đạt lại → vì sao nên đọc → CTA | (chưa duyệt, đưa phương án trước) |

Định dạng mới ngoài bảng trên: **không tự áp dụng**, ghi R = "Đề xuất format mới, chờ duyệt" kèm 2–3 phương án.

**Lời đọc: nói như người thật chia sẻ với người thật.**
- Câu đầu là một tình huống hoặc câu hỏi người xem gật đầu ngay. Không mở bằng tên sản phẩm.
- Dùng từ nói của người mua (giọng Bắc): "các mẹ", "nhé", "hẳn", "chẳng", "là có đồ rồi". Không dùng từ mô tả kiểu catalogue ("thiết kế tinh tế", "chất liệu cao cấp", "sang trọng").
- Mỗi lợi ích gắn với một chi tiết nhìn thấy trên ảnh (nơ, cổ bèo, chất dạ…).
- Có một lý do mua ngay có thật (mùa, dịp, thời tiết). Không bịa khan hiếm ("sắp hết hàng").
- Không nói "mình mua/dùng rồi" nếu chủ dự án chưa thực sự dùng. Dùng "Có set này các mẹ xem nhé".
- 35–65 từ (12–20 giây). Kết thúc bằng CTA tự nhiên: "Mẹ nào cần thì xem ở giỏ hàng nhé."
- Chỉ nói thông tin có trong mô tả sản phẩm hoặc thấy trên ảnh. Không giá (đến khi được duyệt).

**Tự kiểm trước khi ghi Sheet** (thiếu 1 ý thì viết lại):
1. Đọc to câu đầu: người xem có dừng lướt không?
2. Có câu nào nghe như quảng cáo hoặc AI viết không?
3. Có nỗi đau hoặc lý do mua ngay cụ thể không?
4. Có câu nào sai sự thật hoặc phóng đại không?

**Hook trên hình:** ≤ 8 từ, rút từ câu đầu, ghi vào R dạng `Hook: "..."`.

**video.json:** `style: "sale"`, `script` = cột S, `hook` = câu hook, 6–9 cảnh 1,8–2,2 giây, xen cảnh toàn và cảnh cận `focus: [cx, cy, 1.1–1.5]`. Cảnh đầu là ảnh đẹp nhất. `end_card` "Xem ở giỏ hàng". Không ghi `text` cho cảnh (phụ đề tự chạy).

**Caption:** 1–2 câu nối tiếp hook + 3–5 hashtag liên quan. Không hứa hẹn, không giá.

Tuân thủ toàn bộ quy tắc trong `CLAUDE.md`.

## Giọng dự phòng

Chỉ dùng theo bước B.2, và chỉ khi Creative Claw còn từ 10 credit trở lên:
```
generate_speech(model="speech/azure-neural", voice_id="vi-VN-HoaiMyNeural", text=<cột S>)
check_job(job_id) → url;  curl -sSf -o voice.mp3 "<url>"
```
Không tạo lại giọng cho cùng một lời đọc. Nếu lỗi, ghi R và bỏ qua dòng đó.

(`tools/tts_google.py` dành cho Google Cloud TTS khi chủ dự án có khóa API; hiện chưa cấu hình.)

## Báo cáo

- Lời đọc mới đã viết: tên sản phẩm, kênh. Nhắc chủ dự án: mở cột S, tạo giọng (CapCut hoặc tự thu), bỏ file vào thư mục ảnh của sản phẩm.
- Video đã dựng: tên, link Drive, nguồn giọng.
- Dòng đang chờ giọng và số ngày đã chờ.
- Nhắc khi đăng: thêm nhạc thịnh hành (âm lượng nhỏ, khoảng 10–20%), bật nhãn nội dung AI nếu dùng giọng hoặc hình AI, gắn giỏ hàng, đổi M sang `Đã đăng`.
