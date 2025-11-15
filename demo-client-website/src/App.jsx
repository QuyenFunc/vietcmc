import { useState, useEffect } from 'react'
import ProductCard from './components/ProductCard'
import CommentForm from './components/CommentForm'
import CommentList from './components/CommentList'
import WebhookStatus from './components/WebhookStatus'
import ApiConfig from './components/ApiConfig'
import LoadTestPanel from './components/LoadTestPanel'

function App() {
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)

  // Load comments from backend
  const loadComments = async () => {
    try {
      const response = await fetch('/api/comments')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setComments(data.comments || [])
      setLoading(false)
    } catch (error) {
      console.error('Error loading comments:', error)
      setLoading(false)
    }
  }

  // Submit new comment
  const handleSubmitComment = async (commentData) => {
    try {
      const response = await fetch('/api/submit-comment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(commentData)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.success) {
        // Add new comment to list
        setComments(prev => [...prev, data.comment])
        return { success: true }
      }
      
      return { success: false, error: 'Failed to submit comment' }
    } catch (error) {
      console.error('Error submitting comment:', error)
      return { success: false, error: 'Không thể kết nối backend. Hãy đảm bảo server đang chạy!' }
    }
  }

  // Clear all comments
  const handleClearComments = async () => {
    if (!window.confirm(`⚠️ Bạn có chắc chắn muốn xóa tất cả ${comments.length} comments?\nHành động này không thể hoàn tác!`)) {
      return
    }

    try {
      const response = await fetch('/api/comments/clear', {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.success) {
        setComments([])
        alert(`✅ Đã xóa ${data.deleted_count} comments thành công!`)
      }
    } catch (error) {
      console.error('Error clearing comments:', error)
      alert('❌ Lỗi khi xóa comments')
    }
  }

  // Load comments on mount and refresh every 3 seconds
  useEffect(() => {
    loadComments()
    const interval = setInterval(loadComments, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-3">
            🛍️ Demo Shop - Website Khách Hàng
          </h1>
          <p className="text-gray-600 text-lg">
            Mô phỏng website thương mại điện tử với tính năng kiểm duyệt bình luận tự động bằng VietCMS AI
          </p>
        </div>

        {/* API Configuration */}
        <ApiConfig />

        {/* Webhook Status */}
        <WebhookStatus />

        {/* Load Testing Panel */}
        <LoadTestPanel onSubmit={handleSubmitComment} />

        {/* Product & Comments */}
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          <ProductCard />
          
          <div className="p-8 border-t border-gray-200">
            <CommentForm onSubmit={handleSubmitComment} />
          </div>

          <div className="p-8 border-t border-gray-200 bg-gray-50">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-900">
                📝 Bình luận ({comments.length})
              </h2>
              {comments.length > 0 && (
                <button
                  onClick={handleClearComments}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium text-sm"
                >
                  🗑️ Xóa tất cả
                </button>
              )}
            </div>
            <CommentList comments={comments} loading={loading} />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-white text-sm">
          <p>
            Powered by VietCMS Moderation API | Demo Client Website
          </p>
        </div>
      </div>
    </div>
  )
}

export default App

