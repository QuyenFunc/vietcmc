import { useState, useEffect } from 'react'

const TEST_COMMENTS = [
  // ===== CLEAN - Bình luận tích cực/ủng hộ =====
  "Bài viết rất hay và bổ ích! Cảm ơn tác giả đã chia sẻ 👍",
  "Video này đỉnh quá, mình vừa subscribe luôn! 🔥",
  "Cảm ơn bạn đã chia sẻ kinh nghiệm, rất hữu ích!",
  "Nội dung chất lượng, nhất định phải theo dõi ❤️",
  "Chúc mừng bạn, thành công xứng đáng! 🎉",
  "Like và share để nhiều người biết đến hơn!",
  "Ủng hộ kênh, tiếp tục ra video nha!",
  "Hay quá, mong chờ phần tiếp theo!",
  "Mình đồng ý 100% với quan điểm này",
  "Bài viết rất sâu sắc và truyền cảm hứng",

  // ===== CLEAN - Thảo luận/Phản hồi xây dựng =====
  "Mình nghĩ vấn đề này cần được xem xét từ góc độ khác",
  "Ý kiến hay nhưng cần thêm số liệu để chứng minh",
  "Mình không hoàn toàn đồng ý, nhưng tôn trọng quan điểm của bạn",
  "Nếu thêm ví dụ cụ thể sẽ rõ ràng hơn",
  "Luận điểm thú vị, tuy nhiên cần cân nhắc thêm khía cạnh X",
  "Bạn có thể chia sẻ nguồn tham khảo được không?",
  "Góc nhìn mới lạ, nhưng thiếu phân tích sâu",
  "Video hay nhưng hơi dài, nên tóm tắt lại",

  // ===== CLEAN - Tranh luận/Phê bình (KHÔNG xúc phạm) =====
  "Ý kiến này không có cơ sở khoa học",
  "Luận điểm này thiếu logic và mâu thuẫn",
  "Quan điểm này quá cực đoan và phiến diện",
  "Thông tin này không chính xác, cần xác minh lại",
  "Mình hoàn toàn không đồng ý với đánh giá này",
  "Phân tích này có nhiều thiếu sót",

  // ===== CLEAN - Bình luận trung tính =====
  "Đã xem",
  "Cảm ơn đã chia sẻ",
  "Lưu lại xem sau",
  "Ok, ghi nhận",
  "Thú vị đấy",
  "Hmmm, để mình suy nghĩ thêm",

  // ===== CLEAN - Hỏi đáp/Tương tác =====
  "Bạn có thể làm video về chủ đề X không?",
  "Phần này ở phút thứ mấy vậy?",
  "Link tham khảo ở đâu vậy bạn?",
  "Bạn dùng tool gì để làm video này vậy?",
  "Có ai đồng ý với mình không? 🤔",

  // ===== TOXIC - Xúc phạm cá nhân =====
  "Mày ngu như bò",
  "Ngu như chó, không biết gì hết",
  "Thằng này ngu thật, nói năng linh tinh",
  "Đồ rác rưởi, mày ghê tởm quá",
  "Ngu vậy mà cũng dám bình luận",
  "Đồ khốn, làm gì cũng sai",
  "Thằng ngốc này hết biết xấu hổ à?",
  "Mày ngu vậy mà cũng dám cãi?",
  "Nói gì cũng rác, về đi",
  "Đồ ngu, câm mồm đi",

  // ===== TOXIC - Chửi tục/Thô tục =====
  "Ý kiến này ngu vcl",
  "Đm, thằng này ngu vãi",
  "Con mẹ mày",
  "Cái cc không ai quan tâm",
  "Cút đi mày, đồ ngu",
  "Đéo ai cần ý kiến của mày",
  "Vl, ngu thế cũng nói",

  // ===== HATE SPEECH - Phân biệt chủng tộc/Dân tộc =====
  "Bọn dân tộc đó nghèo nàn và lạc hậu",
  "Người châu Phi kém văn minh hơn",
  "Bọn tàu khựa đáng ghét, cút về nước đi",
  "Bọn da đen bẩn thỉu, không đáng tin",
  "Đám dân tộc thiểu số lạc hậu",

  // ===== HATE SPEECH - Phân biệt giới tính =====
  "Đàn bà ngu lắm, chỉ biết nói",
  "Phụ nữ không có não, đừng cãi",
  "Con gái đừng học IT, không đủ thông minh",
  "Chỉ đàn ông mới có tư duy logic, phụ nữ thì không",

  // ===== HATE SPEECH - Phân biệt LGBT =====
  "Đồ gay là bệnh tâm thần",
  "LGBT là tội lỗi, nên bị cấm",
  "Bọn chuyển giới là loạn thần",
  "Người đồng tính đáng bị khinh bỉ",

  // ===== HATE SPEECH - Phân biệt tôn giáo =====
  "Tôn giáo X toàn khủng bố",
  "Người theo đạo Y lạc hậu",
  "Người vô thần không có đạo đức",

  // ===== HARASSMENT - Đe dọa bạo lực =====
  "Tao sẽ tìm mày và đánh cho chừa",
  "Chờ đấy, tao sẽ giết mày",
  "Coi chừng tao cho mày một trận",
  "Chờ đó, tao đến nhà mày bây giờ",
  "Mày chết với tao, coi chừng đi đường",

  // ===== HARASSMENT - Doxxing/Đe dọa lộ thông tin =====
  "Tao sẽ tung địa chỉ nhà mày cho mọi người",
  "Coi chừng tao đăng clip của mày lên mạng",
  "Tao có số điện thoại mày rồi, chờ đó",
  "Sẽ công khai thông tin cá nhân của mày",

  // ===== HARASSMENT - Quấy rối tình dục =====
  "Gái xinh thế này chắc giỏi lắm",
  "Nhắn tin cho anh, anh cho xem cái hay",
  "Body đẹp thế",
  "Nhìn cái đó chắc sướng lắm",

  // ===== SPAM - Quảng cáo/Lừa đảo =====
  "Kiếm tiền online 10 triệu/ngày! Inbox ngay 📞📞📞",
  "GIẢM CÂN SIÊU TỐC không cần ăn kiêng! Mua ngay! 💊",
  "🔥🔥 SALE SỐC GIẢM 90% 🔥🔥 Click: http://scam.com",
  "Cần gái xinh làm dịch vụ, lương cao! Liên hệ: 0xxx",
  "Tăng chiều cao 5cm trong 1 tuần!!!",
  "Hack acc FB chỉ 50k! Liên hệ ngay!",
  "💰💰 ĐẦU TƯ BITCOIN LÃI 200%/THÁNG 💰💰",

  // ===== SPAM - Link rác/Virus =====
  "Click vào đây nhận quà: http://virus.com 🎁🎁🎁",
  "Xem ảnh nóng tại đây: http://malware.net",
  "Bạn trúng 100 triệu! Click để nhận: http://scam.vn",

  // ===== PII - Lộ thông tin cá nhân =====
  "Số điện thoại mình là 0987654321, liên hệ nha",
  "Email: myemail@gmail.com, add friend đi",
  "Địa chỉ nhà mình là 123 Nguyễn Huệ, Quận 1",
  "CMND của mình: 001234567890",
  "STK: Vietcombank 1234567890",

  // ===== Edge Cases - Cần review =====
  "Video này đéo xem được",
  "Ý kiến ngu, không có logic",
  "Chính sách ngu, ai đề ra vậy?",
  "Phim này rác, đạo diễn không biết gì",
]


export default function LoadTestPanel({ onSubmit }) {
  const [requestCount, setRequestCount] = useState(100)
  const [testing, setTesting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null)
  const [batchSize, setBatchSize] = useState(5)
  const [apiConfig, setApiConfig] = useState(null)

  // Load API config on mount
  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        if (data.configured && data.config) {
          setApiConfig(data.config)
        }
      })
      .catch(err => console.error('Failed to load API config:', err))
  }, [])

  // Function to calculate HMAC signature
  const calculateHMAC = async (message, secret) => {
    const encoder = new TextEncoder()
    const keyData = encoder.encode(secret)
    const messageData = encoder.encode(message)

    const key = await crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    )

    const signature = await crypto.subtle.sign('HMAC', key, messageData)
    const hashArray = Array.from(new Uint8Array(signature))
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
    return hashHex
  }

  // Helper for retrying fetch
  const fetchWithRetry = async (url, options, retries = 5, backoff = 2000) => {
    try {
      const response = await fetch(url, options)
      // Retry on 429 (Too Many Requests) or 5xx server errors
      if (!response.ok && (response.status === 429 || response.status >= 500)) {
        throw new Error(`Server error: ${response.status}`)
      }
      return response
    } catch (err) {
      if (retries > 0) {
        console.log(`Retrying... attempts left: ${retries}. Error: ${err.message}`)
        await new Promise(resolve => setTimeout(resolve, backoff))
        return fetchWithRetry(url, options, retries - 1, backoff * 1.5)
      }
      throw err
    }
  }

  // Submit directly to VietCMS API
  const submitToVietCMSAPI = async (commentData, configOverride) => {
    const config = configOverride || apiConfig
    if (!config) {
      throw new Error('API not configured')
    }

    const payload = {
      comment_id: `loadtest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      text: commentData.text,
      metadata: {
        author: commentData.author,
        source: 'demo-website-loadtest'
      }
    }

    const body = JSON.stringify(payload)
    const signature = await calculateHMAC(body, config.hmac_secret)

    const response = await fetchWithRetry(`${config.api_url}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': config.api_key,
        'X-Hub-Signature-256': `sha256=${signature}`
      },
      body: body
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`API error: ${response.status} - ${errorText}`)
    }

    return await response.json()
  }

  const handleLoadTest = async () => {
    if (testing) return

    // Try to load config if not already loaded
    let config = apiConfig
    if (!config) {
      try {
        const response = await fetch('/api/config')
        const data = await response.json()
        if (data.configured && data.config) {
          config = data.config
          setApiConfig(config)
        }
      } catch (err) {
        console.error('Failed to load API config:', err)
      }
    }

    if (!config) {
      alert('⚠️ API not configured! Please configure API before running load test.')
      return
    }

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
          submitToVietCMSAPI(commentData, config)
            .then(result => {
              if (result.success || result.data) {
                successCount++
              } else {
                failCount++
                errors.push({ index: i + 1, error: 'API returned unsuccessful response' })
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

      // Delay between batches to avoid rate limiting
      if (batch < totalBatches - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000))
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
  ]

  return (
    <div className="card p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-accent-primary/10 rounded-lg flex items-center justify-center text-accent-primary">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-dark-text-primary">Performance Testing</h2>
            <p className="text-sm text-dark-text-tertiary">System load analysis</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-status-success rounded-full animate-pulse"></div>
          <span className="text-dark-text-tertiary text-sm">Ready</span>
        </div>
      </div>

      {/* Test Configuration */}
      <div className="bg-dark-secondary rounded-xl p-6 mb-6 border border-dark-border">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-dark-text-secondary mb-3">
              Test Volume
            </label>
            <div className="flex gap-2 mb-3 flex-wrap">
              {presetTests.map(preset => (
                <button
                  key={preset.value}
                  onClick={() => setRequestCount(preset.value)}
                  disabled={testing}
                  className={`px-3 py-1.5 rounded-lg font-mono text-sm font-medium transition-all duration-200 ${requestCount === preset.value
                    ? 'bg-accent-primary text-white shadow-sm'
                    : 'bg-dark-tertiary text-dark-text-secondary hover:bg-dark-quaternary border border-dark-border'
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
              className="input font-mono text-sm"
              placeholder="Enter volume..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-dark-text-secondary mb-3">
              Concurrency Level
            </label>
            <input
              type="number"
              value={batchSize}
              onChange={(e) => setBatchSize(Math.max(1, Math.min(100, parseInt(e.target.value) || 10)))}
              min="1"
              max="100"
              disabled={testing}
              className="input font-mono text-sm"
              placeholder="Default: 10"
            />
            <p className="mt-2 text-xs text-dark-text-tertiary">
              Simultaneous operations per batch. Lower values = more stable testing.
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        {testing && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-dark-text-secondary">Executing test...</span>
              <span className="text-sm font-bold text-accent-primary font-mono">{progress}%</span>
            </div>
            <div className="w-full bg-dark-tertiary rounded-full h-2 overflow-hidden">
              <div
                className="bg-accent-primary h-full rounded-full transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Start Test Button */}
        <button
          onClick={handleLoadTest}
          disabled={testing}
          className="btn-primary w-full"
        >
          {testing ? (
            <span className="flex items-center justify-center gap-3">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Testing... ({progress}%)
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Execute Performance Test
            </span>
          )}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="bg-dark-primary/30 rounded-xl p-6 border border-dark-border">
          <h3 className="text-lg font-bold text-dark-text-primary mb-6 flex items-center gap-3">
            <div className="w-8 h-8 bg-accent-primary/10 rounded-lg flex items-center justify-center text-accent-primary">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            Performance Metrics
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-dark-secondary rounded-lg p-4 text-center border border-dark-border">
              <div className="text-2xl font-bold text-dark-text-primary font-mono">{results.total}</div>
              <div className="text-xs text-dark-text-tertiary mt-1">Total</div>
            </div>
            <div className="bg-dark-secondary rounded-lg p-4 text-center border border-status-success/30">
              <div className="text-2xl font-bold text-status-success font-mono">{results.success}</div>
              <div className="text-xs text-dark-text-tertiary mt-1">Success</div>
            </div>
            <div className="bg-dark-secondary rounded-lg p-4 text-center border border-status-error/30">
              <div className="text-2xl font-bold text-status-error font-mono">{results.failed}</div>
              <div className="text-xs text-dark-text-tertiary mt-1">Failed</div>
            </div>
            <div className="bg-dark-secondary rounded-lg p-4 text-center border border-accent-primary/30">
              <div className="text-2xl font-bold text-accent-primary font-mono">{results.duration}s</div>
              <div className="text-xs text-dark-text-tertiary mt-1">Duration</div>
            </div>
            <div className="bg-dark-secondary rounded-lg p-4 text-center border border-accent-secondary/30">
              <div className="text-2xl font-bold text-accent-secondary font-mono">{results.rps}</div>
              <div className="text-xs text-dark-text-tertiary mt-1">RPS</div>
            </div>
          </div>

          {/* Success Rate */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-dark-text-secondary">Success Rate</span>
              <span className="text-sm font-bold text-status-success font-mono">
                {((results.success / results.total) * 100).toFixed(2)}%
              </span>
            </div>
            <div className="w-full bg-dark-tertiary rounded-full h-2 overflow-hidden">
              <div
                className="bg-status-success h-full rounded-full transition-all duration-500"
                style={{ width: `${(results.success / results.total) * 100}%` }}
              />
            </div>
          </div>



          {/* Errors */}
          {results.errors.length > 0 && (
            <div className="bg-status-error/5 rounded-lg p-4 border border-status-error/20">
              <h4 className="font-bold text-status-error mb-3 flex items-center gap-2 text-sm">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Error Analysis ({results.errors.length} occurrences)
              </h4>
              <div className="text-xs text-status-error space-y-1 max-h-40 overflow-y-auto font-mono">
                {results.errors.map((err, idx) => (
                  <div key={idx} className="p-2 bg-dark-tertiary/50 rounded">
                    <span className="opacity-70">#{err.index}:</span> {err.error}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

