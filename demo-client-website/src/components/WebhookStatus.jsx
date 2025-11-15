import { useState, useEffect } from 'react'

export default function WebhookStatus() {
  const [webhookUrl, setWebhookUrl] = useState('')
  const [isHttps, setIsHttps] = useState(false)

  useEffect(() => {
    const protocol = window.location.protocol
    const origin = window.location.origin
    const url = origin + '/webhooks/moderation'
    
    setWebhookUrl(url)
    setIsHttps(protocol === 'https:')
  }, [])

  return (
    <div className={`rounded-2xl shadow-lg p-6 mb-8 ${
      isHttps 
        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300' 
        : 'bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-300'
    }`}>
      <div className="flex items-start gap-4">
        <div className={`text-4xl ${isHttps ? 'animate-pulse' : ''}`}>
          {isHttps ? '🔒' : '📡'}
        </div>
        
        <div className="flex-1">
          <h4 className={`text-lg font-bold mb-2 ${
            isHttps ? 'text-green-800' : 'text-blue-800'
          }`}>
            {isHttps ? '✅ Webhook Endpoint (HTTPS)' : '⚠️ Webhook Endpoint (HTTP)'}
          </h4>
          
          <div className="bg-white rounded-lg p-3 font-mono text-sm break-all border-2 border-gray-200 mb-2">
            {webhookUrl || 'Đang tải...'}
          </div>

          <div className="text-sm text-gray-700">
            {isHttps ? (
              <div className="flex items-center gap-2 text-green-700">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="font-semibold">Đang chạy trên HTTPS - Sẵn sàng nhận webhook từ VietCMS!</span>
              </div>
            ) : (
              <div>
                <p className="mb-2 text-orange-700 font-semibold">
                  ⚠️ Đang chạy trên HTTP local. Để có HTTPS:
                </p>
                <code className="block bg-gray-800 text-green-400 p-2 rounded text-xs">
                  ngrok http 5000
                </code>
              </div>
            )}
          </div>

          <div className="mt-3 text-xs text-gray-600">
            💡 VietCMS sẽ POST kết quả kiểm duyệt về địa chỉ này
          </div>
        </div>
      </div>
    </div>
  )
}

