export function shortName(fullName = '') {
  const [last, first] = fullName.trim().split(/\s+/)
  return first ? `${last} ${first[0]}.` : last || ''
}

export function formatDate(iso) {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}