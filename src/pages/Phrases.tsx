import { useEffect, useMemo, useState } from 'react';
import { phrases } from '../content';
import { useLanguage } from '../context/LanguageContext';
import type { PhraseCategory } from '../content/types';
import { ReviewBadge } from '../components/ReviewBadge';

const categories: { id: PhraseCategory | 'all'; label_en: string; label_sm: string }[] = [
  { id: 'all', label_en: 'All', label_sm: 'Uma' },
  { id: 'greetings', label_en: 'Greetings & respect', label_sm: 'Fa’afeiloa’iga' },
  { id: 'condolences', label_en: 'Condolences', label_sm: 'Fa’afetai-alofa' },
  { id: 'blessings', label_en: 'Blessings', label_sm: 'Fa’amanuiaga' },
  { id: 'lauga', label_en: 'Lauga / formal speech', label_sm: 'Lauga' },
  { id: 'church', label_en: 'Church', label_sm: 'Lotu' },
  { id: 'faalavelave', label_en: 'Fa’alavelave', label_sm: 'Fa’alavelave' },
];

export function Phrases() {
  const { t, pick, lang } = useLanguage();
  const [cat, setCat] = useState<PhraseCategory | 'all'>('all');

  const filtered = useMemo(() => (cat === 'all' ? phrases : phrases.filter((p) => p.category === cat)), [cat]);

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
        <div className="tile-eyebrow mb-2">{t('nav.phrases')}</div>
        <h1 className="font-display text-3xl md:text-5xl text-navy">{t('modules.phrases')}</h1>
        <p className="lede mt-4 max-w-prose">
          {lang === 'sm'
            ? 'Fa’aupuga aloga’ia ma masani, fa’asoa i gagana e lua ma le faaleoga.'
            : 'Formal and everyday phrases, paired with pronunciation guidance.'}
        </p>
      </header>

      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => setCat(c.id)}
            className={`pill cursor-pointer ${cat === c.id ? 'bg-navy text-sand border-navy' : 'hover:bg-navy/5'}`}
          >
            {lang === 'sm' ? c.label_sm : c.label_en}
          </button>
        ))}
      </div>

      <ul className="space-y-4">
        {filtered.map((p) => (
          <li
            key={p.id}
            id={p.id}
            className="rounded-sm border border-navy/10 bg-white/60 p-5 scroll-mt-24 animate-fadeUp"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="font-display text-2xl text-navy leading-tight">{p.sm}</div>
                <div className="font-serif text-base text-ink/85 mt-1">{p.en}</div>
              </div>
              <ReviewBadge review={p.review} />
            </div>
            <div className="mt-3 grid sm:grid-cols-2 gap-3 text-sm">
              <div>
                <div className="text-[11px] uppercase tracking-widest text-navy/45 mb-1">{t('common.pronunciation')}</div>
                <div className="font-serif italic text-navy/80">/{p.pronunciation}/</div>
              </div>
              <div>
                <div className="text-[11px] uppercase tracking-widest text-navy/45 mb-1">{t('common.context')}</div>
                <div className="font-serif text-ink/85">{pick(p, 'context')}</div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
