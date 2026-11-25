---
name: dung-video
description: Dựng video TikTok 9:16 cho các sản phẩm ở trạng thái "Đã chọn" trong Google Sheet affiliate: tải ảnh từ Drive, viết kịch bản, tạo giọng đọc, render bằng tools/make_video.py, tải video lên Drive, cập nhật Sheet. Dùng trong lần chạy hằng ngày hoặc khi được yêu cầu "dựng video".
---

# Dựng video

Đọc `CLAUDE.md` ở gốc repo trước (ID, cột, gu hình ảnh, quy tắc pháp lý). Làm việc trong thư mục tạm của phiên, không ghi ảnh hay video vào repo.

## 1. Chọn việc

Đọc `'<tab>'!A1:R` của 3 tab. Lấy các dòng M = `Đã chọn`, cột O có link thư mục. Tối đa 3 dòng mỗi kênh, ưu tiên điểm L cao. Dòng thiếu cột O: ghi R = "Cần thư mục ảnh", bỏ qua.

## 2. Lấy ảnh

- Lấy ID thư mục từ link cột O (`.../folders/<ID>`).
- `search_files` với `parentId = '<ID>' and mimeType contains 'image/'`, `excludeContentSnippets: true`.
- `download_file_content` từng ảnh (tối đa 6 ảnh). Kết quả trả về đường dẫn file đã lưu trên máy (`[Image: source: <path>]`). Copy file đó vào thư mục dự án tạm, đặt tên `1.jpg`, `2.jpg`…
- Xem ảnh: ảnh nào nền trắng (dùng `fit: "contain"`), ảnh nào lifestyle (`fit: "cover"`). Bỏ ảnh mờ, ảnh có chữ quảng cáo to, ảnh có mặt người lạ.

## 3. Viết kịch bản

Mỗi video 5–8 cảnh, tổng khoảng 12–20 giây. Chọn 1 format:

| Format | Cấu trúc |
|---|---|
| Hook ảnh đẹp | Cảnh lifestyle đẹp nhất + 1 dòng hook → chi tiết sản phẩm → công dụng/cách dùng thật → cảnh đẹp + CTA |
| Câu hỏi | "Phòng nhỏ có nên…?" → sản phẩm → lý do → CTA |
| Quà tặng (mùa Tết/Valentine) | "Quà Tết cho bố mẹ" → sản phẩm → điểm đáng giá → CTA |
| Sách: 1 ý tưởng | Câu hỏi → ý tưởng diễn đạt lại → bìa sách → CTA |

- **Chữ trên hình:** mỗi cảnh ≤ 1 dòng, ≤ 6 từ. Cảnh đầu `text_style: "title"`.
- **Lời đọc:** 35–60 từ, câu ngắn, giọng nhẹ nhàng, không phóng đại. Chỉ nói thông tin có trong mô tả sản phẩm (mở link cột C nếu cần đọc mô tả; nếu không mở được, chỉ nói điều thấy trên ảnh). Kết thúc bằng "Link sản phẩm ở giỏ hàng nhé."
- Tuân thủ toàn bộ quy tắc trong `CLAUDE.md`.

## 4. Giọng đọc

```
generate_speech(model="speech/azure-neural", voice_id="vi-VN-HoaiMyNeural", text=<lời đọc>)
check_job(job_id) → url (https://cdn.creativeclaw.co/...)
curl -sSf -o voice.mp3 "<url>"
```

Không tạo lại giọng cho cùng một lời đọc. Nếu lỗi, ghi R và bỏ qua dòng đó.

## 5. Render

Viết `video.json` (xem docstring `tools/make_video.py`), có `"audio": "voice.mp3"`, `"grade": "soft"`, `end_card` với text "Link sản phẩm ở giỏ hàng". Thời lượng cảnh tự kéo giãn theo giọng đọc.

```
python3 <repo>/tools/make_video.py <thư mục tạm>/video.json
```

Kiểm tra: `ffprobe` có cả video và audio; trích 3 khung hình (đầu, giữa, cuối), ghép lại và xem để chắc chữ không tràn, sản phẩm rõ.

## 6. Tải lên Drive và cập nhật Sheet

- `sha256sum out.mp4`, rồi `create_file` với `parentId: "1tPGwiNV9KwqkO9Rg777NwdrELaLc2Z0C"`, `contentMimeType: "video/mp4"`, `disableConversionToGoogleType: true`, `base64Content: "sha256:<hash>:<đường dẫn tuyệt đối>"`, `title: "<Kênh> - <Tên ngắn> - <dd.mm>.mp4"`.
- Ghi vào dòng sản phẩm: P = link `viewUrl`, Q = caption, M = `Đã dựng`, R = tóm tắt ngắn (format đã dùng).

**Caption:** 1–2 câu hook + 3–5 hashtag liên quan (`#decortet #nhadep #canho` …). Không hứa hẹn, không giá.

## 7. Báo cáo

Liệt kê video đã dựng (tên, link Drive), dòng bị bỏ qua và lý do, số credit còn lại. Nhắc chủ dự án khi đăng: thêm nhạc thịnh hành, bật nhãn nội dung AI, gắn giỏ hàng, rồi đổi M sang `Đã đăng`.
