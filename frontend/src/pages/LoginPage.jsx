import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/tasks" replace />

  async function onSubmit(e) {
    e.preventDefault()
    const next = {}
    if (!email.trim()) next.email = 'Введите email'
    if (!password) next.password = 'Введите пароль'
    setErrors(next)
    setServerError('')
    if (Object.keys(next).length) return

    setBusy(true)
    try {
      await login(email.trim(), password)
      navigate('/tasks', { replace: true })
    } catch (err) {
      setServerError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const emailBad = errors.email || serverError
  const passBad = errors.password || serverError

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit} noValidate>
        <h1>Система контроля поручений</h1>
        <p className="subtitle">Вход в систему</p>

        {serverError && (
          <div className="banner-error" role="alert">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true">
              <circle cx="11" cy="11" r="9.5" stroke="#dc2626" strokeWidth="1.5" />
              <path d="M11 6v6" stroke="#dc2626" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="11" cy="15.5" r="1" fill="#dc2626" />
            </svg>
            <span>{serverError}</span>
          </div>
        )}

        <div className="field">
          <label htmlFor="email">Email / логин</label>
          <input id="email" className={'input' + (emailBad ? ' invalid' : '')} placeholder="name@firma.ru"
            value={email} onChange={(e) => setEmail(e.target.value)} />
          {errors.email && <span className="field-error">{errors.email}</span>}
        </div>

        <div className="field">
          <label htmlFor="password">Пароль</label>
          <input id="password" type="password" className={'input' + (passBad ? ' invalid' : '')}
            placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
          {errors.password && <span className="field-error">{errors.password}</span>}
        </div>

        <button className="btn-primary" disabled={busy}>Войти</button>
        <Link to="/forgot" className="link-muted">Забыли пароль?</Link>
      </form>
    </div>
  )
}