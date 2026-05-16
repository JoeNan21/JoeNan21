import { Link } from 'react-router-dom';
import { useBookmarks } from '../context/BookmarkContext';
import { ceremonyById, articleById } from '../data';
import { useLanguage } from '../context/LanguageContext';

export function Bookmarks() {
  const { bookmarks } = useBookmarks();
  const { t, pick } = useLanguage();

  const items = bookmarks
    .map((b) => {
      const [kind, id] = b.split(':');
      if (kind === 'ceremony') {
        const c = ceremonyById[id];
        if (!c) return null;
        return { kind, id, title: pick(c, 'title'), subtitle: pick(c, 'eyebrow'), path: `/ceremony/${id}` };
      }
      if (kind === 'article') {
        const a = articleById[id];
        if (!a) return null;
        return { kind, id, title: pick(a, 'title'), subtitle: pick(a, 'eyebrow'), path: `/article/${id}` };
      }
      return null;
    })
    .filter((x): x is { kind: string; id: string; title: string; subtitle: string; path: string } => x !== null);

  return (
    <div className="container-tight py-10 md:py-16">
      <header className="mb-10 animate-fadeUp">
        <div className="tile-eyebrow mb-2">{t('nav.bookmarks')}</div>
        <h1 className="font-display text-3xl md:text-5xl text-navy">{t('bookmarks.title')}</h1>
      </header>

      {items.length === 0 ? (
        <p className="font-serif text-base text-navy/70">{t('bookmarks.empty')}</p>
      ) : (
        <ul className="divide-y divide-navy/10 border-y border-navy/10">
          {items.map((it) => (
            <li key={`${it.kind}-${it.id}`} className="py-4">
              <Link to={it.path} className="group flex items-baseline justify-between gap-4">
                <div>
                  <div className="tile-eyebrow">{it.subtitle}</div>
                  <div className="font-display text-xl text-navy group-hover:text-ochre transition-colors">{it.title}</div>
                </div>
                <svg className="text-navy/40 group-hover:text-ochre transition-colors" width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M1 7h12M9 3l4 4-4 4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
