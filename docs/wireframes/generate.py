"""Sinh wireframe SVG cho sport-shop (grayscale, low-fidelity).

Chạy: python docs/wireframes/generate.py  → ghi đè 4 file .svg trong thư mục này.
"""
import os
from html import escape

OUT = os.path.dirname(os.path.abspath(__file__))  # ghi SVG cạnh file này
os.makedirs(OUT, exist_ok=True)

FONT = "Arial, Helvetica, sans-serif"
INK, MUTED, LINE, FILL, IMG = "#222", "#777", "#9E9E9E", "#F2F2F2", "#E0E0E0"
ERR, NOTE = "#D32F2F", "#EF6C00"


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h, self.items = w, h, []
        self.add(f'<rect width="{w}" height="{h}" fill="#fff"/>')
        self.text(20, 34, title, 20, bold=True)

    def add(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="#fff", stroke=LINE, r=6, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=LINE, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill="#fff", stroke=LINE, sw=1.5):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=14, color=INK, bold=False, anchor="start", strike=False, italic=False):
        st = ""
        fw = ' font-weight="bold"' if bold else ""
        fs = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{fw}{fs}{st}>{escape(s)}</text>')
        if strike:  # vẽ gạch ngang thủ công để chắc chắn hiển thị ở mọi trình xem
            w = len(s) * size * 0.52
            x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
            self.line(x0, y - size * 0.32, x0 + w, y - size * 0.32, color, 1)

    def img(self, x, y, w, h, label=None):
        self.rect(x, y, w, h, IMG, LINE, 4)
        self.line(x, y, x + w, y + h, "#BDBDBD", 1)
        self.line(x + w, y, x, y + h, "#BDBDBD", 1)
        if label:
            self.text(x + w / 2, y + h / 2 + 5, label, 12, MUTED, anchor="middle")

    def button(self, x, y, w, h, label, primary=False, disabled=False, size=14):
        if primary:
            self.rect(x, y, w, h, "#333" if not disabled else "#BDBDBD", "#333" if not disabled else "#BDBDBD", 8)
            self.text(x + w / 2, y + h / 2 + size * 0.35, label, size, "#fff", bold=True, anchor="middle")
        else:
            self.rect(x, y, w, h, "#fff", LINE if not disabled else "#D6D6D6", 8, dash="4 3" if disabled else None)
            self.text(x + w / 2, y + h / 2 + size * 0.35, label, size, INK if not disabled else "#BDBDBD", anchor="middle", strike=disabled)

    def field(self, x, y, w, label, value, error=None, placeholder=False, select=False):
        self.text(x, y, label, 12, MUTED)
        self.rect(x, y + 6, w, 38, "#fff", ERR if error else LINE, 6, 2 if error else 1.5)
        self.text(x + 12, y + 31, value, 14, MUTED if placeholder else INK)
        if select:
            self.text(x + w - 14, y + 31, "▾", 14, MUTED, anchor="end")
        if error:
            self.text(x, y + 62, error, 11, ERR)

    def callout(self, x, y, n):
        self.circle(x, y, 11, NOTE, NOTE)
        self.text(x, y + 4.5, str(n), 12, "#fff", bold=True, anchor="middle")

    def phone(self, x, y, title, w=375, h=812):
        self.text(x, y - 12, title, 14, MUTED, bold=True)
        self.rect(x, y, w, h, "#fff", "#333", 22, 2.5)
        self.text(x + 24, y + 20, "9:41", 11, MUTED, bold=True)
        self.text(x + w - 24, y + 20, "▮▮▮ 🔋", 10, MUTED, anchor="end")

    def notes(self, x, y, items, width=360, title="Ghi chú"):
        self.text(x, y, title, 15, INK, bold=True)
        cy = y + 30
        for n, main, ref in items:
            self.callout(x + 11, cy - 4, n)
            lines = wrap(main, int(width / 7.3))
            for i, ln in enumerate(lines):
                self.text(x + 30, cy + i * 18, ln, 13, INK)
            cy += len(lines) * 18
            self.text(x + 30, cy + 2, ref, 11, NOTE, bold=True)
            cy += 34
        return cy

    def save(self, name):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n' + "\n".join(self.items) + "\n</svg>\n"
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print("saved", path)


def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return lines


def header(s, ox, oy, title=None, back=False, cart=2):
    y = oy + 34
    s.line(ox, oy + 84, ox + 375, oy + 84, "#E0E0E0", 1)
    if back:
        s.text(ox + 18, y + 30, "‹", 28, INK)
        s.text(ox + 44, y + 27, title, 16, INK, bold=True)
    else:
        s.rect(ox + 16, y + 8, 120, 30, FILL, LINE, 4)
        s.text(ox + 76, y + 28, "SPORT SHOP", 13, INK, bold=True, anchor="middle")
        s.circle(ox + 300, y + 21, 9, "#fff", INK, 2)
        s.line(ox + 307, y + 28, ox + 314, y + 35, INK, 2)
    if cart is not None:
        s.rect(ox + 333, y + 11, 22, 20, "#fff", INK, 3, 2)
        s.line(ox + 338, y + 11, ox + 338, y + 6, INK, 2)
        s.line(ox + 350, y + 11, ox + 350, y + 6, INK, 2)
        s.line(ox + 338, y + 6, ox + 350, y + 6, INK, 2)
        if cart:
            s.circle(ox + 357, y + 10, 9, "#333", "#333")
            s.text(ox + 357, y + 14, str(cart), 11, "#fff", bold=True, anchor="middle")


def stepper(s, x, y, val, plus_disabled=False):
    s.rect(x, y, 96, 30, "#fff", LINE, 6)
    s.text(x + 16, y + 21, "−", 16, INK, anchor="middle")
    s.text(x + 48, y + 20, str(val), 14, INK, bold=True, anchor="middle")
    s.text(x + 80, y + 21, "+", 16, "#C8C8C8" if plus_disabled else INK, anchor="middle")
    s.line(x + 32, y, x + 32, y + 30, "#E0E0E0", 1)
    s.line(x + 64, y, x + 64, y + 30, "#E0E0E0", 1)


# =====================================================================
# 01 · Danh sách sản phẩm
# =====================================================================
s = SVG(860, 910, "01 · Danh sách sản phẩm — mobile 375px")
ox, oy = 20, 70
s.phone(ox, oy, "Trạng thái chính")
header(s, ox, oy)
s.callout(ox + 290, oy + 30, 1)

chips = [("Tất cả", True), ("Áo", False), ("Quần", False), ("Giày", False), ("Phụ kiện", False), ("Dụng cụ", False)]
s.add(f'<defs><clipPath id="chipclip"><rect x="{ox + 2}" y="{oy + 92}" width="371" height="44"/></clipPath></defs><g clip-path="url(#chipclip)">')
cx = ox + 16
for label, sel in chips:
    w = len(label) * 8 + 28
    s.rect(cx, oy + 98, w, 32, "#333" if sel else "#fff", "#333" if sel else LINE, 16)
    s.text(cx + w / 2, oy + 119, label, 13, "#fff" if sel else INK, bold=sel, anchor="middle")
    cx += w + 8
s.add(f'<rect x="{ox + 330}" y="{oy + 96}" width="45" height="36" fill="url(#fade)"/>')
s.add('<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient></defs></g>')
s.callout(ox + 8, oy + 90, 2)

s.button(ox + 16, oy + 144, 110, 34, "⚲  Lọc (1)", size=13)
s.button(ox + 189, oy + 144, 170, 34, "Sắp xếp: Mới nhất ▾", size=13)
s.callout(ox + 130, oy + 146, 3)
s.text(ox + 16, oy + 202, "Đang lọc: Chạy bộ · 24 sản phẩm", 12, MUTED)

cards = [
    ("Áo chạy bộ Dri-fit nam", "189.000 ₫", "219.000 ₫", "-14%", False),
    ("Quần short chạy bộ 2 lớp", "189.000 ₫", None, None, False),
    ("Giày chạy bộ đế êm", "690.000 ₫", None, None, True),
    ("Tất chạy bộ cổ ngắn", "Từ 79.000 ₫", None, None, False),
]
for i, (name, price, old, badge, sold_out) in enumerate(cards):
    cxx = ox + 16 + (i % 2) * 177
    cyy = oy + 216 + (i // 2) * 232
    s.img(cxx, cyy, 165, 165)
    if badge:
        s.rect(cxx + 8, cyy + 8, 44, 22, "#333", "#333", 4)
        s.text(cxx + 30, cyy + 24, badge, 12, "#fff", bold=True, anchor="middle")
    if sold_out:
        s.add(f'<rect x="{cxx}" y="{cyy}" width="165" height="165" rx="4" fill="#fff" fill-opacity="0.6"/>')
        s.rect(cxx + 37, cyy + 68, 90, 28, "#fff", INK, 14, 1.5)
        s.text(cxx + 82, cyy + 87, "Hết hàng", 13, INK, bold=True, anchor="middle")
    s.text(cxx, cyy + 186, name, 13, MUTED if sold_out else INK)
    s.text(cxx, cyy + 208, price, 15, MUTED if sold_out else INK, bold=True)
    if old:
        s.text(cxx + 88, cyy + 208, old, 12, MUTED, strike=True)
s.callout(ox + 168, oy + 368, 4)
s.callout(ox + 360, oy + 452, 5)

px = ox + 70
for i, p in enumerate(["‹", "1", "2", "3", "…", "5", "›"]):
    sel = p == "1"
    s.rect(px + i * 34, oy + 694, 28, 30, "#333" if sel else "#fff", "#333" if sel else LINE, 6)
    s.text(px + i * 34 + 14, oy + 714, p, 13, "#fff" if sel else INK, bold=sel, anchor="middle")
s.callout(ox + 52, oy + 706, 6)
s.text(ox + 187, oy + 760, "12 sản phẩm / trang", 11, MUTED, anchor="middle")

nx = 430
end = s.notes(nx, 90, [
    (1, "Biểu tượng giỏ hàng kèm số món đang có trong giỏ", "US-05"),
    (2, "Danh mục cuộn ngang; mục đang chọn tô đậm", "US-01 · API #1"),
    (3, "Lọc theo môn thể thao, khoảng giá; sắp xếp mới nhất / giá tăng / giá giảm. Điều kiện lọc nằm trên URL để gửi link cho bạn bè", "US-04 · API #2"),
    (4, "Có khuyến mãi: giá bán + giá gốc gạch ngang + nhãn % giảm", "US-01"),
    (5, "Hết hàng ở mọi size: vẫn hiện, ảnh mờ, nhãn “Hết hàng”", "US-01"),
    (6, "Phân trang, 12 sản phẩm mỗi trang", "US-01"),
    (7, "Không có kết quả: thông báo + gợi ý sản phẩm (hình 1b)", "US-04"),
], width=390)
# 1b — không có kết quả
bx, by = nx, end + 6
s.text(bx, by, "1b · Không có kết quả", 14, MUTED, bold=True)
s.rect(bx, by + 10, 400, 200, "#fff", "#333", 14, 2)
s.callout(bx + 388, by + 12, 7)
s.circle(bx + 200, by + 50, 16, "#fff", MUTED, 2)
s.line(bx + 211, by + 61, bx + 220, by + 70, MUTED, 2)
s.text(bx + 200, by + 98, "Không tìm thấy sản phẩm cho “áo bóng rổ”", 13, INK, anchor="middle")
s.text(bx + 20, by + 128, "Có thể bạn thích", 12, MUTED, bold=True)
for i in range(3):
    s.img(bx + 20 + i * 124, by + 138, 112, 58)
s.save("01-danh-sach-san-pham.svg")

# =====================================================================
# 02 · Chi tiết sản phẩm
# =====================================================================
s = SVG(860, 910, "02 · Chi tiết sản phẩm — mobile 375px")
ox, oy = 20, 70
s.phone(ox, oy, "Đã chọn màu Đen, size S")
header(s, ox, oy, "Quần legging nữ cạp cao", back=True)
s.img(ox, oy + 85, 375, 330)
s.rect(ox + 315, oy + 97, 48, 22, "#333", "#333", 11)
s.text(ox + 339, oy + 112, "1 / 5", 11, "#fff", bold=True, anchor="middle")
for i in range(5):
    s.circle(ox + 159 + i * 14, oy + 432, 4, "#333" if i == 0 else "#D0D0D0", "#333" if i == 0 else "#D0D0D0")
s.callout(ox + 20, oy + 100, 1)

s.text(ox + 16, oy + 470, "Quần legging nữ cạp cao", 18, INK, bold=True)
s.text(ox + 16, oy + 500, "189.000 ₫", 20, INK, bold=True)
s.text(ox + 125, oy + 499, "219.000 ₫", 14, MUTED, strike=True)
s.rect(ox + 205, oy + 484, 44, 22, "#333", "#333", 4)
s.text(ox + 227, oy + 499, "-14%", 12, "#fff", bold=True, anchor="middle")

s.text(ox + 16, oy + 534, "Màu sắc: Đen", 13, INK, bold=True)
for i, c in enumerate(["#333", "#8D6E63", "#689F38"]):
    s.circle(ox + 32 + i * 44, oy + 562, 15, c, "#fff", 3)
    if i == 0:
        s.circle(ox + 32, oy + 562, 19, "none", INK, 2)
s.callout(ox + 168, oy + 562, 2)

s.text(ox + 16, oy + 604, "Size", 13, INK, bold=True)
s.text(ox + 359, oy + 604, "Bảng size ›", 13, INK, anchor="end")
s.add(f'<line x1="{ox + 287}" y1="{oy + 607}" x2="{ox + 359}" y2="{oy + 607}" stroke="{INK}" stroke-width="1"/>')
s.callout(ox + 280, oy + 586, 3)
for i, (sz, state) in enumerate([("S", "sel"), ("M", ""), ("L", "off"), ("XL", "")]):
    bx = ox + 16 + i * 66
    if state == "sel":
        s.button(bx, oy + 616, 56, 40, sz, primary=True)
    else:
        s.button(bx, oy + 616, 56, 40, sz, disabled=(state == "off"))
s.callout(ox + 190, oy + 616, 4)
s.text(ox + 16, oy + 684, "Chỉ còn 3 sản phẩm", 13, ERR, bold=True)
s.callout(ox + 160, oy + 680, 5)

s.line(ox, oy + 700, ox + 375, oy + 700, "#E0E0E0", 1)
s.text(ox + 16, oy + 724, "Mô tả sản phẩm", 13, INK, bold=True)
s.text(ox + 359, oy + 724, "▾", 13, MUTED, anchor="end")

s.rect(ox + 1, oy + 742, 373, 68, "#fff", "#E0E0E0", 0, 1)
stepper(s, ox + 16, oy + 761, 1)
s.button(ox + 124, oy + 756, 235, 42, "Thêm vào giỏ", primary=True)
s.callout(ox + 362, oy + 752, 6)

nx = 430
end = s.notes(nx, 90, [
    (1, "Ảnh vuốt ngang, tối đa 8 ảnh; số thứ tự + chấm vị trí", "US-03 · API #3"),
    (2, "Chọn màu; màu đang chọn có viền", "US-03"),
    (3, "“Bảng size” mở popup (hình 2b)", "US-03"),
    (4, "Size hết hàng hiện mờ, gạch ngang, không bấm được (size L)", "US-03"),
    (5, "Còn ≤ 5 sản phẩm thì hiện “Chỉ còn N sản phẩm”", "US-03"),
    (6, "Thanh dưới ghim cố định. “Thêm vào giỏ” chỉ bấm được khi đã chọn đủ màu + size; số lượng không vượt tồn kho", "US-03 · US-05"),
    (7, "Không vẽ: chia sẻ link lên Facebook/Zalo phải hiện đúng ảnh, tên, giá → thẻ Open Graph trong <head>", "US-03"),
], width=390)
bx, by = nx, end + 6
s.text(bx, by, "2b · Popup bảng size", 14, MUTED, bold=True)
s.rect(bx, by + 10, 400, 190, "#fff", "#333", 14, 2)
s.text(bx + 20, by + 42, "Bảng size — Quần legging nữ", 14, INK, bold=True)
s.text(bx + 380, by + 42, "✕", 14, MUTED, anchor="end")
cols = ["Size", "Chiều cao (cm)", "Cân nặng (kg)", "Vòng eo (cm)"]
rows = [["S", "150–158", "42–48", "60–66"], ["M", "158–165", "48–55", "66–72"], ["L", "163–170", "55–62", "72–78"], ["XL", "168–175", "62–70", "78–84"]]
for j, c in enumerate(cols):
    s.text(bx + 20 + j * 95, by + 72, c, 11, MUTED, bold=True)
for i, r in enumerate(rows):
    s.line(bx + 20, by + 80 + i * 26, bx + 380, by + 80 + i * 26, "#E0E0E0", 1)
    for j, c in enumerate(r):
        s.text(bx + 20 + j * 95, by + 98 + i * 26, c, 12, INK, bold=(j == 0))
s.save("02-chi-tiet-san-pham.svg")

# =====================================================================
# 03 · Giỏ hàng → Đặt hàng → Thanh toán
# =====================================================================
s = SVG(1270, 1250, "03 · Giỏ hàng → Đặt hàng → Thanh toán — mobile 375px")
# ---- 3a giỏ hàng
ox, oy = 20, 70
s.phone(ox, oy, "3a · Giỏ hàng")
header(s, ox, oy, "Giỏ hàng (3)", back=True, cart=None)
s.rect(ox + 12, oy + 96, 351, 54, "#fff", ERR, 8, 1.5)
s.text(ox + 26, oy + 118, "⚠ “Quần legging nữ” đã giảm giá:", 12, ERR, bold=True)
s.text(ox + 26, oy + 138, "219.000 ₫ → 189.000 ₫", 12, ERR)
s.callout(ox + 360, oy + 98, 1)
items = [
    ("Áo chạy bộ Dri-fit nam", "Size M · Đen", "438.000 ₫", 2, True, "Còn 2 sản phẩm"),
    ("Quần legging nữ cạp cao", "Size S · Đen", "189.000 ₫", 1, False, None),
    ("Tất thể thao cổ trung", "Freesize · Trắng", "79.000 ₫", 1, False, None),
]
for i, (name, var, price, q, maxed, hint) in enumerate(items):
    iy = oy + 166 + i * 108
    s.img(ox + 16, iy, 72, 72)
    s.text(ox + 100, iy + 16, name, 13, INK, bold=True)
    s.text(ox + 100, iy + 36, var, 12, MUTED)
    s.text(ox + 100, iy + 58, price, 14, INK, bold=True)
    stepper(s, ox + 100, iy + 66, q, plus_disabled=maxed)
    if hint:
        s.text(ox + 206, iy + 86, hint, 11, ERR)
    s.text(ox + 352, iy + 16, "🗑", 14, MUTED, anchor="end")
    s.line(ox + 16, iy + 104, ox + 359, iy + 104, "#EEEEEE", 1)
s.callout(ox + 300, oy + 252, 2)
s.text(ox + 16, oy + 512, "Mua thêm 94.000 ₫ để được miễn phí ship", 13, INK, bold=True)
s.rect(ox + 16, oy + 522, 343, 8, FILL, FILL, 4)
s.rect(ox + 16, oy + 522, 303, 8, "#333", "#333", 4)
s.callout(ox + 360, oy + 508, 3)
for i, (k, v) in enumerate([("Tạm tính", "706.000 ₫"), ("Phí ship", "30.000 ₫")]):
    s.text(ox + 16, oy + 568 + i * 26, k, 13, MUTED)
    s.text(ox + 359, oy + 568 + i * 26, v, 13, INK, anchor="end")
s.rect(ox + 1, oy + 730, 373, 80, "#fff", "#E0E0E0", 0, 1)
s.text(ox + 16, oy + 760, "Tổng cộng", 12, MUTED)
s.text(ox + 16, oy + 784, "736.000 ₫", 18, INK, bold=True)
s.button(ox + 150, oy + 748, 209, 44, "Tiến hành đặt hàng", primary=True)

# ---- 3b đặt hàng
ox = 435
s.phone(ox, oy, "3b · Đặt hàng — có lỗi nhập liệu")
header(s, ox, oy, "Đặt hàng", back=True, cart=None)
s.text(ox + 16, oy + 112, "Thông tin nhận hàng", 14, INK, bold=True)
s.field(ox + 16, oy + 136, 343, "Họ tên *", "Nguyễn Văn An")
s.field(ox + 16, oy + 196, 343, "Số điện thoại *", "091234567", error="Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0")
s.callout(ox + 360, oy + 208, 1)
s.field(ox + 16, oy + 284, 166, "Tỉnh/thành *", "Hà Nội", select=True)
s.field(ox + 193, oy + 284, 166, "Phường/xã *", "Phường Láng", select=True)
s.callout(ox + 360, oy + 296, 2)
s.field(ox + 16, oy + 344, 343, "Địa chỉ *", "Số 1, ngõ 2")
s.field(ox + 16, oy + 404, 343, "Ghi chú", "Giao giờ hành chính…", placeholder=True)
s.text(ox + 16, oy + 482, "Thanh toán", 14, INK, bold=True)
for i, (lab, sub, sel) in enumerate([("Chuyển khoản", "Quét mã VietQR", True), ("COD", "Trả tiền khi nhận hàng", False)]):
    yy = oy + 494 + i * 56
    s.rect(ox + 16, yy, 343, 48, "#fff", INK if sel else LINE, 8, 2 if sel else 1.5)
    s.circle(ox + 38, yy + 24, 8, "#fff", INK, 2)
    if sel:
        s.circle(ox + 38, yy + 24, 4, INK, INK)
    s.text(ox + 56, yy + 21, lab, 13, INK, bold=True)
    s.text(ox + 56, yy + 38, sub, 11, MUTED)
s.callout(ox + 360, oy + 496, 3)
s.text(ox + 16, oy + 630, "3 sản phẩm", 13, MUTED)
s.text(ox + 359, oy + 630, "706.000 ₫", 13, INK, anchor="end")
s.text(ox + 16, oy + 654, "Phí ship", 13, MUTED)
s.text(ox + 359, oy + 654, "30.000 ₫", 13, INK, anchor="end")
s.text(ox + 16, oy + 684, "Tổng cộng", 14, INK, bold=True)
s.text(ox + 359, oy + 684, "736.000 ₫", 16, INK, bold=True, anchor="end")
s.rect(ox + 1, oy + 730, 373, 80, "#fff", "#E0E0E0", 0, 1)
s.button(ox + 16, oy + 748, 343, 44, "Đặt hàng", primary=True)
s.callout(ox + 360, oy + 746, 4)

# ---- 3c thanh toán
ox = 850
s.phone(ox, oy, "3c · Thanh toán VietQR")
header(s, ox, oy, "Thanh toán · SP261201-K7QX", back=True, cart=None)
s.rect(ox + 66, oy + 98, 243, 34, FILL, LINE, 17)
s.text(ox + 187, oy + 120, "⏳ Đang chờ thanh toán…", 13, INK, bold=True, anchor="middle")
s.text(ox + 187, oy + 150, "Trang tự cập nhật khi nhận được tiền", 11, MUTED, anchor="middle")
s.callout(ox + 312, oy + 100, 1)
s.rect(ox + 87, oy + 164, 200, 200, "#fff", INK, 4, 2)
for r in range(9):
    for c in range(9):
        if (r * 7 + c * 3 + r * c) % 3 == 0 or (r < 3 and c < 3) or (r < 3 and c > 5) or (r > 5 and c < 3):
            s.add(f'<rect x="{ox + 97 + c * 20}" y="{oy + 174 + r * 20}" width="18" height="18" fill="#555"/>')
s.callout(ox + 290, oy + 166, 2)
info = [("Số tiền", "736.000 ₫", True), ("Nội dung", "SP261201-K7QX", True), ("Ngân hàng", "MB Bank", False), ("Số tài khoản", "0123456789", True), ("Chủ tài khoản", "NGUYEN VAN A", False)]
for i, (k, v, copy) in enumerate(info):
    yy = oy + 396 + i * 40
    s.text(ox + 16, yy, k, 12, MUTED)
    s.text(ox + 120, yy, v, 14, INK, bold=True)
    if copy:
        s.rect(ox + 289, yy - 18, 70, 26, "#fff", LINE, 6)
        s.text(ox + 324, yy, "Sao chép", 11, INK, anchor="middle")
    s.line(ox + 16, yy + 14, ox + 359, yy + 14, "#EEEEEE", 1)
s.callout(ox + 362, oy + 380, 3)
s.text(ox + 187, oy + 610, "Hạn thanh toán: 10:02 ngày 02/12 (còn 23:41:05)", 12, INK, anchor="middle")
s.callout(ox + 18, oy + 606, 4)
s.text(ox + 16, oy + 646, "Khi nhận đủ tiền:", 11, MUTED, bold=True)
s.rect(ox + 16, oy + 656, 343, 60, "#fff", INK, 8, 2)
s.text(ox + 187, oy + 680, "✅ Đã nhận đủ 736.000 ₫", 14, INK, bold=True, anchor="middle")
s.text(ox + 187, oy + 702, "Đơn hàng đang chờ shop xác nhận", 12, MUTED, anchor="middle")
s.callout(ox + 360, oy + 658, 5)
s.button(ox + 16, oy + 748, 343, 44, "Tra cứu đơn hàng")

notes_a = [
    (1, "Báo món đã đổi giá / hết hàng khi mở giỏ (gọi API kiểm tra lại)", "US-05 · API #4"),
    (2, "Nút + bị khóa khi đạt tồn kho; xóa món bằng 🗑", "US-05"),
    (3, "Thanh tiến độ miễn phí ship; ngưỡng do admin cấu hình", "US-06 · API #5"),
]
notes_b = [
    (1, "Lỗi hiện ngay dưới ô sai, chữ đỏ, viền đỏ", "US-06"),
    (2, "Địa chỉ 2 cấp: Tỉnh/thành → Phường/xã", "US-06"),
    (3, "Chọn Chuyển khoản hoặc COD", "US-06"),
    (4, "Bấm xong nút bị khóa + “Đang xử lý…” → chống tạo 2 đơn (kèm Idempotency-Key)", "US-06 · API #6"),
]
notes_c = [
    (1, "Hỏi trạng thái mỗi 5 giây, dừng khi đã nhận tiền", "US-07 · API #7"),
    (2, "Mã VietQR có sẵn số tiền + nội dung = mã đơn", "US-07"),
    (3, "Nút sao chép cho từng thông tin", "US-07"),
    (4, "Đếm ngược hạn thanh toán 24 giờ", "US-07"),
    (5, "Trạng thái sau khi webhook báo nhận đủ tiền", "US-07"),
]
s.notes(20, 920, notes_a, width=360, title="Ghi chú 3a")
s.notes(435, 920, notes_b, width=360, title="Ghi chú 3b")
s.notes(850, 920, notes_c, width=360, title="Ghi chú 3c")
s.save("03-gio-hang-dat-hang-thanh-toan.svg")

# =====================================================================
# 04 · Admin quản lý đơn
# =====================================================================
s = SVG(1320, 1230, "04 · Admin — Quản lý đơn hàng — desktop 1280px")
ox, oy = 20, 60
s.rect(ox, oy, 1280, 800, "#fff", "#333", 10, 2.5)
s.rect(ox, oy, 210, 800, FILL, FILL, 10, 0)
s.line(ox + 210, oy, ox + 210, oy + 800, "#E0E0E0", 1)
s.text(ox + 20, oy + 40, "SPORT SHOP", 15, INK, bold=True)
s.text(ox + 20, oy + 58, "Quản trị", 11, MUTED)
for i, m in enumerate(["Đơn hàng", "Sản phẩm", "Kho", "Thống kê", "Cài đặt"]):
    yy = oy + 96 + i * 44
    if i == 0:
        s.rect(ox + 12, yy - 24, 186, 36, "#333", "#333", 6)
    s.text(ox + 28, yy, m, 14, "#fff" if i == 0 else INK, bold=(i == 0))
s.line(ox + 12, oy + 730, ox + 198, oy + 730, "#DADADA", 1)
s.text(ox + 20, oy + 756, "Trần Thị Bình", 13, INK, bold=True)
s.text(ox + 20, oy + 776, "STAFF · Đăng xuất", 11, MUTED)

mx = ox + 230
s.text(mx, oy + 44, "Đơn hàng", 22, INK, bold=True)
tabs = [("Tất cả", 128), ("Chờ thanh toán", 4), ("Cần xử lý", 1), ("Chờ xác nhận", 5), ("Đang giao", 12), ("Đang hoàn hàng", 2), ("Hoàn thành", 98), ("Đã hủy", 6)]
tx = mx
for i, (t, n) in enumerate(tabs):
    lab = f"{t} ({n})"
    w = len(lab) * 7 + 22
    sel = t == "Đang giao"
    s.text(tx + w / 2, oy + 88, lab, 12, ERR if t == "Cần xử lý" else INK, bold=sel or t == "Cần xử lý", anchor="middle")
    if sel:
        s.line(tx + 4, oy + 98, tx + w - 4, oy + 98, INK, 3)
    tx += w + 4
s.line(mx, oy + 100, ox + 1260, oy + 100, "#E0E0E0", 1)
s.callout(mx - 8, oy + 70, 1)

s.rect(mx, oy + 116, 300, 36, "#fff", LINE, 6)
s.text(mx + 12, oy + 139, "⚲  Tìm mã đơn hoặc SĐT…", 13, MUTED)
s.rect(mx + 312, oy + 116, 220, 36, "#fff", LINE, 6)
s.text(mx + 324, oy + 139, "01/12/2026 – 07/12/2026  ▾", 13, INK)
s.callout(mx + 538, oy + 118, 2)

# bảng
tw = 600
cols = [("Mã đơn", 0), ("Thời gian", 125), ("Khách", 240), ("Tổng tiền", 370), ("Trạng thái", 470)]
s.rect(mx, oy + 168, tw, 36, FILL, FILL, 0, 0)
for c, dx in cols:
    s.text(mx + 12 + dx, oy + 191, c, 12, MUTED, bold=True)
rows = [
    ("SP261207-M3TP", "07/12 09:41", "Lê Minh", "0987 654 321", "459.000 ₫"),
    ("SP261206-Q8ZA", "06/12 21:15", "Phạm Hà", "0903 111 222", "1.038.000 ₫"),
    ("SP261201-K7QX", "01/12 10:02", "Nguyễn Văn An", "0912 345 678", "736.000 ₫"),
    ("SP261130-B4WD", "30/11 16:20", "Đỗ Thu", "0978 000 111", "298.000 ₫"),
    ("SP261129-H2NR", "29/11 08:05", "Vũ Nam", "0966 222 333", "189.000 ₫"),
    ("SP261128-T9KE", "28/11 19:47", "Hoàng Lan", "0915 444 555", "627.000 ₫"),
    ("SP261127-C6YU", "27/11 11:30", "Bùi Đức", "0934 666 777", "79.000 ₫"),
]
for i, (code, t, name, phone, total) in enumerate(rows):
    ry = oy + 204 + i * 56
    if code == "SP261201-K7QX":
        s.rect(mx, ry, tw, 56, "#EDEDED", "#EDEDED", 0, 0)
    s.text(mx + 12, ry + 33, code, 13, INK, bold=True)
    s.text(mx + 137, ry + 33, t, 12, INK)
    s.text(mx + 252, ry + 26, name, 12, INK)
    s.text(mx + 252, ry + 44, phone, 11, MUTED)
    s.text(mx + 382, ry + 33, total, 12, INK, bold=True)
    s.rect(mx + 482, ry + 16, 82, 24, "#fff", INK, 12, 1.2)
    s.text(mx + 523, ry + 32, "Đang giao", 11, INK, anchor="middle")
    s.line(mx, ry + 56, mx + tw, ry + 56, "#EEEEEE", 1)
s.callout(mx + tw + 2, oy + 186, 3)
s.text(mx, oy + 630, "Hiển thị 1–20 / 128 đơn · mới nhất trên cùng", 12, MUTED)
for i, p in enumerate(["‹", "1", "2", "3", "…", "7", "›"]):
    sel = p == "1"
    s.rect(mx + 360 + i * 34, oy + 612, 28, 28, "#333" if sel else "#fff", "#333" if sel else LINE, 6)
    s.text(mx + 374 + i * 34, oy + 631, p, 12, "#fff" if sel else INK, bold=sel, anchor="middle")

# drawer chi tiết
dx0, dw = ox + 860, 420
s.rect(dx0, oy, dw, 800, "#fff", "#333", 0, 1.5)
s.text(dx0 + 20, oy + 38, "SP261201-K7QX", 18, INK, bold=True)
s.text(dx0 + dw - 20, oy + 38, "✕", 16, MUTED, anchor="end")
s.rect(dx0 + 20, oy + 52, 90, 24, "#fff", INK, 12, 1.2)
s.text(dx0 + 65, oy + 68, "Đang giao", 11, INK, anchor="middle")
s.callout(dx0 + dw - 16, oy + 92, 4)

def sec(y, title):
    s.text(dx0 + 20, y, title, 12, MUTED, bold=True)
    s.line(dx0 + 20, y + 8, dx0 + dw - 20, y + 8, "#EEEEEE", 1)

sec(oy + 104, "KHÁCH HÀNG")
s.text(dx0 + 20, oy + 130, "Nguyễn Văn An · 0912 345 678", 13, INK)
s.text(dx0 + 20, oy + 150, "Số 1, ngõ 2, Phường Láng, Hà Nội", 13, INK)
sec(oy + 182, "SẢN PHẨM (giá lúc mua)")
prod = [("Áo chạy bộ Dri-fit nam · M · Đen", "2 × 219.000"), ("Quần legging nữ · S · Đen", "1 × 189.000"), ("Tất thể thao · Freesize · Trắng", "1 × 79.000")]
for i, (p, q) in enumerate(prod):
    s.text(dx0 + 20, oy + 208 + i * 22, p, 12, INK)
    s.text(dx0 + dw - 20, oy + 208 + i * 22, q, 12, INK, anchor="end")
s.text(dx0 + 20, oy + 282, "Phí ship 30.000 · Tổng 736.000 ₫", 13, INK, bold=True)
sec(oy + 314, "THANH TOÁN")
s.text(dx0 + 20, oy + 340, "Chuyển khoản · Đã nhận 736.000 ₫", 13, INK)
s.text(dx0 + 20, oy + 360, "SePay · mã GD FT2633512345 · 01/12 10:15", 11, MUTED)
sec(oy + 392, "LỊCH SỬ TRẠNG THÁI")
hist = [("01/12 10:02", "Tạo đơn → Chờ thanh toán", "Khách"), ("01/12 10:15", "→ Chờ xác nhận (nhận đủ tiền)", "Hệ thống"), ("01/12 14:30", "→ Đang giao", "Trần Thị Bình")]
for i, (t, e, who) in enumerate(hist):
    yy = oy + 420 + i * 44
    s.circle(dx0 + 28, yy - 4, 5, INK if i == 2 else "#fff", INK, 2)
    if i < 2:
        s.line(dx0 + 28, yy + 1, dx0 + 28, yy + 35, LINE, 1.5)
    s.text(dx0 + 44, yy, e, 12, INK, bold=(i == 2))
    s.text(dx0 + 44, yy + 17, f"{t} · {who}", 11, MUTED)
s.rect(dx0, oy + 700, dw, 100, FILL, FILL, 0, 0)
s.text(dx0 + 20, oy + 724, "Chuyển trạng thái", 12, MUTED, bold=True)
s.button(dx0 + 20, oy + 736, 180, 42, "Hoàn thành", primary=True)
s.button(dx0 + 212, oy + 736, 188, 42, "Đang hoàn hàng")
s.callout(dx0 + dw - 14, oy + 714, 5)

end = s.notes(20, 905, [
    (1, "Tab theo trạng thái kèm số lượng; “Cần xử lý” tô đỏ để không bị bỏ sót", "US-12 · API #28"),
    (2, "Tìm theo mã đơn / SĐT; lọc khoảng ngày", "US-12"),
    (3, "Đơn mới nhất trên cùng, 20 đơn/trang; bấm một dòng để mở chi tiết bên phải", "US-12"),
    (4, "Chi tiết: khách, sản phẩm theo giá lúc mua, giao dịch tiền, dòng thời gian (ai đổi, lúc nào)", "US-12 · US-02 · API #29"),
], width=560)
s.notes(660, 905, [
    (5, "Chỉ hiện nút chuyển hợp lệ theo sơ đồ: đơn Đang giao → Hoàn thành / Đang hoàn hàng (không có nút Hủy)", "US-02 · API #30"),
    (6, "Hủy đơn (ở trạng thái cho phép) bắt buộc nhập lý do — hình 4b; đơn đã nhận tiền thì ghi nhận hoàn tiền", "US-02 · API #30, #31"),
], width=300)
bx, by = 1000, 905
s.text(bx, by, "4b · Popup hủy đơn", 14, MUTED, bold=True)
s.rect(bx, by + 12, 300, 210, "#fff", "#333", 10, 2)
s.callout(bx + 290, by + 14, 6)
s.text(bx + 18, by + 42, "Hủy đơn SP261206-Q8ZA?", 14, INK, bold=True)
s.text(bx + 18, by + 64, "Tồn kho sẽ được cộng lại.", 12, MUTED)
s.text(bx + 18, by + 90, "Lý do hủy *", 12, MUTED)
s.rect(bx + 18, by + 98, 264, 56, "#fff", LINE, 6)
s.text(bx + 30, by + 120, "Khách đổi ý, báo qua Messenger", 12, INK)
s.button(bx + 18, by + 168, 120, 38, "Quay lại")
s.button(bx + 150, by + 168, 132, 38, "Xác nhận hủy", primary=True)
s.save("04-admin-quan-ly-don.svg")
