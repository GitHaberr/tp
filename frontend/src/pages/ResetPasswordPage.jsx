import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../api'

export default function ResetPasswordPage() {
  const [params] = useSearchParams()
  const token = params.get('token') || ''
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    if (password.length < 4) {
      setError('Пароль должен быть не короче 4 символов')
      return
    }
    setBusy(true)
    try {
      await api('/auth/reset', { method: 'POST', body: { token, new_password: password } })
      navigate('/login', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit} noValidate>
        <h1>Новый пароль</h1>
        <p className="subtitle small">Придумайте новый пароль для входа.</p>
        <div className="field">
          <label htmlFor="password">Новый пароль</label>
          <input id="password" type="password" className={'input' + (error ? ' invalid' : '')}
            placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <span className="field-error">{error}</span>}
        </div>
        <button className="btn-primary" disabled={busy}>Сохранить пароль</button>
        <Link to="/login" className="link-muted">←  Назад ко входу</Link>
      </form>
    </div>
  )
}