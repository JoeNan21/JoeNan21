import type { ReviewStatus } from '../data/types';
import { useLanguage } from '../context/LanguageContext';

export function ReviewBadge({ review }: { review: ReviewStatus }) {
  const { lang } = useLanguage();
  if (review.status !== 'approved') return null;
  const label = lang === 'sm' ? 'Ua talia e le aganuʻu' : 'Community Reviewed';
  const sub = review.reviewer ? ` · ${review.reviewer}` : '';
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border border-ochre/40 bg-ochre/10 px-2.5 py-1 text-[11px] font-medium text-ochre-600 tracking-wide"
      title={review.review_date ? `Reviewed ${review.review_date}` : 'Reviewed'}
    >
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden>
        <path d="M1 5l2.5 2.5L9 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span>
        {label}
        {sub}
      </span>
    </span>
  );
}
