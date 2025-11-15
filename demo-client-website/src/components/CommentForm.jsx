import { useState } from 'react'

const EXAMPLE_COMMENTS = [
  "Sản phẩm rất tốt, tôi rất hài lòng!",
  "Giao hàng nhanh, đóng gói cẩn thận",
  "Máy đẹp, chạy mượt, pin trâu",
  "Đồ ngu, lừa đảo",
  "Shop bán hàng giả, đmm",
  "Không tốt lắm, hơi thất vọng"
]

export default function CommentForm({ onSubmit }) {
  const [author, setAuthor] = useState('Khách hàng A')
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!text.trim()) {
      setMessage({ type: 'error', text: 'Vui lòng nhập nội dung đánh giá' })
      return
    }

    setLoading(true)
    const result = await onSubmit({ author, text })
    
    if (result.success) {
      setMessage({ type: 'success', text: '✅ Đánh giá của bạn đã được gửi và đang chờ kiểm duyệt!' })
      setText('')
      setTimeout(() => setMessage(''), 3000)
    } else {
      setMessage({ type: 'error', text: '❌ Có lỗi xảy ra!' })
    }
    
    setLoading(false)
  }

  const fillExample = () => {
    const randomExample = EXAMPLE_COMMENTS[Math.floor(Math.random() * EXAMPLE_COMMENTS.length)]
    setText(randomExample)
  }

  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6">
      <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span>✍️</span> Viết đánh giá của bạn
      </h3>

      {message && (
        <div className={`mb-4 p-4 rounded-lg ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Tên của bạn
          </label>
          <input
            type="text"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition outline-none"
            placeholder="VD: Nguyễn Văn A"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Đánh giá của bạn
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition outline-none resize-none"
            rows="4"
            placeholder="Chia sẻ trải nghiệm của bạn về sản phẩm..."
            required
          />
          <button
            type="button"
            onClick={fillExample}
            className="mt-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
          >
            💡 Điền ví dụ mẫu
          </button>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Đang gửi...
            </span>
          ) : (
            'Gửi đánh giá'
          )}
        </button>
      </form>
    </div>
  )
}

