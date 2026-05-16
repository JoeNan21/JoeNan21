import { useMemo, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { buildReviewMarkdown } from '../lib/reviewExport';

export function Review() {
  const { lang } = useLanguage();
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
        <div className="tile-eyebrow mb-2">{lang === 'sm' ? 'Iloiloga' : 'Cultural Review'}</div>
        <h1 className="font-display text-3xl md:text-5xl text-navy">
          {lang === 'sm' ? 'Tu’uina atu mo le iloiloga' : 'Export for matai review'}
        </h1>
        <p className="lede mt-4 max-w-prose">
          {lang === 'sm'
            ? 'Tu’uina atu mea fa’aliliu uma mo le iloiloga e matai a’o le’i fa’asalalauina i tagata lautele. O lo’o ta’u atu fo’i mea fa’apitoa ua mātauina e fesuia’i e tusa ai ma le nu’u.'
            : 'Export every bilingual entry as a clean markdown document for matai review before public release. Entries flagged as varying by nu’u are called out for specific attention.'}
        </p>
      </header>

      <section className="rounded-sm border border-navy/10 bg-white/70 p-6 mb-6 animate-fadeUp">
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-4 text-sm">
          <Stat label="Ceremonies" value={bundle.counts.ceremonies} />
          <Stat label="Articles" value={bundle.counts.articles} />
          <Stat label="Glossary" value={bundle.counts.glossary} />
          <Stat label="Phrases" value={bundle.counts.phrases} />
          <Stat label="Flagged" value={bundle.counts.flagged} tone="ochre" />
          <Stat label="Approved" value={bundle.counts.approved} tone="ochre" />
        </div>
      </section>

      <div className="flex flex-wrap gap-3 mb-8 print:hidden">
        <button type="button" onClick={download} className="btn-primary">
          Download .md
        </button>
        <button type="button" onClick={printPdf} className="btn-ghost">
          Print / Save as PDF
        </button>
        <button type="button" onClick={copy} className="btn-ghost">
          {copied ? 'Copied' : 'Copy markdown'}
        </button>
      </div>

      <section className="rounded-sm border border-navy/10 bg-white p-6 md:p-8 print:border-0 print:p-0">
        <div className="mb-4 text-xs text-navy/55 print:hidden">
          {lang === 'sm'
            ? 'O lo’o va’ai i lalo le ata o lau fa’aliliuga atoa.'
            : 'A preview of the full bilingual export. Print or download for review.'}
        </div>
        <pre className="whitespace-pre-wrap break-words font-serif text-[13px] leading-relaxed text-ink/90">
{bundle.markdown}
        </pre>
      </section>

      <section className="mt-10 rounded-sm border border-navy/10 bg-sand-dark/40 p-6 animate-fadeUp">
        <h2 className="font-display text-xl text-navy mb-3">
          {lang === 'sm' ? 'O le faiga o le fa’asa’oga' : 'How corrections are applied'}
        </h2>
        <ol className="space-y-2 list-decimal pl-5 font-serif text-[15px] text-ink/85 leading-relaxed">
          <li>
            {lang === 'sm'
              ? 'Lomi po o tu’uina atu lenei tusi i se matai mo le iloiloga.'
              : 'Send this exported document to a matai, faife’au, or cultural advisor for review.'}
          </li>
          <li>
            {lang === 'sm'
              ? 'O fa’asa’oga e fa’ailoa mai e tusia i le faila '
              : 'Reviewer corrections are recorded in '}
            <code className="rounded bg-navy/5 px-1 py-0.5 text-xs">src/data/reviewPatches.ts</code>
            {lang === 'sm' ? '.' : ' as a patch entry per id.'}
          </li>
          <li>
            {lang === 'sm'
              ? 'O le tulaga o le “Community Reviewed” o le a fa’aali atu i lea mea ua fa’ataunu’uina.'
              : 'Once a patch is applied with status approved, the Community Reviewed badge appears on that entry across the app.'}
          </li>
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
