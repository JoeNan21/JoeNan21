import { NavLink } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';

interface Item {
  to: string;
  labelKey: string;
  icon: JSX.Element;
}

const HomeIcon = (
  <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <path d="M3 9l7-6 7 6v9a1 1 0 0 1-1 1h-4v-6H8v6H4a1 1 0 0 1-1-1V9z" strokeLinejoin="round" />
  </svg>
);
const ModulesIcon = (
  <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <path d="M3 4h14M3 10h14M3 16h14" strokeLinecap="round" />
  </svg>
);
const WizardIcon = (
  <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <path d="M10 2v3M10 15v3M2 10h3M15 10h3M4.5 4.5l2 2M13.5 13.5l2 2M4.5 15.5l2-2M13.5 6.5l2-2" strokeLinecap="round" />
    <circle cx="10" cy="10" r="2.5" />
  </svg>
);
const PhrasesIcon = (
  <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <path d="M3 4h14v9H8l-4 4V4z" strokeLinejoin="round" />
  </svg>
);
const GlossaryIcon = (
  <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
    <path d="M4 3h9a3 3 0 0 1 3 3v11H7a3 3 0 0 1-3-3V3z" strokeLinejoin="round" />
    <path d="M4 14a3 3 0 0 1 3-3h9" />
  </svg>
);

export function BottomNav() {
  const { t } = useLanguage();
  const items: Item[] = [
    { to: '/', labelKey: 'nav.home', icon: HomeIcon },
    { to: '/modules', labelKey: 'nav.modules', icon: ModulesIcon },
    { to: '/wizard', labelKey: 'nav.wizard', icon: WizardIcon },
    { to: '/phrases', labelKey: 'nav.phrases', icon: PhrasesIcon },
    { to: '/glossary', labelKey: 'nav.glossary', icon: GlossaryIcon },
  ];
  return (
    <nav
      aria-label="Primary"
      className="fixed bottom-0 inset-x-0 z-30 border-t border-navy/10 bg-sand/95 backdrop-blur md:hidden pb-[env(safe-area-inset-bottom)]"
    >
      <ul className="grid grid-cols-5">
        {items.map((it) => (
          <li key={it.to}>
            <NavLink
              to={it.to}
              end={it.to === '/'}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center gap-1 py-2.5 text-[10px] uppercase tracking-widest transition-colors ${
                  isActive ? 'text-ochre' : 'text-navy/60 hover:text-navy'
                }`
              }
            >
              {it.icon}
              <span>{t(it.labelKey)}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
