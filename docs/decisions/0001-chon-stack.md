# 0001 — Chọn stack công nghệ

- Ngày: 04/10/2026
- Trạng thái: Đã chốt

## Bối cảnh
- Website bán trang phục & dụng cụ thể thao cho shop thật (khách là sinh viên, người thu nhập trung bình; phần lớn truy cập bằng điện thoại từ Facebook/Instagram/Threads).
- Đồng thời là project cá nhân để ứng tuyển vị trí **fullstack developer** → cần thể hiện được cả frontend, backend, cơ sở dữ liệu và deploy.
- Người làm: 1 sinh viên, quen JavaScript, đã học React cơ bản.

## Các lựa chọn đã cân nhắc
| Lựa chọn | Ưu | Nhược |
|---|---|---|
| Haravan / Sapo / WooCommerce | Có web trong vài ngày | Gần như không viết code → không có giá trị cho CV |
| Next.js + Supabase | Nhanh, ít code backend | Supabase che mất phần backend – phần phỏng vấn hỏi nhiều nhất |
| **Next.js + NestJS + PostgreSQL** | Tự viết toàn bộ backend; một ngôn ngữ (TypeScript) cho cả hai đầu; cấu trúc NestJS giống Spring nên dễ chuyển sang Java | Lâu hơn (~10–12 tuần), phải tự deploy và vận hành |

## Quyết định
Chọn **Next.js (web) + NestJS (api) + PostgreSQL/Prisma**, viết bằng TypeScript, đóng gói Docker, CI bằng GitHub Actions.

## Hệ quả
- Website ra mắt sau kênh mạng xã hội (shop ra mắt 16/11/2026 trên FB/IG/Threads; web dự kiến giữa tháng 12).
- Phải tự lo bảo mật, sao lưu dữ liệu, giám sát lỗi.
- Phải học TypeScript trước khi vào code chính (Giai đoạn 0).

<!-- Mỗi quyết định quan trọng sau này (ORM, cách xác thực, nơi deploy…) viết thành 1 file mới theo đúng mẫu này: 0002-…, 0003-… -->
