import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { SplashScreen } from './components/UI'
import { apiRequest } from './lib/api'
import { DoctorDashboard } from './pages/DoctorDashboard'
import { LoginPage } from './pages/LoginPage'
import { MeetingRoom } from './pages/MeetingRoom'
import { PatientDashboard } from './pages/PatientDashboard'

const SESSION_KEY = 'lucent.hackathon.session'

function getHomeRoute(role) {
  return role === 'doctor' ? '/doctor' : '/patient'
}

function ProtectedRoute({ session, role, children }) {
  if (!session.token || !session.user) {
    return <Navigate to="/login" replace />
  }
  if (role && session.user.role !== role) {
    return <Navigate to={getHomeRoute(session.user.role)} replace />
  }
  return children
}

function App() {
  const [session, setSession] = useState(() => {
    const saved = window.localStorage.getItem(SESSION_KEY)
    return saved ? JSON.parse(saved) : { token: '', user: null }
  })
  const [booting, setBooting] = useState(Boolean(session.token))

  useEffect(() => {
    if (!session.token) {
      setBooting(false)
      return
    }

    let ignore = false

    async function validateSession() {
      try {
        const response = await apiRequest('/api/auth/me/', { token: session.token })
        if (ignore) {
          return
        }

        const nextSession = { token: session.token, user: response.user }
        setSession(nextSession)
        window.localStorage.setItem(SESSION_KEY, JSON.stringify(nextSession))
      } catch {
        if (!ignore) {
          clearSession()
        }
      } finally {
        if (!ignore) {
          setBooting(false)
        }
      }
    }

    validateSession()

    return () => {
      ignore = true
    }
  }, [session.token])

  function clearSession() {
    const nextSession = { token: '', user: null }
    setSession(nextSession)
    window.localStorage.removeItem(SESSION_KEY)
  }

  function handleAuthenticated(response) {
    const nextSession = { token: response.token, user: response.user }
    setSession(nextSession)
    window.localStorage.setItem(SESSION_KEY, JSON.stringify(nextSession))
  }

  async function handleLogout() {
    try {
      if (session.token) {
        await apiRequest('/api/auth/logout/', { method: 'POST', token: session.token })
      }
    } catch {
      // Keep logout resilient in local demos.
    } finally {
      clearSession()
    }
  }

  if (booting) {
    return <SplashScreen />
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={
          session.token && session.user ? (
            <Navigate to={getHomeRoute(session.user.role)} replace />
          ) : (
            <LoginPage onAuthenticated={handleAuthenticated} />
          )
        }
      />
      <Route
        path="/doctor"
        element={
          <ProtectedRoute session={session} role="doctor">
            <AppShell session={session} onLogout={handleLogout}>
              <DoctorDashboard token={session.token} />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/patient"
        element={
          <ProtectedRoute session={session} role="patient">
            <AppShell session={session} onLogout={handleLogout}>
              <PatientDashboard token={session.token} />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/meeting/:appointmentId"
        element={
          <ProtectedRoute session={session}>
            <AppShell session={session} onLogout={handleLogout} compact>
              <MeetingRoom token={session.token} session={session} />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="*"
        element={<Navigate to={session.token ? getHomeRoute(session.user.role) : '/login'} replace />}
      />
    </Routes>
  )
}

export default App
