import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import apiClient from '../utils/apiClient'

export default function Jobs() {
  const queryClient = useQueryClient()
  const [showConfirm, setShowConfirm] = useState(false)

  const { data: jobsData, isLoading, error } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const res = await apiClient.get('/admin/jobs?page=1&per_page=50')
      return res.data.data
    },
    refetchInterval: 5000,
  })

  const clearJobsMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.delete('/admin/jobs/clear')
      return res.data
    },
    onSuccess: (data) => {
      alert(`✅ Deleted ${data.data.deleted_count} jobs successfully!`)
      queryClient.invalidateQueries(['jobs'])
      setShowConfirm(false)
    },
    onError: (error) => {
      alert(`❌ Error: ${error.message}`)
    }
  })

  const jobs = jobsData?.jobs || []
  const totalJobs = jobsData?.total || 0

  const queuedCount = jobs.filter(j => j.status === 'queued').length
  const processingCount = jobs.filter(j => j.status === 'processing').length
  const completedCount = jobs.filter(j => j.status === 'completed').length

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0 flex justify-center items-center min-h-screen">
        <div className="text-lg text-gray-600">Loading jobs...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error loading jobs</h3>
          <p className="text-red-600 text-sm mt-1">{error.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Jobs Queue Monitor</h1>

        <div className="flex gap-2">
          <div className="text-sm text-gray-600 py-2 px-3 bg-gray-100 rounded">
            Total: <span className="font-bold">{totalJobs}</span> jobs
          </div>
          <button
            onClick={() => setShowConfirm(true)}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition font-medium"
          >
            🗑️ Clear All Jobs
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4">
            <h3 className="text-lg font-bold text-gray-900 mb-2">⚠️ Confirm Delete</h3>
            <p className="text-gray-600 mb-4">
              Are you sure you want to delete all <strong>{totalJobs} jobs</strong> from the database?
              <br />
              <span className="text-red-600 text-sm">This action cannot be undone!</span>
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => clearJobsMutation.mutate()}
                disabled={clearJobsMutation.isPending}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition disabled:opacity-50"
              >
                {clearJobsMutation.isPending ? 'Deleting...' : 'Delete All'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow sm:rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{queuedCount}</div>
              <div className="text-sm text-gray-500">Queued</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-600">{processingCount}</div>
              <div className="text-sm text-gray-500">Processing</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{completedCount}</div>
              <div className="text-sm text-gray-500">Completed</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Job ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Text
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Result
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Time
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">
                  No jobs found
                </td>
              </tr>
            ) : (
              jobs.map((job) => (
                <tr key={job.job_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                    {job.job_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {job.text}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${job.status === 'completed' ? 'bg-green-100 text-green-800' :
                        job.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                          job.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                      }`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {job.moderation_result && (
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${job.moderation_result === 'allowed' ? 'bg-green-100 text-green-800' :
                          job.moderation_result === 'review' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                        }`}>
                        {job.moderation_result}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.processing_duration_ms ? `${job.processing_duration_ms}ms` : '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

