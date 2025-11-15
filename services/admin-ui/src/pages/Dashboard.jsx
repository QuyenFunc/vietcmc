import { useQuery } from '@tanstack/react-query'
import apiClient from '../utils/apiClient'

export default function Dashboard() {
  const { data: healthData, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await apiClient.get('/health')
      return res.data
    },
    refetchInterval: 30000,
  })
  
  const { data: statsData, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await apiClient.get('/admin/stats')
      return res.data.data
    },
    refetchInterval: 10000,
  })
  
  if (statsLoading || healthLoading) {
    return (
      <div className="px-4 py-6 sm:px-0 flex justify-center items-center min-h-screen">
        <div className="text-lg text-gray-600">Loading dashboard...</div>
      </div>
    )
  }

  if (statsError || healthError) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error loading dashboard</h3>
          <p className="text-red-600 text-sm mt-1">
            {statsError?.message || healthError?.message || 'Failed to load data'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard Overview</h1>
      
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-12 w-12 bg-indigo-500 rounded-md flex items-center justify-center text-white text-2xl font-bold">
                  {statsData?.jobs_today || 0}
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Jobs Today</dt>
                  <dd className="text-3xl font-semibold text-gray-900">{statsData?.jobs_today || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-12 w-12 bg-green-500 rounded-md flex items-center justify-center text-white text-2xl font-bold">
                  {statsData?.active_clients || 0}
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Clients</dt>
                  <dd className="text-3xl font-semibold text-gray-900">{statsData?.active_clients || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-12 w-12 bg-yellow-500 rounded-md flex items-center justify-center text-white text-2xl font-bold">
                  {statsData?.success_rate ? Math.round(statsData.success_rate) : '--'}
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                  <dd className="text-3xl font-semibold text-gray-900">{statsData?.success_rate ? `${Math.round(statsData.success_rate)}%` : '--'}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">System Health</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Status</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              healthData?.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {healthData?.status || 'unknown'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Database</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              healthData?.services?.database === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {healthData?.services?.database || 'unknown'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Message Broker</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              healthData?.services?.message_broker === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {healthData?.services?.message_broker || 'unknown'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

