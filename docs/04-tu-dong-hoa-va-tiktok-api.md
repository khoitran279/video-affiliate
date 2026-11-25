# 04 — Tự động hóa và TikTok for Developers

Cập nhật: 25/11/2026

## Giai đoạn 1: đã chạy

```
Bạn: thêm sản phẩm vào Sheet + tạo thư mục ảnh trên Drive, dán link vào cột O
        ↓
06:12 mỗi sáng: phiên Claude tự chạy trên cloud
  1. chon-san-pham: đánh giá dòng "Chờ duyệt", ghi nhận xét cột R, loại hàng vi phạm
  2. dung-video: với dòng "Đã chọn" → tải ảnh → kịch bản → giọng HoaiMy → render
     → tải video lên Drive "Affiliate - Video đã dựng" → điền P (video), Q (caption), M = "Đã dựng"
        ↓
Bạn: xem video trên Drive → đăng TikTok (nhạc, nhãn AI, gắn giỏ) → M = "Đã đăng"
```

| Thành phần | Vị trí |
|---|---|
| Sổ tay agent | `CLAUDE.md` |
| Skill chọn sản phẩm | `.claude/skills/chon-san-pham/SKILL.md` |
| Skill dựng video | `.claude/skills/dung-video/SKILL.md` |
| Công cụ dựng | `tools/make_video.py` |

Đã kiểm tra thông suốt từng khâu: tải ảnh từ Drive riêng tư, tạo giọng Azure HoaiMy (1 credit), tải giọng về, render có tiếng, tải video lên Drive.

## TikTok for Developers: kết luận

**Không nên đầu tư vào TikTok for Developers lúc này để tự động đăng bài.**

### Căn cứ (FACT, từ nguồn đọc được; trang gốc developers.tiktok.com không truy cập được từ máy này)

1. **Hướng dẫn chia sẻ nội dung (Content Sharing Guidelines)** của TikTok liệt kê là **không chấp nhận**: "công cụ tiện ích giúp tải nội dung lên tài khoản do bạn hoặc nhóm của bạn quản lý". Đây đúng là mô hình của dự án (agent đăng lên 3 kênh của chính bạn). Ứng dụng kiểu này nhiều khả năng không qua vòng kiểm duyệt.
2. Ứng dụng **chưa qua kiểm duyệt** chỉ đăng được video **riêng tư**, tối đa 5 người dùng trong 24 giờ, và tài khoản phải để chế độ riêng tư lúc đăng.
3. Ứng dụng phải hướng tới người dùng rộng rãi, không chỉ dùng nội bộ. Người dùng phải tự chọn chế độ riêng tư, thấy tên tài khoản và đồng ý rõ ràng trước mỗi lần đăng.
4. API có tham số `is_aigc` để gắn nhãn nội dung AI. **Không thấy** tài liệu nào cho biết API gắn được sản phẩm TikTok Shop (giỏ hàng affiliate).

### Phương án thay thế (RECOMMENDATION)

| Phương án | Ưu | Nhược |
|---|---|---|
| **A. Tự đăng và hẹn giờ trong TikTok Studio** (app hoặc web) | Hợp lệ 100%, gắn giỏ hàng được, bật nhãn AI được | Mất khoảng 2–3 phút/video |
| B. Dịch vụ lên lịch bên thứ ba đã được TikTok duyệt | Đăng hàng loạt | Có phí; thường không gắn được giỏ hàng TikTok Shop; cần kiểm tra từng dịch vụ |
| C. Tự đăng ký app developer | Toàn quyền | Nhiều khả năng bị từ chối theo căn cứ 1 |

**Khuyến nghị: phương án A.** Mỗi ngày dành khoảng 20–30 phút để đăng và hẹn giờ 6–9 video. Phần tốn thời gian (chọn, dựng, caption) đã tự động.

## Nguồn

- https://developers.tiktok.com/docs/en/content-sharing-guidelines (bản tiếng Trung: https://developers.tiktok.com/docs/zh-Hans/content-sharing-guidelines)
- https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post
- https://www.outstand.so/blog/tiktok-content-posting-api
- https://skedcast.com/resources/guides/tiktok-content-posting-api
