import { useEffect, useState } from 'react'
import { api, setToken } from './api'

export default function App() {
  const [me, setMe] = useState('...')
  useEffect(() => {
    api('/auth/login', { method: 'POST', body: { email: 'boss@firma.ru', password: '1234' } })
      .then((r) => { setToken(r.access_token); return api('/me') })
      .then((u) => setMe(JSON.stringify(u)))
      .catch((e) => setMe('Ошибка: ' + e.message))
  }, [])
  return <pre>{me}</pre>
}
