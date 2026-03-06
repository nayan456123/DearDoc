import { startTransition, useDeferredValue, useEffect, useState } from 'react'
import {
  Navigate,
  NavLink,
  Outlet,
  Route,
  Routes,
  useOutletContext,
} from 'react-router-dom'
import { apiRequest } from './lib/api'

const SESSION_KEY = 'lucent.session'

const NAV_ITEMS = [
  { to: '/', label: 'Command Center' },
  { to: '/patients', label: 'Patient Ledger' },
  { to: '/appointments', label: 'Runway' },
  { to: '/clinicians', label: 'Clinical Network' },
  { to: '/intake', label: 'Intake Board' },
]

function useApiResource(path, token, initialValue, pollMs = 0) {
  const [data, setData] = useState(initialValue)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    let ignore = false

    async function load() {
      setLoading(true)
      setError('')
      try {
        const next = await apiRequest(path, { token })
        if (!ignore) {
          setData(next)
        }
      } catch (requestError) {
        if (!ignore) {
          setError(requestError.message)
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    load()

    return () => {
      ignore = true
    }
  }, [path, reloadKey, token])

  useEffect(() => {
    if (!pollMs || !token) {
      return undefined
    }

    const intervalId = window.setInterval(() => {
      setReloadKey((current) => current + 1)
    }, pollMs)

    return () => window.clearInterval(intervalId)
  }, [pollMs, token])

  return {
    data,
    loading,
    error,
    refetch: () => setReloadKey((current) => current + 1),
  }
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
        const user = await apiRequest('/api/auth/me/', { token: session.token })
        if (ignore) {
          return
        }

        const nextSession = { token: session.token, user }
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

  function handleAuthenticated(nextSession) {
    setSession(nextSession)
    window.localStorage.setItem(SESSION_KEY, JSON.stringify(nextSession))
  }

  async function handleLogout() {
    try {
      if (session.token) {
        await apiRequest('/api/auth/logout/', {
          method: 'POST',
          token: session.token,
        })
      }
    } catch {
      // Keep the UI local-first for logout.
    } finally {
      clearSession()
    }
  }

  if (booting) {
    return <SplashScreen label="Rebuilding care operations workspace" />
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={
          session.token && session.user ? (
            <Navigate to="/" replace />
          ) : (
            <LoginPage onAuthenticated={handleAuthenticated} />
          )
        }
      />
      <Route element={<ProtectedLayout session={session} onLogout={handleLogout} />}>
        <Route index element={<OverviewPage />} />
        <Route path="/patients" element={<PatientsPage />} />
        <Route path="/appointments" element={<AppointmentsPage />} />
        <Route path="/clinicians" element={<CliniciansPage />} />
        <Route path="/intake" element={<IntakePage />} />
      </Route>
      <Route path="*" element={<Navigate to={session.token ? '/' : '/login'} replace />} />
    </Routes>
  )
}

function SplashScreen({ label }) {
  return (
    <div className="splash-shell">
      <div className="splash-card">
        <span className="eyebrow">Lucent Care Ops</span>
        <h1>{label}</h1>
        <p>Securing command surfaces, recovery lanes, and clinician routing.</p>
      </div>
    </div>
  )
}

function LoginPage({ onAuthenticated }) {
  const [username, setUsername] = useState('ops.lead')
  const [password, setPassword] = useState('CommandCenter@123')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

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
      })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-shell">
      <section className="login-intro">
        <div>
          <span className="eyebrow">Telehealth Operations Platform</span>
          <h1>Lucent rebuilds the old clone into a care command room.</h1>
          <p>
            This version is structured around triage, clinician coverage, patient risk, and task
            execution. It is intentionally more serious and operational than the original interface.
          </p>

          <div className="login-metrics">
            <article>
              <strong>24h runway</strong>
              <span>Appointments, field escalations, and pending reviews in one line of sight.</span>
            </article>
            <article>
              <strong>Clinical network</strong>
              <span>Coverage, SLAs, specialties, and openings without dashboard clutter.</span>
            </article>
            <article>
              <strong>SQLite-backed demo</strong>
              <span>Django REST API with seeded operational data for immediate local use.</span>
            </article>
          </div>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div className="login-card-header">
            <span className="eyebrow">Secure Access</span>
            <h2>Enter command room</h2>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
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

            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? 'Authorizing' : 'Sign in'}
            </button>
          </form>

          <div className="demo-accounts">
            <h3>Demo accounts</h3>
            <div className="demo-account-grid">
              <button
                type="button"
                onClick={() => {
                  setUsername('ops.lead')
                  setPassword('CommandCenter@123')
                }}
              >
                <strong>Ops Lead</strong>
                <span>`ops.lead` / `CommandCenter@123`</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setUsername('doctor.rao')
                  setPassword('Doctor@123')
                }}
              >
                <strong>Doctor</strong>
                <span>`doctor.rao` / `Doctor@123`</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

function ProtectedLayout({ session, onLogout }) {
  if (!session.token || !session.user) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="app-shell">
      <aside className="side-rail">
        <div>
          <div className="brand-block">
            <span className="brand-mark">L</span>
            <div>
              <p>Lucent</p>
              <span>Care Operations</span>
            </div>
          </div>

          <nav className="rail-nav">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) => (isActive ? 'rail-link active' : 'rail-link')}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="rail-footer">
          <div>
            <p>{session.user.display_name}</p>
            <span>{session.user.title || session.user.role}</span>
          </div>
          <button type="button" className="ghost-button" onClick={onLogout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="workspace">
        <Outlet context={{ token: session.token, user: session.user }} />
      </main>
    </div>
  )
}

function PageHeader({ title, description, actions, meta }) {
  return (
    <header className="page-header">
      <div>
        <span className="eyebrow">Clinical command surface</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="page-header-meta">
        {meta}
        {actions}
      </div>
    </header>
  )
}

function OverviewPage() {
  const { token, user } = useOutletContext()
  const { data, loading, error, refetch } = useApiResource('/api/overview/', token, null, 45000)

  if (loading && !data) {
    return <SplashScreen label="Pulling live command intelligence" />
  }

  if (error && !data) {
    return <InlineError error={error} retry={refetch} />
  }

  const summary = data.summary

  return (
    <div className="page-stack">
      <PageHeader
        title="Command Center"
        description="A serious operating view of patient risk, clinician coverage, intake flow, and unresolved work."
        meta={
          <div className="header-chip-group">
            <span className="chip strong">{user.region || 'Regional Grid'}</span>
            <span className="chip">{formatClock(new Date())}</span>
          </div>
        }
        actions={
          <button type="button" className="secondary-button" onClick={refetch}>
            Refresh lane
          </button>
        }
      />

      <section className="metric-grid">
        <MetricCard label="Active patients" value={summary.activePatients} tone="calm" />
        <MetricCard label="Critical watchlist" value={summary.criticalWatchlist} tone="critical" />
        <MetricCard label="Appointments next 24h" value={summary.appointmentsNext24h} tone="neutral" />
        <MetricCard label="Intake backlog" value={summary.intakeBacklog} tone="watch" />
        <MetricCard label="SLA breaches" value={summary.slaBreaches} tone="critical" />
        <MetricCard label="Clinicians online" value={summary.coverageOnline} tone="calm" />
      </section>

      <section className="canvas-grid canvas-grid-overview">
        <Panel title="Operational signals" subtitle="Active interruptions and site-level warnings">
          <div className="signal-list">
            {data.signals.map((signal) => (
              <article key={signal.id} className="signal-card">
                <div className="signal-title-row">
                  <StatusBadge value={signal.severity} />
                  <span>{formatRelative(signal.opened_at)}</span>
                </div>
                <h3>{signal.title}</h3>
                <p>{signal.detail}</p>
                <footer>{signal.source}</footer>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Appointment runway" subtitle="The next consults and field actions">
          <div className="timeline-list">
            {data.appointments.map((appointment) => (
              <article key={appointment.id} className="timeline-card">
                <div className="timeline-time">{formatTime(appointment.scheduled_for)}</div>
                <div>
                  <div className="row-between">
                    <h3>{appointment.patient.full_name}</h3>
                    <StatusBadge value={appointment.status} />
                  </div>
                  <p>{appointment.briefing}</p>
                  <footer>
                    <span>{appointment.clinician.profile.display_name}</span>
                    <span>{appointment.queue_label}</span>
                    <span>{appointment.visit_mode}</span>
                  </footer>
                </div>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Priority patients" subtitle="Patients requiring active judgment">
          <div className="patient-watchlist">
            {data.patients.map((patient) => (
              <article key={patient.id} className="watchlist-card">
                <div className="row-between">
                  <div>
                    <h3>{patient.full_name}</h3>
                    <span>{patient.patient_code}</span>
                  </div>
                  <StatusBadge value={patient.risk_level} />
                </div>
                <p>{patient.summary}</p>
                <footer>
                  <span>{patient.primary_condition}</span>
                  <span>{patient.device_readiness}</span>
                  <span>{formatRelative(patient.last_vitals_at)}</span>
                </footer>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Execution board" subtitle="Time-sensitive coordination tasks">
          <TaskList tasks={data.tasks} token={token} onMutated={refetch} />
        </Panel>

        <Panel title="Intake queue" subtitle="New arrivals and unscheduled requests">
          <div className="queue-list">
            {data.intake.map((item) => (
              <article key={item.id} className="queue-card">
                <div className="row-between">
                  <h3>{item.patient_name}</h3>
                  <StatusBadge value={item.severity} />
                </div>
                <p>{item.concern}</p>
                <footer>
                  <span>{item.location}</span>
                  <span>{item.channel}</span>
                  <span>{item.status}</span>
                </footer>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Clinical network" subtitle="Coverage view across active clinicians">
          <div className="network-list">
            {data.network.map((clinician) => (
              <article key={clinician.id} className="network-card">
                <div className="row-between">
                  <div>
                    <h3>{clinician.profile.display_name}</h3>
                    <span>{clinician.specialty}</span>
                  </div>
                  <StatusBadge value={clinician.status} />
                </div>
                <p>{clinician.clinic.name}</p>
                <footer>
                  <span>SLA {clinician.response_sla_hours}h</span>
                  <span>{clinician.languages}</span>
                  <span>Opens {formatTime(clinician.next_opening)}</span>
                </footer>
              </article>
            ))}
          </div>
        </Panel>
      </section>
    </div>
  )
}

function PatientsPage() {
  const { token } = useOutletContext()
  const { data, loading, error, refetch } = useApiResource('/api/patients/', token, [], 0)
  const [search, setSearch] = useState('')
  const deferredSearch = useDeferredValue(search)

  const filteredPatients = data.filter((patient) => {
    const needle = deferredSearch.trim().toLowerCase()
    if (!needle) {
      return true
    }

    return [patient.full_name, patient.patient_code, patient.primary_condition, patient.district]
      .join(' ')
      .toLowerCase()
      .includes(needle)
  })

  return (
    <div className="page-stack">
      <PageHeader
        title="Patient Ledger"
        description="One ledger for risk, device readiness, adherence, and local context."
        actions={
          <button type="button" className="secondary-button" onClick={refetch}>
            Reload ledger
          </button>
        }
      />

      <section className="toolbar">
        <input
          className="search-input"
          placeholder="Search by patient, code, condition, or district"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <div className="chip-group">
          <span className="chip">Total {data.length}</span>
          <span className="chip">Visible {filteredPatients.length}</span>
        </div>
      </section>

      {loading ? <InlineLoading label="Refreshing patient ledger" /> : null}
      {error ? <InlineError error={error} retry={refetch} compact /> : null}

      <section className="ledger-grid">
        {filteredPatients.map((patient) => (
          <article key={patient.id} className="ledger-card">
            <div className="row-between">
              <div>
                <span className="eyebrow">{patient.patient_code}</span>
                <h3>{patient.full_name}</h3>
              </div>
              <StatusBadge value={patient.risk_level} />
            </div>
            <p>{patient.summary}</p>
            <dl className="detail-grid">
              <div>
                <dt>Condition</dt>
                <dd>{patient.primary_condition}</dd>
              </div>
              <div>
                <dt>District</dt>
                <dd>{patient.district}</dd>
              </div>
              <div>
                <dt>Device</dt>
                <dd>{patient.device_readiness}</dd>
              </div>
              <div>
                <dt>Adherence</dt>
                <dd>{patient.adherence_score}%</dd>
              </div>
            </dl>
          </article>
        ))}
      </section>
    </div>
  )
}

function AppointmentsPage() {
  const { token } = useOutletContext()
  const { data, loading, error, refetch } = useApiResource('/api/appointments/', token, [], 0)

  return (
    <div className="page-stack">
      <PageHeader
        title="Runway"
        description="A sequenced view of consults, field visits, and follow-up obligations."
        actions={
          <button type="button" className="secondary-button" onClick={refetch}>
            Refresh runway
          </button>
        }
      />

      {loading ? <InlineLoading label="Refreshing schedule runway" /> : null}
      {error ? <InlineError error={error} retry={refetch} compact /> : null}

      <section className="runway-list">
        {data.map((appointment) => (
          <article key={appointment.id} className="runway-card">
            <div className="runway-left">
              <span className="runway-hour">{formatTime(appointment.scheduled_for)}</span>
              <span className="runway-duration">{appointment.duration_minutes} min</span>
            </div>
            <div className="runway-main">
              <div className="row-between">
                <div>
                  <h3>{appointment.patient.full_name}</h3>
                  <p>{appointment.queue_label}</p>
                </div>
                <StatusBadge value={appointment.status} />
              </div>
              <p>{appointment.briefing}</p>
              <footer>
                <span>{appointment.clinician.profile.display_name}</span>
                <span>{appointment.visit_mode}</span>
                <span>{appointment.patient.primary_condition}</span>
              </footer>
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

function CliniciansPage() {
  const { token } = useOutletContext()
  const { data, loading, error, refetch } = useApiResource('/api/clinicians/', token, [], 0)

  return (
    <div className="page-stack">
      <PageHeader
        title="Clinical Network"
        description="Specialty coverage, response expectations, and opening windows across the care grid."
        actions={
          <button type="button" className="secondary-button" onClick={refetch}>
            Refresh network
          </button>
        }
      />

      {loading ? <InlineLoading label="Refreshing clinician network" /> : null}
      {error ? <InlineError error={error} retry={refetch} compact /> : null}

      <section className="network-grid">
        {data.map((clinician) => (
          <article key={clinician.id} className="network-card large">
            <div className="row-between">
              <div>
                <h3>{clinician.profile.display_name}</h3>
                <p>{clinician.specialty}</p>
              </div>
              <StatusBadge value={clinician.status} />
            </div>
            <dl className="detail-grid">
              <div>
                <dt>Clinic</dt>
                <dd>{clinician.clinic.name}</dd>
              </div>
              <div>
                <dt>SLA</dt>
                <dd>{clinician.response_sla_hours} hours</dd>
              </div>
              <div>
                <dt>Modes</dt>
                <dd>{clinician.consultation_modes}</dd>
              </div>
              <div>
                <dt>Languages</dt>
                <dd>{clinician.languages}</dd>
              </div>
              <div>
                <dt>License</dt>
                <dd>{clinician.license_id}</dd>
              </div>
              <div>
                <dt>Next opening</dt>
                <dd>{formatDateTime(clinician.next_opening)}</dd>
              </div>
            </dl>
          </article>
        ))}
      </section>
    </div>
  )
}

function IntakePage() {
  const { token } = useOutletContext()
  const { data, loading, error, refetch } = useApiResource('/api/intake/', token, [], 0)

  const columns = [
    { key: 'new', title: 'New' },
    { key: 'review', title: 'In Review' },
    { key: 'scheduled', title: 'Scheduled' },
    { key: 'declined', title: 'Declined' },
  ]

  async function setStatus(itemId, status) {
    await apiRequest(`/api/intake/${itemId}/`, {
      method: 'PATCH',
      token,
      body: { status },
    })
    refetch()
  }

  return (
    <div className="page-stack">
      <PageHeader
        title="Intake Board"
        description="A board-level view of incoming demand, review progression, and scheduling decisions."
        actions={
          <button type="button" className="secondary-button" onClick={refetch}>
            Refresh board
          </button>
        }
      />

      {loading ? <InlineLoading label="Refreshing intake board" /> : null}
      {error ? <InlineError error={error} retry={refetch} compact /> : null}

      <section className="board-grid">
        {columns.map((column) => (
          <div key={column.key} className="board-column">
            <div className="board-column-header">
              <h2>{column.title}</h2>
              <span>{data.filter((item) => item.status === column.key).length}</span>
            </div>
            <div className="board-stack">
              {data
                .filter((item) => item.status === column.key)
                .map((item) => (
                  <article key={item.id} className="board-card">
                    <div className="row-between">
                      <h3>{item.patient_name}</h3>
                      <StatusBadge value={item.severity} />
                    </div>
                    <p>{item.concern}</p>
                    <footer>
                      <span>{item.location}</span>
                      <span>{item.channel}</span>
                    </footer>
                    <div className="board-actions">
                      {column.key !== 'review' ? (
                        <button type="button" className="ghost-button" onClick={() => setStatus(item.id, 'review')}>
                          Review
                        </button>
                      ) : null}
                      {column.key !== 'scheduled' ? (
                        <button
                          type="button"
                          className="ghost-button"
                          onClick={() => setStatus(item.id, 'scheduled')}
                        >
                          Schedule
                        </button>
                      ) : null}
                      {column.key !== 'declined' ? (
                        <button
                          type="button"
                          className="ghost-button danger"
                          onClick={() => setStatus(item.id, 'declined')}
                        >
                          Decline
                        </button>
                      ) : null}
                    </div>
                  </article>
                ))}
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}

function TaskList({ tasks, token, onMutated }) {
  async function markDone(taskId) {
    await apiRequest(`/api/tasks/${taskId}/`, {
      method: 'PATCH',
      token,
      body: { status: 'done' },
    })
    onMutated()
  }

  return (
    <div className="task-list">
      {tasks.map((task) => (
        <article key={task.id} className="task-card">
          <div className="row-between">
            <div>
              <h3>{task.title}</h3>
              <span>{task.owner.display_name}</span>
            </div>
            <StatusBadge value={task.priority} />
          </div>
          <p>{task.summary}</p>
          <footer>
            <span>{task.related_patient.full_name}</span>
            <span>{formatDateTime(task.due_at)}</span>
            <span>{task.status}</span>
          </footer>
          {task.status !== 'done' ? (
            <button type="button" className="ghost-button" onClick={() => markDone(task.id)}>
              Mark complete
            </button>
          ) : null}
        </article>
      ))}
    </div>
  )
}

function MetricCard({ label, value, tone }) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  )
}

function Panel({ title, subtitle, children }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </section>
  )
}

function StatusBadge({ value }) {
  return <span className={`status-badge status-${value}`}>{value.replace('_', ' ')}</span>
}

function InlineLoading({ label }) {
  return <div className="inline-notice">{label}…</div>
}

function InlineError({ error, retry, compact = false }) {
  return (
    <div className={compact ? 'inline-notice error compact' : 'inline-notice error'}>
      <span>{error}</span>
      <button type="button" className="ghost-button" onClick={retry}>
        Retry
      </button>
    </div>
  )
}

function formatClock(date) {
  return new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function formatTime(value) {
  return new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function formatRelative(value) {
  const minutes = Math.round((Date.now() - new Date(value).getTime()) / 60000)

  if (minutes < 60) {
    return `${minutes}m ago`
  }

  const hours = Math.round(minutes / 60)
  if (hours < 24) {
    return `${hours}h ago`
  }

  return `${Math.round(hours / 24)}d ago`
}

export default App
