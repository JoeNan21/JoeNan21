import { useLanguage } from '../context/LanguageContext';

export function LanguageToggle({ compact = false }: { compact?: boolean }) {
  const { lang, setLang } = useLanguage();
  return (
    <div className={`inline-flex items-center rounded-full border border-navy/20 bg-white/70 p-0.5 ${compact ? 'text-xs' : 'text-sm'}`} role="group" aria-label="Language">
      <button
        type="button"
        onClick={() => setLang('en')}
        className={`px-3 py-1 rounded-full transition-colors ${lang === 'en' ? 'bg-navy text-sand' : 'text-navy/70 hover:text-navy'}`}
        aria-pressed={lang === 'en'}
      >
        EN
      </button>
      <button
        type="button"
        onClick={() => setLang('sm')}
        className={`px-3 py-1 rounded-full transition-colors ${lang === 'sm' ? 'bg-navy text-sand' : 'text-navy/70 hover:text-navy'}`}
        aria-pressed={lang === 'sm'}
      >
        SM
      </button>
    </div>
  );
}
