import type { ReviewStatus } from '../types/content';
import { useLanguage } from '../context/LanguageContext';

export function ReviewBadge({ review }: { review: ReviewStatus }) {
  const { t } = useLanguage();
  if (review.status !== 'approved') return null;
  const label = t('reviewBadge.label');
  const sub = review.reviewer ? ` · ${review.reviewer}` : '';
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border border-emerald-600/40 bg-emerald-600/10 px-2.5 py-1 text-[11px] font-medium text-emerald-700 tracking-wide"
      title={review.review_date ? `Reviewed ${review.review_date}` : 'Reviewed'}
    >
      <svg width="11" height="11" viewBox="0 0 10 10" fill="none" aria-hidden>
        <path
          d="M1 5l2.5 2.5L9 2"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span>
        ✓ {label}
        {sub}
      </span>
    </span>
  );
}
