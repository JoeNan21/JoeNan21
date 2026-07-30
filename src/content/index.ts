import raw_ceremonies from './ceremonies.json';
import raw_glossary from './glossary.json';
import raw_phrases from './phrases.json';

import faamatai from './articles/faamatai-overview.json';
import howTitles from './articles/how-titles-bestowed.json';
import faalavelave from './articles/faalavelave-overview.json';
import ietoga from './articles/ietoga-guide.json';
import dresscode from './articles/dress-code.json';

import { applyPatch, ceremonyPatches, articlePatches, glossaryPatches, phrasePatches } from './reviewPatches';
import type { Ceremony, Article, GlossaryEntry, Phrase } from '../types/content';

const raw_articles = [faamatai, howTitles, faalavelave, ietoga, dresscode] as unknown as Article[];

export const ceremonies: Ceremony[] = (raw_ceremonies as unknown as Ceremony[]).map((c) => applyPatch(c, ceremonyPatches));
export const articles: Article[] = raw_articles.map((a) => applyPatch(a, articlePatches));
export const glossary: GlossaryEntry[] = (raw_glossary as unknown as GlossaryEntry[]).map((g) => applyPatch(g, glossaryPatches));
export const phrases: Phrase[] = (raw_phrases as unknown as Phrase[]).map((p) => applyPatch(p, phrasePatches));

export const ceremonyById = Object.fromEntries(ceremonies.map((c) => [c.id, c]));
export const articleById = Object.fromEntries(articles.map((a) => [a.id, a]));
export const glossaryById = Object.fromEntries(glossary.map((g) => [g.id, g]));
export const phraseById = Object.fromEntries(phrases.map((p) => [p.id, p]));

export type { Ceremony, Article, GlossaryEntry, Phrase } from '../types/content';
