import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await api('/auth/forgot', { method: 'POST', body: { email: email.trim() } })
      setSent(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit} noValidate>
        <h1>Восстановление пароля</h1>

        {sent ? (
          <p className="subtitle small">Ссылка для сброса пароля отправлена на {email}.</p>
        ) : (
          <>
            <p className="subtitle small">Укажите email — мы отправим ссылку для сброса пароля.</p>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input id="email" className={'input' + (error ? ' invalid' : '')} placeholder="name@firma.ru"
                value={email} onChange={(e) => setEmail(e.target.value)} />
              {error && <span className="field-error">{error}</span>}
            </div>
            <button className="btn-primary" disabled={busy}>Отправить ссылку</button>
          </>
        )}

        <Link to="/login" className="link-muted">←  Назад ко входу</Link>
      </form>
    </div>
  )
}