export interface Bilingual {
  en: string;
  sm: string;
}

export interface ReviewStatus {
  status: 'draft' | 'reviewed' | 'approved';
  reviewer: string | null;
  review_date: string | null;
  varies_by_nuu?: boolean;
  note?: string;
}

export interface Step {
  step: number;
  title_en: string;
  title_sm: string;
  body_en: string;
  body_sm: string;
}

export interface Role {
  role_en: string;
  role_sm: string;
  duty_en: string;
  duty_sm: string;
}

export interface DoDont {
  do_en: string;
  do_sm: string;
}

export type PhraseCategory =
  | 'greetings'
  | 'condolences'
  | 'blessings'
  | 'lauga'
  | 'church'
  | 'faalavelave';

export interface Phrase {
  id: string;
  category: PhraseCategory;
  sm: string;
  en: string;
  pronunciation: string;
  context_en: string;
  context_sm: string;
  review: ReviewStatus;
}

export interface Ceremony {
  id: string;
  title_en: string;
  title_sm: string;
  eyebrow_en: string;
  eyebrow_sm: string;
  overview_en: string;
  overview_sm: string;
  roles: Role[];
  steps: Step[];
  prepare_en: string[];
  prepare_sm: string[];
  wear_en: string[];
  wear_sm: string[];
  phrases: string[];
  mistakes_en: string[];
  mistakes_sm: string[];
  review: ReviewStatus;
}

export interface GlossaryEntry {
  id: string;
  term: string;
  pronunciation?: string;
  meaning_en: string;
  meaning_sm: string;
  related?: string[];
  review: ReviewStatus;
}

export interface Article {
  id: string;
  title_en: string;
  title_sm: string;
  eyebrow_en: string;
  eyebrow_sm: string;
  body_en: string;
  body_sm: string;
  sections?: Step[];
  review: ReviewStatus;
}
