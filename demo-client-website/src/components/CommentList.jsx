import React, { useState, useEffect, useRef, useMemo } from 'react'

const STATUS_CONFIG = {
  pending: {
    label: 'Processing',
    bgColor: 'bg-dark-tertiary',
    borderColor: 'border-dark-border',
    textColor: 'text-dark-text-secondary',
    badgeBg: 'bg-yellow-500/10',
    badgeText: 'text-yellow-500',
    badgeBorder: 'border-yellow-500/20',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  },
  allowed: {
    label: 'Approved',
    bgColor: 'bg-dark-tertiary',
    borderColor: 'border-dark-border',
    textColor: 'text-dark-text-primary',
    badgeBg: 'bg-status-success/10',
    badgeText: 'text-status-success',
    badgeBorder: 'border-status-success/20',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    )
  },
  review: {
    label: 'Review Needed',
    bgColor: 'bg-dark-tertiary',
    borderColor: 'border-status-warning/30',
    textColor: 'text-dark-text-primary',
    badgeBg: 'bg-status-warning/10',
    badgeText: 'text-status-warning',
    badgeBorder: 'border-status-warning/20',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    )
  },
  reject: {
    label: 'Rejected',
    bgColor: 'bg-dark-tertiary',
    borderColor: 'border-status-error/30',
    textColor: 'text-dark-text-secondary',
    badgeBg: 'bg-status-error/10',
    badgeText: 'text-status-error',
    badgeBorder: 'border-status-error/20',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    )
  }
}

function CommentItem({ comment, isHighlighted }) {
  const status = comment.moderation_result || 'pending'
  const config = STATUS_CONFIG[status]

  return (
    <div
      id={`comment-${comment.id}`}
      className={`bg-dark-secondary border border-dark-border rounded-lg p-5 transition-all duration-300 hover:border-dark-text-quaternary ${status === 'reject' ? 'opacity-75' : ''} ${isHighlighted ? 'ring-2 ring-accent-primary animate-pulse' : ''}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-dark-tertiary rounded-full flex items-center justify-center text-dark-text-secondary font-bold text-sm border border-dark-border">
            {comment.author.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="font-medium text-dark-text-primary text-sm">{comment.author}</div>
            <div className="text-xs text-dark-text-tertiary">
              {new Date(comment.created_at).toLocaleString('en-US')}
            </div>
          </div>
        </div>

        <div className={`flex items-center gap-1.5 ${config.badgeBg} ${config.badgeText} px-2.5 py-1 rounded-full text-xs font-medium border ${config.badgeBorder}`}>
          {config.icon}
          <span>{config.label}</span>
        </div>
      </div>

      {/* Comment Text */}
      <div className={`text-sm leading-relaxed mb-4 ${status === 'reject' ? 'text-dark-text-tertiary line-through' : 'text-dark-text-secondary'}`}>
        {comment.type === 'image' ? (
          <div className="mt-2">
            <img
              src={comment.text}
              alt="User content"
              className="max-w-full h-auto rounded-lg max-h-72 border border-dark-border object-contain bg-black/20"
              onError={(e) => { e.target.style.display = 'none'; e.target.parentElement.innerText = '❌ Failed to load image' }}
            />
            <a href={comment.text} target="_blank" rel="noopener noreferrer" className="block text-xs text-accent-primary mt-1 hover:underline truncate">
              {comment.text}
            </a>
            {comment.extracted_text !== undefined && (
              <div className="mt-2 p-2 bg-dark-tertiary/50 rounded-lg border border-dark-border">
                <div className="text-xs text-dark-text-tertiary uppercase font-bold tracking-wider mb-1">📝 OCR Extracted Text</div>
                <div className="text-sm text-dark-text-primary font-mono">
                  {comment.extracted_text ? `"${comment.extracted_text}"` : <span className="text-status-warning italic">Could not extract text from image</span>}
                </div>
              </div>
            )}
          </div>
        ) : comment.type === 'audio' ? (
          <div className="mt-2 bg-dark-tertiary/50 p-3 rounded-lg border border-dark-border">
            <audio controls src={comment.text} className="w-full mb-2" />
            <a href={comment.text} target="_blank" rel="noopener noreferrer" className="block text-xs text-accent-primary hover:underline truncate mb-2">
              Source: {comment.text}
            </a>
            {comment.transcribed_text && (
              <div className="text-xs text-dark-text-secondary border-t border-dark-border pt-2 mt-2">
                <span className="text-dark-text-tertiary uppercase text-[10px] font-bold tracking-wider block mb-1">Transcript</span>
                "{comment.transcribed_text}"
              </div>
            )}
          </div>
        ) : (
          comment.text
        )}
      </div>

      {/* Moderation Info */}
      {comment.moderation_result && (
        <div className="bg-dark-primary/50 rounded-lg p-4 text-sm border border-dark-border">
          <div className="flex items-center gap-2 font-medium text-dark-text-primary mb-3 text-xs uppercase tracking-wider">
            <svg className="w-4 h-4 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            AI Analysis
          </div>

          <div className="grid grid-cols-3 gap-4 mb-3">
            <div>
              <div className="text-dark-text-tertiary text-xs mb-1">Sentiment</div>
              <div className={`font-medium text-sm ${comment.sentiment === 'positive' ? 'text-status-success' :
                comment.sentiment === 'negative' ? 'text-status-error' :
                  'text-dark-text-secondary'
                }`}>
                {comment.sentiment === 'positive' ? 'Positive' :
                  comment.sentiment === 'negative' ? 'Negative' :
                    'Neutral'}
              </div>
            </div>

            <div>
              <div className="text-dark-text-tertiary text-xs mb-1">Confidence</div>
              <div className="font-medium text-dark-text-primary text-sm">
                {comment.confidence ? (comment.confidence * 100).toFixed(1) + '%' : 'N/A'}
              </div>
            </div>

            <div>
              <div className="text-dark-text-tertiary text-xs mb-1">Time</div>
              <div className="font-medium text-dark-text-primary text-sm">
                {comment.processing_time ? comment.processing_time + 'ms' : 'N/A'}
              </div>
            </div>
          </div>

          {comment.reasoning && (
            <div className="pt-3 border-t border-dark-border">
              <div className="text-dark-text-tertiary text-xs mb-1">Reasoning</div>
              <div className="text-dark-text-secondary text-xs">{comment.reasoning}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const SectionHeader = ({ title, count, color, icon, id }) => {
  if (count === 0) return null

  return (
    <div id={id} className={`flex items-center gap-2 py-2 px-3 rounded-lg border ${color} mb-3 mt-6 first:mt-0 scroll-mt-24`}>
      {icon}
      <span className="font-semibold text-sm">{title}</span>
      <span className="ml-auto text-xs opacity-75">{count}</span>
    </div>
  )
}

// Quick Navigation Tabs Component with NEW badge
const QuickNav = ({ counts, newCounts, onNavigate, activeSection, onMarkAsSeen }) => {
  const tabs = [
    { key: 'allowed', label: '✅ Approved', count: counts.allowed, newCount: newCounts.allowed, color: 'text-status-success bg-status-success/10 border-status-success/30', newBadgeColor: 'bg-status-success text-white' },
    { key: 'review', label: '⚠️ Review', count: counts.review, newCount: newCounts.review, color: 'text-status-warning bg-status-warning/10 border-status-warning/30', newBadgeColor: 'bg-status-warning text-black' },
    { key: 'reject', label: '❌ Rejected', count: counts.reject, newCount: newCounts.reject, color: 'text-status-error bg-status-error/10 border-status-error/30', newBadgeColor: 'bg-status-error text-white' },
    { key: 'pending', label: '⏳ Processing', count: counts.pending, newCount: newCounts.pending, color: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30', newBadgeColor: 'bg-yellow-500 text-black' },
  ]

  const visibleTabs = tabs.filter(t => t.count > 0)
  if (visibleTabs.length === 0) return null

  const handleClick = (tabKey) => {
    onNavigate(tabKey)
    // Mark comments in this section as seen
    if (onMarkAsSeen) {
      onMarkAsSeen(tabKey)
    }
  }

  return (
    <div className="sticky top-20 z-40 bg-dark-primary/90 backdrop-blur-sm pt-5 pb-3 -mx-6 px-6 mb-4 border-b border-dark-border">
      <div className="flex items-center gap-3 overflow-x-auto overflow-y-visible">
        <span className="text-xs text-dark-text-tertiary font-medium whitespace-nowrap">Quick Jump:</span>
        {visibleTabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => handleClick(tab.key)}
            className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all whitespace-nowrap hover:scale-105 ${tab.color} ${activeSection === tab.key ? 'ring-2 ring-accent-primary' : ''}`}
          >
            <span>{tab.label}</span>
            <span className="font-bold">({tab.count})</span>

            {/* NEW badge */}
            {tab.newCount > 0 && (
              <span className={`absolute -top-2 -right-2 min-w-[20px] h-5 px-1.5 rounded-full ${tab.newBadgeColor} text-[10px] font-bold flex items-center justify-center animate-pulse shadow-lg`}>
                +{tab.newCount}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}


export default function CommentList({ comments, loading, highlightId }) {
  const [activeSection, setActiveSection] = useState(null)
  const [seenCommentIds, setSeenCommentIds] = useState(() => {
    // Load seen IDs from localStorage on mount
    try {
      const saved = localStorage.getItem('seenCommentIds')
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })
  const containerRef = useRef(null)

  // Save seen IDs to localStorage when changed
  useEffect(() => {
    try {
      localStorage.setItem('seenCommentIds', JSON.stringify(seenCommentIds))
    } catch {
      // Ignore localStorage errors
    }
  }, [seenCommentIds])

  // Group comments by status (memoized for performance)
  const groupedComments = useMemo(() => {
    const groups = {
      allowed: [],
      review: [],
      reject: [],
      pending: []
    }

    comments.forEach(comment => {
      const status = comment.moderation_result || comment.status || 'pending'
      if (groups[status]) {
        groups[status].push(comment)
      } else {
        groups.pending.push(comment)
      }
    })

    // Sort within each group by newest first
    Object.keys(groups).forEach(key => {
      groups[key].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    })

    return groups
  }, [comments])

  // Scroll to section when navigating
  const handleNavigate = (sectionKey) => {
    const element = document.getElementById(`section-${sectionKey}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setActiveSection(sectionKey)
      // Remove highlight after 2 seconds
      setTimeout(() => setActiveSection(null), 2000)
    }
  }

  // Mark comments in a section as seen
  const markSectionAsSeen = (sectionKey) => {
    const sectionComments = groupedComments[sectionKey] || []
    const newSeenIds = sectionComments
      .map(c => c.id)
      .filter(id => id && !seenCommentIds.includes(id))

    if (newSeenIds.length > 0) {
      setSeenCommentIds(prev => [...prev, ...newSeenIds])
    }
  }

  // Scroll to highlighted comment when it changes
  useEffect(() => {
    if (highlightId) {
      const element = document.getElementById(`comment-${highlightId}`)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  }, [highlightId])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-dark-text-tertiary">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary mb-3"></div>
        <p className="text-sm">Loading comments...</p>
      </div>
    )
  }

  if (comments.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-dark-tertiary rounded-full flex items-center justify-center mx-auto mb-4 text-dark-text-quaternary">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <p className="text-dark-text-secondary font-medium mb-1">No comments yet</p>
        <p className="text-dark-text-tertiary text-sm">Submit a comment to see AI analysis in action</p>
      </div>
    )
  }

  // Calculate counts
  const counts = {
    allowed: groupedComments.allowed.length,
    review: groupedComments.review.length,
    reject: groupedComments.reject.length,
    pending: groupedComments.pending.length
  }

  // Calculate NEW counts (comments not yet seen)
  const newCounts = {
    allowed: groupedComments.allowed.filter(c => c.id && !seenCommentIds.includes(c.id)).length,
    review: groupedComments.review.filter(c => c.id && !seenCommentIds.includes(c.id)).length,
    reject: groupedComments.reject.filter(c => c.id && !seenCommentIds.includes(c.id)).length,
    pending: groupedComments.pending.filter(c => c.id && !seenCommentIds.includes(c.id)).length
  }

  return (
    <div ref={containerRef} className="space-y-1">
      {/* Quick Navigation with NEW badges */}
      <QuickNav
        counts={counts}
        newCounts={newCounts}
        onNavigate={handleNavigate}
        activeSection={activeSection}
        onMarkAsSeen={markSectionAsSeen}
      />


      {/* Approved Section */}
      <SectionHeader
        id="section-allowed"
        title="✅ Approved Comments"
        count={groupedComments.allowed.length}
        color="bg-status-success/5 border-status-success/20 text-status-success"
        icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>}
      />
      {groupedComments.allowed.map((comment, index) => (
        <CommentItem
          key={comment.id || `allowed-${index}`}
          comment={comment}
          isHighlighted={highlightId === comment.id}
        />
      ))}

      {/* Review Section */}
      <SectionHeader
        id="section-review"
        title="⚠️ Needs Review"
        count={groupedComments.review.length}
        color="bg-status-warning/5 border-status-warning/20 text-status-warning"
        icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>}
      />
      {groupedComments.review.map((comment, index) => (
        <CommentItem
          key={comment.id || `review-${index}`}
          comment={comment}
          isHighlighted={highlightId === comment.id}
        />
      ))}

      {/* Rejected Section */}
      <SectionHeader
        id="section-reject"
        title="❌ Rejected Comments"
        count={groupedComments.reject.length}
        color="bg-status-error/5 border-status-error/20 text-status-error"
        icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>}
      />
      {groupedComments.reject.map((comment, index) => (
        <CommentItem
          key={comment.id || `reject-${index}`}
          comment={comment}
          isHighlighted={highlightId === comment.id}
        />
      ))}

      {/* Processing Section */}
      <SectionHeader
        id="section-pending"
        title="⏳ Processing"
        count={groupedComments.pending.length}
        color="bg-yellow-500/5 border-yellow-500/20 text-yellow-500"
        icon={<svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>}
      />
      {groupedComments.pending.map((comment, index) => (
        <CommentItem
          key={comment.id || `pending-${index}`}
          comment={comment}
          isHighlighted={highlightId === comment.id}
        />
      ))}
    </div>
  )
}
