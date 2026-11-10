import { STATUSES } from '../statuses'

export default function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{STATUSES[status] || status}</span>
}