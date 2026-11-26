---
name: chon-san-pham
description: Đánh giá các sản phẩm ở trạng thái "Chờ duyệt" trong Google Sheet theo dõi affiliate, ghi nhận xét và đề xuất. Dùng trong lần chạy hằng ngày hoặc khi chủ dự án nói "xem bảng", "chấm sản phẩm".
---

# Chọn sản phẩm

Đọc `CLAUDE.md` ở gốc repo trước (ID Sheet, cột, quy tắc pháp lý).

## Các bước

1. Với mỗi tab `Nhà đẹp`, `Phụ kiện`, `Sách`: đọc `'<tab>'!A1:R` bằng `get_values` (dải mở, không đoán dòng cuối).
2. Lọc các dòng có cột M = `Chờ duyệt` và cột R còn trống (chưa đánh giá).
3. Với mỗi dòng, đánh giá theo thứ tự:
   - **Loại ngay** nếu vi phạm quy tắc 4 trong `CLAUDE.md` (hàng nhái, sách lậu, hàng cấm). Đặt M = `Loại`, R = lý do ngắn.
   - **Điểm cột L** (công thức tự tính): 4–5 là tốt.
   - **Hợp định vị kênh** (bảng "Ba kênh" trong `CLAUDE.md`) và **dễ bán qua video**: có nỗi đau hoặc dịp dùng rõ, ảnh shop đủ đẹp để cắt cận chi tiết. Dựa vào tên sản phẩm và, nếu có, ảnh trong thư mục cột O.
   - **Mùa vụ:** trước Tết (đến khoảng 25/01) ưu tiên decor Tết, quà Tết, bếp Tết. Sau 15/01 chỉ ưu tiên hàng có kho trong nước (cột J = `Có`).
   - **Thiếu ảnh:** nếu cột O trống, ghi R = "Cần thư mục ảnh".
4. Ghi cột R một câu: kết luận + lý do, ví dụ: `Nên làm: 5 điểm, hợp decor Tết, hoa hồng 30.000đ/đơn.` hoặc `Chưa nên: 4,6 sao, ảnh shop mờ.`
5. **Không tự đổi sang `Đã chọn`.** Chủ dự án duyệt bước này. Chỉ được đổi sang `Loại` theo bước 3.
6. Ghi theo từng ô (`update_values` vào `'<tab>'!R<n>` hoặc `M<n>`). Không ghi đè cột G, L, N.

## Báo cáo

Liệt kê tối đa 5 sản phẩm nên làm nhất mỗi kênh (tên, điểm, hoa hồng/đơn) để chủ dự án chuyển sang `Đã chọn`.
