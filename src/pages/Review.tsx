import { useMemo, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { buildReviewMarkdown } from '../lib/reviewExport';

export function Review() {
  const { t } = useLanguage();
  const bundle = useMemo(() => buildReviewMarkdown(), []);
  const [copied, setCopied] = useState(false);

  const download = () => {
    const blob = new Blob([bundle.markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tautua-review-${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const printPdf = () => {
    window.print();
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(bundle.markdown);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  return (
    <div className="container-tight py-10 md:py-16">
      <header className="mb-8 animate-fadeUp">
        <div className="tile-eyebrow mb-2">{t('review.eyebrow')}</div>
        <h1 className="font-display text-3xl md:text-5xl text-navy">{t('review.title')}</h1>
        <p className="lede mt-4 max-w-prose">{t('review.subtitle')}</p>
      </header>

      <section className="rounded-sm border border-navy/10 bg-white/70 p-6 mb-6 animate-fadeUp">
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-4 text-sm">
          <Stat label={t('review.stat.ceremonies')} value={bundle.counts.ceremonies} />
          <Stat label={t('review.stat.articles')} value={bundle.counts.articles} />
          <Stat label={t('review.stat.glossary')} value={bundle.counts.glossary} />
          <Stat label={t('review.stat.phrases')} value={bundle.counts.phrases} />
          <Stat label={t('review.stat.flagged')} value={bundle.counts.flagged} tone="ochre" />
          <Stat label={t('review.stat.approved')} value={bundle.counts.approved} tone="ochre" />
        </div>
      </section>

      <div className="flex flex-wrap gap-3 mb-8 print:hidden">
        <button type="button" onClick={download} className="btn-primary">
          {t('review.download')}
        </button>
        <button type="button" onClick={printPdf} className="btn-ghost">
          {t('review.print')}
        </button>
        <button type="button" onClick={copy} className="btn-ghost">
          {copied ? t('review.copied') : t('review.copy')}
        </button>
      </div>

      <section className="rounded-sm border border-navy/10 bg-white p-6 md:p-8 print:border-0 print:p-0">
        <div className="mb-4 text-xs text-navy/55 print:hidden">{t('review.previewNote')}</div>
        <pre className="whitespace-pre-wrap break-words font-serif text-[13px] leading-relaxed text-ink/90">
{bundle.markdown}
        </pre>
      </section>

      <section className="mt-10 rounded-sm border border-navy/10 bg-sand-dark/40 p-6 animate-fadeUp">
        <h2 className="font-display text-xl text-navy mb-3">{t('review.corrections.title')}</h2>
        <ol className="space-y-2 list-decimal pl-5 font-serif text-[15px] text-ink/85 leading-relaxed">
          <li>{t('review.corrections.step1')}</li>
          <li>
            {t('review.corrections.step2a')}
            <code className="rounded bg-navy/5 px-1 py-0.5 text-xs">src/content/review-patch.json</code>
            {t('review.corrections.step2b')}
          </li>
          <li>{t('review.corrections.step3')}</li>
        </ol>
      </section>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: number; tone?: 'ochre' }) {
  return (
    <div>
      <div className={`font-display text-2xl ${tone === 'ochre' ? 'text-ochre' : 'text-navy'}`}>{value}</div>
      <div className="text-[11px] uppercase tracking-widest text-navy/55 mt-1">{label}</div>
    </div>
  );
}
