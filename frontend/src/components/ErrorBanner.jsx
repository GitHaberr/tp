export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="banner-error" role="alert">
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
        <circle cx="11" cy="11" r="9.5" stroke="#dc2626" strokeWidth="1.5" />
        <path d="M11 6v6" stroke="#dc2626" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="11" cy="15.5" r="1" fill="#dc2626" />
      </svg>
      <span className="banner-text">{message}</span>
      {onRetry && <button type="button" className="btn-retry" onClick={onRetry}>Повторить</button>}
    </div>
  )
}