import { startTransition, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiRequest } from '../lib/api'

function getHomeRoute(role) {
  return role === 'doctor' ? '/doctor' : '/patient'
}

export function LoginPage({ onAuthenticated }) {
  const [username, setUsername] = useState('doctor.rao')
  const [password, setPassword] = useState('Doctor@123')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      const response = await apiRequest('/api/auth/login/', {
        method: 'POST',
        body: { username, password },
      })

      startTransition(() => {
        onAuthenticated(response)
        navigate(getHomeRoute(response.user.role), { replace: true })
      })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-shell">
      <section className="login-hero">
        <span className="eyebrow">Lucent Sync</span>
        <h1>Doctor-guided telehealth built for a hackathon, not a legacy ops dashboard.</h1>
        <p>
          The product now has only two roles. The doctor controls schedule, kanban flow, and live
          sessions. The patient books with PulseMatch Copilot and joins a real local WebRTC room.
        </p>

        <div className="hero-points">
          <article>
            <strong>PulseMatch Copilot</strong>
            <span>Turns raw symptoms into urgency, prep checklist, and slot suggestions.</span>
          </article>
          <article>
            <strong>Doctor-controlled Kanban</strong>
            <span>Moves appointments from requested to live without an admin panel.</span>
          </article>
          <article>
            <strong>Local-first WebRTC</strong>
            <span>Works for localhost testing in two tabs or two browsers before hosting.</span>
          </article>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div>
            <span className="eyebrow">Role Access</span>
            <h2>Enter the demo</h2>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              <span>Username</span>
              <input value={username} onChange={(event) => setUsername(event.target.value)} />
            </label>
            <label>
              <span>Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error ? <p className="form-error">{error}</p> : null}
            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? 'Entering...' : 'Open product'}
            </button>
          </form>

          <div className="demo-card-grid">
            <button
              type="button"
              className="demo-card"
              onClick={() => {
                setUsername('doctor.rao')
                setPassword('Doctor@123')
              }}
            >
              <strong>Doctor</strong>
              <span>`doctor.rao` / `Doctor@123`</span>
            </button>
            <button
              type="button"
              className="demo-card"
              onClick={() => {
                setUsername('patient.asha')
                setPassword('Patient@123')
              }}
            >
              <strong>Patient</strong>
              <span>`patient.asha` / `Patient@123`</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}
