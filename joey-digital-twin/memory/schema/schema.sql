-- Joey Digital Twin - memory schema (PostgreSQL-compatible)
--
-- NOT PROVISIONED IN v0.1. v0.1 stores these records as local JSON under
-- memory/. This DDL exists so migration to Supabase/Postgres is a load, not a
-- rewrite, and so the shape of memory is reviewable now.
--
-- Design notes:
--   * Memory is RELATIONAL first. Vector retrieval may later supplement it; it
--     must not become the whole memory system (docs/architecture.md).
--   * Nothing is deleted. Supersession is a link, not a DELETE, so the system
--     can always answer "where did this belief come from?".
--   * Contradictions are stored, not resolved.

CREATE TYPE record_type AS ENUM (
  'PERSON','COMPANY','ROLE','RELATIONSHIP','EVENT','DECISION','CLAIM',
  'EVIDENCE','OUTCOME','PREFERENCE','FRAMEWORK','LESSON','COMMITMENT'
);

CREATE TYPE evidence_grade AS ENUM ('FACT','INFERENCE','ASSUMPTION','UNKNOWN');

CREATE TABLE memory_record (
  id            text PRIMARY KEY,
  type          record_type  NOT NULL,
  label         text         NOT NULL DEFAULT '',
  attributes    jsonb        NOT NULL DEFAULT '{}'::jsonb,
  tags          text[]       NOT NULL DEFAULT '{}',
  grade         evidence_grade NOT NULL DEFAULT 'FACT',
  confidence    real         NOT NULL DEFAULT 0.5 CHECK (confidence BETWEEN 0 AND 1),
  source        text,
  provenance    text         NOT NULL,   -- which ingestion run / document
  recorded_at   timestamptz  NOT NULL,   -- when the system learned it
  occurred_at   timestamptz,             -- when it happened in the world
  superseded_by text REFERENCES memory_record(id),
  synthetic     boolean      NOT NULL DEFAULT false,
  approved      boolean      NOT NULL DEFAULT false,
  CONSTRAINT fact_requires_source CHECK (grade <> 'FACT' OR source IS NOT NULL),
  CONSTRAINT no_self_supersede    CHECK (superseded_by IS DISTINCT FROM id)
);

-- Explicit supersession chain. Newer does not automatically win; a link must
-- be recorded by a human or an approved ingestion process.
CREATE TABLE memory_supersedes (
  newer_id text NOT NULL REFERENCES memory_record(id),
  older_id text NOT NULL REFERENCES memory_record(id),
  reason   text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (newer_id, older_id)
);

-- Contradictions are first-class and are never auto-resolved.
CREATE TABLE memory_contradiction (
  a_id     text NOT NULL REFERENCES memory_record(id),
  b_id     text NOT NULL REFERENCES memory_record(id),
  detected_at timestamptz NOT NULL DEFAULT now(),
  resolved_by text,                       -- human only; NULL = open
  note     text,
  PRIMARY KEY (a_id, b_id)
);

CREATE TABLE memory_edge (
  from_id  text NOT NULL REFERENCES memory_record(id),
  to_id    text NOT NULL REFERENCES memory_record(id),
  relation text NOT NULL,                 -- works_at, decided, produced, learned_from
  confidence real NOT NULL DEFAULT 0.5,
  provenance text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (from_id, to_id, relation)
);

-- Reproducibility: what was run, with what, and what came out.
CREATE TABLE decision_run (
  id            uuid PRIMARY KEY,
  case_id       text NOT NULL,
  mode          text NOT NULL,
  provider      text NOT NULL,
  model         text,
  engine_version text NOT NULL,
  authority     text NOT NULL DEFAULT 'READ_ONLY',
  retrieved_ids text[] NOT NULL DEFAULT '{}',
  recommendation jsonb NOT NULL,          -- the decision contract
  confidence    real NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE evaluation_result (
  run_id        uuid REFERENCES decision_run(id),
  case_id       text NOT NULL,
  exact_agreement boolean NOT NULL,
  material_agreement boolean NOT NULL,
  reasoning_similarity real NOT NULL,
  red_team_recall real NOT NULL,
  brier         real NOT NULL,
  PRIMARY KEY (run_id, case_id)
);

CREATE INDEX ON memory_record USING gin (tags);
CREATE INDEX ON memory_record (type);
CREATE INDEX ON memory_record (superseded_by);
