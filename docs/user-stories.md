# User stories

Mẫu: **Là** <vai trò>, **tôi muốn** <hành động>, **để** <mục đích>.
Mỗi story kèm *Tiêu chí chấp nhận* — điều kiện cụ thể để biết story đã làm xong. Sau này mỗi tiêu chí sẽ thành một test case.

Vai trò: **Khách** (không cần tài khoản) · **Admin** (thành viên nhóm shop)

---

## Ví dụ mẫu

### US-01 · Khách xem sản phẩm theo danh mục
**Là** khách, **tôi muốn** xem danh sách sản phẩm theo danh mục (Áo, Quần, Giày…), **để** nhanh chóng tìm món mình cần.

Tiêu chí chấp nhận:
- [ ] Mỗi sản phẩm hiện: ảnh, tên, giá (nếu có khuyến mãi thì hiện giá gốc gạch ngang)
- [ ] Sản phẩm đã hết hàng ở mọi size vẫn hiện nhưng có nhãn "Hết hàng"
- [ ] Mỗi trang tối đa 12 sản phẩm, có phân trang
- [ ] Hiển thị tốt trên màn hình rộng 375px

### US-02 · Admin cập nhật trạng thái đơn hàng
**Là** admin, **tôi muốn** đổi trạng thái đơn (Chờ xác nhận → Đang giao → Hoàn thành / Đã hủy), **để** cả nhóm biết đơn đang ở bước nào.

Tiêu chí chấp nhận:
- [ ] Chỉ người đã đăng nhập với vai trò admin mới đổi được
- [ ] Không thể chuyển ngược từ "Hoàn thành" về trạng thái trước
- [ ] Hủy đơn thì số lượng trong đơn được cộng trả lại tồn kho
- [ ] Lưu lại ai đổi, đổi lúc nào

---

## Bạn tự viết tiếp

Gợi ý các nhóm tính năng cần có story (mỗi nhóm 1–3 story):

**Khách**
- Xem chi tiết sản phẩm, chọn size/màu
- Tìm kiếm sản phẩm
- Thêm vào giỏ, sửa số lượng, xóa khỏi giỏ
- Đặt hàng (nhập tên, SĐT, địa chỉ; chọn COD hoặc chuyển khoản)
- Thanh toán chuyển khoản bằng mã VietQR
- Tra cứu đơn hàng

**Admin**
- Đăng nhập / đăng xuất
- Thêm, sửa, ẩn sản phẩm; upload ảnh
- Quản lý tồn kho theo từng size/màu
- Xem danh sách đơn, lọc theo trạng thái
- Xem thống kê doanh thu theo ngày/tháng
