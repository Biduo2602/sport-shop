# Lộ trình học & xây dựng

Stack: **Next.js** (web) · **NestJS** (api) · **PostgreSQL + Prisma** · **Docker** · **GitHub Actions** — toàn bộ TypeScript.

Cách làm mỗi giai đoạn: đọc mục *Học* → làm mục *Việc* → trả lời được hết *Tự kiểm tra* mới sang giai đoạn sau.
Gặp câu không trả lời được → đó chính là câu phỏng vấn sẽ hỏi, ghi lại vào `docs/notes.md`.

---

## Giai đoạn 0 — Nền tảng (3–5 ngày)

### Git & GitHub
- [ ] `git init`, commit đầu tiên, tạo repo **public** trên GitHub và push
- [ ] Thử quy trình làm việc thật: tạo nhánh `docs/user-stories` → commit → mở Pull Request → tự review → merge
- [ ] Viết commit theo chuẩn [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`

### Web & HTTP
- [ ] Mở một trang bán hàng bất kỳ → DevTools (F12) → tab **Network** → xem 1 request: method, URL, status code, headers, response JSON
- [ ] Gọi API công khai bằng `curl` hoặc extension Thunder Client:
  - `GET https://dummyjson.com/products?limit=5`
  - `POST https://dummyjson.com/products/add` với body JSON
- [ ] Tự viết ra giấy: chuyện gì xảy ra từ lúc gõ URL đến lúc trang hiện ra (DNS → TCP → TLS → HTTP request → response → render)

### TypeScript
- [ ] Học: kiểu cơ bản, `interface` / `type`, union, generic cơ bản, `async/await` — [TS Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [ ] Bài tập: viết `playground/cart.ts` gồm kiểu `Product`, `CartItem` và hàm `calcTotal(items, discountPercent)`; chạy bằng `npx tsx playground/cart.ts`

### Tự kiểm tra
1. GET khác POST thế nào? PUT khác PATCH thế nào?
2. 401 khác 403 ra sao? 400 khác 404 khác 500?
3. Vì sao nói REST là *stateless*?
4. `git merge` khác `git rebase`? Khi nào dùng cái nào?
5. Vì sao dùng TypeScript thay vì JavaScript?

---

## Giai đoạn 1 — Phân tích & thiết kế (1 tuần)
- [ ] Viết user stories → `docs/user-stories.md`
- [ ] Vẽ ERD trên [dbdiagram.io](https://dbdiagram.io) → lưu mã nguồn `docs/erd.dbml` + ảnh `docs/erd.png`
- [ ] Liệt kê API endpoints → `docs/api.md` (method, path, ai được gọi, request, response)
- [ ] Wireframe 4 màn: Trang chủ · Chi tiết sản phẩm · Giỏ hàng/Đặt hàng · Admin quản lý đơn (Figma hoặc Excalidraw)

**Tự kiểm tra**
1. Vì sao tách `products` và `product_variants` thay vì để size/màu trong `products`?
2. Vì sao `order_items` phải lưu lại giá lúc mua, không đọc giá từ bảng sản phẩm?
3. Quan hệ 1-n và n-n khác nhau thế nào, cài đặt n-n trong SQL ra sao?

---

## Giai đoạn 2 — API sản phẩm (1–2 tuần)
PostgreSQL chạy bằng Docker Compose · NestJS module/controller/service · Prisma schema & migration · CRUD sản phẩm + biến thể · lọc, phân trang · validate DTO · xử lý lỗi tập trung · Swagger

## Giai đoạn 3 — Xác thực admin (1 tuần)
Băm mật khẩu bằng bcrypt · JWT access token · Guard phân quyền · Chống brute-force cơ bản

## Giai đoạn 4 — Giao diện khách (2 tuần)
Next.js App Router · SSG/SSR cho trang sản phẩm · giỏ hàng (state + localStorage) · form đặt hàng (react-hook-form + zod) · responsive mobile-first

## Giai đoạn 5 — Đơn hàng & thanh toán (1–2 tuần) ⭐
Tạo đơn trong transaction · chống bán vượt tồn kho khi 2 người mua cùng lúc · VietQR · webhook SePay: xác thực chữ ký + idempotency

## Giai đoạn 6 — Trang quản trị (1 tuần)
Quản lý đơn & trạng thái · upload ảnh · thống kê doanh thu

## Giai đoạn 7 — Kiểm thử & chất lượng (1 tuần)
Jest unit test cho service · Playwright test luồng mua hàng · ESLint + Prettier · pre-commit hook

## Giai đoạn 8 — Deploy & DevOps (1 tuần)
Dockerfile · GitHub Actions (lint → test → build) · VPS + Nginx + HTTPS · biến môi trường & secrets · Sentry

## Giai đoạn 9 — Đóng gói cho CV
README: sơ đồ kiến trúc, link demo, ảnh chụp, tài khoản demo, mục *Khó khăn & cách giải quyết* · số liệu thật (số đơn, điểm Lighthouse)
