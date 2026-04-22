import { useEffect, type ReactNode } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/cn'

interface Props {
  open: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  side?: 'right' | 'bottom'
  wide?: boolean
}

export function Drawer({ open, onClose, title, children, side = 'right', wide }: Props) {
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  const panel =
    side === 'right'
      ? cn(
          'fixed right-0 top-0 bottom-0 w-full bg-surface border-l border-line z-50 flex flex-col',
          wide ? 'sm:max-w-2xl' : 'sm:max-w-md',
        )
      : 'fixed inset-x-0 bottom-0 max-h-[92vh] bg-surface border-t border-line z-50 rounded-t-xl flex flex-col'

  return (
    <div className="fixed inset-0 z-40">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />
      <div className={panel} role="dialog" aria-modal>
        <div className="flex items-center justify-between px-4 py-3 border-b border-line flex-shrink-0">
          <h2 className="text-sm font-semibold tracking-wide text-ink">{title}</h2>
          <button
            className="btn-icon"
            onClick={onClose}
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-4 py-4">{children}</div>
      </div>
    </div>
  )
}
