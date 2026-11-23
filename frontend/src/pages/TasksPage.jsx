import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import { STATUSES } from '../statuses'
import { shortName, formatDate } from '../format'

export default function TasksPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [tasks, setTasks] = useState([])
  const [reviewCount, setReviewCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState('all')
  const [status, setStatus] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    const params = new URLSearchParams({ scope: tab })
    if (status) params.set('status', status)
    api(`/tasks?${params}`)
      .then(setTasks)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [tab, status])

  useEffect(() => {
    api('/tasks?scope=review').then((r) => setReviewCount(r.length)).catch(() => {})
  }, [])

  const tabs = [
    { id: 'all', label: 'Все' },
    { id: 'mine', label: 'Мои (как исполнитель)' },
    { id: 'review', label: `На проверке (${reviewCount})` },
  ]

  return (
    <Layout>
      <div className="tabs">
        {tabs.map((t) => (
          <button key={t.id} className={'tab' + (tab === t.id ? ' active' : '')} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="toolbar">
        <select className="input select" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">Статус: Все</option>
          {Object.entries(STATUSES).map(([value, label]) => (
            <option key={value} value={value}>Статус: {label}</option>
          ))}
        </select>
        {user.role === 'boss' && (
          <Link to="/tasks/new" className="btn-primary">+ Создать поручение</Link>
        )}
      </div>

      {error && <div className="banner-error" role="alert">{error}</div>}

      <table className="table">
        <thead>
          <tr><th>Название</th><th>Исполнитель</th><th>Срок</th><th>Статус</th></tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id} className="clickable" onClick={() => navigate(`/tasks/${t.id}`)}>
              <td>{t.title}</td>
              <td>{shortName(t.assignee)}</td>
              <td>{formatDate(t.deadline)}</td>
              <td><StatusBadge status={t.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      {!loading && !error && tasks.length === 0 && <div className="empty">Поручений нет</div>}
    </Layout>
  )
}