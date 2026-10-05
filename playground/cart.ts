export type Size = "S" | "M" | "L" | "XL";

export interface Product {
  id: string;
  name: string;
  price: number;
  salePrice?: number;
}

export interface CartItem {
  product: Product;
  quantity: number;
  size: Size;
}

export function getUnitPrice(product: Product): number {
  return product.salePrice ?? product.price;
}

export function calcTotal(items: CartItem[], discountPercent: number = 0): number {
  // Chỉ chấp nhận giá trị chắc chắn hợp lệ: Number.isFinite loại cả NaN và Infinity
  if (!Number.isFinite(discountPercent) || discountPercent < 0 || discountPercent > 100) {
    throw new Error("Phần trăm giảm giá phải nằm trong khoảng từ 0 đến 100.");
  }

  const subtotal = items.reduce((total, item) => {
    // Number.isInteger loại cả NaN, Infinity và số lẻ như 1.5
    if (!Number.isInteger(item.quantity) || item.quantity <= 0) {
      throw new Error(`Số lượng của sản phẩm "${item.product.name}" phải là số nguyên lớn hơn 0.`);
    }
    return total + getUnitPrice(item.product) * item.quantity;
  }, 0);

  // Nhân trước, chia sau để hạn chế sai số số thực; tiền VNĐ luôn làm tròn về số nguyên
  return Math.round((subtotal * (100 - discountPercent)) / 100);
}
