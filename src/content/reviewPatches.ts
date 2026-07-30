import type { ReviewStatus } from '../types/content';
import patchData from './review-patch.json';

export interface PatchEntry {
  fields?: Record<string, string>;
  review: ReviewStatus;
}

export type PatchSet = Record<string, PatchEntry>;

export const ceremonyPatches: PatchSet = (patchData.ceremonyPatches ?? {}) as PatchSet;
export const articlePatches: PatchSet = (patchData.articlePatches ?? {}) as PatchSet;
export const glossaryPatches: PatchSet = (patchData.glossaryPatches ?? {}) as PatchSet;
export const phrasePatches: PatchSet = (patchData.phrasePatches ?? {}) as PatchSet;

export function applyPatch<T extends { id: string; review: ReviewStatus }>(
  item: T,
  patches: PatchSet
): T {
  const patch = patches[item.id];
  if (!patch) return item;
  const merged: T = { ...item };
  if (patch.fields) {
    for (const [k, v] of Object.entries(patch.fields)) {
      (merged as unknown as Record<string, unknown>)[k] = v;
    }
  }
  merged.review = patch.review;
  return merged;
}
