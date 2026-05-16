import { ceremonies, articles, glossary, phrases } from '../data';
import type { Ceremony, Article, GlossaryEntry, Phrase, ReviewStatus } from '../data/types';

function statusLabel(r: ReviewStatus): string {
  if (r.status === 'approved') {
    const who = r.reviewer ? ` (${r.reviewer}${r.review_date ? `, ${r.review_date}` : ''})` : '';
    return `Status: APPROVED${who}`;
  }
  if (r.status === 'reviewed') {
    return `Status: REVIEWED — pending sign-off${r.reviewer ? ` (${r.reviewer})` : ''}`;
  }
  return 'Status: DRAFT — AI-generated, pending matai review';
}

function flagsFor(r: ReviewStatus): string {
  const flags: string[] = [];
  if (r.varies_by_nuu) flags.push('FLAG: Varies by nu\'u — confirm against village protocol.');
  if (r.note) flags.push(`Note: ${r.note}`);
  return flags.length ? `\n> ${flags.join('\n> ')}` : '';
}

function pair(label: string, en: string, sm: string): string {
  return `\n#### ${label}\n\n**EN:** ${en.trim()}\n\n**SM:** ${sm.trim()}\n`;
}

function pairList(label: string, en: string[], sm: string[]): string {
  if (!en.length && !sm.length) return '';
  const lines = [`\n#### ${label}\n`];
  const max = Math.max(en.length, sm.length);
  for (let i = 0; i < max; i++) {
    lines.push(`${i + 1}. **EN:** ${en[i] ?? '—'}`);
    lines.push(`   **SM:** ${sm[i] ?? '—'}`);
  }
  return lines.join('\n') + '\n';
}

function renderCeremony(c: Ceremony): string {
  const parts: string[] = [];
  parts.push(`### ${c.title_en} — ${c.title_sm}`);
  parts.push(`*${c.eyebrow_en} / ${c.eyebrow_sm}*`);
  parts.push(`\n${statusLabel(c.review)}${flagsFor(c.review)}`);
  parts.push(pair('Overview', c.overview_en, c.overview_sm));
  parts.push('\n#### Roles');
  for (const r of c.roles) {
    parts.push(`- **${r.role_en}** / *${r.role_sm}*`);
    parts.push(`  - EN: ${r.duty_en}`);
    parts.push(`  - SM: ${r.duty_sm}`);
  }
  parts.push('\n#### Protocol order');
  for (const s of c.steps) {
    parts.push(`\n**${s.step}. ${s.title_en}** — *${s.title_sm}*`);
    parts.push(`- EN: ${s.body_en}`);
    parts.push(`- SM: ${s.body_sm}`);
  }
  parts.push(pairList('What to prepare', c.prepare_en, c.prepare_sm));
  parts.push(pairList('What to wear', c.wear_en, c.wear_sm));
  parts.push(pairList('Common mistakes', c.mistakes_en, c.mistakes_sm));
  return parts.join('\n');
}

function renderArticle(a: Article): string {
  const parts: string[] = [];
  parts.push(`### ${a.title_en} — ${a.title_sm}`);
  parts.push(`*${a.eyebrow_en} / ${a.eyebrow_sm}*`);
  parts.push(`\n${statusLabel(a.review)}${flagsFor(a.review)}`);
  parts.push(pair('Body', a.body_en, a.body_sm));
  if (a.sections?.length) {
    parts.push('\n#### Sections');
    for (const s of a.sections) {
      parts.push(`\n**${s.step}. ${s.title_en}** — *${s.title_sm}*`);
      parts.push(`- EN: ${s.body_en}`);
      parts.push(`- SM: ${s.body_sm}`);
    }
  }
  return parts.join('\n');
}

function renderGlossary(g: GlossaryEntry): string {
  const parts: string[] = [];
  parts.push(`### ${g.term}${g.pronunciation ? ` *(${g.pronunciation})*` : ''}`);
  parts.push(`\n${statusLabel(g.review)}${flagsFor(g.review)}`);
  parts.push(`\n- **EN:** ${g.meaning_en}`);
  parts.push(`- **SM:** ${g.meaning_sm}`);
  return parts.join('\n');
}

function renderPhrase(p: Phrase): string {
  const parts: string[] = [];
  parts.push(`### ${p.sm}`);
  parts.push(`*Pronunciation:* ${p.pronunciation}`);
  parts.push(`\n${statusLabel(p.review)}${flagsFor(p.review)}`);
  parts.push(`\n- **EN meaning:** ${p.en}`);
  parts.push(`- **EN context:** ${p.context_en}`);
  parts.push(`- **SM context:** ${p.context_sm}`);
  return parts.join('\n');
}

export interface ReviewBundle {
  markdown: string;
  generatedAt: string;
  counts: { ceremonies: number; articles: number; glossary: number; phrases: number; flagged: number; approved: number };
}

export function buildReviewMarkdown(): ReviewBundle {
  const lines: string[] = [];
  const now = new Date();
  const iso = now.toISOString().slice(0, 10);

  const all = [
    ...ceremonies.map((c) => c.review),
    ...articles.map((a) => a.review),
    ...glossary.map((g) => g.review),
    ...phrases.map((p) => p.review),
  ];
  const flagged = all.filter((r) => r.varies_by_nuu).length;
  const approved = all.filter((r) => r.status === 'approved').length;

  lines.push(`# Tautua — Cultural Review Export`);
  lines.push(`Generated ${iso}\n`);
  lines.push(`Each entry below shows the English source, the Samoan translation, the current review status, and any cultural flags.\n`);
  lines.push(`Items flagged **Varies by nu'u** should be reviewed against the protocol of the specific village or denomination you are advising on.\n`);
  lines.push(`---\n`);
  lines.push(`## Summary`);
  lines.push(`- Ceremonies: ${ceremonies.length}`);
  lines.push(`- Articles: ${articles.length}`);
  lines.push(`- Glossary entries: ${glossary.length}`);
  lines.push(`- Phrases: ${phrases.length}`);
  lines.push(`- Flagged 'varies by nu'u': ${flagged}`);
  lines.push(`- Currently approved: ${approved}\n`);

  lines.push(`---\n## Ceremonies\n`);
  for (const c of ceremonies) lines.push(renderCeremony(c) + '\n\n---\n');

  lines.push(`\n## Articles\n`);
  for (const a of articles) lines.push(renderArticle(a) + '\n\n---\n');

  lines.push(`\n## Glossary\n`);
  for (const g of glossary) lines.push(renderGlossary(g) + '\n\n---\n');

  lines.push(`\n## Phrases\n`);
  for (const p of phrases) lines.push(renderPhrase(p) + '\n\n---\n');

  lines.push(`\n## How to submit corrections\n`);
  lines.push(`Edit this document with your corrections. The maintainer will translate accepted changes into \`src/data/reviewPatches.ts\` using the format:\n`);
  lines.push('```ts');
  lines.push(`export const ceremonyPatches = {`);
  lines.push(`  "wedding": {`);
  lines.push(`    fields: { overview_sm: "your corrected text" },`);
  lines.push(`    review: { status: "approved", reviewer: "Your title and name", review_date: "${iso}" }`);
  lines.push(`  }`);
  lines.push(`};`);
  lines.push('```');

  return {
    markdown: lines.join('\n'),
    generatedAt: now.toISOString(),
    counts: {
      ceremonies: ceremonies.length,
      articles: articles.length,
      glossary: glossary.length,
      phrases: phrases.length,
      flagged,
      approved,
    },
  };
}
