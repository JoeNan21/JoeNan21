import { ceremonies as raw_ceremonies } from './ceremonies';
import { articles as raw_articles } from './articles';
import { glossary as raw_glossary } from './glossary';
import { phrases as raw_phrases } from './phrases';
import { applyPatch, ceremonyPatches, articlePatches, glossaryPatches, phrasePatches } from './reviewPatches';
import type { Ceremony, Article, GlossaryEntry, Phrase } from './types';

export const ceremonies: Ceremony[] = raw_ceremonies.map((c) => applyPatch(c, ceremonyPatches));
export const articles: Article[] = raw_articles.map((a) => applyPatch(a, articlePatches));
export const glossary: GlossaryEntry[] = raw_glossary.map((g) => applyPatch(g, glossaryPatches));
export const phrases: Phrase[] = raw_phrases.map((p) => applyPatch(p, phrasePatches));

export const ceremonyById = Object.fromEntries(ceremonies.map((c) => [c.id, c]));
export const articleById = Object.fromEntries(articles.map((a) => [a.id, a]));
export const glossaryById = Object.fromEntries(glossary.map((g) => [g.id, g]));
export const phraseById = Object.fromEntries(phrases.map((p) => [p.id, p]));

export type { Ceremony, Article, GlossaryEntry, Phrase } from './types';
