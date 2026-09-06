# Knowledge ingestion — specification only

**NOT IMPLEMENTED IN v0.1. This is deliberate.**

No ingester exists because no source has been provided and approved. Building one
first would create pressure to use it, and "explicit ingestion" would become
"whatever was lying around".

## Planned sources

CVs, emails, meeting transcripts, sales notes, documents, decision records,
writing samples, CRM exports, Sorrento operational data, CAOS documents.

## Non-negotiable rules for any future ingester

1. **Nothing is ingested automatically.** Every source is selected deliberately,
   by Joey, per run. No directory watching, no inbox scraping, no bulk import.
2. **Provenance is mandatory.** Every produced record carries the run id, the
   source document, and a locator within it. A record whose origin cannot be
   traced is dropped, not downgraded.
3. **Grades are assigned conservatively.** Extracted content is `INFERENCE` or
   `ASSUMPTION` by default. `FACT` requires a direct, quotable source.
4. **Joey's assertions are facts about what Joey said**, and at most inferences
   about the world.
5. **Nothing about third parties is inferred.** A person mentioned in an email
   gets a record of the mention, not a personality profile.
6. **Existing records are never overwritten.** New information creates a new
   record with an explicit `supersedes` link. Nothing is deleted.
7. **Contradictions are recorded, not resolved.**
8. **A dry run is mandatory.** Every ingester reports what it would write before
   writing anything.

## The question the system must be able to answer

> Where did this belief about Joey come from?

Every design decision here serves that. An ingester that cannot answer it for
every record it produces is not fit to run.

## Format

Ingesters emit `MemoryRecord` JSON (`src/twin/memory/schema.py`) into
`memory/<category>/`. The store validates on load and rejects unknown fields, so
schema drift fails loudly rather than silently.
