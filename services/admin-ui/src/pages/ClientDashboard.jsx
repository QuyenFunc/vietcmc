import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ClientDashboard() {
  const [clientInfo, setClientInfo] = useState(null)
  const [stats, setStats] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showApiKey, setShowApiKey] = useState(false)
  const [showSecret, setShowSecret] = useState(false)
  const [editingWebhook, setEditingWebhook] = useState(false)
  const [newWebhookUrl, setNewWebhookUrl] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    const token = localStorage.getItem('client_token')
    const info = JSON.parse(localStorage.getItem('client_info') || '{}')
    
    if (!token) {
      navigate('/client-login')
      return
    }

    setClientInfo(info)
    
    try {
      // Load stats
      const statsResponse = await fetch('/api/v1/client/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const statsData = await statsResponse.json()
      if (statsData.success) {
        setStats(statsData.data)
      }

      // Load recent jobs
      const jobsResponse = await fetch('/api/v1/client/jobs?page=1&per_page=10', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const jobsData = await jobsResponse.json()
      if (jobsData.success) {
        setJobs(jobsData.data.jobs || [])
      }
    } catch (err) {
      console.error('Error loading dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('client_token')
    localStorage.removeItem('client_info')
    navigate('/client-login')
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Đã copy!')
  }

  const handleEditWebhook = () => {
    setNewWebhookUrl(clientInfo?.webhook_url || '')
    setEditingWebhook(true)
  }

  const handleCancelEditWebhook = () => {
    setEditingWebhook(false)
    setNewWebhookUrl('')
  }

  const handleSaveWebhook = async () => {
    const token = localStorage.getItem('client_token')
    
    try {
      const response = await fetch('/api/v1/client/webhook', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ webhook_url: newWebhookUrl })
      })

      const data = await response.json()

      if (data.success) {
        // Update local state
        const updatedInfo = { ...clientInfo, webhook_url: data.data.webhook_url }
        setClientInfo(updatedInfo)
        localStorage.setItem('client_info', JSON.stringify(updatedInfo))
        
        setEditingWebhook(false)
        alert('Cập nhật webhook URL thành công!')
      } else {
        alert('Lỗi: ' + (data.message || 'Không thể cập nhật'))
      }
    } catch (err) {
      console.error('Error updating webhook:', err)
      alert('Lỗi khi cập nhật webhook URL')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-gray-600">Đang tải...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {clientInfo?.organization_name}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {clientInfo?.email}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* API Credentials */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Thông tin API
          </h2>
          
          <div className="space-y-4">
            {/* App ID */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                App ID
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={clientInfo?.app_id || ''}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                />
                <button
                  onClick={() => copyToClipboard(clientInfo?.app_id)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                >
                  Copy
                </button>
              </div>
            </div>

            {/* API Key */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                API Key
              </label>
              <div className="flex items-center gap-2">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  readOnly
                  value={clientInfo?.api_key || '••••••••••••••••••••'}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                />
                <button
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
                >
                  {showApiKey ? 'Ẩn' : 'Hiện'}
                </button>
                <button
                  onClick={() => copyToClipboard(clientInfo?.api_key)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                >
                  Copy
                </button>
              </div>
            </div>

            {/* HMAC Secret */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                HMAC Secret
              </label>
              <div className="flex items-center gap-2">
                <input
                  type={showSecret ? 'text' : 'password'}
                  readOnly
                  value={clientInfo?.hmac_secret || '••••••••••••••••••••'}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                />
                <button
                  onClick={() => setShowSecret(!showSecret)}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
                >
                  {showSecret ? 'Ẩn' : 'Hiện'}
                </button>
                <button
                  onClick={() => copyToClipboard(clientInfo?.hmac_secret)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                >
                  Copy
                </button>
              </div>
            </div>

            {/* Webhook URL */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Webhook URL
              </label>
              {editingWebhook ? (
                <div className="space-y-2">
                  <input
                    type="url"
                    value={newWebhookUrl}
                    onChange={(e) => setNewWebhookUrl(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://your-domain.com/webhook"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleSaveWebhook}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                    >
                      Lưu
                    </button>
                    <button
                      onClick={handleCancelEditWebhook}
                      className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
                    >
                      Hủy
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={clientInfo?.webhook_url || ''}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                  />
                  <button
                    onClick={handleEditWebhook}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                  >
                    Sửa
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Jobs hôm nay</div>
              <div className="text-3xl font-bold text-blue-600">{stats.jobs_today || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Tổng jobs</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_jobs || 0}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Tỷ lệ thành công</div>
              <div className="text-3xl font-bold text-green-600">{stats.success_rate || 0}%</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Trung bình/phút</div>
              <div className="text-3xl font-bold text-purple-600">{stats.avg_per_minute || 0}</div>
            </div>
          </div>
        )}

        {/* Recent Jobs */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-bold text-gray-900">Jobs gần đây</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Job ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Text</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kết quả</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thời gian</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                      Chưa có jobs nào
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr key={job.job_id}>
                      <td className="px-6 py-4 text-sm font-mono text-gray-900">
                        {job.job_id.substring(0, 8)}...
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {job.text?.substring(0, 50)}...
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          job.status === 'completed' ? 'bg-green-100 text-green-800' :
                          job.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                          job.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {job.moderation_result && (
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            job.moderation_result === 'allowed' ? 'bg-green-100 text-green-800' :
                            job.moderation_result === 'review' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {job.moderation_result}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {job.created_at ? new Date(job.created_at).toLocaleString('vi-VN') : '-'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}

