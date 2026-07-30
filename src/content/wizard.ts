import wizardData from './wizard.json';

export interface WizardOption {
  id: string;
  label_en: string;
  label_sm: string;
}

export interface WizardQuestion {
  id: string;
  label_en: string;
  label_sm: string;
}

export interface WizardAnswer {
  event: string;
  role: string;
  question: string;
  title_en: string;
  title_sm: string;
  guidance_en: string[];
  guidance_sm: string[];
  link?: { kind: 'ceremony' | 'article'; id: string };
}

export const events: WizardOption[] = wizardData.events;
export const roles: WizardOption[] = wizardData.roles;
export const questions: WizardQuestion[] = wizardData.questions;
export const answers: WizardAnswer[] = wizardData.answers as WizardAnswer[];

export function findAnswer(event: string, role: string, question: string): WizardAnswer | undefined {
  return (
    answers.find((a) => a.event === event && a.role === role && a.question === question) ||
    answers.find((a) => (a.event === event || a.event === '*') && a.role === role && a.question === question) ||
    answers.find((a) => a.event === event && (a.role === role || a.role === '*') && a.question === question) ||
    answers.find(
      (a) =>
        (a.event === '*' || a.event === event) &&
        (a.role === '*' || a.role === role) &&
        a.question === question
    )
  );
}
