export default function ProductCard() {
  return (
    <div className="p-8">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Product Image */}
        <div className="w-full md:w-64 h-64 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg">
          <span className="text-8xl">📱</span>
        </div>

        {/* Product Details */}
        <div className="flex-1">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">
            iPhone 15 Pro Max - 256GB
          </h2>
          
          <div className="text-4xl font-bold text-indigo-600 mb-3">
            29.990.000₫
          </div>

          <div className="flex items-center gap-2 mb-4">
            <div className="text-2xl text-yellow-400">
              ⭐⭐⭐⭐⭐
            </div>
            <span className="text-gray-600">
              (4.8/5 - 1,234 đánh giá)
            </span>
          </div>

          <div className="space-y-2 text-gray-700">
            <div className="flex items-center gap-2">
              <span className="font-semibold">🔥 Chip:</span>
              <span>A17 Pro - Hiệu năng vượt trội</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">📸 Camera:</span>
              <span>48MP - Chụp ảnh chuyên nghiệp</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">📱 Màn hình:</span>
              <span>Super Retina XDR 6.7 inch</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">⚡ Chất liệu:</span>
              <span>Khung Titanium - Siêu bền</span>
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <button className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition">
              Mua ngay
            </button>
            <button className="px-6 py-3 border-2 border-indigo-600 text-indigo-600 rounded-xl font-semibold hover:bg-indigo-50 transition">
              Thêm vào giỏ
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

