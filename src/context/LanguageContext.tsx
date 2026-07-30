import { createContext, useContext, useEffect, useMemo, useState, ReactNode } from 'react';
import en from '../content/ui/en.json';
import sm from '../content/ui/sm.json';

export type Lang = 'en' | 'sm';

type Dict = Record<string, string>;

const dictionaries: Record<Lang, Dict> = { en, sm };

interface LanguageContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  toggle: () => void;
  t: (key: string, fallback?: string) => string;
  pick: (obj: unknown, key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

const STORAGE_KEY = 'tautua_lang';

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    if (typeof window === 'undefined') return 'en';
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored === 'sm' || stored === 'en' ? stored : 'en';
  });

  useEffect(() => {
    document.documentElement.lang = lang;
    window.localStorage.setItem(STORAGE_KEY, lang);
  }, [lang]);

  const value = useMemo<LanguageContextValue>(() => {
    const setLang = (l: Lang) => setLangState(l);
    const toggle = () => setLangState((prev) => (prev === 'en' ? 'sm' : 'en'));
    const t = (key: string, fallback?: string): string => {
      const dict = dictionaries[lang];
      return dict[key] ?? dictionaries.en[key] ?? fallback ?? key;
    };
    const pick = (obj: unknown, key: string): string => {
      if (!obj || typeof obj !== 'object') return '';
      const record = obj as Record<string, unknown>;
      const suffix = lang === 'en' ? '_en' : '_sm';
      const primary = record[`${key}${suffix}`];
      if (typeof primary === 'string' && primary.length > 0) return primary;
      const fallback = record[`${key}_en`];
      return typeof fallback === 'string' ? fallback : '';
    };
    return { lang, setLang, toggle, t, pick };
  }, [lang]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider');
  return ctx;
}
