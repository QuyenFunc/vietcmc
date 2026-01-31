export default function ProductCard() {
  return (
    <div className="card p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-dark-text-primary mb-2">
            AI Content Analyzer
          </h2>
          <div className="flex items-center gap-3">
            <span className="badge bg-accent-primary/10 text-accent-primary border border-accent-primary/20">
              v2.0.1
            </span>
            <span className="badge bg-status-success/10 text-status-success border border-status-success/20">
              ACTIVE
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-dark-text-primary">99.8%</div>
          <div className="text-dark-text-tertiary text-sm">Accuracy Rate</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-dark-primary/50 rounded-lg p-3 border border-dark-border">
          <div className="text-dark-text-tertiary text-xs mb-1">Speed</div>
          <div className="text-lg font-bold text-dark-text-primary">0.3ms</div>
        </div>

        <div className="bg-dark-primary/50 rounded-lg p-3 border border-dark-border">
          <div className="text-dark-text-tertiary text-xs mb-1">Uptime</div>
          <div className="text-lg font-bold text-dark-text-primary">99.9%</div>
        </div>

        <div className="bg-dark-primary/50 rounded-lg p-3 border border-dark-border">
          <div className="text-dark-text-tertiary text-xs mb-1">Processed</div>
          <div className="text-lg font-bold text-dark-text-primary">2.5M+</div>
        </div>
      </div>

      <div className="space-y-3 mb-6">
        <div className="flex items-center gap-3 text-sm text-dark-text-secondary">
          <svg className="w-4 h-4 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>Multi-language support (50+ languages)</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-dark-text-secondary">
          <svg className="w-4 h-4 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>Real-time content analysis</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-dark-text-secondary">
          <svg className="w-4 h-4 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>Advanced toxicity detection</span>
        </div>
      </div>

      <div className="flex gap-3">
        <button className="btn-primary flex-1 flex items-center justify-center gap-2">
          View Analytics
        </button>
        <button className="btn-secondary flex-1 flex items-center justify-center gap-2">
          Configure
        </button>
      </div>
    </div>
  )
}

