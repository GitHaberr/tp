import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import Layout from '../components/Layout'
import StatusBadge from '../components/StatusBadge'
import { shortName, formatDate } from '../format'

export default function TaskPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [task, setTask] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    setTask(null)
    setError('')
    api(`/tasks/${id}`)
      .then(setTask)
      .catch((e) => setError(e.message))
  }, [id])

  return (
    <Layout>
      <h1 className="page-title">
        <button type="button" className="back-btn" onClick={() => navigate('/tasks')} aria-label="Назад">←</button>
        {task && task.title}
        {task && <StatusBadge status={task.status} />}
      </h1>

      {error && <div className="banner-error" role="alert">{error}</div>}

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
          </div>

          <aside className="history">
            <h2>История изменений</h2>
          </aside>
        </div>
      )}
    </Layout>
  )
}