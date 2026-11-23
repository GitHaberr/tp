import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import ErrorBanner from '../components/ErrorBanner'
import { STATUSES, NEXT_STATUSES } from '../statuses'
import { shortName, formatDate, formatDateTime } from '../format'

const NETWORK_MESSAGE = 'Не удалось отправить статус на сервер. Проверьте соединение и повторите попытку.'

function changeText(h) {
  if (h.old_status && h.new_status) {
    return `Статус: ${STATUSES[h.old_status] || h.old_status} → ${STATUSES[h.new_status] || h.new_status}`
  }
  return h.action_label
}

const isAssignee = (task, user) =>
  task.assignee_id !== undefined ? task.assignee_id === user.id : task.assignee === user.full_name

export default function TaskPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [task, setTask] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const [busy, setBusy] = useState(false)

  function load() {
    api(`/tasks/${id}`).then(setTask).catch((e) => setError(e.message))
    api(`/tasks/${id}/history`).then(setHistory).catch(() => {})
  }

  useEffect(() => {
    setTask(null)
    setHistory([])
    setError('')
    setActionError(null)
    load()
  }, [id])

  async function run(request) {
    setActionError(null)
    setMenuOpen(false)
    setBusy(true)
    try {
      await request()
      load()
    } catch (err) {
      setActionError({ message: err.message, network: err.network, retry: () => run(request) })
    } finally {
      setBusy(false)
    }
  }

  const changeStatus = (status) =>
    run(() => api(`/tasks/${id}/status`, { method: 'PATCH', body: { status } }))
  const submit = () => run(() => api(`/tasks/${id}/submit`, { method: 'POST' }))

  const mine = task && isAssignee(task, user)
  const options = task ? NEXT_STATUSES[task.status] || [] : []

  return (
    <Layout>
      <h1 className="page-title">
        <button type="button" className="back-btn" onClick={() => navigate('/tasks')} aria-label="Назад">←</button>
        {task && task.title}
        {task && <StatusBadge status={task.status} />}
      </h1>

      {error && <div className="banner-error" role="alert">{error}</div>}
      {actionError && (
        actionError.network
          ? <ErrorBanner message={NETWORK_MESSAGE} onRetry={actionError.retry} />
          : <ErrorBanner message={actionError.message} />
      )}

      {task && (
        <div className="columns">
          <div className="details">
            <div className="info">
              <div className="info-item">
                <span className="info-label">Поставил</span>
                <span className="info-value">{shortName(task.author)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Исполнитель</span>
                <span className="info-value">{shortName(task.assignee)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Срок</span>
                <span className="info-value">{formatDate(task.deadline)}</span>
              </div>
            </div>

            <div className="field">
              <label>Описание</label>
              <div className="description">{task.description}</div>
            </div>

            {mine && ['new', 'in_progress'].includes(task.status) && (
              <div className="form-actions">
                <div className="menu-wrap">
                  <button type="button" className="btn-secondary" disabled={busy || options.length === 0}
                    onClick={() => setMenuOpen((o) => !o)}>
                    Изменить статус ▾
                  </button>
                  {menuOpen && (
                    <div className="menu">
                      {options.map((s) => (
                        <button key={s} type="button" onClick={() => changeStatus(s)}>{STATUSES[s]}</button>
                      ))}
                    </div>
                  )}
                </div>
                {task.status === 'in_progress' && (
                  <button type="button" className="btn-primary" disabled={busy} onClick={submit}>
                    Готово — передать на проверку
                  </button>
                )}
              </div>
            )}
          </div>

          <aside className="history">
            <h2>История изменений</h2>
            {history.map((h) => (
              <div className="history-entry" key={h.id}>
                <span className="history-head">{formatDateTime(h.created_at)} — {shortName(h.user)}</span>
                <span className="history-text">{changeText(h)}</span>
                {h.comment && <span className="history-text">{h.comment}</span>}
              </div>
            ))}
          </aside>
        </div>
      )}
    </Layout>
  )
}