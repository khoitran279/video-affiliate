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
4. Tải ảnh, viết `video.json` theo kịch bản ở cột S: các cảnh đi theo thứ tự ý của lời đọc, chữ trên hình là **từ khóa** của từng đoạn (không cần trùng từng chữ, vì giọng tự thu có thể lệch kịch bản). Có `"audio": "voice.mp3"`, `"grade": "soft"`, `end_card` "Link sản phẩm ở giỏ hàng". Thời lượng cảnh tự kéo giãn theo giọng.
5. Render và kiểm tra:
   ```
   python3 <repo>/tools/make_video.py <thư mục tạm>/video.json
   ```
   `ffprobe` phải có cả video và audio. Trích 3 khung hình (đầu, giữa, cuối), ghép lại và xem: chữ không tràn, sản phẩm rõ.
6. Tải lên Drive: `sha256sum out.mp4`, rồi `create_file` với `parentId: "1tPGwiNV9KwqkO9Rg777NwdrELaLc2Z0C"`, `contentMimeType: "video/mp4"`, `disableConversionToGoogleType: true`, `base64Content: "sha256:<hash>:<đường dẫn tuyệt đối>"`, `title: "<Kênh> - <Tên ngắn> - <dd.mm>.mp4"`.
7. Ghi Sheet: P = link `viewUrl`, Q = caption, M = `Đã dựng`, R = "Đã dựng dd/mm, giọng: <file của chủ dự án | HoaiMy dự phòng>".

---

## Kịch bản

| Format | Cấu trúc |
|---|---|
| Hook ảnh đẹp | Cảnh lifestyle đẹp nhất + 1 dòng hook → chi tiết sản phẩm → công dụng/cách dùng thật → cảnh đẹp + CTA |
| Câu hỏi | "Phòng nhỏ có nên…?" → sản phẩm → lý do → CTA |
| Quà tặng (mùa Tết/Valentine) | "Quà Tết cho bố mẹ" → sản phẩm → điểm đáng giá → CTA |
| Sách: 1 ý tưởng | Câu hỏi → ý tưởng diễn đạt lại → bìa sách → CTA |

- **Lời đọc:** 35–60 từ (khoảng 12–20 giây), câu ngắn, giọng nhẹ nhàng, không phóng đại. Chỉ nói thông tin có trong mô tả sản phẩm (mở link cột C nếu cần; nếu không mở được, chỉ nói điều thấy trên ảnh). Kết thúc: "Link sản phẩm ở giỏ hàng nhé."
- **Chữ trên hình:** mỗi cảnh ≤ 1 dòng, ≤ 6 từ. Cảnh đầu `text_style: "title"`. 5–8 cảnh.
- **Caption:** 1–2 câu hook + 3–5 hashtag liên quan. Không hứa hẹn, không giá.
- Tuân thủ toàn bộ quy tắc trong `CLAUDE.md`.

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
