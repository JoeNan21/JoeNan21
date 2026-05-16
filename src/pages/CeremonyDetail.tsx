import { Link, useParams } from 'react-router-dom';
import { ceremonyById, phraseById } from '../data';
import { useLanguage } from '../context/LanguageContext';
import { ReviewBadge } from '../components/ReviewBadge';
import { BookmarkButton } from '../components/BookmarkButton';

export function CeremonyDetail() {
  const { id } = useParams<{ id: string }>();
  const ceremony = id ? ceremonyById[id] : undefined;
  const { t, pick, lang } = useLanguage();

  if (!ceremony) {
    return (
      <div className="container-tight py-20 text-center">
        <p className="text-navy/60">Not found.</p>
        <Link to="/modules" className="mt-4 inline-block underline">{t('common.back')}</Link>
      </div>
    );
  }

  const phraseList = ceremony.phrases.map((pid) => phraseById[pid]).filter(Boolean);

  return (
    <article className="container-tight py-10 md:py-16">
      <Link to="/modules" className="inline-flex items-center gap-2 text-sm text-navy/60 hover:text-navy mb-8">
        <svg width="14" height="10" viewBox="0 0 14 10" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M13 5H1M5 1L1 5l4 4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        {t('common.back')}
      </Link>

      <header className="mb-10 animate-fadeUp">
        <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
          <div className="tile-eyebrow">{pick(ceremony, 'eyebrow')}</div>
          <div className="flex items-center gap-2">
            <ReviewBadge review={ceremony.review} />
            <BookmarkButton id={`ceremony:${ceremony.id}`} />
          </div>
        </div>
        <h1 className="font-display text-4xl md:text-6xl text-navy leading-tight">{pick(ceremony, 'title')}</h1>
        <p className="lede mt-5">{pick(ceremony, 'overview')}</p>
        {ceremony.review.varies_by_nuu && (
          <div className="mt-6 rounded-sm border-l-4 border-ochre bg-ochre/5 px-4 py-3 text-sm text-navy/80">
            <strong className="font-medium text-ochre-600">
              {lang === 'sm' ? 'E fesuia’i e tusa ai ma le nu’u.' : 'Varies by nu’u.'}
            </strong>{' '}
            {lang === 'sm'
              ? 'Talanoa ma matai o lou aiga po o le nu’u mo tu fa’apitoa.'
              : 'Speak with the matai of your aiga or village for protocol specific to your context.'}
          </div>
        )}
      </header>

      <section className="mb-10 animate-fadeUp">
        <h2 className="font-display text-2xl text-navy mb-4">{t('common.roles')}</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {ceremony.roles.map((r, i) => (
            <div key={i} className="rounded-sm border border-navy/10 bg-white/60 p-4">
              <div className="font-display text-lg text-navy">{pick(r, 'role')}</div>
              <p className="font-serif text-sm text-navy/75 mt-2 leading-relaxed">{pick(r, 'duty')}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-10 animate-fadeUp">
        <h2 className="font-display text-2xl text-navy mb-4">{t('common.steps')}</h2>
        <ol className="space-y-6">
          {ceremony.steps.map((s) => (
            <li key={s.step} className="grid grid-cols-12 gap-4">
              <div className="col-span-2 sm:col-span-1">
                <div className="font-display text-3xl text-ochre leading-none">{s.step}</div>
              </div>
              <div className="col-span-10 sm:col-span-11 border-l-2 border-navy/10 pl-5 pb-2">
                <h3 className="font-display text-xl text-navy">{pick(s, 'title')}</h3>
                <p className="font-serif text-base text-ink/85 mt-2 leading-relaxed">{pick(s, 'body')}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="grid md:grid-cols-2 gap-8 mb-10 animate-fadeUp">
        <div>
          <h2 className="font-display text-xl text-navy mb-3">{t('common.prepare')}</h2>
          <ul className="space-y-2">
            {(lang === 'sm' ? ceremony.prepare_sm : ceremony.prepare_en).map((item, i) => (
              <li key={i} className="flex gap-3 font-serif text-[15px] leading-relaxed">
                <span className="mt-2 h-1 w-3 shrink-0 bg-ochre" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2 className="font-display text-xl text-navy mb-3">{t('common.wear')}</h2>
          <ul className="space-y-2">
            {(lang === 'sm' ? ceremony.wear_sm : ceremony.wear_en).map((item, i) => (
              <li key={i} className="flex gap-3 font-serif text-[15px] leading-relaxed">
                <span className="mt-2 h-1 w-3 shrink-0 bg-ochre" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {phraseList.length > 0 && (
        <section className="mb-10 animate-fadeUp">
          <h2 className="font-display text-xl text-navy mb-4">{t('common.phrases')}</h2>
          <ul className="space-y-3">
            {phraseList.map((p) => (
              <li key={p.id} className="rounded-sm border border-navy/10 bg-white/60 p-4">
                <div className="font-display text-lg text-navy">{p.sm}</div>
                <div className="text-xs text-navy/55 italic mt-0.5">/{p.pronunciation}/</div>
                <div className="font-serif text-sm text-ink/85 mt-2">{p.en}</div>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="rounded-sm border border-terracotta/30 bg-terracotta/5 p-6 animate-fadeUp">
        <h2 className="font-display text-xl text-terracotta mb-3">{t('common.mistakes')}</h2>
        <ul className="space-y-2">
          {(lang === 'sm' ? ceremony.mistakes_sm : ceremony.mistakes_en).map((item, i) => (
            <li key={i} className="flex gap-3 font-serif text-[15px] leading-relaxed">
              <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full border border-terracotta" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>
    </article>
  );
}
