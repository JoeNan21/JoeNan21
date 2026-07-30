import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { search } from '../lib/search';

export function SearchBar() {
  const { t } = useLanguage();
  const [q, setQ] = useState('');
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const ref = useRef<HTMLDivElement>(null);

  const results = useMemo(() => search(q, 8), [q]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  return (
    <div ref={ref} className="relative">
      <div className="relative">
        <svg
          aria-hidden
          className="absolute left-4 top-1/2 -translate-y-1/2 text-navy/40"
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <circle cx="7" cy="7" r="5" />
          <path d="M11 11l4 4" strokeLinecap="round" />
        </svg>
        <input
          type="search"
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder={t('home.search.placeholder')}
          className="w-full rounded-sm border border-navy/15 bg-white/70 pl-11 pr-4 py-3 text-sm placeholder:text-navy/40 focus:outline-none focus:border-ochre focus:bg-white"
        />
      </div>
      {open && q.length >= 2 && (
        <div className="absolute z-30 mt-2 w-full overflow-hidden rounded-sm border border-navy/10 bg-white shadow-lg">
          {results.length === 0 ? (
            <div className="px-4 py-3 text-sm text-navy/60">{t('search.empty')}</div>
          ) : (
            <ul>
              {results.map((r) => (
                <li key={`${r.kind}-${r.id}`}>
                  <button
                    type="button"
                    onClick={() => {
                      setOpen(false);
                      setQ('');
                      navigate(r.path);
                    }}
                    className="block w-full border-b border-navy/5 px-4 py-3 text-left transition-colors hover:bg-sand"
                  >
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="font-medium text-navy">{r.title}</span>
                      <span className="text-[10px] uppercase tracking-widest text-navy/40">{r.kind}</span>
                    </div>
                    <div className="text-xs text-navy/60 mt-0.5 line-clamp-1">{r.subtitle}</div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
