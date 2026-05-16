import { useState } from 'react';
import { glossaryById } from '../data';
import { useLanguage } from '../context/LanguageContext';

export function GlossaryTerm({ id, children }: { id: string; children: React.ReactNode }) {
  const entry = glossaryById[id];
  const { pick } = useLanguage();
  const [open, setOpen] = useState(false);
  if (!entry) return <>{children}</>;
  return (
    <span className="relative inline-block">
      <button type="button" onClick={() => setOpen((v) => !v)} className="glossary-link">
        {children}
      </button>
      {open && (
        <span className="absolute left-0 z-20 mt-1 w-72 rounded-sm border border-navy/15 bg-white p-3 text-sm shadow-lg">
          <span className="block font-display text-navy text-base">{entry.term}</span>
          {entry.pronunciation && (
            <span className="block text-xs text-navy/60 mt-0.5">/{entry.pronunciation}/</span>
          )}
          <span className="block mt-2 text-ink/85 font-serif text-sm leading-relaxed">{pick(entry, 'meaning')}</span>
        </span>
      )}
    </span>
  );
}
