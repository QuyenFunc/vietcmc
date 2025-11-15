const STATUS_CONFIG = {
  pending: {
    label: '⏳ Đang kiểm duyệt',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-400',
    textColor: 'text-yellow-800',
    badgeBg: 'bg-yellow-100',
    badgeText: 'text-yellow-800'
  },
  allowed: {
    label: '✅ Đã duyệt',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-400',
    textColor: 'text-green-800',
    badgeBg: 'bg-green-100',
    badgeText: 'text-green-800'
  },
  review: {
    label: '⚠️ Cần xem xét',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-400',
    textColor: 'text-orange-800',
    badgeBg: 'bg-orange-100',
    badgeText: 'text-orange-800'
  },
  reject: {
    label: '❌ Bị từ chối',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-400',
    textColor: 'text-red-800',
    badgeBg: 'bg-red-100',
    badgeText: 'text-red-800'
  }
}

function CommentItem({ comment }) {
  const status = comment.moderation_result || 'pending'
  const config = STATUS_CONFIG[status]

  return (
    <div className={`${config.bgColor} border-l-4 ${config.borderColor} rounded-lg p-6 ${
      status === 'reject' ? 'opacity-60' : ''
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
            {comment.author.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="font-semibold text-gray-900">{comment.author}</div>
            <div className="text-xs text-gray-500">
              {new Date(comment.created_at).toLocaleString('vi-VN')}
            </div>
          </div>
        </div>
        
        <span className={`${config.badgeBg} ${config.badgeText} px-3 py-1 rounded-full text-xs font-bold uppercase`}>
          {config.label}
        </span>
      </div>

      {/* Comment Text */}
      <div className={`text-gray-800 leading-relaxed mb-3 ${
        status === 'reject' ? 'line-through' : ''
      }`}>
        {comment.text}
      </div>

      {/* Moderation Info */}
      {comment.moderation_result && (
        <div className="bg-white rounded-lg p-4 mt-4 space-y-2 text-sm border border-gray-200">
          <div className="font-bold text-indigo-600 mb-2">
            🤖 Kết quả AI Kiểm Duyệt:
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="font-semibold text-gray-700">Cảm xúc:</span>
              <span className="ml-2 text-gray-900">
                {comment.sentiment === 'positive' ? '😊 Tích cực' : 
                 comment.sentiment === 'negative' ? '😞 Tiêu cực' : 
                 '😐 Trung lập'}
              </span>
            </div>
            
            <div>
              <span className="font-semibold text-gray-700">Độ tin cậy:</span>
              <span className="ml-2 text-gray-900">
                {comment.confidence ? (comment.confidence * 100).toFixed(1) + '%' : 'N/A'}
              </span>
            </div>
          </div>

          {comment.reasoning && (
            <div className="pt-2 border-t border-gray-200">
              <span className="font-semibold text-gray-700">Lý do:</span>
              <span className="ml-2 text-gray-900">{comment.reasoning}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function CommentList({ comments, loading }) {
  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Đang tải đánh giá...</p>
      </div>
    )
  }

  if (comments.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">💬</div>
        <p className="text-gray-500 text-lg">Chưa có đánh giá nào</p>
        <p className="text-gray-400 text-sm mt-2">Hãy là người đầu tiên đánh giá sản phẩm!</p>
      </div>
    )
  }

  return (
    <div>
      <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span>💬</span> Đánh giá từ khách hàng
        <span className="text-indigo-600">({comments.length})</span>
      </h3>

      <div className="space-y-4">
        {[...comments].reverse().map((comment, index) => (
          <CommentItem key={comment.id || index} comment={comment} />
        ))}
      </div>
    </div>
  )
}

