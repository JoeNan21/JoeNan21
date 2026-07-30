import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { LanguageToggle } from './LanguageToggle';
import { BottomNav } from './BottomNav';

export function Layout() {
  const { t } = useLanguage();
  const location = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
  }, [location.pathname]);

  const navItems = [
    { to: '/', label: t('nav.home') },
    { to: '/modules', label: t('nav.modules') },
    { to: '/wizard', label: t('nav.wizard') },
    { to: '/phrases', label: t('nav.phrases') },
    { to: '/glossary', label: t('nav.glossary') },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-sand text-ink">
      <header className="sticky top-0 z-20 border-b border-navy/10 bg-sand/85 backdrop-blur">
        <div className="container-wide flex items-center justify-between py-3.5">
          <Link to="/" className="flex items-center gap-2.5 group">
            <span className="flex h-9 w-9 items-center justify-center rounded-sm bg-navy font-display text-ochre text-xl">T</span>
            <span className="hidden sm:flex flex-col leading-tight">
              <span className="font-display text-lg text-navy">{t('app.name')}</span>
              <span className="text-[10px] uppercase tracking-[0.2em] text-navy/55">{t('app.tagline')}</span>
            </span>
          </Link>
          <nav className="hidden md:flex items-center gap-1" aria-label="Primary desktop">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `rounded-sm px-3 py-1.5 text-sm transition-colors ${
                    isActive ? 'bg-navy/5 text-navy font-medium' : 'text-navy/70 hover:text-navy'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <Link
              to="/bookmarks"
              className="inline-flex p-2 rounded-sm text-navy/60 hover:text-navy"
              aria-label={t('nav.bookmarks')}
            >
              <svg width="16" height="18" viewBox="0 0 16 18" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
                <path d="M2 1h12v16L8 13 2 17V1z" strokeLinejoin="round" />
              </svg>
            </Link>
            <LanguageToggle />
          </div>
        </div>
      </header>

      <main className="flex-1 animate-fadeIn pb-24 md:pb-0">
        <Outlet />
      </main>

      <footer className="mt-16 border-t border-navy/10 bg-navy text-sand/85 pb-20 md:pb-0">
        <div className="container-wide py-10">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="font-display text-2xl italic text-ochre">{t('footer.principle')}</p>
              <p className="mt-2 max-w-xl text-sm leading-relaxed text-sand/70">{t('footer.note')}</p>
            </div>
            <div className="text-xs text-sand/55 space-y-1">
              <div>© {new Date().getFullYear()} Tautua</div>
              <Link to="/review" className="hover:text-ochre underline underline-offset-4">{t('footer.reviewLink')}</Link>
            </div>
          </div>
        </div>
      </footer>

      <BottomNav />
    </div>
  );
}
