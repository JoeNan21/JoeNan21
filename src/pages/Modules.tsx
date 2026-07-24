import { Link } from 'react-router-dom';
import { ceremonies, articles } from '../content';
import { useLanguage } from '../context/LanguageContext';
import { ReviewBadge } from '../components/ReviewBadge';

export function Modules() {
  const { t, pick, lang } = useLanguage();
  return (
    <div className="container-wide py-10 md:py-16">
      <header className="mb-12 animate-fadeUp">
        <div className="tile-eyebrow mb-2">{t('nav.modules')}</div>
        <h1 className="font-display text-3xl md:text-5xl text-navy">
          {lang === 'sm' ? 'Vaega o le tusi fa’asino' : 'The library'}
        </h1>
        <p className="lede mt-4 max-w-prose">
          {lang === 'sm'
            ? 'O sauniga ma le fa’amatalaga atoa o tu, fa’amatai, ma le fa’alavelave.'
            : 'Every ceremony and the full body of articles on protocol, fa’amatai, and obligation.'}
        </p>
      </header>

      <section className="mb-16 animate-fadeUp">
        <div className="tile-eyebrow mb-4">{t('modules.ceremonies')}</div>
        <ul className="divide-y divide-navy/10 border-y border-navy/10">
          {ceremonies.map((c) => (
            <li key={c.id} className="py-5">
              <Link to={`/ceremony/${c.id}`} className="group grid grid-cols-12 gap-4 items-baseline">
                <div className="col-span-12 sm:col-span-3 font-display text-xl text-navy group-hover:text-ochre transition-colors">
                  {pick(c, 'title')}
                </div>
                <div className="col-span-12 sm:col-span-7 text-sm text-navy/70 line-clamp-2 leading-relaxed">
                  {pick(c, 'overview')}
                </div>
                <div className="col-span-12 sm:col-span-2 flex items-center justify-end gap-2 text-xs">
                  <ReviewBadge review={c.review} />
                  <svg className="text-navy/40 group-hover:text-ochre transition-colors" width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M1 7h12M9 3l4 4-4 4" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="animate-fadeUp">
        <div className="tile-eyebrow mb-4">{lang === 'sm' ? 'Tala fa’avae' : 'Reference articles'}</div>
        <div className="grid sm:grid-cols-2 gap-4">
          {articles.map((a) => (
            <Link key={a.id} to={`/article/${a.id}`} className="tile">
              <div className="flex items-center justify-between mb-2">
                <span className="tile-eyebrow">{pick(a, 'eyebrow')}</span>
                <ReviewBadge review={a.review} />
              </div>
              <h3 className="font-display text-xl text-navy leading-snug">{pick(a, 'title')}</h3>
              <p className="mt-2 text-sm text-navy/65 line-clamp-3 font-serif leading-relaxed">{pick(a, 'body')}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
