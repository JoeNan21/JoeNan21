import { Link, useParams } from 'react-router-dom';
import { articleById } from '../content';
import { useLanguage } from '../context/LanguageContext';
import { ReviewBadge } from '../components/ReviewBadge';
import { BookmarkButton } from '../components/BookmarkButton';

export function ArticleDetail() {
  const { id } = useParams<{ id: string }>();
  const article = id ? articleById[id] : undefined;
  const { t, pick } = useLanguage();

  if (!article) {
    return (
      <div className="container-tight py-20 text-center">
        <p className="text-navy/60">{t('common.notFound')}</p>
        <Link to="/modules" className="mt-4 inline-block underline">{t('common.back')}</Link>
      </div>
    );
  }

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
          <div className="tile-eyebrow">{pick(article, 'eyebrow')}</div>
          <div className="flex items-center gap-2">
            <ReviewBadge review={article.review} />
            <BookmarkButton id={`article:${article.id}`} />
          </div>
        </div>
        <h1 className="font-display text-4xl md:text-6xl text-navy leading-tight">{pick(article, 'title')}</h1>
        {article.review.varies_by_nuu && (
          <div className="mt-6 rounded-sm border-l-4 border-ochre bg-ochre/5 px-4 py-3 text-sm text-navy/80">
            <strong className="font-medium text-ochre-600">{t('variesByNuu.label')}</strong>{' '}
            {t('variesByNuu.note')}
          </div>
        )}
      </header>

      <div className="prose-body">
        <p>{pick(article, 'body')}</p>
      </div>

      {article.sections && article.sections.length > 0 && (
        <section className="mt-10 space-y-8">
          {article.sections.map((s) => (
            <div key={s.step}>
              <h2 className="font-display text-2xl text-navy mb-2">{pick(s, 'title')}</h2>
              <p className="font-serif text-base sm:text-lg text-ink/90 leading-relaxed">{pick(s, 'body')}</p>
            </div>
          ))}
        </section>
      )}
    </article>
  );
}
