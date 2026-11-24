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
const isAuthor = (task, user) =>
  task.author_id !== undefined ? task.author_id === user.id : task.author === user.full_name

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
  const [comment, setComment] = useState('')
  const [commentError, setCommentError] = useState('')

  function load() {
    api(`/tasks/${id}`).then(setTask).catch((e) => setError(e.message))
    api(`/tasks/${id}/history`).then(setHistory).catch(() => {})
  }

  useEffect(() => {
    setTask(null)
    setHistory([])
    setError('')
    setActionError(null)
    setComment('')
    setCommentError('')
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
  const approve = () =>
    run(async () => {
      await api(`/tasks/${id}/approve`, { method: 'POST', body: { comment: comment.trim() } })
      setComment('')
    })

  function reject() {
    if (!comment.trim()) {
      setCommentError('Укажите комментарий — он обязателен при возврате поручения')
      return
    }
    setCommentError('')
    run(async () => {
      await api(`/tasks/${id}/reject`, { method: 'POST', body: { comment: comment.trim() } })
      setComment('')
    })
  }

  const mine = task && isAssignee(task, user)
  const author = task && isAuthor(task, user)
  const canEdit = author && task.status !== 'done'
  const options = task ? NEXT_STATUSES[task.status] || [] : []

  const editButton = (
    <button type="button" className="btn-secondary" disabled={busy}
      onClick={() => navigate(`/tasks/${id}/edit`)}>
      Редактировать
    </button>
  )

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
            {author && task.status === 'review' && (
              <>
                <div className="field">
                  <label htmlFor="review-comment">Комментарий к проверке</label>
                  <textarea id="review-comment" className={'input short' + (commentError ? ' invalid' : '')}
                    placeholder="Необязательно при подтверждении, обязательно при возврате"
                    value={comment}
                    onChange={(e) => { setComment(e.target.value); setCommentError('') }} />
                  {commentError && <span className="field-error">{commentError}</span>}
                </div>
                <div className="form-actions">
                  <button type="button" className="btn-primary" disabled={busy} onClick={approve}>
                    Подтвердить выполнение
                  </button>
                  <button type="button" className="btn-secondary" disabled={busy} onClick={reject}>
                    Вернуть в работу
                  </button>
                  {canEdit && editButton}
                </div>
              </>
            )}

            {canEdit && task.status !== 'review' && (
              <div className="form-actions">{editButton}</div>
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