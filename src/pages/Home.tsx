import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { SearchBar } from '../components/SearchBar';

const moduleTiles = [
  { eyebrowKey: 'modules.faamatai', descKey: 'modules.faamatai.desc', to: '/article/faamatai-overview', num: '01' },
  { eyebrowKey: 'modules.ceremonies', descKey: 'modules.ceremonies.desc', to: '/modules', num: '02' },
  { eyebrowKey: 'modules.faalavelave', descKey: 'modules.faalavelave.desc', to: '/article/faalavelave-overview', num: '03' },
  { eyebrowKey: 'modules.ava', descKey: 'modules.ava.desc', to: '/ceremony/ava', num: '04' },
  { eyebrowKey: 'modules.phrases', descKey: 'modules.phrases.desc', to: '/phrases', num: '05' },
  { eyebrowKey: 'modules.ietoga', descKey: 'modules.ietoga.desc', to: '/article/ietoga-guide', num: '06' },
  { eyebrowKey: 'modules.dress', descKey: 'modules.dress.desc', to: '/article/dress-code', num: '07' },
  { eyebrowKey: 'modules.glossary', descKey: 'modules.glossary.desc', to: '/glossary', num: '08' },
];

const quickEvents: { id: string; label_en: string; label_sm: string }[] = [
  { id: 'wedding', label_en: 'Wedding', label_sm: `Fa'aipoipoga` },
  { id: 'funeral', label_en: 'Funeral / ifoga', label_sm: 'Maliu' },
  { id: 'faalavelave', label_en: `Fa'alavelave`, label_sm: `Fa'alavelave` },
  { id: 'saofai', label_en: `Title bestowal`, label_sm: `Saofa'i` },
  { id: 'white-sunday', label_en: 'White Sunday', label_sm: 'Lotu a Tamaiti' },
  { id: 'fono', label_en: 'Fono', label_sm: 'Fono' },
  { id: 'church', label_en: 'Church service', label_sm: 'Lotu' },
  { id: 'other', label_en: 'Other', label_sm: 'Isi' },
];

const quickEventLink: Record<string, string> = {
  wedding: '/ceremony/wedding',
  funeral: '/ceremony/funeral',
  faalavelave: '/article/faalavelave-overview',
  saofai: '/ceremony/saofai',
  'white-sunday': '/ceremony/white-sunday',
  fono: '/article/faamatai-overview',
  church: '/ceremony/toonai',
  other: '/wizard',
};

export function Home() {
  const { t, lang } = useLanguage();
  return (
    <div className="container-wide py-10 md:py-16">
      <section className="grid md:grid-cols-12 gap-10 md:gap-16 items-start mb-16">
        <div className="md:col-span-7 animate-fadeUp">
          <div className="tile-eyebrow mb-3">{t('home.greeting')}</div>
          <h1 className="font-display text-4xl md:text-6xl leading-[1.05] text-navy">
            {t('app.name')}
            <span className="block text-ochre italic font-medium text-2xl md:text-3xl mt-4">
              {t('app.tagline')}
            </span>
          </h1>
          <p className="lede mt-6 max-w-prose">{t('app.subtitle')}</p>
          <div className="mt-8 max-w-xl">
            <SearchBar />
          </div>
          <div className="mt-4">
            <Link to="/wizard" className="btn-primary">
              {t('home.openWizard')}
              <svg width="14" height="10" viewBox="0 0 14 10" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M1 5h12M9 1l4 4-4 4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>
          </div>
        </div>
        <aside className="md:col-span-5 md:pt-6 animate-fadeUp">
          <div className="rounded-sm border border-navy/10 bg-white/60 p-6 md:p-7">
            <p className="font-display italic text-xl md:text-2xl text-navy leading-snug">
              "{t('app.principle')}"
            </p>
            <p className="mt-3 text-sm text-navy/65">
              {lang === 'sm'
                ? 'O le mataupu silisili o le aganu\'u Sāmoa, ma o le agaga o lenei tusi fa\'asino.'
                : 'The guiding principle of Samoan life, and the spirit of this reference.'}
            </p>
          </div>
        </aside>
      </section>

      <section className="mb-16 animate-fadeUp">
        <div className="flex items-end justify-between mb-6 gap-6">
          <div>
            <div className="tile-eyebrow">{t('home.quick.title')}</div>
            <h2 className="font-display text-2xl md:text-3xl text-navy mt-1">{t('home.quick.subtitle')}</h2>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {quickEvents.map((q) => (
            <Link
              key={q.id}
              to={quickEventLink[q.id] ?? '/wizard'}
              className="tile flex flex-col gap-1"
            >
              <span className="font-display text-navy text-lg leading-tight">{lang === 'sm' ? q.label_sm : q.label_en}</span>
              <span className="text-xs text-navy/55">{lang === 'sm' ? q.label_en : q.label_sm}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="animate-fadeUp">
        <div className="flex items-end justify-between mb-6 gap-6">
          <div>
            <div className="tile-eyebrow">{t('home.modules.title')}</div>
            <h2 className="font-display text-2xl md:text-3xl text-navy mt-1">{t('home.modules.subtitle')}</h2>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {moduleTiles.map((m) => (
            <Link key={m.to} to={m.to} className="tile group">
              <div className="flex items-baseline justify-between mb-3">
                <span className="font-display text-ochre text-2xl">{m.num}</span>
                <svg className="text-navy/30 group-hover:text-ochre transition-colors" width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M1 13L13 1M4 1h9v9" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <h3 className="font-display text-lg text-navy leading-snug">{t(m.eyebrowKey)}</h3>
              <p className="mt-2 text-sm text-navy/65 leading-relaxed">{t(m.descKey)}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
