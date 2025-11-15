import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import ClientLogin from './pages/ClientLogin'
import ClientDashboard from './pages/ClientDashboard'
import Dashboard from './pages/Dashboard'
import Clients from './pages/Clients'
import Jobs from './pages/Jobs'
import Logs from './pages/Logs'
import Layout from './components/Layout'
import { useAuthStore } from './stores/authStore'

function PrivateRoute({ children }) {
  const { token } = useAuthStore()
  return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      {/* Removed local Register route so /register is served by API */}
      <Route path="/client-login" element={<ClientLogin />} />
      <Route path="/client-dashboard" element={<ClientDashboard />} />
      
      {/* Admin routes (protected) */}
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="clients" element={<Clients />} />
        <Route path="jobs" element={<Jobs />} />
        <Route path="logs" element={<Logs />} />
      </Route>
    </Routes>
  )
}

export default App

