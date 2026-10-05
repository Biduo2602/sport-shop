# Ghi chú học tập

Ghi lại những gì quan sát được khi làm bài tập, và **rút ra được gì**. Câu nào chưa chắc thì vẫn ghi câu trả lời của mình, đánh dấu ❓ để hỏi lại.

---

## Giai đoạn 0 · Bài 1 — Quan sát request bằng DevTools

### Số liệu đã quan sát

**Shopee — trang chủ, lần truy cập thứ hai (cửa sổ thường)**
- Tổng: ~550–590 request cho một lần mở trang
- Request trang HTML: `GET https://shopee.vn/` → `200 OK`, máy chủ `147.136.175.193:443`
- Response headers đáng chú ý: `Content-Type: text/html`, `Content-Encoding: gzip`, `Cache-Control: no-cache`, `Server: nginx`, `Strict-Transport-Security: max-age=31536000`, `Access-Control-Allow-Origin: *`
- Timing: **không có** DNS / Initial connection / SSL · Waiting for server response **389 ms** · Content download 32 ms · Tổng **424 ms**
- Một API (lọc Fetch/XHR): `get_payment_info` trả JSON dạng `{ error: 0, error_msg: null, data: {...} }`

**DummyJSON — lần đầu truy cập (cửa sổ ẩn danh)**
- Timing: DNS lookup **66 ms** · Initial connection **84 ms** (trong đó SSL **44 ms**) · Waiting for server response **58 ms** · Content download 2 ms · Tổng **211 ms**
- Bấm F5 không có request nào 304 → mọi response đều có `Cache-Control: no-store`

**MDN (developer.mozilla.org) — bấm F5**
- Trang HTML trả **304**; request gửi kèm `If-None-Match` = giá trị `ETag` của lần tải trước
- Nhiều file JS/CSS/ảnh ghi *(memory cache)* / *(disk cache)* ở cột Size

### Rút ra được gì

**1. Một trang web = hàng trăm request, không phải một.**
Trình duyệt tải file HTML trước; HTML chỉ đến các file JS, CSS, ảnh, font → trình duyệt tải tiếp; JS chạy xong lại gọi các API (Fetch/XHR) để lấy dữ liệu JSON đổ vào trang. Ngoài ra còn các request theo dõi quảng cáo (`tr/` là Meta Pixel, `activityi` là Google Ads).

**2. Request và response đều có cấu trúc giống nhau: dòng đầu + headers + body.**
- Request: *method + URL* · headers · body (GET không có body)
- Response: *status code* · headers · body
- **Headers là "thông tin về dữ liệu"**, ví dụ `Content-Type` cho biết body là HTML hay JSON, `Content-Encoding: gzip` cho biết body đã được nén.

**3. Thời gian một request = kết nối + chờ server + tải về.**

```
DNS (đổi tên miền → IP) → TCP (bắt tay kết nối) → TLS (mã hóa) → gửi request → chờ server xử lý (TTFB) → tải response
└──────────── chỉ xảy ra khi mở kết nối MỚI ───────────┘
```

- Lần đầu vào DummyJSON: riêng phần kết nối đã mất ~150 ms (DNS 66 + TCP/TLS 84), nhiều hơn cả thời gian server xử lý (58 ms).
- Vào lại Shopee: không có DNS/TCP/TLS vì trình duyệt **dùng lại kết nối cũ** (keep-alive) và đã nhớ IP → tiết kiệm được phần đó.
- SSL nằm *bên trong* Initial connection vì bắt tay TLS diễn ra ngay sau khi TCP kết nối xong, và DevTools tính cả hai là "mở kết nối".
- Ở Shopee, **chờ server (TTFB) chiếm 389/424 ms** → phần chậm nhất nằm ở backend (truy vấn dữ liệu, dựng HTML), không phải ở đường truyền.

**4. Cache có 3 mức, từ nhanh đến chậm.**

| Cách | Có gửi request tới server? | Server trả gì | Khi nào xảy ra |
|---|---|---|---|
| *(memory cache)* / *(disk cache)* | **Không** | — | Response còn hạn (`max-age` chưa hết) |
| **304 Not Modified** | **Có**, kèm `If-None-Match: <ETag>` | Chỉ header, **body rỗng** | Hết hạn hoặc `no-cache` → hỏi lại server "có gì mới không?" |
| **200** tải lại toàn bộ | Có | Toàn bộ nội dung | Lần đầu, hoặc `no-store`, hoặc dữ liệu đã đổi |

- `no-cache` **không** có nghĩa "không được cache": được lưu, nhưng mỗi lần dùng phải hỏi lại server (Shopee dùng cho trang HTML để giá/khuyến mãi luôn mới).
- `no-store` mới là "không được lưu" → không bao giờ có 304 (DummyJSON).
- Nút Back không gửi request nào vì Chrome giữ nguyên cả trang trong bộ nhớ (**bfcache**).

**5. Status code chia theo nhóm.**
`2xx` thành công (200 OK) · `3xx` chuyển hướng / dùng bản cũ (301, 307, 304) · `4xx` lỗi do client gửi sai · `5xx` lỗi phía server.
Gõ `http://` bị chuyển sang `https://`: server trả **301** (chuyển vĩnh viễn), hoặc nếu tên miền bật **HSTS** thì trình duyệt tự chuyển luôn (**307 Internal Redirect**) mà không cần hỏi server.

**6. Bảo mật: cookie trong request headers chính là "chìa khóa" đăng nhập.**
Không chụp màn hình, không commit phần cookie lên repo.

### Áp dụng vào project sport-shop

| Điều đã học | Dùng ở đâu |
|---|---|
| `Content-Type: application/json`, status code | Giai đoạn 2 — API trả đúng status: 200, 201, 400, 401, 404 |
| Envelope `{ error, data }` của Shopee | Giai đoạn 1 — quyết định format response/lỗi trong `docs/api.md` |
| TTFB là phần chậm nhất | Giai đoạn 2, 5 — index cơ sở dữ liệu, tránh truy vấn thừa |
| `Cache-Control`, ETag, 304 | Giai đoạn 4 — cache trang sản phẩm; **không** cache giỏ hàng, đơn hàng |
| CORS (`Access-Control-Allow-Origin`) | Giai đoạn 4 — web (Next.js) gọi api (NestJS) khác tên miền |
| `Server: nginx`, `gzip`, HSTS | Giai đoạn 8 — tự cấu hình Nginx, bật nén và HTTPS |

### Câu hỏi thêm: API nên báo lỗi bằng HTTP status hay bằng trường `error` trong body?
Shopee trả `{ error: 0, error_msg: null, data }`, kiểu "envelope": luôn bọc dữ liệu trong một lớp vỏ có mã lỗi riêng.

- **Chỉ dùng mã lỗi trong body (luôn trả 200):** client buộc phải đọc body mới biết thành công hay thất bại; trình duyệt, cache, công cụ giám sát đều tưởng mọi request đều thành công.
- **Chỉ dùng HTTP status:** đúng chuẩn, mọi công cụ hiểu ngay, nhưng một mình status không đủ để hiển thị lỗi cụ thể cho người dùng (trường nào sai, sai thế nào).
- **Kết hợp (chọn cho sport-shop):** status đúng nghĩa (200, 201, 400, 401, 404, 500…) **và** body lỗi có cấu trúc thống nhất, ví dụ
  `{ "statusCode": 400, "message": ["price phải lớn hơn 0"], "error": "Bad Request" }` (đây cũng là format mặc định của NestJS). Thành công thì trả thẳng dữ liệu, không cần vỏ `error: 0`.

Lý do Shopee dùng envelope: hệ thống rất lớn, có lớp **BFF** (Backend For Frontend, chính là `bff_meta`) gom nhiều dịch vụ, cần mã lỗi nghiệp vụ chi tiết hơn HTTP status. Với project cỡ sport-shop thì không cần.

### Tự kiểm tra

**Vì sao lần đầu vào một trang luôn chậm hơn những lần sau?**
1. Phải tra **DNS** để đổi tên miền ra IP; lần sau hệ điều hành/trình duyệt đã nhớ (DummyJSON: 66 ms lần đầu, 5 ms lần sau).
2. Phải mở **kết nối TCP + TLS** mới (~150 ms ở DummyJSON); lần sau dùng lại kết nối cũ (keep-alive), như ở Shopee không còn 3 dòng này.
3. Phải tải **toàn bộ** JS, CSS, ảnh, font; lần sau phần lớn lấy từ *(memory/disk cache)* hoặc chỉ nhận **304** với body rỗng.
4. Bấm Back thì gần như tức thì vì **bfcache** giữ nguyên cả trang trong bộ nhớ.

**Trang sản phẩm và trang giỏ hàng nên đặt `Cache-Control` thế nào?**

| | Trang / API sản phẩm | Giỏ hàng, đặt hàng, tra cứu đơn, admin |
|---|---|---|
| Dữ liệu | Công khai, giống nhau với mọi người | Riêng của từng người, có thông tin cá nhân |
| Thay đổi | Thỉnh thoảng (giá, mô tả) | Liên tục (số lượng, tồn kho, trạng thái) |
| Header | `public, max-age=60` (cache ngắn, hết hạn thì hỏi lại bằng ETag → 304). Ảnh sản phẩm có hash trong tên file: `max-age=31536000, immutable` | `private, no-store` |
| Nếu đặt sai | Trang chậm, server tốn tải vô ích | Khách thấy giá/tồn kho cũ; tệ hơn, CDN/proxy cache nhầm và **hiện đơn của người này cho người khác** |

**DevTools cho thấy TTFB 3 giây: lỗi ở frontend hay backend?**
**Backend.** TTFB là khoảng từ lúc gửi xong request đến lúc nhận byte đầu tiên, tức thời gian server xử lý (cộng một lượt đi-về mạng, chỉ vài chục ms). Frontend (tải JS, render) chỉ bắt đầu *sau* TTFB. Nguyên nhân thường gặp: truy vấn cơ sở dữ liệu thiếu index, lỗi N+1 query, gọi API bên ngoài chậm, server quá tải. Cách điều tra: ghi log thời gian từng bước, hoặc dùng header `Server-Timing` để DevTools hiện chi tiết.

---

## Giai đoạn 0 · Bài 2 — Gửi request bằng curl

Chạy ngày 05/10/2026 trên máy cá nhân (Git Bash, curl 8.9.0).

| # | Lệnh | Method | Status | Ý nghĩa của status | Kích thước body |
|---|---|---|---|---|---|
| 1 | `/products?limit=2&select=title,price` | GET | **200** OK | Thành công, trả dữ liệu | 170 B |
| 2 | `/products/9999` | GET | **404** Not Found | Không có tài nguyên này | 46 B |
| 3 | `/auth/me` không kèm token | GET | **401** Unauthorized | Chưa xác thực: server không biết bạn là ai | 38 B |
| 4 | `/products/add` | POST | **201** Created | Đã tạo tài nguyên mới (`id: 195`) | 46 B |
| 5 | `/products/195` | GET | **404** Not Found | Sản phẩm vừa "tạo" không tồn tại | 45 B |
| 6 | `/products/add` với `{title:}` | POST | **400** Bad Request | Client gửi dữ liệu sai cú pháp JSON | 83 B |
| 7 | `/products/1` với `{"price":99}` | PATCH | **200** OK | Đã sửa một phần, trả về **toàn bộ** sản phẩm sau khi sửa | 548 B |
| 8 | `/products/1` | DELETE | **200** OK | Đã xóa; body có `isDeleted: true`, `deletedOn` | — |
| 9 | `/products/1` kèm `If-None-Match` đúng ETag | GET | **304** Not Modified | Dữ liệu chưa đổi, dùng lại bản đang có | **0 B** (so với 1.510 B) |
| 10 | `/products/1` kèm ETag sai 1 ký tự | GET | **200** OK | ETag không khớp → server gửi lại toàn bộ | 1.510 B |

### Rút ra được gì

**1. Vì sao tạo sản phẩm trả 201 nhưng lấy lại thì 404?**
DummyJSON là **API giả lập**: các lệnh POST/PUT/PATCH/DELETE chỉ *giả vờ* thành công và trả về kết quả trông như thật, nhưng **không ghi gì vào cơ sở dữ liệu**. `id: 195` chỉ là `total` (194) + 1. Bài học: status 2xx chỉ là *lời server nói*; muốn chắc dữ liệu đã được lưu thì phải đọc lại. Sau này viết test cho API của mình cũng phải kiểm tra như vậy.

**2. Vì sao tạo mới trả 201 mà không phải 200?**
`201 Created` nói rõ **có một tài nguyên mới vừa được tạo ra**, còn `200` chỉ là "thành công" chung chung. Client nhờ đó phân biệt được tạo mới với đọc/sửa. Theo chuẩn, 201 nên kèm header `Location: /products/195` trỏ tới tài nguyên mới; DummyJSON không có, API của mình nên có.

**3. Lỗi 400 là của client hay server? 4xx khác 5xx thế nào?**
400 là **lỗi của client**: gửi JSON sai. Gửi lại y nguyên thì vẫn lỗi, client phải sửa request.

| | 4xx | 5xx |
|---|---|---|
| Lỗi của | Client (gửi sai, thiếu quyền, tài nguyên không có) | Server (bug, cơ sở dữ liệu sập, quá tải) |
| Gửi lại y nguyên | Vẫn lỗi | Có thể được nếu sự cố đã qua |
| Ai cần xử lý | Người dùng / code frontend | **Lập trình viên backend, phải có cảnh báo** |

**4. DELETE trả `isDeleted: true` thay vì xóa hẳn: giống quy tắc nào trong user stories?**
Đây là **xóa mềm (soft delete)**: chỉ đánh dấu, không xóa dòng dữ liệu. Giống **US-10**: *sản phẩm đã có trong đơn hàng thì chỉ ẩn, không xóa hẳn*. Lợi ích: đơn hàng cũ vẫn tra được sản phẩm, khôi phục được khi xóa nhầm, giữ được lịch sử. Cái giá: **mọi truy vấn** đều phải nhớ lọc `isDeleted = false`.

**5. Thông tin kết nối từ `curl -v`**
- IP: `104.21.61.23` (DNS trả về 4 địa chỉ: 2 IPv4 + 2 IPv6, đều thuộc **Cloudflare**)
- TLS: **TLS 1.3**, mã hóa `TLS_AES_256_GCM_SHA384`, chứng chỉ do Google Trust Services cấp, hết hạn 06/11/2026
- HTTP: curl dùng **HTTP/1.1**; trình duyệt dùng **HTTP/2** (server chọn `h2` khi bắt tay TLS). Khác nhau vì curl của Git Bash dùng thư viện TLS Schannel của Windows, bản này không thương lượng HTTP/2.

**Quan sát thêm**
- **Bỏ dấu nháy quanh URL (lệnh 1):** bash hiểu `&` là "chạy nền", nên URL bị cắt còn `...?limit=2`, phần `select=title,price` bị bỏ → server trả sản phẩm **đầy đủ mọi trường** thay vì chỉ `title, price`. Không báo lỗi gì, đây là loại lỗi khó phát hiện nhất.
- **PATCH (lệnh 7):** gửi chỉ `{"price":99}` nhưng nhận về cả sản phẩm (548 B). Đây là quy ước phổ biến để client có ngay trạng thái mới mà không phải GET lại.
- **304 (lệnh 9):** tiết kiệm **toàn bộ 1.510 B body**; header vẫn được gửi. Với trang có hàng trăm request, phần tiết kiệm này rất lớn.
- **Sửa 1 ký tự ETag (lệnh 10):** nhận 200 với body đầy đủ. Server so sánh ETag, không khớp nghĩa là client đang giữ phiên bản khác → gửi bản mới.
- **ETag từ đâu ra:** `W/"5e6-LuZgXJ6APIKHswyRKC9GQ6dxUNE"` do **Express tự sinh** cho mọi response. `5e6` (hệ 16) = **1.510** = đúng độ dài body; phần sau là mã băm nội dung. `W/` nghĩa là *weak*: hai response tương đương về ý nghĩa, không đảm bảo giống từng byte. API này vừa có ETag vừa có `no-store`, nên trình duyệt không lưu và không dùng tới ETag; chỉ client tự gửi `If-None-Match` (như curl) mới tận dụng được. NestJS chạy trên Express nên API của sport-shop cũng sẽ tự có header này.

---

## Giai đoạn 0 · Bài 3 — Chuyện gì xảy ra khi gõ `https://dummyjson.com/products/1`

Số đo từ `curl -w` (thời điểm cộng dồn từ lúc bắt đầu):

```
0 ms ─ DNS ─► 5 ms ─ TCP ─► 66 ms ─ TLS ─► 197 ms ─ gửi request + server xử lý ─► 265 ms (byte đầu tiên) ─ tải body ─► xong
```

**1. Phân tích URL.** `https` → cổng mặc định **443**; tên miền `dummyjson.com`; đường dẫn `/products/1`. Nếu tên miền có trong danh sách **HSTS**, trình duyệt tự đổi `http` → `https` trước khi làm gì khác (307 Internal Redirect ở bài 1).

**2. DNS: đổi tên miền thành IP.**
`nslookup dummyjson.com` (máy chủ DNS `8.8.8.8`) trả về 4 địa chỉ: `104.21.61.23`, `172.67.205.42` và 2 địa chỉ IPv6, đều của Cloudflare. Nhiều IP để chia tải và dự phòng. Bằng chứng: Chrome *DNS lookup* 66 ms lần đầu; curl lần sau chỉ 5 ms vì đã được nhớ.

**3. TCP: bắt tay 3 bước** (SYN → SYN-ACK → ACK) tới `104.21.61.23:443` để có một kênh truyền tin cậy.
Bằng chứng: `* Connected to dummyjson.com (104.21.61.23) port 443`; Chrome *Initial connection*.

**4. TLS: thiết lập mã hóa.** Hai bên chào nhau, server gửi **chứng chỉ** (trình duyệt kiểm tra: đúng tên miền, còn hạn, do tổ chức tin cậy cấp, ở đây là Google Trust Services), thống nhất khóa mã hóa (**TLS 1.3**) và chọn giao thức HTTP (**ALPN** → `h2`). Từ đây mọi dữ liệu đều được mã hóa.
Bằng chứng: Chrome *SSL* 44 ms, nằm *bên trong* Initial connection vì TLS chạy ngay trên kết nối TCP vừa mở và DevTools tính chung là "mở kết nối".

**5. Gửi HTTP request** (đã được mã hóa bên trong TLS):
```
> GET /products/1 HTTP/1.1
> Host: dummyjson.com
> User-Agent: curl/8.9.0
> Accept: */*
```

**6. Server xử lý.** Request tới **Cloudflare** (CDN) trước: nếu có sẵn bản cache thì trả luôn (header `cf-cache-status: HIT`), không thì chuyển về server gốc (Node.js/Express) để lấy dữ liệu và tạo JSON.
Bằng chứng: Chrome *Waiting for server response* 58 ms; curl từ 197 ms đến 265 ms.

**7. Nhận HTTP response.** Dòng trạng thái `< HTTP/1.1 200 OK`, các header (`content-type`, `etag`, `cache-control`…), rồi body 1.510 B. Kết nối được **giữ lại** (keep-alive) cho các request sau.

**8. Trình duyệt render** (curl không có bước này): đọc HTML → dựng cây DOM; đọc CSS → CSSOM; chạy JS; tính bố cục (layout) rồi vẽ (paint). Trong lúc đọc HTML, gặp `<script>`, `<link>`, `<img>` → lặp lại bước 5–7 (dùng lại kết nối đã mở). Đó là lý do một trang như Shopee có hàng trăm request.

---

## Giai đoạn 0 · Bài 4 — TypeScript: tính tiền giỏ hàng

Code: [`playground/cart.ts`](../playground/cart.ts) (kiểu dữ liệu + 2 hàm) · [`playground/main.ts`](../playground/main.ts) (18 trường hợp kiểm tra). Chạy: `npx tsx playground/main.ts` → **18 đạt, 0 lỗi**.

### Kiến thức TypeScript đã dùng

| Cú pháp | Dùng để làm gì trong bài |
|---|---|
| `type Size = "S" \| "M" \| "L" \| "XL"` | **Union of literal types**: `size` chỉ nhận đúng 4 giá trị, gõ `"XXL"` bị báo lỗi |
| `salePrice?: number` | **Optional property**: không phải sản phẩm nào cũng có khuyến mãi |
| `product.salePrice ?? product.price` | **Nullish coalescing**: chỉ lấy `price` khi `salePrice` là `undefined`/`null`. Dùng `\|\|` sẽ sai với quà tặng `salePrice: 0` (0 bị coi là "không có") |
| `discountPercent: number = 0` | **Default parameter**: không truyền thì mặc định không giảm giá |
| `items: CartItem[]`, `: number` sau tên hàm | Kiểu mảng, kiểu trả về của hàm |
| `items.reduce((total, item) => ..., 0)` | Cộng dồn mảng thành một giá trị |
| `export` / `import { type Product } from "./cart"` | Tách code thành module; `type` báo rằng chỉ import kiểu, không có code chạy |

### Bài học 1 — Kiểm tra dữ liệu: chỉ chấp nhận cái chắc chắn đúng

Bản đầu kiểm tra bằng cách **liệt kê cái sai để chặn**:
```ts
if (discountPercent < 0 || discountPercent > 100) throw ...   // NaN lọt qua!
if (item.quantity <= 0) throw ...                              // NaN, 1.5 lọt qua!
```
`NaN < 0` và `NaN > 100` đều là `false` → NaN đi thẳng vào phép tính, tổng tiền thành `NaN` mà không ai báo. `quantity: 1.5` cũng được chấp nhận.

Bản sửa đổi cách nghĩ — **chỉ chấp nhận cái chắc chắn đúng, còn lại đều là lỗi**:
```ts
if (!Number.isFinite(discountPercent) || discountPercent < 0 || discountPercent > 100) throw ...
if (!Number.isInteger(item.quantity) || item.quantity <= 0) throw ...
```
- `Number.isFinite` loại NaN và Infinity; `Number.isInteger` loại thêm số lẻ.
- Hai hàm này **không tự đổi kiểu**: `Number.isFinite("10")` là `false`. Hàm cũ `isFinite("10")` (không có `Number.`) lại đổi chuỗi sang số rồi trả `true`.
- Cách nghĩ này áp dụng cho mọi dữ liệu từ bên ngoài: form, request API, webhook.

### Bài học 2 — Tính tiền với số thực

`0.1 + 0.2 = 0.30000000000000004` trong JavaScript vì máy tính lưu số thực dạng nhị phân, có sai số.
- Tính theo thứ tự **nhân trước, chia sau**: `subtotal * (100 - discount) / 100`, ít sai số hơn `subtotal * (1 - discount / 100)`.
- **Làm tròn** kết quả cuối (`Math.round`) vì VNĐ không có số lẻ.
- Trong cơ sở dữ liệu luôn lưu tiền VNĐ dạng **số nguyên**, không dùng số thực.

### Bài học 3 — Thí nghiệm: `tsx` khác `tsc` thế nào

Thêm 2 dòng cố ý sai vào cuối `main.ts`:
```ts
calcTotal(cart, "10");                                            // chuỗi thay vì số
const bad: CartItem = { product: ao, size: "XXL", quantity: 1 };  // size không tồn tại
```

| | `npx tsx playground/main.ts` | `npx tsc --noEmit --strict ...` |
|---|---|---|
| Có chạy chương trình không? | **Có** — chạy hết 18 test rồi mới gặp lỗi | **Không** — dừng ngay, chưa chạy dòng nào |
| Phát hiện `"10"` | Chỉ nhờ đoạn kiểm tra `Number.isFinite` → ném lỗi **lúc đang chạy** | ✅ `Argument of type 'string' is not assignable to parameter of type 'number'` |
| Phát hiện `"XXL"` | ❌ **Không bao giờ** — chạy như bình thường | ✅ `Type '"XXL"' is not assignable to type 'Size'` |

**Vì sao:** `tsx` chỉ **xóa hết phần kiểu dữ liệu** rồi chạy như JavaScript thường — nhanh, nhưng không kiểm tra gì. `tsc` mới là trình **kiểm tra kiểu**.

**Ngược lại**, `tsc --strict` báo ✅ cho bản code đầu dù NaN và 1.5 vẫn lọt — vì `NaN` và `1.5` đều thuộc kiểu `number`.

**Kết luận: cần cả hai lớp bảo vệ**

| Lớp | Kiểm tra gì | Khi nào | Bắt được |
|---|---|---|---|
| TypeScript (`tsc`) | **Kiểu**: có phải số không, có đúng 4 size không | Lúc viết code, trước khi chạy | `"10"`, `"XXL"`, gõ sai tên trường |
| Kiểm tra trong code | **Giá trị**: số có hợp lý không | Lúc chạy, với dữ liệu thật | NaN, 1.5, âm, ngoài khoảng |

Áp dụng vào sport-shop:
- Dữ liệu từ trình duyệt gửi lên API là JSON — TypeScript **không** kiểm soát được thứ client gửi → Giai đoạn 2 phải có **DTO validation** cho mọi request.
- Giai đoạn 7: CI chạy `tsc` trước mỗi lần merge để không có lỗi kiểu nào lọt lên `main`. Khi dev chỉ chạy bằng `tsx` hay Next.js dev server thì lỗi kiểu có thể không hiện ra.

### Câu hỏi còn mở
- **`id` là số tự tăng hay chuỗi (UUID)?** Bài này chọn chuỗi. Quyết định chính thức ở Giai đoạn 1 khi thiết kế cơ sở dữ liệu → ghi thành `docs/decisions/0002-...`.
- **Sản phẩm giá âm chặn ở đâu?** Không phải trong `calcTotal` mà ở lúc admin tạo/sửa sản phẩm (US-10) — dữ liệu sai phải bị chặn ngay từ cửa vào.

---

## Giai đoạn 0 · Tự kiểm tra (ROADMAP)

**1. GET khác POST thế nào? PUT khác PATCH thế nào?**

| | GET | POST |
|---|---|---|
| Mục đích | Đọc dữ liệu | Tạo mới / gửi dữ liệu để xử lý |
| Body | Không có; tham số nằm trên URL (lộ trong lịch sử, log) | Có |
| Gọi lại nhiều lần | Kết quả như nhau, không thay đổi gì (*an toàn*, *idempotent*) | Mỗi lần tạo thêm một bản ghi (**không** idempotent: bấm 2 lần thành 2 đơn, xem US-06) |
| Cache được | Có | Không |

- **PUT**: gửi **toàn bộ** tài nguyên để thay thế; trường nào không gửi coi như bị xóa. Idempotent.
- **PATCH**: chỉ gửi **những trường cần sửa** (Bài 2, lệnh 7 chỉ gửi `price`).

**2. 401 khác 403 ra sao? 400 khác 404 khác 500?**
- **401 Unauthorized**: *chưa xác thực*, server không biết bạn là ai (gọi `/auth/me` không có token).
- **403 Forbidden**: *đã biết bạn là ai nhưng không có quyền* (ví dụ tài khoản nhân viên gọi API chỉ dành cho chủ shop).
- **400**: request sai (JSON hỏng, thiếu trường bắt buộc). **404**: request đúng nhưng tài nguyên không tồn tại. **500**: server gặp lỗi không lường trước, không phải lỗi của client.

**3. Vì sao nói REST là *stateless*?**
Server **không nhớ gì** về các request trước. Mỗi request phải tự mang đủ thông tin để xử lý: ví dụ gọi `/auth/me` thì *lần nào* cũng phải gửi kèm token, server không "nhớ" là bạn đã đăng nhập. Lợi ích: request nào cũng có thể đến bất kỳ server nào sau bộ cân bằng tải, nên dễ mở rộng thêm server. Trạng thái (giỏ hàng, phiên đăng nhập) nằm ở client (localStorage, token) hoặc trong cơ sở dữ liệu, không nằm trong bộ nhớ của server.

**4. `git merge` khác `git rebase`? Khi nào dùng cái nào?**
- **merge** giữ nguyên lịch sử, thêm một commit gộp có hai commit cha: an toàn, thấy rõ nhánh tách/gộp, nhưng lịch sử rối hơn.
- **rebase** chép lại các commit của mình lên đầu nhánh đích, tạo commit **mới** (hash đổi): lịch sử thẳng một đường.
- **Quy tắc vàng:** không rebase nhánh người khác đang dùng chung. Rebase dùng cho nhánh cá nhân chưa chia sẻ (ví dụ cập nhật nhánh tính năng theo `main` mới nhất); merge dùng khi gộp vào nhánh chung.
- Trên GitHub tương ứng 3 nút: *Create a merge commit*, *Squash and merge*, *Rebase and merge*. PR #1 dùng Squash vì cả PR chỉ là một thay đổi.

**5. Vì sao dùng TypeScript thay vì JavaScript?**
- **Bắt lỗi khi đang viết code** thay vì khi chạy: gọi `calcTotal(items, "10")` (chuỗi thay vì số) bị báo đỏ ngay trong VS Code; với JS thì chạy ra kết quả sai mà không báo gì.
- **Gợi ý code và đổi tên an toàn**: VS Code biết chính xác một đối tượng có những trường nào.
- **Kiểu dữ liệu chính là tài liệu**: nhìn kiểu `Product` là biết API trả gì; Prisma sinh sẵn kiểu từ cơ sở dữ liệu, dùng chung cho cả NestJS và Next.js.
- Cái giá: phải học thêm, thêm bước biên dịch. Với project nhiều file và nhiều tầng như sport-shop thì lợi nhiều hơn hại.
