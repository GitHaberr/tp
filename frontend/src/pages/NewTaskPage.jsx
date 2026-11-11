import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import Layout from '../components/Layout'

const today = () => new Date().toLocaleDateString('sv-SE')

export default function NewTaskPage() {
  const navigate = useNavigate()
  const [subordinates, setSubordinates] = useState([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [assigneeId, setAssigneeId] = useState('')
  const [deadline, setDeadline] = useState('')
  const [errors, setErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api('/users/subordinates')
      .then(setSubordinates)
      .catch((e) => setFormError(e.message))
  }, [])

  function validate() {
    const next = {}
    if (!title.trim()) next.title = 'Введите название поручения'
    if (!assigneeId) next.assignee = 'Выберите исполнителя'
    if (!deadline) next.deadline = 'Укажите срок выполнения'
    else if (deadline < today()) next.deadline = 'Срок не может быть раньше сегодняшней даты'
    return next
  }

  async function onSubmit(e) {
    e.preventDefault()
    setFormError('')
    const next = validate()
    setErrors(next)
    if (Object.keys(next).length) return

    setBusy(true)
    try {
      await api('/tasks', {
        method: 'POST',
        body: { title: title.trim(), description, assignee_id: Number(assigneeId), deadline },
      })
      navigate('/tasks')
    } catch (err) {
      const m = err.message
      if (m.includes('название')) setErrors({ title: m })
      else if (m.includes('исполнител')) setErrors({ assignee: m })
      else if (m.includes('Срок')) setErrors({ deadline: m })
      else setFormError(m)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Layout>
      <h1 className="page-title">
        <button type="button" className="back-btn" onClick={() => navigate('/tasks')} aria-label="Назад">←</button>
        Новое поручение
      </h1>

      <form className="form-card" onSubmit={onSubmit} noValidate>
        {formError && <div className="banner-error" role="alert">{formError}</div>}

        <div className="field">
          <label htmlFor="title">Название *</label>
          <input id="title" className={'input' + (errors.title ? ' invalid' : '')}
            placeholder="Введите название поручения" value={title} onChange={(e) => setTitle(e.target.value)} />
          {errors.title && <span className="field-error">{errors.title}</span>}
        </div>

        <div className="field">
          <label htmlFor="description">Описание</label>
          <textarea id="description" className="input" placeholder="Что нужно сделать…"
            value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>

        <div className="form-row">
          <div className="field">
            <label htmlFor="assignee">Исполнитель *</label>
            <select id="assignee" className={'input' + (errors.assignee ? ' invalid' : '') + (assigneeId ? '' : ' empty')}
              value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)}>
              <option value="">Выбрать сотрудника</option>
              {subordinates.map((u) => (
                <option key={u.id} value={u.id}>{u.full_name}</option>
              ))}
            </select>
            {errors.assignee && <span className="field-error">{errors.assignee}</span>}
          </div>

          <div className="field">
            <label htmlFor="deadline">Срок выполнения *</label>
            <input id="deadline" type="date" className={'input' + (errors.deadline ? ' invalid' : '')}
              value={deadline} onChange={(e) => setDeadline(e.target.value)} />
            {errors.deadline && <span className="field-error">{errors.deadline}</span>}
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-primary" disabled={busy}>Сохранить и назначить</button>
          <button type="button" className="btn-secondary" onClick={() => navigate('/tasks')}>Отмена</button>
        </div>
      </form>
    </Layout>
  )
}