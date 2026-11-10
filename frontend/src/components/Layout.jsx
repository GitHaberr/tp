import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import { shortName } from '../format'

const ROLES = { boss: 'начальник', employee: 'сотрудник' }

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  return (
    <>
      <header className="header">
        <Link to="/tasks" className="header-title">Поручения</Link>
        <div className="header-user">
          <span>{shortName(user.full_name)} ({ROLES[user.role]})</span>
          <span className="header-sep" />
          <button className="link-btn" onClick={logout}>Выход</button>
        </div>
      </header>
      <main className="page">{children}</main>
    </>
  )
}