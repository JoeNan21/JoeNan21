import { cn } from '@/lib/cn'

type Tone = 'ok' | 'warn' | 'bad' | 'muted' | 'gold' | 'teal'

const colours: Record<Tone, string> = {
  ok: 'bg-ok',
  warn: 'bg-warn',
  bad: 'bg-bad',
  muted: 'bg-muted',
  gold: 'bg-gold',
  teal: 'bg-teal',
}

export function Dot({ tone = 'muted', className }: { tone?: Tone; className?: string }) {
  return <span className={cn('inline-block rounded-full w-2 h-2', colours[tone], className)} />
}
