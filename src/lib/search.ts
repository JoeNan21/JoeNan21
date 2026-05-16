import { ceremonies, articles, glossary, phrases } from '../data';

export interface SearchHit {
  id: string;
  kind: 'ceremony' | 'article' | 'glossary' | 'phrase';
  title: string;
  subtitle: string;
  path: string;
  score: number;
}

interface Document {
  hit: Omit<SearchHit, 'score'>;
  haystack: string;
}

const docs: Document[] = [];

for (const c of ceremonies) {
  const haystack = [
    c.title_en,
    c.title_sm,
    c.overview_en,
    c.overview_sm,
    c.steps.map((s) => `${s.title_en} ${s.body_en} ${s.title_sm} ${s.body_sm}`).join(' '),
    c.roles.map((r) => `${r.role_en} ${r.role_sm} ${r.duty_en} ${r.duty_sm}`).join(' '),
  ]
    .join(' ')
    .toLowerCase();
  docs.push({
    hit: { id: c.id, kind: 'ceremony', title: c.title_en, subtitle: c.title_sm, path: `/ceremony/${c.id}` },
    haystack,
  });
}

for (const a of articles) {
  const haystack = [a.title_en, a.title_sm, a.body_en, a.body_sm, a.sections?.map((s) => `${s.title_en} ${s.body_en}`).join(' ')]
    .join(' ')
    .toLowerCase();
  docs.push({
    hit: { id: a.id, kind: 'article', title: a.title_en, subtitle: a.title_sm, path: `/article/${a.id}` },
    haystack,
  });
}

for (const g of glossary) {
  const haystack = [g.term, g.meaning_en, g.meaning_sm].join(' ').toLowerCase();
  docs.push({
    hit: { id: g.id, kind: 'glossary', title: g.term, subtitle: g.meaning_en.slice(0, 80), path: `/glossary#${g.id}` },
    haystack,
  });
}

for (const p of phrases) {
  const haystack = [p.sm, p.en, p.context_en, p.context_sm].join(' ').toLowerCase();
  docs.push({
    hit: { id: p.id, kind: 'phrase', title: p.sm, subtitle: p.en, path: `/phrases#${p.id}` },
    haystack,
  });
}

export function search(query: string, max = 20): SearchHit[] {
  const q = query.trim().toLowerCase();
  if (q.length < 2) return [];
  const terms = q.split(/\s+/).filter(Boolean);
  const results: SearchHit[] = [];
  for (const doc of docs) {
    let score = 0;
    for (const t of terms) {
      const titleMatch = doc.hit.title.toLowerCase().includes(t);
      const subtitleMatch = doc.hit.subtitle.toLowerCase().includes(t);
      const bodyMatch = doc.haystack.includes(t);
      if (titleMatch) score += 5;
      else if (subtitleMatch) score += 3;
      else if (bodyMatch) score += 1;
    }
    if (score > 0) results.push({ ...doc.hit, score });
  }
  results.sort((a, b) => b.score - a.score);
  return results.slice(0, max);
}
