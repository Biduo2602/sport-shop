# Đặc tả REST API

> Giai đoạn 1 · Bước 4. Nguồn: [user-stories.md](user-stories.md), [database.md](database.md), [erd.dbml](erd.dbml).
> Giai đoạn 2 sẽ sinh tài liệu Swagger tự động từ code; file này là bản thiết kế **trước khi code** để thống nhất giữa frontend và backend.

## 1. Quy ước chung

### Đường dẫn
| Quy ước | Ví dụ đúng | Ví dụ sai | Lý do |
|---|---|---|---|
| Tiền tố phiên bản | `/api/v1/products` | `/products` | Sau này đổi format response thì mở `v2`, app cũ vẫn chạy |
| Danh từ số nhiều, không dùng động từ | `POST /orders` | `POST /createOrder` | Method đã nói hành động; đường dẫn chỉ nói *tài nguyên nào* |
| Chữ thường, nối bằng gạch ngang | `/order-lookups` | `/orderLookups`, `/order_lookups` | Thống nhất, dễ đọc trên URL |
| Lồng tối đa 1 cấp | `/products/{id}/variants` | `/categories/{id}/products/{id}/variants` | URL dài, khó dùng lại |
| API quản trị có tiền tố riêng | `/api/v1/admin/orders` | trộn chung với API khách | Dễ gắn kiểm tra đăng nhập cho cả nhóm, dễ chặn ở Nginx |

### Dữ liệu
- JSON dùng **camelCase** (`salePrice`, `createdAt`) — quy ước của JavaScript. Cơ sở dữ liệu dùng snake_case; Prisma lo việc chuyển đổi.
- **Tiền: số nguyên VNĐ** (`219000`), không gửi chuỗi đã định dạng (`"219.000 ₫"`) — định dạng là việc của frontend.
- **Thời gian: chuỗi ISO 8601 theo UTC** (`"2026-12-01T03:15:00Z"`) — frontend đổi sang giờ Việt Nam khi hiển thị.
- Enum gửi đúng giá trị trong ERD: `"PENDING_PAYMENT"`, `"BANK_TRANSFER"`…

### Phân trang (mọi API trả danh sách)
Request: `?page=1&limit=12` (mặc định `page=1`, `limit=12`, tối đa `limit=50`).
```json
{
  "data": [ ... ],
  "meta": { "page": 1, "limit": 12, "total": 57, "totalPages": 5 }
}
```

### Xác thực
- API khách: **không cần đăng nhập**.
- API `/admin/*`: header `Authorization: Bearer <accessToken>` (JWT nhận từ API đăng nhập, hết hạn sau 8 giờ — US-09).
- Webhook: xác thực bằng khóa bí mật do SePay gửi kèm trong header (chi tiết theo tài liệu SePay, cấu hình ở Giai đoạn 5).

### Format lỗi (mọi lỗi 4xx/5xx)
Dùng format mặc định của NestJS:
```json
{
  "statusCode": 400,
  "message": ["customerPhone phải gồm 10 chữ số, bắt đầu bằng 0"],
  "error": "Bad Request"
}
```
`message` là **mảng** khi lỗi kiểm tra dữ liệu (để frontend hiện lỗi cạnh từng ô), là **chuỗi** với các lỗi khác.

### Status code dùng trong hệ thống
| Code | Khi nào | Ví dụ |
|---|---|---|
| 200 OK | Đọc / sửa thành công | `GET /products`, `PATCH /admin/products/{id}` |
| 201 Created | Tạo mới thành công (kèm header `Location` nếu tài nguyên có đường dẫn để đọc lại) | `POST /orders` |
| 204 No Content | Thành công, không cần trả dữ liệu | `POST /admin/auth/logout` |
| 400 Bad Request | Dữ liệu gửi lên sai định dạng / thiếu / không hợp lệ | `quantity: 1.5` |
| 401 Unauthorized | Chưa đăng nhập, token sai hoặc hết hạn | Gọi `/admin/*` không có token |
| 403 Forbidden | Đã đăng nhập nhưng không đủ quyền | `STAFF` gọi API chỉ dành cho `OWNER` |
| 404 Not Found | Tài nguyên không tồn tại (kể cả đã ẩn) | `GET /products/khong-co` |
| 409 Conflict | Dữ liệu đúng định dạng nhưng **mâu thuẫn với trạng thái hiện tại** | Hết hàng lúc đặt · trùng SKU · chuyển trạng thái đơn sai sơ đồ |
| 429 Too Many Requests | Gọi quá nhiều lần | Tra cứu đơn sai 10 lần / 15 phút (US-08) |
| 500 Internal Server Error | Lỗi không lường trước phía server | — |

---

## 2. Endpoint mẫu (viết đầy đủ)

### `GET /api/v1/products` — Danh sách sản phẩm
- **User story:** US-01, US-04
- **Quyền:** Public
- **Query:**

| Tham số | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `category` | string | Không | slug danh mục, vd `ao-the-thao` |
| `sport` | enum `sport` | Không | vd `running` |
| `q` | string | Không | Tìm theo tên, không phân biệt hoa thường và dấu |
| `minPrice`, `maxPrice` | int | Không | Lọc theo giá bán thực tế |
| `sort` | `newest` \| `price_asc` \| `price_desc` | Không | Mặc định `newest` |
| `page`, `limit` | int | Không | Xem *Phân trang* |

- **200 OK:**
```json
{
  "data": [
    {
      "id": 12,
      "slug": "ao-chay-bo-dri-fit",
      "name": "Áo chạy bộ Dri-fit",
      "thumbnailUrl": "https://cdn.example.com/p/12/0.webp",
      "price": 219000,
      "salePrice": 189000,
      "inStock": true
    }
  ],
  "meta": { "page": 1, "limit": 12, "total": 1, "totalPages": 1 }
}
```
- **Ghi chú:**
  - Không trả sản phẩm `isHidden = true` (US-01).
  - `price` / `salePrice` lấy theo biến thể **rẻ nhất** của sản phẩm (hiện "Từ 189.000 ₫").
  - `inStock = false` khi mọi biến thể đều hết hàng — vẫn hiện, gắn nhãn "Hết hàng" (US-01).
  - Không trả số tồn kho chính xác ở danh sách — đối thủ không cần biết shop còn bao nhiêu hàng.
- **Lỗi:** `400` — `sort` không hợp lệ, `minPrice > maxPrice`, `limit > 50`.

### `POST /api/v1/orders` — Đặt hàng
- **User story:** US-06
- **Quyền:** Public
- **Header:** `Idempotency-Key: <uuid do frontend sinh mỗi lần mở trang đặt hàng>` (bắt buộc)
- **Body:**
```json
{
  "customerName": "Nguyễn Văn An",
  "customerPhone": "0912345678",
  "province": "Hà Nội",
  "ward": "Phường Láng",
  "addressDetail": "Số 1, ngõ 2",
  "note": "Giao giờ hành chính",
  "paymentMethod": "BANK_TRANSFER",
  "items": [
    { "variantId": 31, "quantity": 2 },
    { "variantId": 47, "quantity": 1 }
  ]
}
```
  Chỉ gửi `variantId` và `quantity` — **không gửi giá**. Server tự tra giá, tự tính `subtotal`, `shippingFee`, `total`.
- **201 Created** *(không kèm `Location`: đơn hàng không có API đọc công khai theo mã — xem 4.1)*
```json
{
  "code": "SP261201-K7QX",
  "status": "PENDING_PAYMENT",
  "paymentMethod": "BANK_TRANSFER",
  "subtotal": 627000,
  "shippingFee": 0,
  "total": 627000,
  "paymentDueAt": "2026-12-02T03:15:00Z",
  "payment": {
    "bankName": "MB Bank",
    "accountNumber": "0123456789",
    "accountName": "NGUYEN VAN A",
    "transferContent": "SP261201-K7QX",
    "qrImageUrl": "https://img.vietqr.io/image/..."
  }
}
```
  Với `COD`: `status = "PENDING_CONFIRM"`, `paymentDueAt` và `payment` là `null`.
- **Lỗi:**

| Code | Khi nào |
|---|---|
| 400 | Thiếu trường, SĐT sai định dạng, `items` rỗng, `quantity` không phải số nguyên dương, thiếu `Idempotency-Key` |
| 404 | `variantId` không tồn tại hoặc sản phẩm đã ẩn |
| 409 | Không đủ tồn kho — `message` nêu rõ món nào, còn bao nhiêu (US-06) |

- **Gửi lại cùng `Idempotency-Key`:** trả lại **đúng đơn đã tạo** (200), không tạo đơn mới — xử lý trường hợp bấm 2 lần hoặc mạng chập chờn rồi trình duyệt gửi lại.

---

## 3. Danh sách endpoint

Tiền tố `/api/v1` được lược bỏ trong bảng cho gọn. **Ưu tiên** theo user story: Must = cần cho bản ra mắt.

### 3.1 Khách — không cần đăng nhập

| # | Method | Đường dẫn | Mô tả | User story | Ưu tiên |
|---|---|---|---|---|---|
| 1 | GET | `/categories` | Danh mục đang hiện, theo thứ tự | US-01 | Must |
| 2 | GET | `/products` | Danh sách sản phẩm: lọc, tìm kiếm, sắp xếp, phân trang *(chi tiết ở mục 2)* | US-01, 04 | Must |
| 3 | GET | `/products/{slug}` | Chi tiết: ảnh, mô tả, các biến thể kèm giá và tình trạng hàng ("Chỉ còn N" khi ≤ 5) | US-03 | Must |
| 4 | GET | `/variants?ids=31,47` | Giá và tồn kho **hiện tại** của các biến thể trong giỏ → báo khi giá/tồn kho đã đổi | US-05 | Must |
| 5 | GET | `/checkout-settings` | Phí ship, ngưỡng miễn phí ship (đọc từ `settings`) | US-06 | Must |
| 6 | POST | `/orders` | Đặt hàng *(chi tiết ở mục 2)* | US-06 | Must |
| 7 | GET | `/orders/{code}/payment-status` | Trạng thái thanh toán — trang thanh toán hỏi định kỳ | US-07 | Must |
| 8 | POST | `/order-lookups` | Tra cứu đơn bằng mã đơn + SĐT (gửi trong body) | US-08 | Should |

### 3.2 Admin — cần `Authorization: Bearer <token>`

**Đăng nhập**

| # | Method | Đường dẫn | Mô tả | User story | Ưu tiên |
|---|---|---|---|---|---|
| 9 | POST | `/admin/auth/login` | Đăng nhập → trả `accessToken` | US-09 | Must |
| 10 | POST | `/admin/auth/logout` | Đăng xuất → 204 | US-09 | Must |
| 11 | GET | `/admin/auth/me` | Thông tin admin đang đăng nhập (tên, vai trò) | US-09 | Must |

**Danh mục, sản phẩm, biến thể, ảnh**

| # | Method | Đường dẫn | Mô tả | User story | Ưu tiên |
|---|---|---|---|---|---|
| 12 | GET | `/admin/categories` | Tất cả danh mục, kể cả đang ẩn | US-10 | Must |
| 13 | POST | `/admin/categories` | Thêm danh mục | US-10 | Must |
| 14 | PATCH | `/admin/categories/{id}` | Sửa tên, thứ tự, ẩn/hiện | US-10 | Must |
| 15 | GET | `/admin/products` | Danh sách sản phẩm, kể cả đã ẩn; tìm theo tên/SKU | US-10 | Must |
| 16 | POST | `/admin/products` | Thêm sản phẩm **kèm danh sách biến thể** | US-10 | Must |
| 17 | GET | `/admin/products/{id}` | Chi tiết để sửa | US-10 | Must |
| 18 | PATCH | `/admin/products/{id}` | Sửa thông tin chung; ẩn/hiện (`isHidden`) | US-10 | Must |
| 19 | DELETE | `/admin/products/{id}` | Xóa hẳn — **chỉ** khi chưa từng bán; đã bán → 409, gợi ý ẩn | US-10 | Should |
| 20 | POST | `/admin/products/{id}/variants` | Thêm biến thể (size/màu mới) | US-10 | Must |
| 21 | PATCH | `/admin/variants/{id}` | Sửa giá, giá khuyến mãi, ngưỡng tồn tối thiểu — **không sửa tồn kho ở đây** | US-10 | Must |
| 22 | POST | `/admin/products/{id}/images` | Upload ảnh (`multipart/form-data`; jpg/png/webp ≤ 2 MB; tối đa 8 ảnh) | US-10 | Must |
| 23 | PATCH | `/admin/product-images/{id}` | Đổi thứ tự / chọn ảnh đại diện | US-10 | Should |
| 24 | DELETE | `/admin/product-images/{id}` | Xóa ảnh | US-10 | Must |

**Kho**

| # | Method | Đường dẫn | Mô tả | User story | Ưu tiên |
|---|---|---|---|---|---|
| 25 | GET | `/admin/inventory?lowStock=true` | Tồn kho theo từng biến thể; lọc biến thể dưới ngưỡng | US-11 | Must |
| 26 | POST | `/admin/inventory-movements` | Nhập hàng / điều chỉnh kiểm kê — **đường duy nhất để admin đổi tồn kho** | US-11 | Must |
| 27 | GET | `/admin/inventory-movements?variantId=` | Lịch sử kho: ai, lúc nào, bao nhiêu, lý do | US-11 | Must |

**Đơn hàng & thanh toán**

| # | Method | Đường dẫn | Mô tả | User story | Ưu tiên |
|---|---|---|---|---|---|
| 28 | GET | `/admin/orders` | Danh sách: lọc trạng thái, khoảng ngày; tìm mã đơn / SĐT | US-12 | Must |
| 29 | GET | `/admin/orders/{id}` | Chi tiết: sản phẩm, khách, lịch sử trạng thái, các giao dịch tiền | US-12 | Must |
| 30 | POST | `/admin/orders/{id}/transitions` | Chuyển trạng thái `{ toStatus, reason }` → 201; sai sơ đồ → 409 | US-02 | Must |
| 31 | POST | `/admin/orders/{id}/refunds` | Ghi nhận đã hoàn tiền `{ amount, refundedAt, note }` | US-02, 07 | Must |
| 32 | GET | `/admin/payment-transactions?unmatched=true` | Tiền đến nhưng không khớp đơn nào | US-07 | Should |
| 33 | PATCH | `/admin/payment-transactions/{id}` | Gắn giao dịch không khớp vào đúng đơn `{ orderId }` | US-07 | Should |

**Thống kê & cài đặt**

| # | Method | Đường dẫn | Mô tả | User story | Ưu tiên |
|---|---|---|---|---|---|
| 34 | GET | `/admin/stats/revenue?from=&to=&groupBy=day` | Doanh thu, số đơn, giá trị đơn trung bình (chỉ đơn Hoàn thành) | US-13 | Could |
| 35 | GET | `/admin/stats/top-products?from=&to=&limit=5` | Sản phẩm bán chạy theo số lượng | US-13 | Could |
| 36 | GET | `/admin/settings` | Xem cài đặt | US-06 | Must |
| 37 | PATCH | `/admin/settings/{key}` | Sửa phí ship, ngưỡng miễn phí ship, tài khoản ngân hàng — **chỉ OWNER** | US-06 | Must |

### 3.3 Hệ thống

| # | Method | Đường dẫn | Mô tả | Gọi bởi | Ưu tiên |
|---|---|---|---|---|---|
| 38 | POST | `/webhooks/sepay` | Nhận thông báo tiền vào; xác thực khóa bí mật; chống xử lý lặp | SePay | Must |
| 39 | GET | `/health` | Kiểm tra API và kết nối cơ sở dữ liệu còn sống | Docker, công cụ giám sát (Giai đoạn 8) | Must |

**Tổng: 39 endpoint** — 8 cho khách, 29 cho admin, 2 cho hệ thống. Bản ra mắt (Must) cần 32.

### 3.4 Đề xuất bổ sung user story
ERD có vai trò `OWNER` *"quản lý tài khoản admin"* nhưng chưa có user story nào → chưa liệt kê API. Nếu cần: thêm **US-14 · Chủ shop quản lý tài khoản nhân viên** với `GET / POST / PATCH /admin/admins` (tạo, đổi vai trò, tắt tài khoản). Tạm thời có thể tạo tài khoản admin bằng script seed khi deploy.

---

## 4. Các quyết định thiết kế

### 4.1 Tra cứu đơn dùng `POST /order-lookups` thay vì `GET /orders/{code}?phone=...`
Đọc dữ liệu thì theo REST nên dùng GET — nhưng GET đặt **số điện thoại lên URL**, mà URL bị lưu ở rất nhiều nơi (bài HTTP, Giai đoạn 0):
- lịch sử trình duyệt, ai dùng chung máy cũng xem được;
- log truy cập của Nginx và server;
- header `Referer` gửi sang trang khác khi bấm link;
- công cụ đo lường (Meta Pixel, Google Analytics) ghi lại URL trang.

Đưa SĐT vào **body của POST** thì không bị ghi theo những đường trên, và response cũng không bị cache. Coi mỗi lần tra cứu là "tạo một yêu cầu tra cứu" (`order-lookups`) để tên đường dẫn vẫn là danh từ. Đây là đánh đổi có chủ đích: **bảo vệ dữ liệu cá nhân quan trọng hơn đúng chuẩn REST tuyệt đối**.

### 4.2 Đổi trạng thái đơn dùng `POST /admin/orders/{id}/transitions` thay vì `PATCH /admin/orders/{id}`
Đổi trạng thái không phải "sửa một cột" mà là **một hành động có hệ quả**:
- phải kiểm tra theo sơ đồ trạng thái (chuyển sai → 409);
- ghi một dòng `order_status_history`, bắt buộc có lý do khi hủy;
- có thể cộng lại tồn kho (hủy đơn, nhận hàng hoàn) — trong cùng một transaction.

Nếu dùng `PATCH { status }` chung với các trường khác, rất dễ có đoạn code đổi `status` mà quên các bước trên. Endpoint riêng biến mỗi lần chuyển thành **một bản ghi mới** (201), đúng với việc thật sự xảy ra trong cơ sở dữ liệu.

Cùng lý do, **tồn kho không sửa được qua `PATCH /admin/variants/{id}`** mà chỉ qua `POST /admin/inventory-movements` (#26) — đúng nguyên tắc *"chỉ đổi tồn kho qua một đường duy nhất"* trong `database.md`.

### 4.3 Trang thanh toán biết tiền đã về bằng cách **hỏi định kỳ** (polling)
Luồng: SePay → webhook (#38) → server cập nhật đơn. Trình duyệt của khách không nhận được webhook, nên trang thanh toán gọi `GET /orders/{code}/payment-status` (#7) **mỗi 5 giây**, dừng khi đã nhận đủ tiền hoặc sau 15 phút.

| Cách | Ưu | Nhược |
|---|---|---|
| **Hỏi định kỳ (chọn)** | Đơn giản, chạy qua mọi proxy/CDN, dễ debug | Tốn vài request thừa — không đáng kể với lượng khách của shop |
| Server-Sent Events | Server đẩy ngay khi có tiền | Phải giữ kết nối mở, cấu hình Nginx thêm |
| WebSocket | Hai chiều, thời gian thực | Quá phức tạp cho nhu cầu "chờ một sự kiện" |

Response của #7 **chỉ có** `status`, `amountPaid`, `total` — không có tên, SĐT, địa chỉ — vì đây là API công khai: dù mã đơn có phần ngẫu nhiên (ADR 0002), chỉ trả những gì trang thanh toán thật sự cần.
