export function AppShell({ session, onLogout, compact = false, children }) {
  return (
    <div className={compact ? 'app-shell compact' : 'app-shell'}>
      <header className="topbar">
        <div className="brand-line">
          <span className="brand-dot">L</span>
          <div>
            <strong>Lucent Sync</strong>
            <span>Doctor-patient telehealth studio</span>
          </div>
        </div>

        <div className="topbar-actions">
          <span className="role-pill">{session.user.role}</span>
          <button type="button" className="ghost-button" onClick={onLogout}>
            Sign out
          </button>
        </div>
      </header>
      <main className="workspace">{children}</main>
    </div>
  )
}
