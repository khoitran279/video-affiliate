# Dự án: 3 kênh TikTok affiliate dựng video bằng AI

Chủ dự án làm việc bằng tiếng Việt. Mọi nội dung (kịch bản, caption, nhận xét, báo cáo) viết bằng tiếng Việt.

## Tài nguyên cố định

| Tài nguyên | ID / đường dẫn |
|---|---|
| Google Sheet "Theo dõi sản phẩm affiliate" | `1KGzpF1lh5xX_AgoFbc9gC06kMTvECPsKAxpae5xCvRA` |
| Tab của Sheet | `Hướng dẫn` (tiêu chí B10:B13, tổng quan), `Nhà đẹp`, `Phụ kiện`, `Sách` |
| Drive: thư mục ảnh đầu vào | `1xWdv5WbQmzTYHy9Cvq6hmxVZgaFbUp4i` ("Affiliate - Ảnh sản phẩm") |
| Drive: thư mục video đầu ra | `1tPGwiNV9KwqkO9Rg777NwdrELaLc2Z0C` ("Affiliate - Video đã dựng") |
| Công cụ dựng video | `tools/make_video.py` (đọc docstring ở đầu file) |
| Font | `tools/fonts/` (Playfair Display, Be Vietnam Pro; có đủ dấu tiếng Việt) |

### Cột của mỗi tab kênh (hàng 1 là tiêu đề, dữ liệu từ hàng 2)

A Ngày thêm · B Tên sản phẩm · C Link · D Nguồn · E Giá (đ) · F Hoa hồng (%) · **G Hoa hồng/đơn (công thức, không ghi đè)** · H Lượt bán · I Số sao · J Kho trong nước · K Ảnh/video đẹp · **L Điểm (công thức, không ghi đè)** · M Trạng thái · N Ghi chú (của chủ dự án, không sửa) · O Thư mục ảnh (link Drive) · P Video (Claude điền) · Q Caption (Claude điền) · R Nhận xét của Claude (Claude điền) · S Lời đọc (Claude viết, chủ dự án tạo giọng)

Trạng thái (cột M): `Chờ duyệt` → `Đã chọn` → `Chờ giọng` → `Đã dựng` → `Đã đăng`, hoặc `Loại`.

## Giọng đọc: chủ dự án tự tạo file âm thanh

Chủ dự án tạo giọng bằng CapCut Pro, công cụ khác, hoặc tự thu giọng mình, rồi bỏ file âm thanh (`.mp3`, `.m4a`, `.wav`, hoặc video `.mp4`/`.mov` để tách tiếng) vào **thư mục ảnh của sản phẩm** (cột O). Agent viết lời đọc ở cột S, chờ file, rồi dựng video khớp với file đó.

Dự phòng: dòng ở `Chờ giọng` quá **2 ngày** mà chưa có file thì dựng bằng giọng Azure `vi-VN-HoaiMyNeural` qua Creative Claw (khoảng 1 credit) và ghi rõ ở cột R.

Sheet dùng locale vi_VN: **công thức ngăn cách bằng dấu `;`**, số thập phân dùng dấu phẩy khi hiển thị.

## Ba kênh

| Kênh | Định vị | Ghi chú |
|---|---|---|
| Nhà đẹp | Decor, gia dụng, nhà cửa tối giản | Mùa Tết: decor Tết, bếp Tết, quà Tết |
| Phụ kiện | Túi, đồ da, trang sức tối giản, khăn, kính | Quà Tết, Valentine 14/02 |
| Sách | Diễn đạt lại 1 ý tưởng của sách, sách làm quà | Chỉ shop chính hãng |

## Phong cách kênh affiliate (KHÔNG dùng gu thương hiệu cá nhân)

Các kênh affiliate tách biệt hoàn toàn với thương hiệu cá nhân bất động sản của chủ dự án. Gu "tông trầm, chữ ít và mảnh" trong cài đặt cá nhân **không áp dụng** ở đây. Mục tiêu duy nhất: giữ người xem và ra đơn.

- **Giây đầu:** hook to, rõ, đặt ở 1/4 trên màn hình (chữ đậm trên khối trắng). Hình đầu là cảnh sản phẩm đẹp nhất.
- **Phụ đề chạy theo giọng** suốt video (chữ trắng viền đen, tối đa 2 dòng chia đều). Truyền `script` vào `make_video.py`.
- **Font hook và phụ đề: UTM Impact** (chủ dự án chọn 26/11). Công cụ dùng `tools/fonts/UTM-Impact.ttf` nếu có; chưa có thì dùng Anton (kiểu Impact, miễn phí).
- **Màu theo hàng thật:** `grade: "true"`, chỉ tăng tương phản và độ nét. Không giảm bão hòa.
- **Nhịp vừa (chủ dự án chọn 26/11):** 1,8–2,2 giây/cảnh, 6–9 cảnh. Xen cảnh toàn với cảnh cận chi tiết (`focus`): nơ, cổ áo, chất vải, đường may.
- Chuyển cảnh bằng chuyển động (zoom punch). Không sticker, không hiệu ứng lòe loẹt.
- Thẻ cuối: "Xem ở giỏ hàng" có mũi tên chỉ xuống.
- Video 9:16, bản gốc 1080×1920, 12–25 giây. Bản tải lên Drive là `*_drive.mp4` (720×1280, dưới 3 MB, công cụ tự xuất) vì connector Drive giới hạn khoảng 3 MB mỗi lần.
- **Trước khi tự động hóa một định dạng mới:** đưa chủ dự án xem 2–3 phương án (kịch bản và bản nháp) để chọn.

### Kịch bản đã duyệt (26/11/2026)

- **A – Nỗi đau:** mở bằng tình huống khó chịu có thật của người mua → sản phẩm giải quyết thế nào (chi tiết thấy được) → thông tin chọn mua (size, dịp dùng) → CTA.
- **C – Gấp theo mùa:** mở bằng mốc thời gian thật (Noel, Tết, 14/02) + câu hỏi → một sản phẩm dùng được cho dịp đó → CTA. Chỉ dùng khi mốc còn ≥ 5 ngày.
- B – Giá (chưa duyệt): không dùng cho đến khi chủ dự án cho phép.

## Quy tắc bắt buộc (pháp lý và chính sách)

Căn cứ: Luật Quảng cáo sửa đổi số 75/2025/QH15 (hiệu lực 01/01/2026); chính sách nội dung AI của TikTok.

1. **Không quảng cáo sai:** chỉ nói điều có trong mô tả sản phẩm hoặc thấy được trên ảnh. Không hứa công dụng sức khỏe, làm đẹp, tâm linh ("chiêu tài"). Không viết lời chứng thực giả kiểu "mình dùng 3 tháng rồi".
2. **Sản phẩm trên video phải đúng hàng thật:** chỉ dùng ảnh/video của shop. Không dùng AI tạo hoặc chỉnh hình sản phẩm. Chỉnh màu ở mức `grade: "soft"`.
3. **Không ghi giá** trên video trừ khi cột E có giá và ghi chú yêu cầu. Giá đổi liên tục.
4. **Loại ngay** (đặt `Loại`, ghi lý do ở cột R): hàng nhái thương hiệu, sách lậu (giá rẻ bất thường so với giá bìa, shop không chính hãng), rượu từ 15 độ, pháo, thuốc, thực phẩm chức năng, sản phẩm có tuyên bố chữa bệnh.
5. **Trang sức:** chỉ ghi "bạc 925" khi mô tả shop có giấy kiểm định.
6. **Sách:** không đọc hoặc chụp lại nhiều trang. Diễn đạt ý tưởng bằng lời của kênh; trích dẫn ngắn có ghi tác giả.
7. Video có giọng hoặc cảnh AI thì khi đăng phải bật nhãn "Nội dung do AI tạo" trên TikTok. Nhắc việc này trong báo cáo.
8. **Không đăng bài, không gắn link, không mua hàng** thay chủ dự án. Không chia sẻ file Drive công khai.

## Quy trình hằng ngày

Chạy lần lượt hai skill:

1. `.claude/skills/chon-san-pham/SKILL.md`: đánh giá các dòng `Chờ duyệt`.
2. `.claude/skills/dung-video/SKILL.md`: viết lời đọc cho dòng `Đã chọn`; dựng video cho dòng `Chờ giọng` đã có file âm thanh.

Giới hạn mỗi lần chạy: tối đa **3 video mỗi kênh**, tổng tối đa 9. Giọng dự phòng Azure tốn khoảng 1 credit Creative Claw. Nếu còn dưới 10 credit, không dùng giọng dự phòng và báo.

Kết thúc mỗi lần chạy bằng báo cáo ngắn: đã đánh giá bao nhiêu sản phẩm, đã dựng video nào (kèm link Drive), lỗi gì, chủ dự án cần làm gì tiếp.
