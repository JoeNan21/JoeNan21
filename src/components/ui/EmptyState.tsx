import type { ReactNode } from 'react'

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string
  body?: string
  action?: ReactNode
}) {
  return (
    <div className="rounded border border-dashed border-line bg-surface/60 p-6 text-center">
      <div className="text-ink font-medium text-sm mb-1">{title}</div>
      {body && <div className="text-muted text-xs leading-relaxed mb-4">{body}</div>}
      {action}
    </div>
  )
}
