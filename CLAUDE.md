# Tautua

Bilingual (English / Samoan) mobile-first PWA — a protocol reference for
diaspora Samoans covering the faʻamatai system, ceremonial functions,
faʻalavelave obligations, the ʻava ceremony, dress codes, and a phrase
library with pronunciation.

Guiding principle: **O le ala i le pule o le tautua** — leadership
through service. That principle should show up in how the app treats
both users and the cultural material itself: humble, careful, deferring
to matai authority on anything that varies by aiga or nuʻu.

---

## Stack

- React 18 + TypeScript + Vite
- Tailwind CSS (custom navy / ochre / sand palette, Cormorant Garamond + DM Sans + Source Serif)
- react-router v6
- vite-plugin-pwa (offline support — users reference this at events with no signal)
- localStorage for language preference and bookmarks (`tautua_lang`, `tautua_bookmarks`)
- No backend; no analytics

## Commands

```bash
npm install        # first time
npm run dev        # vite dev server on :5173
npm run build      # tsc -b && vite build (CI-clean must stay green)
npm run preview    # preview the built bundle on :4173
```

`npm run build` is the source of truth. It runs the TypeScript project
references first, then Vite. Get this green before pushing.

---

## Layout

```
src/
├── main.tsx                        # entry — wraps app in LanguageProvider + BookmarkProvider + Router
├── App.tsx                         # routes
├── components/                     # Layout, Header, BottomNav, SearchBar, LanguageToggle, BookmarkButton, ReviewBadge, GlossaryTerm
├── context/                        # LanguageContext (lang + t + pick), BookmarkContext
├── types/
│   └── content.ts                  # Ceremony, Article, GlossaryEntry, Phrase, ReviewStatus
├── content/                        # everything user-facing lives here as JSON
│   ├── ui/{en,sm}.json             # all UI chrome strings — never hardcode user-facing copy
│   ├── ceremonies.json             # 10 ceremonies with roles/steps/prepare/wear/mistakes
│   ├── articles/                   # reference articles (one JSON per article)
│   │   ├── faamatai-overview.json  # 8 sections
│   │   ├── faalavelave-overview.json # 8 sections
│   │   ├── ietoga-guide.json
│   │   ├── dress-code.json
│   │   ├── how-titles-bestowed.json
│   │   └── index.json              # ordered list of article ids
│   ├── glossary.json               # 25 key terms in both languages
│   ├── phrases.json                # bilingual phrase library w/ pronunciation
│   ├── wizard.json                 # decision-tree data (events / roles / questions / answers)
│   ├── wizard.ts                   # thin loader exporting typed arrays + findAnswer()
│   ├── review-patch.json           # reviewer overrides — see "Cultural Review" below
│   ├── reviewPatches.ts            # loads review-patch.json + applyPatch helper
│   └── index.ts                    # merges JSON + patches into typed exports
├── lib/
│   ├── search.ts                   # tiny in-memory search across all content
│   └── reviewExport.ts             # builds the markdown bundle for /review
├── pages/                          # Home, Modules, CeremonyDetail, ArticleDetail, Glossary, Phrases, Wizard, Bookmarks, Review
└── styles/index.css                # tailwind layers + component classes (.tile, .pill, .btn, etc.)
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
- **Never hardcode Samoan (or English) strings in components** — add
  a key to both `ui/en.json` and `ui/sm.json` and call `t('key')`.
- Add new languages by extending `Lang` in `LanguageContext` and adding
  a new dictionary file — most components are already lang-agnostic.

### Okina and macrons

All Samoan text uses:

- Okina `ʻ` (U+02BB) — not ASCII apostrophe `'`, not curly `ʼ`
- Macrons `ā ē ī ō ū` where the vowel is long (`mālō`, `tāua`, `lāuga`, `nuʻu`)

Content is JSON, so quoting is straightforward — no backtick tricks
needed. When authoring new content, copy from an existing entry to see
the correct diacriticals; if unsure, mark the entry `varies_by_nuu: true`
and note the ambiguity for the reviewer.

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
  "AI-generated — pending matai review" in the review export.
- Mark `varies_by_nuu: true` on anything where protocol genuinely
  differs between villages / denominations — the export calls these out
  for specific attention and the UI shows an inline "Varies by nuʻu" note.
- Do not change `status` directly in the content JSON. Status promotion
  belongs in `review-patch.json` (see below) so review work stays
  reviewable as a discrete diff.

## Cultural review layer

The whole point of this app is that AI-generated cultural content is
not authoritative. Three pieces wire that into the product:

1. **`/review` route** — `src/pages/Review.tsx` calls
   `buildReviewMarkdown()` from `src/lib/reviewExport.ts` to render a
   clean bilingual markdown bundle. Each entry shows EN original → SM
   translation → status + flags. The page offers download, print-to-PDF,
   and copy actions. Send this document to a matai / faifeʻau / cultural
   advisor for review.
2. **`review-patch.json`** — corrections come back as patches keyed by
   entry id, in the form:
   ```jsonc
   {
     "ceremonyPatches": {
       "wedding": {
         "fields": { "overview_sm": "corrected text" },
         "review": { "status": "approved", "reviewer": "Matai name", "review_date": "2026-05-16" }
       }
     }
   }
   ```
   `applyPatch` in `reviewPatches.ts` merges these into the raw data at
   import time via `src/content/index.ts`. No DB, no admin UI for V1.
3. **`ReviewBadge`** — surfaces a subtle green ✓ "Community Reviewed"
   chip only when an entry has `status: 'approved'`. Absence of the
   badge means: accurate to best knowledge, pending formal review — no
   disclaimer is shown, just clean content.

When adding new ceremonies / articles / phrases, follow the same
pattern: parallel `_en` / `_sm` fields, a default `draft` review status,
and a `varies_by_nuu` flag if the protocol meaningfully differs across
villages.

---

## Design direction

Refined Pacific editorial — not tourist kitsch, not generic mobile UI.
Cormorant Garamond display, deep ocean navy, warm ochre, sand background,
respectful negative space. Subtle motion (`animate-fadeUp` / `fadeIn`),
no bouncing, no emoji in UI chrome, line icons only.

Colour tokens live in `tailwind.config.js`: `navy` (`#0D1B2A`), `ochre`
(`#C9882E`), `sand` (`#F7F3EE`), `terracotta`, `ink` (`#1A1A1A`).
Component classes live in `src/styles/index.css` (`.tile`, `.pill`,
`.btn-primary`, `.btn-ghost`, `.lede`, `.prose-body`).

Note: `@apply group` is not valid in Tailwind — add the `group` class
inline on the JSX element instead.

Mobile-first, 375px base. BottomNav shows on `< md`; desktop uses the
top nav row.

---

## Branch & workflow

- Active branch: `claude/tautua-samoan-protocol-6uBaU`.
- Don't push to other branches without explicit permission.
- `npm run build` must be green before pushing.
- Don't create a PR unless asked.
