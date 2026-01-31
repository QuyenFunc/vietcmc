import { useState, useRef } from 'react'
import { Tab } from '@headlessui/react'

const EXAMPLE_COMMENTS = [
  "Very helpful and informative article! Thanks for sharing 👍",
  "This video is amazing, just subscribed! 🔥",
  "Thank you for sharing your experience, very useful!",
  "Garbage, not worth watching!",
  "Fraud shop, everyone be careful!",
]

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function CommentForm({ onSubmit }) {
  const [author, setAuthor] = useState('Customer A')
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [type, setType] = useState('text')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    // Limit file size (e.g., 5MB)
    if (selectedFile.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'File too large (max 5MB)' })
      return
    }

    setFile(selectedFile)

    // Create preview
    const objectUrl = URL.createObjectURL(selectedFile)
    setPreview(objectUrl)
    setMessage('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    let contentToSubmit = text

    if (type !== 'text') {
      if (!file) {
        setMessage({ type: 'error', text: `Please select a ${type} file` })
        return
      }
      // For demo: convert file to Base64 to simulate upload URL/content
      // in production, you would upload to S3/Cloudinary first and get URL
      const reader = new FileReader()
      reader.readAsDataURL(file)

      setLoading(true)

      reader.onload = async () => {
        contentToSubmit = reader.result // Base64 string

        await submitData(contentToSubmit)
      }
      reader.onerror = () => {
        setLoading(false)
        setMessage({ type: 'error', text: 'File read error' })
      }
      return
    }

    if (!text.trim()) {
      setMessage({ type: 'error', text: 'Please enter content' })
      return
    }

    setLoading(true)
    await submitData(contentToSubmit)
  }

  const submitData = async (content) => {
    const result = await onSubmit({
      author,
      text: content,
      type
    })

    if (result.success) {
      // Enhanced success message with navigation options
      setMessage({
        type: 'success',
        text: '✅ Moderation request sent!',
        comment: result.comment, // Store the comment for navigation
        showNavigation: true
      })
      setText('')
      setFile(null)
      setPreview(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      // Don't auto-dismiss - let user click to navigate
    } else {
      setMessage({ type: 'error', text: '❌ An error occurred!' })
      setTimeout(() => setMessage(''), 3000)
    }
    setLoading(false)
  }

  // Scroll to result section
  const scrollToResult = (sectionId) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      // Add temporary highlight effect
      element.classList.add('ring-2', 'ring-accent-primary')
      setTimeout(() => {
        element.classList.remove('ring-2', 'ring-accent-primary')
      }, 2000)
    }
    setMessage('') // Clear message after navigation
  }


  const fillExample = () => {
    if (type !== 'text') return
    const randomExample = EXAMPLE_COMMENTS[Math.floor(Math.random() * EXAMPLE_COMMENTS.length)]
    setText(randomExample)
  }

  const resetForm = (newType) => {
    setType(newType)
    setText('')
    setFile(null)
    setPreview(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
    setMessage('')
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-dark-text-primary flex items-center gap-2">
          Moderation Demo
        </h3>
        <div className="flex items-center gap-2">
          <span className="badge bg-status-success/10 text-status-success border border-status-success/20">
            AI Ready
          </span>
        </div>
      </div>

      <Tab.Group onChange={(index) => {
        const types = ['text', 'image']
        resetForm(types[index])
      }}>
        <Tab.List className="flex space-x-1 rounded-xl bg-dark-secondary p-1 mb-5">
          {['Text', 'Upload Image'].map((category) => (
            <Tab
              key={category}
              className={({ selected }) =>
                classNames(
                  'w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all',
                  selected
                    ? 'bg-accent-primary text-white shadow font-bold'
                    : 'text-dark-text-secondary hover:bg-white/[0.12] hover:text-white'
                )
              }
            >
              {category}
            </Tab>
          ))}
        </Tab.List>
      </Tab.Group>

      {message && (
        <div className={`mb-6 p-4 rounded-lg border text-sm ${message.type === 'success'
          ? 'bg-status-success/10 border-status-success/20 text-status-success'
          : 'bg-status-error/10 border-status-error/20 text-status-error'
          }`}>
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <span className="font-medium">{message.text}</span>
            {message.type === 'success' && (
              <button
                type="button"
                onClick={() => setMessage('')}
                className="text-xs opacity-60 hover:opacity-100 transition-opacity"
              >
                ✕ Close
              </button>
            )}
          </div>

          {/* Quick Navigation Buttons */}
          {message.showNavigation && (
            <div className="mt-3 pt-3 border-t border-status-success/20">
              <div className="text-xs opacity-75 mb-2">📍 Click to view results:</div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => scrollToResult('section-pending')}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-500 border border-yellow-500/30 hover:bg-yellow-500/30 transition-all hover:scale-105"
                >
                  ⏳ Processing
                </button>
                <button
                  type="button"
                  onClick={() => scrollToResult('section-allowed')}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium bg-status-success/20 text-status-success border border-status-success/30 hover:bg-status-success/30 transition-all hover:scale-105"
                >
                  ✅ Approved
                </button>
                <button
                  type="button"
                  onClick={() => scrollToResult('section-review')}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium bg-status-warning/20 text-status-warning border border-status-warning/30 hover:bg-status-warning/30 transition-all hover:scale-105"
                >
                  ⚠️ Review
                </button>
                <button
                  type="button"
                  onClick={() => scrollToResult('section-reject')}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium bg-status-error/20 text-status-error border border-status-error/30 hover:bg-status-error/30 transition-all hover:scale-105"
                >
                  ❌ Rejected
                </button>
              </div>
            </div>
          )}
        </div>
      )}


      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-dark-text-secondary mb-2">
            User Name
          </label>
          <input
            type="text"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="input"
            placeholder="Enter user name..."
            required
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-dark-text-secondary">
              {type === 'text' ? 'Content' : `Upload ${type === 'image' ? 'image' : 'audio'} file`}
            </label>
            {type === 'text' && (
              <button
                type="button"
                onClick={fillExample}
                className="text-xs text-accent-primary hover:text-accent-secondary font-medium transition-colors"
              >
                Auto-fill Example
              </button>
            )}
          </div>

          {type === 'text' ? (
            <div className="relative">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="input resize-none w-full"
                rows="4"
                placeholder="Type a comment to analyze..."
              />
              <div className="absolute bottom-2 right-2 text-xs text-dark-text-tertiary">
                {text.length} chars
              </div>
            </div>
          ) : (
            <div className="border-2 border-dashed border-dark-border rounded-lg p-6 text-center hover:border-accent-primary/50 transition-colors bg-dark-secondary/30">
              <input
                ref={fileInputRef}
                type="file"
                accept={type === 'image' ? "image/*" : "audio/*"}
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />

              {!preview ? (
                <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-full bg-dark-tertiary flex items-center justify-center">
                    <svg className="w-6 h-6 text-dark-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <span className="text-sm font-medium text-accent-primary">Click to upload {type === 'image' ? 'image' : 'audio'} file</span>
                  <span className="text-xs text-dark-text-tertiary">Max size: 5MB</span>
                </label>
              ) : (
                <div className="relative">
                  {type === 'image' ? (
                    <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded-lg object-contain" />
                  ) : (
                    <div className="bg-dark-tertiary p-4 rounded-lg flex items-center gap-3 justify-center">
                      <svg className="w-8 h-8 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 10l12-3" />
                      </svg>
                      <span className="text-sm font-medium text-dark-text-primary truncate max-w-[200px]">
                        {file?.name}
                      </span>
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => {
                      setFile(null)
                      setPreview(null)
                      if (fileInputRef.current) fileInputRef.current.value = ''
                    }}
                    className="absolute -top-2 -right-2 bg-status-error text-white rounded-full p-1 hover:bg-red-600 transition-colors shadow-lg"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading || (type !== 'text' && !file) || (type === 'text' && !text.trim())}
          className="btn-primary w-full flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              Submit for Analysis
            </span>
          )}
        </button>
      </form>
    </div>
  )
}

