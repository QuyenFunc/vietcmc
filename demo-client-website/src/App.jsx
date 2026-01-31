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
      return { success: false, error: 'Could not connect to backend. Please make sure the server is running!' }
    }
  }

  // Clear all comments
  const handleClearComments = async () => {
    if (!window.confirm(`⚠️ Are you sure you want to delete all ${comments.length} comments?\nThis action cannot be undone!`)) {
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
        alert(`✅ Deleted ${data.deleted_count} comments successfully!`)
      }
    } catch (error) {
      console.error('Error clearing comments:', error)
      alert('❌ Error deleting comments')
    }
  }

  // Load comments on mount and refresh every 3 seconds
  useEffect(() => {
    loadComments()
    const interval = setInterval(loadComments, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-dark-primary text-dark-text-primary">
      {/* Navigation Bar */}
      <nav className="border-b border-dark-border bg-dark-secondary/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between max-w-7xl">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-accent-primary rounded-lg flex items-center justify-center text-white font-bold">
              V
            </div>
            <span className="font-bold text-lg tracking-tight">VietCMS AI</span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-status-success/10 text-status-success border border-status-success/20">
              <span className="w-2 h-2 bg-status-success rounded-full"></span>
              System Active
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-7xl space-y-8">
        {/* Header Section */}
        <header className="py-8">
          <h1 className="text-4xl font-bold mb-4 text-balance">
            Advanced Content Moderation Platform
          </h1>
          <p className="text-dark-text-secondary text-lg max-w-2xl text-balance">
            Real-time AI analysis for community safety. Detect toxicity, sentiment, and spam instantly with our advanced machine learning models.
          </p>
        </header>

        {/* Configuration & Status Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ApiConfig />
          <WebhookStatus />
        </div>

        {/* Load Testing */}
        <LoadTestPanel onSubmit={handleSubmitComment} />

        {/* Main Demo Area */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Product & Input */}
          <div className="lg:col-span-5 space-y-6">
            {/* ProductCard removed */}
            <CommentForm onSubmit={handleSubmitComment} />
          </div>

          {/* Right Column: Analysis Results */}
          <div className="lg:col-span-7">
            <div className="card h-full flex flex-col">
              <div className="p-6 border-b border-dark-border flex justify-between items-center bg-dark-secondary rounded-t-xl">
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    Live Analysis Feed
                  </h2>
                  <span className="badge bg-dark-tertiary text-dark-text-secondary border border-dark-border">
                    {comments.length}
                  </span>
                </div>
                {comments.length > 0 && (
                  <button
                    onClick={handleClearComments}
                    className="text-xs text-status-error hover:text-red-400 font-medium transition-colors px-3 py-1.5 rounded-lg hover:bg-red-500/10"
                  >
                    Clear History
                  </button>
                )}
              </div>
              <div className="p-6 flex-1 bg-dark-primary/30">
                <CommentList comments={comments} loading={loading} />
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default App

