import { useState } from 'react';
import { Link } from 'react-router-dom';
import { events, roles, questions, findAnswer } from '../content/wizard';
import { useLanguage } from '../context/LanguageContext';

type Step = 1 | 2 | 3 | 4;

export function Wizard() {
  const { t, lang } = useLanguage();
  const [step, setStep] = useState<Step>(1);
  const [event, setEvent] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);

  const reset = () => {
    setStep(1);
    setEvent(null);
    setRole(null);
    setQuestion(null);
  };

  const answer = event && role && question ? findAnswer(event, role, question) : undefined;

  return (
    <div className="container-tight py-10 md:py-16">
      <header className="mb-10 animate-fadeUp">
        <div className="tile-eyebrow mb-2">{t('nav.wizard')}</div>
        <h1 className="font-display text-3xl md:text-5xl text-navy">{t('wizard.title')}</h1>
        <p className="lede mt-4">{t('wizard.subtitle')}</p>
      </header>

      <ol className="flex items-center gap-2 mb-8 text-xs uppercase tracking-widest text-navy/55">
        {[
          { n: 1, label: t('wizard.step.event'), val: event },
          { n: 2, label: t('wizard.step.role'), val: role },
          { n: 3, label: t('wizard.step.question'), val: question },
        ].map((s) => (
          <li key={s.n} className="flex items-center gap-2">
            <span
              className={`flex h-6 w-6 items-center justify-center rounded-full border text-[11px] ${
                step >= s.n ? 'bg-navy text-sand border-navy' : 'border-navy/30 text-navy/45'
              }`}
            >
              {s.n}
            </span>
            <span className={step === s.n ? 'text-navy font-medium' : ''}>{s.label}</span>
            {s.n < 3 && <span className="text-navy/20">·</span>}
          </li>
        ))}
      </ol>

      {step === 1 && (
        <div className="grid sm:grid-cols-2 gap-3 animate-fadeUp">
          {events.map((e) => (
            <button
              key={e.id}
              type="button"
              onClick={() => {
                setEvent(e.id);
                setStep(2);
              }}
              className="tile text-left"
            >
              <div className="font-display text-xl text-navy">{lang === 'sm' ? e.label_sm : e.label_en}</div>
              <div className="text-xs text-navy/55 mt-1">{lang === 'sm' ? e.label_en : e.label_sm}</div>
            </button>
          ))}
        </div>
      )}

      {step === 2 && (
        <div className="grid sm:grid-cols-2 gap-3 animate-fadeUp">
          {roles.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => {
                setRole(r.id);
                setStep(3);
              }}
              className="tile text-left"
            >
              <div className="font-display text-xl text-navy">{lang === 'sm' ? r.label_sm : r.label_en}</div>
              <div className="text-xs text-navy/55 mt-1">{lang === 'sm' ? r.label_en : r.label_sm}</div>
            </button>
          ))}
        </div>
      )}

      {step === 3 && (
        <div className="grid sm:grid-cols-2 gap-3 animate-fadeUp">
          {questions.map((qn) => (
            <button
              key={qn.id}
              type="button"
              onClick={() => {
                setQuestion(qn.id);
                setStep(4);
              }}
              className="tile text-left"
            >
              <div className="font-display text-lg text-navy">{lang === 'sm' ? qn.label_sm : qn.label_en}</div>
            </button>
          ))}
        </div>
      )}

      {step === 4 && (
        <div className="animate-fadeUp">
          <div className="rounded-sm border border-navy/10 bg-white p-6 md:p-8">
            <div className="tile-eyebrow mb-3">{t('wizard.guidance')}</div>
            {answer ? (
              <>
                <h2 className="font-display text-2xl md:text-3xl text-navy">
                  {lang === 'sm' ? answer.title_sm : answer.title_en}
                </h2>
                <ol className="mt-6 space-y-4">
                  {(lang === 'sm' ? answer.guidance_sm : answer.guidance_en).map((line, i) => (
                    <li key={i} className="flex gap-4">
                      <span className="font-display text-2xl text-ochre leading-none w-6 shrink-0">{i + 1}</span>
                      <p className="font-serif text-base text-ink/90 leading-relaxed">{line}</p>
                    </li>
                  ))}
                </ol>
                {answer.link && (
                  <Link
                    to={answer.link.kind === 'ceremony' ? `/ceremony/${answer.link.id}` : `/article/${answer.link.id}`}
                    className="btn-ghost mt-8"
                  >
                    {lang === 'sm' ? 'Va’ai le tala atoa' : 'Read the full protocol'}
                    <svg width="14" height="10" viewBox="0 0 14 10" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M1 5h12M9 1l4 4-4 4" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </Link>
                )}
              </>
            ) : (
              <p className="font-serif text-base text-navy/75">
                {lang === 'sm'
                  ? 'E le’i maua se tali patino. Ia matau, e tatau ona talanoa pea ma lou matai mo le aiga ma le nu’u.'
                  : 'No specific answer is recorded yet for this combination. Speak with your matai for guidance specific to your aiga and nu’u.'}
              </p>
            )}
          </div>
          <div className="mt-6 flex justify-between">
            <button type="button" onClick={() => setStep(3)} className="btn-ghost">
              {t('common.prev')}
            </button>
            <button type="button" onClick={reset} className="btn-primary">
              {t('common.reset')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
