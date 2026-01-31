import { useState, useEffect } from 'react'

export default function ApiConfig() {
  const [config, setConfig] = useState({
    api_url: '',
    api_key: '',
    hmac_secret: '',
    webhook_url: ''
  })
  const [savedConfig, setSavedConfig] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const maskSecret = (value) => {
    if (!value) return ''
    if (value.length <= 8) return value
    return `${value.slice(0, 4)}...${value.slice(-4)}`
  }

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
        setConfig({
          api_url: data.config?.api_url || data.default_api_url || '',
          api_key: data.config?.api_key || '',
          hmac_secret: data.config?.hmac_secret || '',
          webhook_url: data.config?.webhook_url || ''
        })
        setShowForm(false)
      } else {
        setShowForm(true)
        setConfig(prev => ({
          ...prev,
          api_url: data.default_api_url || ''
        }))
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
        setSavedConfig({
          ...config,
          api_key_preview: maskSecret(config.api_key),
          hmac_secret_preview: maskSecret(config.hmac_secret)
        })
        setShowForm(false)
        setTestResult({ type: 'success', message: '✅ Configuration saved successfully!' })
      } else {
        setTestResult({ type: 'error', message: '❌ Error: ' + (data.error || 'Failed to save config') })
      }
    } catch (error) {
      setTestResult({ type: 'error', message: '❌ Connection failed' })
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
        setTestResult({ type: 'success', message: '✅ Connection successful! API is working.' })
      } else {
        setTestResult({ type: 'error', message: '❌ Connection failed: ' + (data.error || 'Unknown error') })
      }
    } catch (error) {
      setTestResult({ type: 'error', message: '❌ Could not test connection' })
    } finally {
      setLoading(false)
    }
  }

  const handleClear = async () => {
    if (!confirm('Are you sure you want to clear the configuration?')) return

    try {
      await fetch('/api/config', { method: 'DELETE' })
      setConfig({ api_url: '', api_key: '', hmac_secret: '', webhook_url: '' })
      setSavedConfig(null)
      setShowForm(true)
      setTestResult({ type: 'success', message: '✅ Configuration cleared' })
      await loadConfig()
    } catch (error) {
      setTestResult({ type: 'error', message: '❌ Could not clear configuration' })
    }
  }

  if (!showForm && savedConfig) {
    return (
      <div className="card p-6 border-l-4 border-l-status-success">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-status-success/10 rounded-lg flex items-center justify-center text-status-success">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-dark-text-primary">API Configuration Active</h3>
                <p className="text-sm text-status-success">VietCMS integration ready</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-dark-primary/50 rounded-lg p-3 border border-dark-border">
                <div className="text-xs text-dark-text-tertiary mb-1">API Endpoint</div>
                <div className="text-sm font-mono text-dark-text-secondary truncate">{savedConfig.api_url}</div>
              </div>
              <div className="bg-dark-primary/50 rounded-lg p-3 border border-dark-border">
                <div className="text-xs text-dark-text-tertiary mb-1">API Key</div>
                <div className="text-sm font-mono text-dark-text-secondary">{savedConfig.api_key_preview || maskSecret(savedConfig.api_key)}</div>
              </div>
              <div className="bg-dark-primary/50 rounded-lg p-3 border border-dark-border">
                <div className="text-xs text-dark-text-tertiary mb-1">Webhook URL</div>
                <div className="text-sm font-mono text-dark-text-secondary truncate">{savedConfig.webhook_url || 'Not configured'}</div>
              </div>
            </div>
          </div>
          <div className="flex gap-2 ml-4">
            <button
              onClick={() => setShowForm(true)}
              className="btn-secondary text-sm px-4 py-2"
            >
              Edit
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 text-status-error hover:bg-status-error/10 rounded-lg transition text-sm font-medium"
            >
              Clear
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-accent-primary/10 rounded-lg flex items-center justify-center text-accent-primary">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h3 className="text-xl font-bold text-dark-text-primary">API Configuration</h3>
          <p className="text-sm text-dark-text-tertiary">VietCMS integration settings</p>
        </div>
      </div>

      {testResult && (
        <div className={`mb-6 p-4 rounded-lg border text-sm ${testResult.type === 'success'
            ? 'bg-status-success/10 border-status-success/20 text-status-success'
            : 'bg-status-error/10 border-status-error/20 text-status-error'
          }`}>
          <div className="flex items-center gap-2">
            {testResult.type === 'success' ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            <span className="font-medium">{testResult.message}</span>
          </div>
        </div>
      )}

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-dark-text-secondary mb-2">
            API Endpoint <span className="text-status-error">*</span>
          </label>
          <input
            type="url"
            value={config.api_url}
            onChange={(e) => setConfig({ ...config, api_url: e.target.value })}
            className="input font-mono text-sm"
            placeholder="https://api.vietcms.ai/api/v1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-text-secondary mb-2">
            API Key <span className="text-status-error">*</span>
          </label>
          <input
            type="text"
            value={config.api_key}
            onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
            className="input font-mono text-sm"
            placeholder="api_xxxxxxxxxxxxxxxx"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-text-secondary mb-2">
            HMAC Secret <span className="text-status-error">*</span>
          </label>
          <input
            type="password"
            value={config.hmac_secret}
            onChange={(e) => setConfig({ ...config, hmac_secret: e.target.value })}
            className="input font-mono text-sm"
            placeholder="hmac_xxxxxxxxxxxxxxxx"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-dark-text-secondary mb-2">
            Webhook URL
            <span className="text-dark-text-tertiary font-normal ml-2">(optional)</span>
          </label>
          <input
            type="url"
            value={config.webhook_url}
            onChange={(e) => setConfig({ ...config, webhook_url: e.target.value })}
            className="input font-mono text-sm"
            placeholder="https://your-tunnel.trycloudflare.com/webhooks/moderation"
          />
          <p className="text-xs text-dark-text-tertiary mt-2 font-mono">
            [TIP] Use cloudflared tunnel: cloudflared tunnel --url http://localhost:5000
          </p>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            onClick={handleTest}
            disabled={loading || !config.api_url || !config.api_key || !config.hmac_secret}
            className="btn-secondary"
          >
            {loading ? 'Testing...' : 'Test Connection'}
          </button>

          <button
            onClick={handleSave}
            disabled={loading || !config.api_url || !config.api_key || !config.hmac_secret}
            className="btn-primary"
          >
            {loading ? 'Saving...' : 'Save Configuration'}
          </button>

          {savedConfig && (
            <button
              onClick={() => setShowForm(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      <div className="mt-6 bg-dark-primary/30 rounded-lg p-4 border border-dark-border">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-accent-primary mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-sm text-dark-text-secondary">
            <div className="font-semibold text-dark-text-primary mb-2">Setup Instructions:</div>
            <ol className="space-y-1 text-dark-text-tertiary">
              <li>1. Login to <a href="http://localhost/client-login" target="_blank" className="text-accent-primary hover:text-accent-secondary underline">VietCMS Dashboard</a></li>
              <li>2. Copy API Key and HMAC Secret</li>
              <li>3. Paste into this form and click "Save Configuration"</li>
              <li>4. Submit content to test integration</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}

