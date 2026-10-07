# Thiết kế cơ sở dữ liệu

> Giai đoạn 1 · Bước 1 — Danh sách thực thể · Bước 2 — Quan hệ giữa các bảng · Bước 3 — ERD: [`erd.dbml`](erd.dbml) (vẽ trên dbdiagram.io).

## Cách tìm thực thể

Đọc từng user story, gạch chân danh từ. Một danh từ thành **bảng** khi trả lời "có" cả 3 câu:
1. Có cần **lưu lâu dài**?
2. Có **nhiều bản ghi**?
3. Có **thông tin riêng** của nó?

Nếu chỉ là một đặc điểm của thứ khác → **cột**. Nếu danh sách cố định, ít giá trị, không có thông tin riêng → **enum**.

## Danh sách bảng (11)

### Nhóm sản phẩm

| Bảng | Lưu thông tin gì (trường chính) | Từ user story | Vì sao là bảng riêng |
|---|---|---|---|
| `categories` | tên, slug (đường dẫn), thứ tự hiển thị, đang hiện/ẩn | US-01 | Nhiều danh mục, mỗi cái có tên và đường dẫn riêng |
| `products` | danh mục, tên, slug, môn thể thao, mô tả, đã ẩn (xóa mềm) | US-01, 03, 04, 10 | Thông tin **chung** của một mẫu sản phẩm, không phụ thuộc size/màu |
| `product_variants` | sản phẩm, **SKU** (không trùng), size, màu, giá, giá khuyến mãi, **tồn kho**, ngưỡng tồn tối thiểu | US-03, 05, 10, 11 | Mỗi tổ hợp size/màu có SKU, giá và tồn kho **riêng** — khách mua một *biến thể*, không mua một *sản phẩm* |
| `product_images` | sản phẩm, đường dẫn ảnh, thứ tự | US-03, 10 | Một sản phẩm có tối đa 8 ảnh, cần sắp thứ tự |

### Nhóm đơn hàng & thanh toán

| Bảng | Lưu thông tin gì (trường chính) | Từ user story | Vì sao là bảng riêng |
|---|---|---|---|
| `orders` | **mã đơn**, tên khách, SĐT, tỉnh / phường (địa giới 2 cấp), địa chỉ, ghi chú, phương thức thanh toán, **trạng thái**, tạm tính, phí ship, tổng tiền, số tiền đã nhận, hạn thanh toán | US-06, 07, 08, 12 | Trung tâm của hệ thống |
| `order_items` | đơn hàng, biến thể, **tên sản phẩm, size, màu, đơn giá lúc mua** (bản sao), số lượng, thành tiền | US-06, 10 | Một đơn có nhiều món. Lưu **bản sao** giá và tên để đổi giá sản phẩm sau này không làm sai đơn cũ (US-10) |
| `order_status_history` | đơn hàng, trạng thái cũ → mới, **ai đổi** (admin, hoặc trống nếu hệ thống tự đổi), lý do, thời điểm | US-02, 08 | Một đơn đổi trạng thái nhiều lần; US-02 bắt lưu ai/lúc nào/lý do; US-08 hiện các mốc thời gian cho khách |
| `payment_transactions` | đơn hàng (có thể trống), **mã giao dịch ngân hàng** (không trùng), loại (tiền vào / hoàn tiền), số tiền, nội dung chuyển khoản, thời điểm, dữ liệu webhook gốc | US-02, 07 | Một đơn có thể nhận **nhiều** lần chuyển (thiếu → chuyển bù); mã giao dịch **không trùng** giúp webhook gửi lặp chỉ xử lý một lần; tiền có thể đến cho đơn đã hủy hoặc không khớp đơn nào |

### Nhóm kho, quản trị & cấu hình

| Bảng | Lưu thông tin gì (trường chính) | Từ user story | Vì sao là bảng riêng |
|---|---|---|---|
| `inventory_movements` | biến thể, **số lượng thay đổi** (+ nhập / − xuất), lý do (nhập hàng, điều chỉnh, bán, hủy đơn, hoàn hàng), đơn hàng liên quan, admin thực hiện, ghi chú, thời điểm | US-11, 02 | US-11 bắt lưu lịch sử *ai, lúc nào, bao nhiêu, lý do*. Cột `stock` ở `product_variants` chỉ là **số dư hiện tại**; bảng này là **sổ cái** giải thích vì sao có số dư đó |
| `admins` | email (không trùng), **mật khẩu đã băm**, tên, vai trò, **đang hoạt động** (tắt thay vì xóa), số lần đăng nhập sai, khóa đến lúc nào, lần đăng nhập cuối | US-09 | Nhiều thành viên nhóm, mỗi người một tài khoản; cần biết *ai* đã đổi trạng thái đơn, nhập kho |
| `settings` | khóa, giá trị (vd `free_shipping_threshold`, `shipping_fee`, thông tin tài khoản ngân hàng) | US-06, 07 | Admin đổi được mà không cần sửa code và deploy lại |

## Bước 2 — Quan hệ giữa các bảng

| # | Quan hệ | Kiểu | Khóa ngoại (bảng.cột) | Bắt buộc / được trống | ON DELETE | Lý do |
|---|---|---|---|---|---|---|
| 1 | categories – products | 1-n | `products.category_id` | Bắt buộc | restrict | Không cho xóa danh mục khi còn sản phẩm — phải chuyển sản phẩm sang danh mục khác trước |
| 2 | products – product_variants | 1-n | `product_variants.product_id` | Bắt buộc | restrict | Biến thể có lịch sử kho và đơn hàng; muốn bỏ thì ẩn sản phẩm |
| 3 | products – product_images | 1-n | `product_images.product_id` | Bắt buộc | **cascade** | Ảnh *thuộc hẳn* về sản phẩm, không bảng nào khác trỏ tới ảnh → sản phẩm (chưa từng bán) bị xóa thật thì ảnh đi theo |
| 4 | orders – order_items | 1-n | `order_items.order_id` | Bắt buộc | restrict | Về ý nghĩa thì cascade hợp lý (chi tiết thuộc về đơn), nhưng đơn hàng **không bao giờ bị xóa** → restrict làm lưới an toàn nếu ai đó lỡ tay |
| 5 | product_variants – order_items | 1-n | `order_items.variant_id` | Bắt buộc | restrict | **Chính ràng buộc này thực thi US-10 ở tầng cơ sở dữ liệu**: biến thể đã từng bán thì không xóa được, dù code có lỗi |
| 6 | orders – order_status_history | 1-n | `order_status_history.order_id` | Bắt buộc | restrict | Lịch sử là bằng chứng, không được mất |
| 7 | admins – order_status_history | 1-n | `order_status_history.changed_by` | **Được trống** | restrict | Trống = hệ thống tự đổi (webhook nhận tiền, tự hủy sau 24h). Restrict chứ không `set null`: set null sẽ xóa mất dấu vết *ai đã làm* → admin nghỉ việc thì **tắt** (`is_active = false`), không xóa |
| 8 | orders – payment_transactions | 1-n | `payment_transactions.order_id` | **Được trống** | restrict | Trống = tiền đến nhưng nội dung chuyển khoản không khớp đơn nào; vẫn phải lưu để admin xử lý |
| 9 | product_variants – inventory_movements | 1-n | `inventory_movements.variant_id` | Bắt buộc | restrict | Mọi biến động kho đều thuộc về một biến thể cụ thể |
| 10 | orders – inventory_movements | 1-n | `inventory_movements.order_id` | **Được trống** | restrict | Có đơn: trừ kho khi bán, cộng lại khi hủy/hoàn. Trống: nhập hàng, điều chỉnh kiểm kê |
| 11 | admins – inventory_movements | 1-n | `inventory_movements.admin_id` | **Được trống** | restrict | Có admin: nhập hàng, điều chỉnh. Trống: hệ thống tự trừ khi khách đặt hàng |
| 12 | orders – product_variants | **n-n** | *Không nối thẳng* — đi qua `order_items` (`order_id` + `variant_id`) | — | — | Một đơn có nhiều biến thể, một biến thể nằm trong nhiều đơn. `order_items` là **bảng trung gian có dữ liệu riêng** (số lượng, giá lúc mua) |
| 13 | admins – payment_transactions | 1-n | `payment_transactions.admin_id` | **Được trống** | restrict | *(Phát hiện thêm khi điền bảng)* Hoàn tiền do admin ghi nhận thủ công → cần biết ai ghi. Tiền vào qua webhook thì trống |

`settings` không có quan hệ với bảng nào.

### Rút ra từ bảng trên
- **Gần như mọi quan hệ đều `restrict`**: dữ liệu của shop là lịch sử mua bán và sổ sách — không xóa, chỉ ẩn (`is_hidden`) hoặc tắt (`is_active`). `restrict` biến quy tắc đó thành ràng buộc mà **cơ sở dữ liệu tự cưỡng chế**, kể cả khi code có bug.
- **`cascade` chỉ dùng khi bảng con thuộc hẳn về bảng cha** và không ai khác tham chiếu tới (ảnh sản phẩm).
- **Khóa ngoại được trống** ⇔ "việc này có thể do hệ thống tự làm" hoặc "dữ liệu có thể không gắn với gì" (tiền không khớp đơn).
- Quan hệ n-n luôn cần bảng trung gian; bảng trung gian thường **có dữ liệu riêng** chứ không chỉ 2 khóa ngoại.

## Cố ý **không** tạo bảng

Phần phỏng vấn hay hỏi ngược: *"Sao không có bảng X?"*

| Thứ | Lưu ở đâu | Lý do |
|---|---|---|
| **Giỏ hàng** | `localStorage` của trình duyệt | US-05: giỏ hàng không cần đăng nhập; chỉ khi đặt hàng mới gửi lên server |
| **Khách hàng** | Thông tin khách nằm thẳng trong `orders` | US-06: đặt hàng không cần tài khoản. Lưu thẳng vào đơn còn giữ đúng địa chỉ *tại thời điểm đặt* |
| **Size, màu** | Cột trong `product_variants` | Chỉ là đặc điểm của biến thể, không có thông tin riêng |
| **Môn thể thao** | Cột enum trong `products` | Danh sách cố định ~7 giá trị, không có thông tin riêng |
| **Trạng thái đơn** | Cột enum trong `orders` | 7 giá trị cố định theo sơ đồ trong `user-stories.md` |
| **Đếm lần tra cứu sai** (US-08) | Bộ nhớ tạm của server (sau này có thể dùng Redis) | Dữ liệu ngắn hạn (15 phút), ghi rất nhiều — không đáng lưu vào cơ sở dữ liệu |

## Quy ước chung (áp dụng cho mọi bảng)
- Tên bảng **tiếng Anh, chữ thường, số nhiều, nối bằng gạch dưới**: `order_items`, không phải `OrderItem` hay `chi_tiet_don`.
- Mọi bảng có `id`, `created_at`; bảng có sửa đổi thì thêm `updated_at`. Kiểu của `id` (số tự tăng hay UUID) → quyết định ở `docs/decisions/0002-...`.
- **Tiền VNĐ lưu số nguyên**, không dùng số thực (bài học từ `playground/cart.ts`).
- Trạng thái, phương thức thanh toán, lý do kho… dùng **enum**, không lưu chuỗi tự do.

## Tự kiểm tra

### 1. Vì sao `order_items` phải lưu tên sản phẩm và đơn giá, trong khi đã có `variant_id`?
`variant_id` chỉ là **con trỏ tới trạng thái hiện tại** của biến thể. Giá, tên, thậm chí cả sản phẩm đều có thể đổi sau khi khách đặt hàng.

> Ví dụ: khách mua áo giá 219.000 ngày 01/12. Ngày 15/12 shop giảm còn 189.000. Nếu đơn chỉ lưu `variant_id` rồi đọc giá hiện tại, tra cứu đơn sẽ hiện 189.000 — **sai với số tiền khách đã trả**, doanh thu tháng 12 tính sai, đối soát với ngân hàng không khớp.

Đơn hàng là **chứng từ tài chính**: phải phản ánh đúng những gì khách đã đồng ý *tại thời điểm mua*. Vì vậy `order_items` chụp lại (*snapshot*) tên, size, màu, đơn giá. Đây là **lặp dữ liệu có chủ đích** — một ngoại lệ hợp lý của nguyên tắc "không lặp dữ liệu" (chuẩn hóa).

`variant_id` vẫn giữ lại để: cộng trả tồn kho khi hủy đơn, thống kê sản phẩm bán chạy (US-13), dẫn link về trang sản phẩm.

### 2. Đã có cột `stock`, vì sao còn cần `inventory_movements`? Có thể lệch không, chống lệch thế nào?
Giống tài khoản ngân hàng: **số dư** và **sao kê**.

| | `product_variants.stock` (số dư) | `inventory_movements` (sao kê) |
|---|---|---|
| Trả lời câu hỏi | *Còn bao nhiêu?* | *Vì sao còn bấy nhiêu? Ai làm, lúc nào?* |
| Dùng khi | Hiện "Còn hàng / Hết hàng", kiểm tra khi đặt hàng — đọc rất nhiều, phải nhanh | Kiểm kê thấy lệch, điều tra mất hàng, US-11 xem lịch sử |
| Nếu chỉ có cái này | Không giải thích được khi kho thực tế lệch với số trên web | Mỗi lần hiện sản phẩm phải cộng toàn bộ lịch sử (`SUM`) → chậm dần theo thời gian |

**Có thể lệch** nếu code cập nhật một nơi mà quên nơi kia, hoặc server lỗi giữa hai lệnh ghi. Cách chống:
1. Luôn ghi **cả hai trong cùng một transaction** — hoặc cả hai thành công, hoặc không cái nào được ghi.
2. Chỉ cho phép đổi tồn kho qua **một hàm duy nhất** trong code (vd `InventoryService.adjust()`), không chỗ nào khác được sửa thẳng cột `stock`.
3. Ràng buộc trong cơ sở dữ liệu: `CHECK (stock >= 0)` — US-11 "tồn kho không bao giờ âm".
4. Định kỳ **đối soát**: `SUM(change)` của mỗi biến thể phải bằng `stock`; lệch thì báo động.

### 3. Vì sao mã giao dịch ngân hàng phải không được trùng?
Dịch vụ webhook (SePay, Casso…) **gửi lại** nếu không nhận được phản hồi 200 kịp thời — mạng chập chờn, server khởi động lại, xử lý quá lâu. Vì vậy **cùng một giao dịch có thể đến nhiều lần**.

Nếu không có ràng buộc, mỗi lần đến lại ghi thêm một dòng tiền vào:
- Khách chuyển 300.000 cho đơn 600.000, webhook đến 2 lần → hệ thống ghi nhận 600.000 → đơn **bị coi là đã trả đủ** và được giao, shop mất 300.000.
- Doanh thu, đối soát ngân hàng đều sai.

Vì sao phải là **ràng buộc trong cơ sở dữ liệu** chứ không chỉ kiểm tra trong code: hai lần gửi có thể đến **cùng lúc**. Cả hai cùng kiểm tra "giao dịch này đã có chưa?" → đều thấy "chưa" → đều ghi. Ràng buộc `UNIQUE` là lớp chặn cuối: lần ghi thứ hai bị cơ sở dữ liệu từ chối, code bắt lỗi đó, coi như "đã xử lý rồi" và vẫn trả 200 để dịch vụ ngừng gửi lại. Tính chất "làm nhiều lần cũng như làm một lần" này gọi là **idempotency**.

### 4. Muốn cho khách tạo tài khoản và xem lại đơn cũ, phải thay đổi gì?
- **Thêm bảng `customers`**: email/SĐT (không trùng), mật khẩu đã băm, tên. Có thể thêm `customer_addresses` nếu cho lưu nhiều địa chỉ.
- **`orders` thêm cột `customer_id`, cho phép trống**: vẫn cho khách vãng lai đặt hàng, và các đơn cũ đã có không bị ảnh hưởng. Thêm một cột cho phép trống là thay đổi **an toàn**, không phá dữ liệu cũ.
- **Vẫn giữ** tên, SĐT, địa chỉ trong `orders` (lý do như câu 1: địa chỉ lúc giao có thể khác địa chỉ hiện tại trong tài khoản).
- Gắn đơn cũ (đặt khi chưa có tài khoản) vào tài khoản mới: khớp theo SĐT **sau khi xác minh bằng OTP**, nếu không ai cũng nhận được đơn của người khác.
- Tùy chọn: chuyển giỏ hàng từ `localStorage` vào bảng `carts` để đồng bộ giữa điện thoại và máy tính.
- Cân nhắc: gộp `admins` và `customers` thành một bảng `users` có cột vai trò, hay tách riêng? Tách riêng thì lỗi ở phần khách hàng khó ảnh hưởng tới tài khoản quản trị — an toàn hơn.
