export function shortName(fullName = '') {
  const [last, first] = fullName.trim().split(/\s+/)
  return first ? `${last} ${first[0]}.` : last || ''
}

export function formatDate(iso) {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

export function formatDateTime(iso) {
  if (!iso) return ''
  const [date, time = ''] = iso.split('T')
  return `${formatDate(date)} ${time.slice(0, 5)}`
}