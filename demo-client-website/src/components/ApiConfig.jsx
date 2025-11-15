import { useState, useEffect } from 'react'

export default function ApiConfig() {
  const [config, setConfig] = useState({
    api_key: '',
    hmac_secret: '',
    webhook_url: ''
  })
  const [savedConfig, setSavedConfig] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // Load current config
  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const response = await fetch('/api/config')
      const data = await response.json()
      if (data.configured) {
        setSavedConfig(data.config)
        setConfig(data.config)
      } else {
        setShowForm(true) // Nếu chưa config thì hiện form
      }
    } catch (error) {
      console.error('Error loading config:', error)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    setTestResult(null)
    
    try {
      const response = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      
      const data = await response.json()
      
      if (data.success) {
        setSavedConfig(config)
        setShowForm(false)
        setTestResult({ type: 'success', message: '✅ Cấu hình đã được lưu thành công!' })
      } else {
        setTestResult({ type: 'error', message: '❌ Lỗi: ' + (data.error || 'Không thể lưu cấu hình') })
      }
    } catch (error) {
      setTestResult({ type: 'error', message: '❌ Không thể kết nối backend' })
    } finally {
      setLoading(false)
    }
  }

  const handleTest = async () => {
    setLoading(true)
    setTestResult(null)
    
    try {
      const response = await fetch('/api/test-config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      
      const data = await response.json()
      
      if (data.success) {
        setTestResult({ type: 'success', message: '✅ Kết nối thành công! API hoạt động bình thường.' })
      } else {
        setTestResult({ type: 'error', message: '❌ Kết nối thất bại: ' + (data.error || 'Unknown error') })
      }
    } catch (error) {
      setTestResult({ type: 'error', message: '❌ Không thể test kết nối' })
    } finally {
      setLoading(false)
    }
  }

  const handleClear = async () => {
    if (!confirm('Bạn có chắc muốn xóa cấu hình VietCMS API?')) return
    
    try {
      await fetch('/api/config', { method: 'DELETE' })
      setConfig({ api_key: '', hmac_secret: '', webhook_url: '' })
      setSavedConfig(null)
      setShowForm(true)
      setTestResult({ type: 'success', message: '✅ Đã xóa cấu hình' })
    } catch (error) {
      setTestResult({ type: 'error', message: '❌ Không thể xóa cấu hình' })
    }
  }

  if (!showForm && savedConfig) {
    return (
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 mb-8 border border-green-200">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-bold text-green-800 mb-2 flex items-center gap-2">
              <span>✅</span> VietCMS API đã được cấu hình
            </h3>
            <div className="text-sm text-green-700 space-y-1">
              <p><strong>API Key:</strong> {savedConfig.api_key?.substring(0, 20)}...</p>
              <p><strong>Webhook URL:</strong> {savedConfig.webhook_url}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition text-sm"
            >
              Sửa
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition text-sm"
            >
              Xóa
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 mb-8 border border-yellow-200">
      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span>⚙️</span> Cấu hình VietCMS API
      </h3>
      
      {testResult && (
        <div className={`mb-4 p-4 rounded-lg ${
          testResult.type === 'success' 
            ? 'bg-green-100 text-green-800 border border-green-300' 
            : 'bg-red-100 text-red-800 border border-red-300'
        }`}>
          {testResult.message}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            API Key <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={config.api_key}
            onChange={(e) => setConfig({...config, api_key: e.target.value})}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition outline-none font-mono text-sm"
            placeholder="api_xxxxxxxxxxxxxxxx"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            HMAC Secret <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            value={config.hmac_secret}
            onChange={(e) => setConfig({...config, hmac_secret: e.target.value})}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition outline-none font-mono text-sm"
            placeholder="hmac_xxxxxxxxxxxxxxxx"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Webhook URL (optional)
          </label>
          <input
            type="url"
            value={config.webhook_url}
            onChange={(e) => setConfig({...config, webhook_url: e.target.value})}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition outline-none font-mono text-sm"
            placeholder="https://your-tunnel.trycloudflare.com/webhooks/moderation"
          />
          <p className="text-xs text-gray-600 mt-1">
            💡 Để nhận webhook, cần chạy: <code className="bg-gray-200 px-1 rounded">cloudflared tunnel --url http://localhost:5000</code>
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleTest}
            disabled={loading || !config.api_key || !config.hmac_secret}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Đang test...' : 'Test kết nối'}
          </button>
          
          <button
            onClick={handleSave}
            disabled={loading || !config.api_key || !config.hmac_secret}
            className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Đang lưu...' : 'Lưu cấu hình'}
          </button>

          {savedConfig && (
            <button
              onClick={() => setShowForm(false)}
              className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
            >
              Hủy
            </button>
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800">
          <strong>📌 Hướng dẫn:</strong><br/>
          1. Đăng nhập vào <a href="http://localhost/client-login" target="_blank" className="underline">VietCMS Dashboard</a><br/>
          2. Copy API Key và HMAC Secret<br/>
          3. Dán vào form này và click "Lưu cấu hình"<br/>
          4. Submit comment để test
        </p>
      </div>
    </div>
  )
}

