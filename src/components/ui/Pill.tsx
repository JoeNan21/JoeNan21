import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

type Tone = 'gold' | 'teal' | 'ok' | 'warn' | 'bad' | 'muted'

const styles: Record<Tone, string> = {
  gold: 'bg-gold/15 text-gold border border-gold/30',
  teal: 'bg-teal/20 text-[#6fb3b3] border border-teal/40',
  ok: 'bg-ok/15 text-ok border border-ok/30',
  warn: 'bg-warn/15 text-warn border border-warn/30',
  bad: 'bg-bad/15 text-bad border border-bad/30',
  muted: 'bg-elevated text-muted border border-line',
}

export function Pill({
  tone = 'muted',
  children,
  className,
}: {
  tone?: Tone
  children: ReactNode
  className?: string
}) {
  return <span className={cn('pill', styles[tone], className)}>{children}</span>
}
