import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function Register() {
  const [formData, setFormData] = useState({
    organization_name: '',
    email: '',
    password: '',
    confirm_password: '',
    webhook_url: ''
  })
  const [credentials, setCredentials] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Validate passwords match
    if (formData.password !== formData.confirm_password) {
      setError('Mật khẩu xác nhận không khớp!')
      setLoading(false)
      return
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError('Mật khẩu phải có ít nhất 8 ký tự!')
      setLoading(false)
      return
    }

    try {
      const response = await fetch('/api/v1/register', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          organization_name: formData.organization_name,
          email: formData.email,
          password: formData.password,
          webhook_url: formData.webhook_url
        })
      })

      const data = await response.json()

      if (data.success) {
        setCredentials(data.data)
      } else {
        setError(data.error?.message || 'Đăng ký thất bại')
      }
    } catch (err) {
      setError('Không thể kết nối đến server. Vui lòng thử lại.')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Đã copy vào clipboard!')
  }

  const downloadCredentials = () => {
    const content = `VietCMS Moderation Service - Credentials
=====================================

Organization: ${formData.organization_name}
Email: ${formData.email}
Webhook URL: ${formData.webhook_url}

App ID: ${credentials.app_id}
API Key: ${credentials.api_key}
HMAC Secret: ${credentials.hmac_secret}

Created: ${credentials.created_at}

⚠️ GIỮ BÍ MẬT - Không chia sẻ với người khác!
`
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vietcms-credentials-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Success Screen - Hiển thị credentials
  if (credentials) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-3xl w-full bg-white rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Đăng ký thành công! 🎉
            </h1>
            <p className="text-gray-600 text-lg">
              Tài khoản của bạn đã được tạo. Vui lòng lưu thông tin bên dưới.
            </p>
          </div>

          {/* Warning Box */}
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  ⚠️ CHÚ Ý QUAN TRỌNG
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Thông tin này <strong>CHỈ HIỂN THỊ MỘT LẦN DUY NHẤT</strong></li>
                    <li>Vui lòng copy hoặc download ngay</li>
                    <li>Không chia sẻ với người khác</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Credentials */}
          <div className="space-y-4 mb-6">
            {/* App ID */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                App ID
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={credentials.app_id}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white font-mono text-sm"
                />
                <button
                  onClick={() => copyToClipboard(credentials.app_id)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </button>
              </div>
            </div>

            {/* API Key */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                API Key <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={credentials.api_key}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white font-mono text-sm"
                />
                <button
                  onClick={() => copyToClipboard(credentials.api_key)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </button>
              </div>
            </div>

            {/* HMAC Secret */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                HMAC Secret <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={credentials.hmac_secret}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white font-mono text-sm"
                />
                <button
                  onClick={() => copyToClipboard(credentials.hmac_secret)}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </button>
              </div>
            </div>

            {/* Webhook URL */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Webhook URL
              </label>
              <input
                type="text"
                readOnly
                value={credentials.webhook_url}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white font-mono text-sm"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={downloadCredentials}
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download dưới dạng file
            </button>
            <Link
              to="/login"
              className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition font-semibold text-center"
            >
              Đăng nhập Admin
            </Link>
          </div>

          {/* Help Text */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">📚 Bước tiếp theo:</h3>
            <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
              <li>Sử dụng API Key và HMAC Secret để gọi API</li>
              <li>Đọc tài liệu tại: <a href="/docs" className="underline">docs/api-specification.md</a></li>
              <li>Sử dụng Client SDK (Python/NodeJS) để tích hợp nhanh</li>
            </ol>
          </div>
        </div>
      </div>
    )
  }

  // Registration Form
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            VietCMS Moderation
          </h1>
          <p className="text-gray-600">
            Đăng ký tài khoản để sử dụng dịch vụ kiểm duyệt
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Đăng ký Client
          </h2>

          {/* Error Alert */}
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Organization Name */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Tên tổ chức <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="organization_name"
                value={formData.organization_name}
                onChange={handleChange}
                required
                placeholder="VD: Công ty ABC"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="admin@company.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
              <p className="mt-1 text-xs text-gray-500">
                Email phải là duy nhất, không trùng với client khác
              </p>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Mật khẩu <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength="8"
                placeholder="Ít nhất 8 ký tự"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
              <p className="mt-1 text-xs text-gray-500">
                Dùng để đăng nhập vào dashboard của bạn
              </p>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Xác nhận mật khẩu <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
                minLength="8"
                placeholder="Nhập lại mật khẩu"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            {/* Webhook URL */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Webhook URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                name="webhook_url"
                value={formData.webhook_url}
                onChange={handleChange}
                required
                placeholder="https://yoursite.com/webhooks/moderation"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
              <p className="mt-1 text-xs text-gray-500">
                Địa chỉ để nhận kết quả kiểm duyệt (phải là HTTPS)
              </p>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-blue-700">
                    Sau khi đăng ký, bạn sẽ nhận được <strong>API Key</strong> và <strong>HMAC Secret</strong> để gọi API, và có thể đăng nhập vào dashboard để xem thống kê.
                  </p>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Đang xử lý...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Đăng ký ngay
                </>
              )}
            </button>
          </form>

          {/* Footer Links */}
          <div className="mt-6 text-center text-sm text-gray-600">
            <p>
              Đã có tài khoản?{' '}
              <Link to="/client-login" className="text-blue-600 hover:text-blue-700 font-semibold">
                Đăng nhập Client
              </Link>
              {' '} | {' '}
              <Link to="/login" className="text-gray-600 hover:text-gray-700">
                Admin
              </Link>
            </p>
          </div>
        </div>

        {/* Help Text */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>
            Cần hỗ trợ?{' '}
            <a href="mailto:support@vietcms.com" className="text-blue-600 hover:underline">
              support@vietcms.com
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

