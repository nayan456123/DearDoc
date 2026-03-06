import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { EmptyState, InlineError, SplashScreen, StatusPill } from '../components/UI'
import { apiRequest } from '../lib/api'
import { formatDateTime } from '../lib/formatters'
import { useApiResource } from '../lib/useApiResource'

export function PatientDashboard({ token }) {
  const { data, loading, error, refetch } = useApiResource('/api/patient/dashboard/', token, null)
  const [concern, setConcern] = useState('')
  const [symptoms, setSymptoms] = useState('')
  const [patientNotes, setPatientNotes] = useState('')
  const [preview, setPreview] = useState(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [bookingSlotId, setBookingSlotId] = useState(null)
  const navigate = useNavigate()

  async function generatePreview(event) {
    event.preventDefault()
    setLoadingPreview(true)
    try {
      const response = await apiRequest('/api/triage/preview/', {
        method: 'POST',
        token,
        body: { concern, symptoms, notes: patientNotes },
      })
      setPreview(response)
    } finally {
      setLoadingPreview(false)
    }
  }

  async function bookSlot(slotId) {
    setBookingSlotId(slotId)
    try {
      await apiRequest('/api/appointments/request/', {
        method: 'POST',
        token,
        body: {
          slot_id: slotId,
          concern,
          symptoms,
          patient_notes: patientNotes,
        },
      })
      setConcern('')
      setSymptoms('')
      setPatientNotes('')
      setPreview(null)
      refetch()
    } finally {
      setBookingSlotId(null)
    }
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
          <span className="eyebrow">Patient side</span>
          <h1>Ask for help, get a smart slot suggestion, then join the call.</h1>
          <p>
            PulseMatch Copilot reads the concern in natural language, recommends urgency, and
            prepares the doctor before the session even starts.
          </p>
        </div>
        <button type="button" className="secondary-button" onClick={refetch}>
          Refresh my dashboard
        </button>
      </section>

      <section className="main-grid patient-grid">
        <section className="panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">Innovation</span>
              <h2>PulseMatch Copilot</h2>
            </div>
          </div>
          <form className="triage-form" onSubmit={generatePreview}>
            <label>
              <span>Main concern</span>
              <input value={concern} onChange={(event) => setConcern(event.target.value)} />
            </label>
            <label>
              <span>Symptoms</span>
              <textarea value={symptoms} onChange={(event) => setSymptoms(event.target.value)} />
            </label>
            <label>
              <span>Extra notes</span>
              <textarea value={patientNotes} onChange={(event) => setPatientNotes(event.target.value)} />
            </label>
            <button type="submit" className="primary-button" disabled={loadingPreview || !concern || !symptoms}>
              {loadingPreview ? 'Analyzing...' : 'Generate smart brief'}
            </button>
          </form>

          {preview ? (
            <div className="copilot-card">
              <div className="row-between">
                <strong>{preview.specialty_hint}</strong>
                <StatusPill value={preview.urgency} />
              </div>
              <p>{preview.summary}</p>
              <div className="score-line">
                <span>Pulse score</span>
                <strong>{preview.triage_score}</strong>
              </div>
              <ul>
                {preview.checklist.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>

        <section className="panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">Scheduling</span>
              <h2>Suggested slots</h2>
            </div>
          </div>
          <div className="slot-grid">
            {data.availableSlots.length ? (
              data.availableSlots.map((slot) => (
                <article key={slot.id} className="slot-card">
                  <strong>{formatDateTime(slot.starts_at)}</strong>
                  <p>{slot.doctor.user_profile.display_name}</p>
                  <span>{slot.label || 'Live consult slot'}</span>
                  <button
                    type="button"
                    className="ghost-button"
                    disabled={bookingSlotId === slot.id || !concern || !symptoms}
                    onClick={() => bookSlot(slot.id)}
                  >
                    {bookingSlotId === slot.id ? 'Booking...' : 'Book this slot'}
                  </button>
                </article>
              ))
            ) : (
              <EmptyState
                title="No slots available"
                detail="The doctor has not opened any time slots yet. Ask the doctor to publish availability first."
              />
            )}
          </div>
        </section>

        <section className="panel wide">
          <div className="section-head">
            <div>
              <span className="eyebrow">My meetings</span>
              <h2>Upcoming and completed consults</h2>
            </div>
          </div>
          <div className="meeting-list">
            {data.appointments.length ? (
              data.appointments.map((appointment) => (
                <article key={appointment.id} className="meeting-card">
                  <div className="row-between">
                    <div>
                      <strong>{appointment.doctor.user_profile.display_name}</strong>
                      <span>{appointment.concern}</span>
                    </div>
                    <StatusPill value={appointment.status} />
                  </div>
                  <p>{appointment.copilot_summary}</p>
                  <footer>
                    <span>{formatDateTime(appointment.starts_at)}</span>
                    <span>{appointment.innovation_tag}</span>
                  </footer>
                  <div className="card-actions">
                    {(appointment.status === 'confirmed' || appointment.status === 'live') ? (
                      <button
                        type="button"
                        className="ghost-button"
                        onClick={() => navigate(`/meeting/${appointment.id}`)}
                      >
                        Join meeting
                      </button>
                    ) : null}
                  </div>
                </article>
              ))
            ) : (
              <EmptyState
                title="No meetings booked"
                detail="Generate a PulseMatch brief and book one of the doctor slots to create your first appointment."
              />
            )}
          </div>
        </section>
      </section>
    </div>
  )
}
