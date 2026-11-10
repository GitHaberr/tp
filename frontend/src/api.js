const TOKEN_KEY = 'token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

export async function api(path, { method = 'GET', body } = {}) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch('/api' + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new Error('Ошибка соединения')
  }

  const data = await res.json().catch(() => null)

  if (res.status === 401 && token) {
    clearToken()
    window.location.href = '/login'
  }
  if (!res.ok) {
    throw new Error(typeof data?.detail === 'string' ? data.detail : 'Что-то пошло не так')
  }
  return data
}