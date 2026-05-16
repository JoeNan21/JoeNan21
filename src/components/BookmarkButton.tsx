import { useBookmarks } from '../context/BookmarkContext';
import { useLanguage } from '../context/LanguageContext';

export function BookmarkButton({ id }: { id: string }) {
  const { isBookmarked, toggle } = useBookmarks();
  const { t } = useLanguage();
  const active = isBookmarked(id);
  return (
    <button
      type="button"
      onClick={() => toggle(id)}
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
        active ? 'border-ochre text-ochre bg-ochre/10' : 'border-navy/15 text-navy/70 hover:border-ochre/50 hover:text-ochre'
      }`}
      aria-pressed={active}
    >
      <svg width="12" height="14" viewBox="0 0 12 14" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.5" aria-hidden>
        <path d="M1 1h10v12L6 9.5 1 13V1z" strokeLinejoin="round" />
      </svg>
      {active ? t('common.bookmarked') : t('common.bookmark')}
    </button>
  );
}
