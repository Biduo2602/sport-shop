import { calcTotal, getUnitPrice, type CartItem, type Product } from "./cart";

// ----- Dữ liệu kiểm tra -----
const ao: Product = { id: "1", name: "Áo chạy bộ Dri-fit", price: 219000 };
const legging: Product = { id: "2", name: "Quần legging", price: 219000, salePrice: 189000 };
const tat: Product = { id: "3", name: "Tất thể thao", price: 79000 };
const quaTang: Product = { id: "4", name: "Quà tặng", price: 50000, salePrice: 0 };

const cart: CartItem[] = [
  { product: ao, size: "M", quantity: 2 },
  { product: legging, size: "S", quantity: 1 },
  { product: tat, size: "L", quantity: 3 },
];

// ----- Hàm hỗ trợ in kết quả -----
let passed = 0;
let failed = 0;

function expectEqual(label: string, actual: unknown, expected: unknown): void {
  if (actual === expected) {
    passed++;
    console.log(`✅ ${label} → ${actual}`);
  } else {
    failed++;
    console.log(`❌ ${label} → ${actual} (mong đợi ${expected})`);
  }
}

function expectThrow(label: string, fn: () => unknown): void {
  try {
    const result = fn();
    failed++;
    console.log(`❌ ${label} → không ném lỗi, trả về ${result}`);
  } catch (e) {
    passed++;
    console.log(`✅ ${label} → ném lỗi: ${(e as Error).message}`);
  }
}

// ----- Theo đề bài -----
console.log("--- Theo đề bài");
expectEqual("calcTotal(cart)", calcTotal(cart), 864000);
expectEqual("calcTotal(cart, 10)", calcTotal(cart, 10), 777600);
expectEqual("calcTotal(cart, 15)", calcTotal(cart, 15), 734400);
expectEqual("calcTotal([], 10)", calcTotal([], 10), 0);
expectThrow("quantity = 0", () => calcTotal([{ product: tat, size: "L", quantity: 0 }]));
expectThrow("discount = 120", () => calcTotal(cart, 120));

// ----- getUnitPrice -----
console.log("--- getUnitPrice");
expectEqual("có khuyến mãi", getUnitPrice(legging), 189000);
expectEqual("không khuyến mãi", getUnitPrice(ao), 219000);
expectEqual("salePrice = 0 (quà tặng)", getUnitPrice(quaTang), 0);

// ----- Dữ liệu bất thường -----
console.log("--- Dữ liệu bất thường");
expectThrow("discount = NaN", () => calcTotal(cart, NaN));
expectThrow("discount = Infinity", () => calcTotal(cart, Infinity));
expectThrow("discount = -5", () => calcTotal(cart, -5));
expectThrow("quantity = NaN", () => calcTotal([{ product: tat, size: "L", quantity: NaN }]));
expectThrow("quantity = 1.5", () => calcTotal([{ product: tat, size: "L", quantity: 1.5 }]));
expectThrow("quantity = -1", () => calcTotal([{ product: tat, size: "L", quantity: -1 }]));

// ----- Biên -----
console.log("--- Giá trị biên");
expectEqual("discount = 0", calcTotal(cart, 0), 864000);
expectEqual("discount = 100", calcTotal(cart, 100), 0);
expectEqual("discount lẻ = 12.5", calcTotal(cart, 12.5), 756000);

console.log(`\nKết quả: ${passed} đạt, ${failed} lỗi`);
