# Tautua

Bilingual (English / Samoan) mobile-first PWA — a protocol reference for
diaspora Samoans covering the fa'amatai system, ceremonial functions,
fa'alavelave obligations, the 'ava ceremony, dress codes, and a phrase
library with pronunciation.

Guiding principle: **O le ala i le pule o le tautua** — leadership
through service. That principle should show up in how the app treats
both users and the cultural material itself: humble, careful, deferring
to matai authority on anything that varies by aiga or nu'u.

---

## Stack

- React 18 + TypeScript + Vite
- Tailwind CSS (custom navy / ochre / sand palette, Playfair + DM Sans + Source Serif)
- react-router v6
- vite-plugin-pwa (offline support — users reference this at events with no signal)
- localStorage for language preference and bookmarks
- No backend; no analytics

## Commands

```bash
npm install        # first time
npm run dev        # vite dev server on :5173
npm run build      # tsc -b && vite build (CI-clean must stay green)
npm run preview    # preview the built bundle
```

`npm run build` is the source of truth. It runs the TypeScript project
references first, then Vite. Get this green before pushing.

---

## Layout

```
src/
├── main.tsx                    # entry — wraps app in LanguageProvider + BookmarkProvider + Router
├── App.tsx                     # routes
├── components/                 # Layout, SearchBar, LanguageToggle, BookmarkButton, ReviewBadge, GlossaryTerm
├── context/                    # LanguageContext (lang + t + pick), BookmarkContext
├── content/
│   ├── ui/{en,sm}.json         # all UI chrome strings — never hardcode user-facing copy
│   ├── types.ts                # Ceremony, Article, GlossaryEntry, Phrase, ReviewStatus
│   ├── ceremonies.ts           # ten ceremonies, each with roles/steps/prepare/wear/mistakes
│   ├── articles.ts             # reference articles (fa'amatai overview, fa'alavelave, 'ie toga, dress)
│   ├── glossary.ts             # 25 key terms in both languages
│   ├── phrases.ts              # bilingual phrase library w/ pronunciation
│   ├── wizard.ts               # decision-tree answers for the Protocol Wizard
│   ├── reviewPatches.ts        # reviewer overrides — see "Cultural Review" below
│   └── index.ts                # exports raw content with patches applied
├── lib/
│   ├── search.ts               # tiny in-memory search across all content
│   └── reviewExport.ts         # builds the markdown bundle for /review
├── pages/                      # Home, Modules, CeremonyDetail, ArticleDetail, Glossary, Phrases, Wizard, Bookmarks, Review
└── styles/index.css            # tailwind layers + component classes (.tile, .pill, .btn, etc.)
```

---

## Bilingual conventions

- **Every user-visible string is bilingual.** Content objects carry
  parallel `_en` / `_sm` fields. UI chrome lives in
  `src/content/ui/{en,sm}.json` and is read with `t(key)`.
- For content objects, use the `pick(obj, 'title')` helper from
  `useLanguage()` — it resolves to `obj.title_sm` when the user is in
  Samoan mode, falling back to `_en`. Never read `_en` / `_sm` directly
  from components.
- Add new languages by extending `Lang` in `LanguageContext` and adding
  a new dictionary file — most components are already lang-agnostic.

### Apostrophes in TypeScript data

Samoan content is dense with apostrophes (`fa'asamoa`, `aiga`,
`fa'alavelave`, `'ie toga`). **Use backtick template literals for any
string with apostrophes** — single-quoted strings break the parser and
the failure mode is dozens of cascading TS errors hundreds of lines
away from the real bug. Existing files follow this rule; keep it.

---

## Content architecture

Each ceremony / article / glossary entry / phrase carries a
`review: ReviewStatus` field:

```ts
{ status: 'draft' | 'reviewed' | 'approved',
  reviewer: string | null,
  review_date: 'YYYY-MM-DD' | null,
  varies_by_nuu?: boolean,
  note?: string }
```

- New content defaults to `status: 'draft'` and is labelled
  "AI-generated — pending matai review" in the export.
- Mark `varies_by_nuu: true` on anything where protocol genuinely
  differs between villages / denominations — the export calls these out
  for specific attention and the UI shows an inline note.
- Do not change `status` directly in the content files. Status promotion
  belongs in `reviewPatches.ts` (see below) so review work stays
  reviewable as a discrete diff.

## Cultural review layer

The whole point of this app is that AI-generated cultural content is
not authoritative. Three pieces wire that into the product:

1. **`/review` route** — `src/pages/Review.tsx` calls
   `buildReviewMarkdown()` from `src/lib/reviewExport.ts` to render a
   clean bilingual markdown bundle. Each entry shows EN original → SM
   translation → status + flags. The page offers download, print-to-PDF,
   and copy actions. Send this document to a matai / faife'au / cultural
   advisor for review.
2. **`reviewPatches.ts`** — corrections come back as patches keyed by
   entry id, in the form:
   ```ts
   export const ceremonyPatches = {
     wedding: {
       fields: { overview_sm: "corrected text" },
       review: { status: 'approved', reviewer: 'Matai name', review_date: '2026-05-16' }
     }
   };
   ```
   `applyPatch` (in the same file) merges these into the raw data at
   import time via `src/data/index.ts`. No DB, no admin UI for V1.
3. **`ReviewBadge`** — surfaces a subtle ochre "Community Reviewed"
   chip only when an entry has `status: 'approved'`. Absence of the
   badge means: accurate to best knowledge, pending formal review.

When adding new ceremonies / articles / phrases, follow the same
pattern: parallel `_en` / `_sm` fields, a default `draft` review status,
and a `varies_by_nuu` flag if the protocol meaningfully differs across
villages.

---

## Design direction

Refined Pacific editorial — not tourist kitsch, not generic mobile UI.
Heavyweight serif display, deep ocean navy, warm ochre, sand background,
respectful negative space. Subtle motion (`animate-fadeUp` / `fadeIn`),
no bouncing, no emoji in UI chrome, line icons only.

Colour tokens live in `tailwind.config.js`: `navy`, `ochre`, `sand`,
`terracotta`, `ink`. Component classes live in `src/styles/index.css`
(`.tile`, `.pill`, `.btn-primary`, `.btn-ghost`, `.lede`, `.prose-body`).

Note: `@apply group` is not valid in Tailwind — add the `group` class
inline on the JSX element instead (already done on Home tiles).

---

## Branch & workflow

- Active branch: `claude/tautua-samoan-protocol-6uBaU`.
- Don't push to other branches without explicit permission.
- `npm run build` must be green before pushing.
- Don't create a PR unless asked.
