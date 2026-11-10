import { createContext, useContext, useEffect, useState } from 'react'
import { api, getToken, setToken, clearToken } from './api'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!getToken())

  useEffect(() => {
    if (!getToken()) return
    api('/me').then(setUser).catch(() => clearToken()).finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const { access_token } = await api('/auth/login', { method: 'POST', body: { email, password } })
    setToken(access_token)
    setUser(await api('/me'))
  }

  function logout() {
    clearToken()
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
}