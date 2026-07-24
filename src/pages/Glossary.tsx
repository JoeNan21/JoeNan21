import { useEffect, useMemo, useState } from 'react';
import { glossary } from '../content';
import { useLanguage } from '../context/LanguageContext';
import { ReviewBadge } from '../components/ReviewBadge';

export function Glossary() {
  const { t, pick, lang } = useLanguage();
  const [q, setQ] = useState('');

  const filtered = useMemo(() => {
    const query = q.toLowerCase().trim();
    if (!query) return glossary;
    return glossary.filter(
      (g) =>
        g.term.toLowerCase().includes(query) ||
        g.meaning_en.toLowerCase().includes(query) ||
        g.meaning_sm.toLowerCase().includes(query)
    );
  }, [q]);

  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (hash) {
      const el = document.getElementById(hash);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, []);

  return (
    <div className="container-tight py-10 md:py-16">
      <header className="mb-8 animate-fadeUp">
        <div className="tile-eyebrow mb-2">{t('nav.glossary')}</div>
        <h1 className="font-display text-3xl md:text-5xl text-navy">{t('modules.glossary')}</h1>
        <p className="lede mt-4 max-w-prose">
          {lang === 'sm'
            ? 'O upu uma o lo’o aoga i totonu o le tusi fa’asino, fa’asoa i gagana e lua.'
            : 'Every term used across the app, defined in both languages.'}
        </p>
      </header>

      <input
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={lang === 'sm' ? 'Su’e se upu…' : 'Filter terms…'}
        className="w-full rounded-sm border border-navy/15 bg-white/70 px-4 py-3 text-sm placeholder:text-navy/40 focus:outline-none focus:border-ochre focus:bg-white mb-8"
      />

      <ul className="divide-y divide-navy/10 border-y border-navy/10">
        {filtered.map((g) => (
          <li key={g.id} id={g.id} className="py-5 scroll-mt-24">
            <div className="flex items-baseline justify-between gap-3 flex-wrap">
              <div className="flex items-baseline gap-3">
                <span className="font-display text-xl text-navy">{g.term}</span>
                {g.pronunciation && <span className="text-xs italic text-navy/55">/{g.pronunciation}/</span>}
              </div>
              <ReviewBadge review={g.review} />
            </div>
            <p className="font-serif text-base text-ink/90 mt-2 leading-relaxed">{pick(g, 'meaning')}</p>
            {g.related && g.related.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                {g.related.map((r) => (
                  <a key={r} href={`#${r}`} className="pill hover:bg-navy/5">
                    {r}
                  </a>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
