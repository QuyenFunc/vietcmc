import { useState } from 'react'

const TEST_COMMENTS = [
  // ===== CLEAN - Bình luận tích cực/ủng hộ =====
  "Bài viết rất hay và bổ ích! Cảm ơn tác giả đã chia sẻ 👍",
  "Video này thật tuyệt vời, đã subscribe kênh rồi! 🔥",
  "Cảm ơn bạn đã chia sẻ kinh nghiệm, rất hữu ích!",
  "Nội dung chất lượng, rất đáng để theo dõi ❤️",
  "Chúc mừng bạn, thành công xứng đáng! 🎉",
  "Like và share để nhiều người biết đến!",
  "Ủng hộ kênh, tiếp tục làm video nhé!",
  "Hay quá, chờ đợi phần tiếp theo!",
  "Đồng ý 100% với quan điểm này",
  "Bài viết rất sâu sắc và đầy cảm hứng",
  
  // ===== CLEAN - Thảo luận/góp ý xây dựng =====
  "Tôi nghĩ vấn đề này cần xem xét thêm góc độ khác",
  "Ý kiến hay nhưng cần thêm dữ liệu để chứng minh",
  "Tôi không hoàn toàn đồng ý, nhưng tôn trọng quan điểm của bạn",
  "Có thể bổ sung thêm ví dụ cụ thể sẽ rõ hơn",
  "Lập luận thú vị, tuy nhiên cần xem xét thêm khía cạnh X",
  "Bạn có thể chia sẻ nguồn tham khảo được không?",
  "Góc nhìn mới mẻ, nhưng thiếu phân tích sâu",
  "Video hay nhưng hơi dài, nên tóm gọn lại",
  
  // ===== CLEAN - Tranh luận/phê bình ý kiến (KHÔNG xúc phạm) =====
  "Ý kiến này không có cơ sở khoa học",
  "Lập luận này thiếu logic và mâu thuẫn",
  "Quan điểm này quá cực đoan và một chiều",
  "Thông tin này không chính xác, cần kiểm chứng",
  "Tôi hoàn toàn không đồng ý với nhận định này",
  "Phân tích này sai lầm ở nhiều điểm",
  
  // ===== CLEAN - Bình luận trung lập =====
  "Đã xem",
  "Cảm ơn đã chia sẻ",
  "Lưu lại xem sau",
  "Ok, noted",
  "Thú vị đấy",
  "Hmmm, để tôi suy nghĩ thêm",
  
  // ===== CLEAN - Hỏi đáp/tương tác =====
  "Bạn có thể làm video về chủ đề X không?",
  "Cho mình hỏi phần này ở phút mấy nhỉ?",
  "Link tham khảo ở đâu bạn ơi?",
  "Bạn dùng công cụ gì để làm video vậy?",
  "Có ai đồng ý với tôi không? 🤔",
  
  // ===== TOXIC - Xúc phạm cá nhân =====
  "Mày là thằng ngu ngốc, đần độn",
  "Đồ ngu như chó, biết gì đâu mà nói",
  "Thằng này ngu vãi, nói chuyện vớ vẩn",
  "Mày là đồ khốn nạn, đáng ghét",
  "Ngu người ra, đừng có comment nữa",
  "Đồ ngớ ngẩn, làm gì cũng sai",
  "Thằng ngu này không biết xấu hổ à?",
  "Mày ngu thế này còn dám tranh luận?",
  "Cái mồm mày nói toàn shit",
  "Đồ đần độn, bớt nói đi",
  
  // ===== TOXIC - Chửi thề thô tục =====
  "Cái quan điểm ngu si vãi lồn",
  "Đm, thằng này ngu quá",
  "Đồ chó đẻ, mẹ kiếp",
  "Đéo ai quan tâm ý kiến mày",
  "Cút đi đồ ngu, vcl",
  "Shit, ngu vãi đái",
  "Fuck off, đồ ngốc",
  
  // ===== HATE SPEECH - Phân biệt chủng tộc/dân tộc =====
  "Bọn người Việt nghèo nàn lạc hậu",
  "Người châu Phi thì kém văn minh",
  "Bọn Tàu đáng ghét, nên đuổi về nước",
  "Người da đen thấp kém, không nên tin",
  "Bọn dân tộc miền núi thì mất dạy",
  
  // ===== HATE SPEECH - Phân biệt giới tính =====
  "Đàn bà ngu ngốc, chỉ biết nói",
  "Phụ nữ thì không có não, đừng tranh luận",
  "Con gái không nên học IT, không đủ trí",
  "Đàn ông mới có tư duy logic, đàn bà thì thôi",
  
  // ===== HATE SPEECH - Kỳ thị LGBT =====
  "Bọn đồng tính là bệnh hoạn",
  "LGBT là tội lỗi, nên cấm",
  "Người chuyển giới thì bệnh tâm thần",
  "Bọn gay đáng bị khinh thường",
  
  // ===== HATE SPEECH - Kỳ thị tôn giáo =====
  "Tôn giáo X thì toàn khủng bố",
  "Người theo đạo Y thì lạc hậu",
  "Bọn vô thần thì vô đạo đức",
  
  // ===== HARASSMENT - Đe dọa bạo lực =====
  "Tao sẽ tìm mày và đánh cho một trận",
  "Đợi tao, tao sẽ giết mày",
  "Coi chừng kẻo tao cho mày một trận",
  "Mày đợi đấy, tao sẽ tìm đến nhà",
  "Sẽ cho mày biết tay, cẩn thận đi đường",
  
  // ===== HARASSMENT - Đe dọa doxxing/tung clip =====
  "Tao sẽ lộ địa chỉ nhà mày cho mọi người biết",
  "Cẩn thận kẻo tung clip mày lên mạng",
  "Tao có số điện thoại mày rồi, đợi đấy",
  "Sẽ public thông tin cá nhân của mày",
  
  // ===== HARASSMENT - Quấy rối tình dục =====
  "Gái xinh thế này chắc bú cu giỏi nhỉ",
  "Inbox với anh, anh cho em xem hàng",
  "Thân hình ngon quá, dm",
  "Nhìn mông to thế, chắc sướng lắm",
  
  // ===== SPAM - Quảng cáo/lừa đảo =====
  "Kiếm tiền online 10 triệu/ngày! Inbox ngay 📞📞📞",
  "Giảm cân SIÊU TỐC không cần ăn kiêng! Mua ngay! 💊",
  "🔥🔥 SALE SỐC 90% 🔥🔥 Click: http://scam.com",
  "Cần gái xinh phục vụ, lương cao! Zalo: 0xxx",
  "Thuốc tăng kích thước 5cm trong 1 tuần!!!",
  "Hack tài khoản FB chỉ 100k! Liên hệ ngay!",
  "💰💰 ĐẦU TƯ BITCOIN LỜI 200%/THÁNG 💰💰",
  
  // ===== SPAM - Link rác/virus =====
  "Click vào đây để nhận quà: http://virus.com 🎁🎁🎁",
  "Xem ảnh nóng của bạn tại đây: http://malware.net",
  "Bạn đã trúng 100 triệu! Click nhận: http://scam.vn",
  
  // ===== PII - Lộ thông tin cá nhân =====
  "Số điện thoại tôi là 0987654321, liên hệ nhé",
  "Email: myemail@gmail.com, add friend",
  "Địa chỉ nhà tôi là 123 Lê Lợi, Q1, TPHCM",
  "CCCD của tôi: 001234567890",
  "Tài khoản ngân hàng: Vietcombank 1234567890",
  
  // ===== Edge Cases - Cần review =====
  "Video này tệ như shit, không xem được",
  "Ý kiến ngu ngốc vãi, không có logic gì cả",
  "Chính sách ngu người, ai nghĩ ra vậy trời?",
  "Phim này rác, đạo diễn ngu như chó",
]

export default function LoadTestPanel({ onSubmit }) {
  const [requestCount, setRequestCount] = useState(100)
  const [testing, setTesting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null)
  const [batchSize, setBatchSize] = useState(10)

  const handleLoadTest = async () => {
    if (testing) return

    setTesting(true)
    setProgress(0)
    setResults(null)

    const startTime = Date.now()
    let successCount = 0
    let failCount = 0
    const errors = []

    // Split into batches to avoid overwhelming the browser
    const totalBatches = Math.ceil(requestCount / batchSize)

    for (let batch = 0; batch < totalBatches; batch++) {
      const batchStart = batch * batchSize
      const batchEnd = Math.min(batchStart + batchSize, requestCount)
      const promises = []

      for (let i = batchStart; i < batchEnd; i++) {
        const randomComment = TEST_COMMENTS[Math.floor(Math.random() * TEST_COMMENTS.length)]
        const commentData = {
          author: `Test User ${i + 1}`,
          text: randomComment
        }

        promises.push(
          onSubmit(commentData)
            .then(result => {
              if (result.success) {
                successCount++
              } else {
                failCount++
                errors.push({ index: i + 1, error: result.error })
              }
            })
            .catch(error => {
              failCount++
              errors.push({ index: i + 1, error: error.message })
            })
        )
      }

      await Promise.all(promises)
      setProgress(Math.round((batchEnd / requestCount) * 100))

      // Small delay between batches
      if (batch < totalBatches - 1) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }

    const endTime = Date.now()
    const duration = ((endTime - startTime) / 1000).toFixed(2)
    const rps = (successCount / (duration || 1)).toFixed(2)

    setResults({
      total: requestCount,
      success: successCount,
      failed: failCount,
      duration,
      rps,
      errors: errors.slice(0, 10) // Show first 10 errors only
    })

    setTesting(false)
  }

  const presetTests = [
    { label: '100 requests', value: 100 },
    { label: '500 requests', value: 500 },
    { label: '1000 requests', value: 1000 },
    { label: '2000 requests', value: 2000 },
  ]

  return (
    <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl shadow-xl p-6 mb-8">
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">🚀</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Load Testing</h2>
          <p className="text-sm text-gray-600">Kiểm tra khả năng chịu tải của hệ thống</p>
        </div>
      </div>

      {/* Test Configuration */}
      <div className="bg-white rounded-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Số lượng requests
            </label>
            <div className="flex gap-2 mb-3 flex-wrap">
              {presetTests.map(preset => (
                <button
                  key={preset.value}
                  onClick={() => setRequestCount(preset.value)}
                  disabled={testing}
                  className={`px-4 py-2 rounded-lg font-medium transition ${
                    requestCount === preset.value
                      ? 'bg-orange-600 text-white shadow-lg'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {preset.label}
                </button>
              ))}
            </div>
            <input
              type="number"
              value={requestCount}
              onChange={(e) => setRequestCount(Math.max(1, parseInt(e.target.value) || 1))}
              min="1"
              max="10000"
              disabled={testing}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition outline-none disabled:opacity-50"
              placeholder="Nhập số lượng..."
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Batch size (requests/batch)
            </label>
            <input
              type="number"
              value={batchSize}
              onChange={(e) => setBatchSize(Math.max(1, Math.min(100, parseInt(e.target.value) || 10)))}
              min="1"
              max="100"
              disabled={testing}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-200 transition outline-none disabled:opacity-50"
              placeholder="VD: 10"
            />
            <p className="mt-2 text-xs text-gray-500">
              Số requests gửi đồng thời trong mỗi batch. Giá trị nhỏ hơn = ổn định hơn.
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        {testing && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-semibold text-gray-700">Đang gửi requests...</span>
              <span className="text-sm font-bold text-orange-600">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-orange-500 to-red-500 h-full rounded-full transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Start Test Button */}
        <button
          onClick={handleLoadTest}
          disabled={testing}
          className="w-full px-6 py-4 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-lg font-bold text-lg hover:shadow-2xl transform hover:-translate-y-0.5 transition disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {testing ? (
            <span className="flex items-center justify-center gap-3">
              <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Đang test... ({progress}%)
            </span>
          ) : (
            `🚀 Bắt đầu Load Test (${requestCount.toLocaleString()} requests)`
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="bg-white rounded-lg p-6 border-2 border-orange-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            📊 Kết quả Test
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-gray-900">{results.total}</div>
              <div className="text-sm text-gray-600 mt-1">Tổng số</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center border-2 border-green-200">
              <div className="text-3xl font-bold text-green-600">{results.success}</div>
              <div className="text-sm text-gray-600 mt-1">Thành công</div>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center border-2 border-red-200">
              <div className="text-3xl font-bold text-red-600">{results.failed}</div>
              <div className="text-sm text-gray-600 mt-1">Thất bại</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center border-2 border-blue-200">
              <div className="text-3xl font-bold text-blue-600">{results.duration}s</div>
              <div className="text-sm text-gray-600 mt-1">Thời gian</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center border-2 border-purple-200">
              <div className="text-3xl font-bold text-purple-600">{results.rps}</div>
              <div className="text-sm text-gray-600 mt-1">RPS</div>
            </div>
          </div>

          {/* Success Rate */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-semibold text-gray-700">Success Rate</span>
              <span className="text-sm font-bold text-green-600">
                {((results.success / results.total) * 100).toFixed(2)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-green-500 to-emerald-500 h-full rounded-full"
                style={{ width: `${(results.success / results.total) * 100}%` }}
              />
            </div>
          </div>

          {/* Performance Analysis */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 mb-4">
            <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
              💡 Phân tích hiệu suất
            </h4>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>
                • <strong>Thông lượng:</strong> {results.rps} requests/giây
              </li>
              <li>
                • <strong>Độ tin cậy:</strong> {((results.success / results.total) * 100).toFixed(2)}% thành công
              </li>
              {results.rps >= 50 && (
                <li className="text-green-700">
                  ✅ <strong>Xuất sắc!</strong> Hệ thống xử lý rất tốt với tốc độ cao
                </li>
              )}
              {results.rps >= 20 && results.rps < 50 && (
                <li className="text-blue-700">
                  ✅ <strong>Tốt!</strong> Hệ thống xử lý ổn định
                </li>
              )}
              {results.rps < 20 && (
                <li className="text-orange-700">
                  ⚠️ <strong>Cần cải thiện:</strong> Thông lượng thấp hơn mong đợi
                </li>
              )}
            </ul>
          </div>

          {/* Errors */}
          {results.errors.length > 0 && (
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <h4 className="font-bold text-red-800 mb-2">
                ⚠️ Lỗi ({results.errors.length} đầu tiên)
              </h4>
              <div className="text-xs text-red-700 space-y-1 max-h-40 overflow-y-auto">
                {results.errors.map((err, idx) => (
                  <div key={idx}>
                    Request #{err.index}: {err.error}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Warning */}
      <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="text-2xl">⚠️</span>
          <div className="text-sm text-yellow-800">
            <strong className="font-bold">Lưu ý:</strong> Load testing sẽ tạo nhiều requests đến hệ thống.
            Điều này có thể ảnh hưởng đến hiệu suất và tạo nhiều dữ liệu test. Chỉ sử dụng trong môi trường development!
          </div>
        </div>
      </div>
    </div>
  )
}

