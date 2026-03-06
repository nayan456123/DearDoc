export function SplashScreen() {
  return (
    <div className="splash-shell">
      <div className="splash-card">
        <span className="eyebrow">Hackathon Build</span>
        <h1>Loading Lucent Sync.</h1>
        <p>Preparing PulseMatch triage, scheduling lanes, and the local WebRTC room.</p>
      </div>
    </div>
  )
}

export function MetricCard({ label, value }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  )
}

export function StatusPill({ value }) {
  return <span className={`status-pill status-${value}`}>{value.replace('_', ' ')}</span>
}

export function InlineError({ error, retry }) {
  return (
    <div className="inline-error">
      <span>{error}</span>
      <button type="button" className="ghost-button" onClick={retry}>
        Retry
      </button>
    </div>
  )
}

export function EmptyState({ title, detail }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <p>{detail}</p>
    </div>
  )
}
