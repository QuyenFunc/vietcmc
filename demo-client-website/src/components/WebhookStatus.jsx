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
    <div className={`card p-6 border-l-4 ${isHttps
        ? 'border-l-status-success'
        : 'border-l-status-warning'
      }`}>
      <div className="flex items-start gap-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isHttps
            ? 'bg-status-success/10 text-status-success'
            : 'bg-status-warning/10 text-status-warning'
          }`}>
          {isHttps ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
            </svg>
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-3 mb-4">
            <h4 className={`text-lg font-bold ${isHttps ? 'text-status-success' : 'text-status-warning'
              }`}>
              {isHttps ? 'Secure Webhook Endpoint' : 'Local Webhook Endpoint'}
            </h4>
            <div className={`px-2 py-0.5 rounded-full text-xs font-medium ${isHttps
                ? 'bg-status-success/10 text-status-success border border-status-success/20'
                : 'bg-status-warning/10 text-status-warning border border-status-warning/20'
              }`}>
              {isHttps ? 'HTTPS' : 'HTTP'}
            </div>
          </div>

          <div className="bg-dark-primary/50 rounded-lg p-3 font-mono text-sm break-all border border-dark-border mb-4">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-dark-text-tertiary flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              <span className="text-dark-text-secondary">{webhookUrl || 'Loading...'}</span>
            </div>
          </div>

          <div className="space-y-3">
            {isHttps ? (
              <div className="flex items-center gap-3 p-3 bg-status-success/5 rounded-lg border border-status-success/10">
                <svg className="w-5 h-5 text-status-success flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <div className="font-medium text-status-success text-sm">Secure Connection Active</div>
                  <div className="text-xs text-dark-text-tertiary">Ready to receive webhooks from VietCMS</div>
                </div>
              </div>
            ) : (
              <div className="p-3 bg-status-warning/5 rounded-lg border border-status-warning/10">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-status-warning" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span className="font-medium text-status-warning text-sm">Local Development Mode</span>
                </div>
                <div className="text-xs text-dark-text-secondary mb-2">For HTTPS tunnel, run:</div>
                <div className="bg-dark-primary rounded p-2 font-mono text-xs text-accent-primary border border-dark-border inline-block">
                  ngrok http 5000
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 flex items-center gap-2 text-xs text-dark-text-tertiary">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>VietCMS will POST moderation results to this endpoint</span>
          </div>
        </div>
      </div>
    </div>
  )
}

