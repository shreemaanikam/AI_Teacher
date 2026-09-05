export type Screen =
  | "landing"
  | "onboarding"
  | "dashboard"
  | "create-lesson"
  | "document-processing"
  | "lesson-plan"
  | "lesson-player"
  | "question"
  | "evaluation-wrong"
  | "evaluation-correct"
  | "misconception"
  | "adaptive"
  | "adaptive-question"
  | "assessment"
  | "report"
  | "learning-path"
  | "analytics"
  | "profile"
  | "documents";

export interface LearnerProfileData {
  name: string;
  level: string;
  language: string;
  style: string;
  time: string;
  depth: string;
  goal: string;
  knowledge: string;
}

export interface LessonProgress {
  overallMastery: number;
  streak: number;
  currentTopic: string;
  currentConcept: string;
  resistanceMastery: number;
  voltageMastery: number;
  currentMastery: number;
  ohmsLawMastery: number;
  circuitsMastery: number;
  misconceptionDetected: boolean;
  misconceptionResolved: boolean;
  strategy: string;
}

export interface DocumentItem {
  name: string;
  type: string;
  pages: number;
  chapters: number;
  concepts: number;
  status: "grounded" | "processing" | "error";
  lastUsed: string;
  size: string;
}
