import { useState } from 'react'
import { Check, Copy } from 'lucide-react'
import { cn } from '@/lib/cn'

export function CopyButton({
  text,
  label = 'Copy',
  className,
}: {
  text: string
  label?: string
  className?: string
}) {
  const [copied, setCopied] = useState(false)
  const onClick = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    } catch {
      // clipboard blocked — fall back
      const ta = document.createElement('textarea')
      ta.value = text
      document.body.appendChild(ta)
      ta.select()
      try {
        document.execCommand('copy')
        setCopied(true)
        setTimeout(() => setCopied(false), 1800)
      } catch {
        // swallow
      }
      document.body.removeChild(ta)
    }
  }
  return (
    <button
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-2 rounded px-3 text-xs font-medium border transition-colors',
        copied
          ? 'border-ok/50 text-ok bg-ok/10'
          : 'border-line text-muted hover:text-gold hover:border-gold',
        className,
      )}
      style={{ minHeight: 44 }}
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
      {copied ? 'Copied' : label}
    </button>
  )
}
