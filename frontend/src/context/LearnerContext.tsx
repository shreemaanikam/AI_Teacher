import { createContext, useContext, useState, ReactNode } from "react";
import type { LearnerProfileData, LessonProgress, DocumentItem } from "../types";

interface LearnerContextType {
  profile: LearnerProfileData;
  updateProfile: (updates: Partial<LearnerProfileData>) => void;
  progress: LessonProgress;
  updateProgress: (updates: Partial<LessonProgress>) => void;
  documents: DocumentItem[];
  addDocument: (doc: DocumentItem) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

const defaultProfile: LearnerProfileData = {
  name: "Alex",
  level: "Beginner",
  language: "Tamil",
  style: "Analogy First",
  time: "10",
  depth: "Balanced",
  goal: "Master Physics fundamentals",
  knowledge: "Basics from high school physics",
};

const defaultProgress: LessonProgress = {
  overallMastery: 82,
  streak: 7,
  currentTopic: "Ohm's Law: Voltage & Current",
  currentConcept: "Resistance",
  resistanceMastery: 32,
  voltageMastery: 85,
  currentMastery: 72,
  ohmsLawMastery: 68,
  circuitsMastery: 55,
  misconceptionDetected: false,
  misconceptionResolved: false,
  strategy: "Analogy First + Visual",
};

const initialDocs: DocumentItem[] = [
  { name: "Physics Notes.pdf", type: "PDF", pages: 24, chapters: 6, concepts: 18, status: "grounded", lastUsed: "Today", size: "2.4 MB" },
  { name: "Electricity Textbook.pdf", type: "PDF", pages: 48, chapters: 12, concepts: 34, status: "grounded", lastUsed: "Sep 3", size: "5.1 MB" },
  { name: "Lab Report — Circuits.docx", type: "DOCX", pages: 8, chapters: 2, concepts: 6, status: "processing", lastUsed: "Sep 2", size: "0.8 MB" },
  { name: "Physics Formula Sheet.pdf", type: "PDF", pages: 2, chapters: 1, concepts: 22, status: "grounded", lastUsed: "Sep 1", size: "0.2 MB" },
  { name: "Research Paper — Ohm.pdf", type: "PDF", pages: 12, chapters: 3, concepts: 8, status: "error", lastUsed: "Aug 31", size: "1.1 MB" },
];

const LearnerContext = createContext<LearnerContextType | undefined>(undefined);

export function LearnerProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<LearnerProfileData>(defaultProfile);
  const [progress, setProgress] = useState<LessonProgress>(defaultProgress);
  const [documents, setDocuments] = useState<DocumentItem[]>(initialDocs);
  const [searchQuery, setSearchQuery] = useState("");

  const updateProfile = (updates: Partial<LearnerProfileData>) => {
    setProfile(prev => ({ ...prev, ...updates }));
  };

  const updateProgress = (updates: Partial<LessonProgress>) => {
    setProgress(prev => ({ ...prev, ...updates }));
  };

  const addDocument = (doc: DocumentItem) => {
    setDocuments(prev => [doc, ...prev]);
  };

  return (
    <LearnerContext.Provider
      value={{
        profile,
        updateProfile,
        progress,
        updateProgress,
        documents,
        addDocument,
        searchQuery,
        setSearchQuery,
      }}
    >
      {children}
    </LearnerContext.Provider>
  );
}

export function useLearner() {
  const context = useContext(LearnerContext);
  if (!context) {
    throw new Error("useLearner must be used within a LearnerProvider");
  }
  return context;
}
