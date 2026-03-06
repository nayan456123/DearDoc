import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { StatusPill, InlineError, MetricCard, SplashScreen } from '../components/UI'
import { apiRequest } from '../lib/api'
import { formatDateTime } from '../lib/formatters'
import { useApiResource } from '../lib/useApiResource'

const DOCTOR_COLUMNS = [
  { key: 'requested', label: 'Requested' },
  { key: 'confirmed', label: 'Confirmed' },
  { key: 'live', label: 'Live' },
  { key: 'completed', label: 'Completed' },
]

export function DoctorDashboard({ token }) {
  const { data, loading, error, refetch } = useApiResource('/api/doctor/dashboard/', token, null)
  const [slotForm, setSlotForm] = useState({
    starts_at: '',
    ends_at: '',
    label: 'Fast consult',
    visit_mode: 'video',
  })
  const [creatingSlot, setCreatingSlot] = useState(false)
  const navigate = useNavigate()

  async function createSlot(event) {
    event.preventDefault()
    setCreatingSlot(true)
    try {
      await apiRequest('/api/slots/', {
        method: 'POST',
        token,
        body: slotForm,
      })
      refetch()
    } finally {
      setCreatingSlot(false)
    }
  }

  async function updateStatus(appointmentId, nextStatus) {
    await apiRequest(`/api/appointments/${appointmentId}/status/`, {
      method: 'PATCH',
      token,
      body: { status: nextStatus },
    })
    refetch()
  }

  if (loading && !data) {
    return <SplashScreen />
  }

  if (error && !data) {
    return <InlineError error={error} retry={refetch} />
  }

  return (
    <div className="page-shell">
      <section className="hero-panel">
        <div>
          <span className="eyebrow">Doctor cockpit</span>
          <h1>Run schedule, triage, and live consults from one place.</h1>
          <p>
            This is the doctor-operated control surface. No extra admin panel, no ops-heavy
            dashboards, just scheduling, appointment flow, and live meeting access.
          </p>
        </div>
        <button type="button" className="secondary-button" onClick={refetch}>
          Refresh doctor board
        </button>
      </section>

      <section className="metric-row">
        <MetricCard label="Booked today" value={data.stats.bookedToday} />
        <MetricCard label="Waiting requests" value={data.stats.waitingRequests} />
        <MetricCard label="Live now" value={data.stats.liveNow} />
        <MetricCard label="Open slots" value={data.stats.openSlots} />
      </section>

      <section className="main-grid doctor-grid">
        <section className="panel wide">
          <div className="section-head">
            <div>
              <span className="eyebrow">Kanban</span>
              <h2>Meeting pipeline</h2>
            </div>
          </div>

          <div className="kanban-grid">
            {DOCTOR_COLUMNS.map((column) => (
              <div key={column.key} className="kanban-column">
                <div className="kanban-column-head">
                  <h3>{column.label}</h3>
                  <span>{data.appointments.filter((item) => item.status === column.key).length}</span>
                </div>
                <div className="kanban-stack">
                  {data.appointments
                    .filter((item) => item.status === column.key)
                    .map((appointment) => (
                      <article key={appointment.id} className="appointment-card">
                        <div className="row-between">
                          <div>
                            <strong>{appointment.patient.user_profile.display_name}</strong>
                            <span>{appointment.concern}</span>
                          </div>
                          <StatusPill value={appointment.urgency} />
                        </div>
                        <p>{appointment.copilot_summary}</p>
                        <footer>
                          <span>{formatDateTime(appointment.starts_at)}</span>
                          <span>Score {appointment.triage_score}</span>
                        </footer>
                        <div className="card-actions">
                          {appointment.status === 'requested' ? (
                            <button
                              type="button"
                              className="ghost-button"
                              onClick={() => updateStatus(appointment.id, 'confirmed')}
                            >
                              Confirm
                            </button>
                          ) : null}
                          {(appointment.status === 'confirmed' || appointment.status === 'live') ? (
                            <button
                              type="button"
                              className="ghost-button"
                              onClick={() => navigate(`/meeting/${appointment.id}`)}
                            >
                              Join room
                            </button>
                          ) : null}
                          {appointment.status === 'confirmed' ? (
                            <button
                              type="button"
                              className="ghost-button"
                              onClick={() => updateStatus(appointment.id, 'live')}
                            >
                              Mark live
                            </button>
                          ) : null}
                          {appointment.status === 'live' ? (
                            <button
                              type="button"
                              className="ghost-button"
                              onClick={() => updateStatus(appointment.id, 'completed')}
                            >
                              Complete
                            </button>
                          ) : null}
                        </div>
                      </article>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">Schedule</span>
              <h2>Create availability</h2>
            </div>
          </div>
          <form className="slot-form" onSubmit={createSlot}>
            <label>
              <span>Start</span>
              <input
                type="datetime-local"
                value={slotForm.starts_at}
                onChange={(event) => setSlotForm((current) => ({ ...current, starts_at: event.target.value }))}
              />
            </label>
            <label>
              <span>End</span>
              <input
                type="datetime-local"
                value={slotForm.ends_at}
                onChange={(event) => setSlotForm((current) => ({ ...current, ends_at: event.target.value }))}
              />
            </label>
            <label>
              <span>Label</span>
              <input
                value={slotForm.label}
                onChange={(event) => setSlotForm((current) => ({ ...current, label: event.target.value }))}
              />
            </label>
            <button type="submit" className="primary-button" disabled={creatingSlot}>
              {creatingSlot ? 'Saving...' : 'Add slot'}
            </button>
          </form>

          <div className="mini-list">
            {data.slots.slice(0, 6).map((slot) => (
              <article key={slot.id} className="mini-card">
                <strong>{formatDateTime(slot.starts_at)}</strong>
                <p>{slot.label || 'Consult slot'}</p>
                <StatusPill value={slot.status} />
              </article>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">Innovation</span>
              <h2>PulseMatch briefs</h2>
            </div>
          </div>
          <div className="innovation-list">
            {data.appointments
              .slice()
              .sort((left, right) => right.triage_score - left.triage_score)
              .map((appointment) => (
                <article key={appointment.id} className="innovation-card">
                  <div className="row-between">
                    <strong>{appointment.patient.user_profile.display_name}</strong>
                    <span className="score-pill">{appointment.triage_score}</span>
                  </div>
                  <p>{appointment.copilot_summary}</p>
                  <ul>
                    {appointment.copilot_checklist.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
              ))}
          </div>
        </section>
      </section>
    </div>
  )
}
