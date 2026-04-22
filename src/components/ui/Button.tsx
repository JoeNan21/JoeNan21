import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

type Variant = 'gold' | 'teal' | 'ghost' | 'danger'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  full?: boolean
}

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = 'gold', full, className, ...rest },
  ref,
) {
  const base = 'btn'
  const v =
    variant === 'gold'
      ? 'btn-gold'
      : variant === 'teal'
        ? 'btn-teal'
        : variant === 'danger'
          ? 'btn-danger'
          : 'btn-ghost'
  return <button ref={ref} className={cn(base, v, full && 'w-full', className)} {...rest} />
})
