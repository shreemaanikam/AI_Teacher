import { useState, useEffect } from "react";
import type { Screen } from "./types";
import { LearnerProvider } from "./context/LearnerContext";
import ErrorBoundary from "./components/ErrorBoundary";
import Landing from "./screens/Landing";
import Onboarding from "./screens/Onboarding";
import Dashboard from "./screens/Dashboard";
import CreateLesson from "./screens/CreateLesson";
import DocumentProcessing from "./screens/DocumentProcessing";
import LessonPlan from "./screens/LessonPlan";
import LessonPlayer from "./screens/LessonPlayer";
import QuestionCheckpoint from "./screens/QuestionCheckpoint";
import EvaluationResult from "./screens/EvaluationResult";
import MisconceptionDetected from "./screens/MisconceptionDetected";
import AdaptiveReteaching from "./screens/AdaptiveReteaching";
import FinalAssessment from "./screens/FinalAssessment";
import LearningReport from "./screens/LearningReport";
import LearningPath from "./screens/LearningPath";
import Analytics from "./screens/Analytics";
import LearnerProfile from "./screens/LearnerProfile";
import DocumentsLibrary from "./screens/DocumentsLibrary";

const VALID_SCREENS: Set<string> = new Set([
  "landing",
  "onboarding",
  "dashboard",
  "create-lesson",
  "document-processing",
  "lesson-plan",
  "lesson-player",
  "question",
  "evaluation-wrong",
  "evaluation-correct",
  "misconception",
  "adaptive",
  "adaptive-question",
  "assessment",
  "report",
  "learning-path",
  "analytics",
  "profile",
  "documents",
]);

function getInitialScreen(): Screen {
  if (typeof window === "undefined") return "dashboard";
  const params = new URLSearchParams(window.location.search);
  const qScreen = params.get("screen");
  if (qScreen && VALID_SCREENS.has(qScreen)) return qScreen as Screen;
  
  const hash = window.location.hash.replace(/^#\/?/, "");
  if (hash && VALID_SCREENS.has(hash)) return hash as Screen;

  return "dashboard";
}

export type { Screen };

export default function App() {
  const [screen, setScreen] = useState<Screen>(getInitialScreen);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace(/^#\/?/, "");
      if (hash && VALID_SCREENS.has(hash)) {
        setScreen(hash as Screen);
      }
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (s: Screen) => {
    window.scrollTo({ top: 0, behavior: "smooth" });
    window.location.hash = s;
    setScreen(s);
  };

  const props = { navigate, currentScreen: screen };

  return (
    <LearnerProvider>
      <div className="min-h-full bg-[#F9F8F5]">
        <ErrorBoundary fallbackScreen={screen} onReset={() => navigate("dashboard")}>
          {screen === "landing" && <Landing {...props} />}
          {screen === "onboarding" && <Onboarding {...props} />}
          {screen === "dashboard" && <Dashboard {...props} />}
          {screen === "create-lesson" && <CreateLesson {...props} />}
          {screen === "document-processing" && <DocumentProcessing {...props} />}
          {screen === "lesson-plan" && <LessonPlan {...props} />}
          {screen === "lesson-player" && <LessonPlayer {...props} />}
          {screen === "question" && <QuestionCheckpoint {...props} />}
          {screen === "evaluation-wrong" && <EvaluationResult {...props} correct={false} />}
          {screen === "evaluation-correct" && <EvaluationResult {...props} correct={true} />}
          {screen === "misconception" && <MisconceptionDetected {...props} />}
          {screen === "adaptive" && <AdaptiveReteaching {...props} showQuestion={false} />}
          {screen === "adaptive-question" && <AdaptiveReteaching {...props} showQuestion={true} />}
          {screen === "assessment" && <FinalAssessment {...props} />}
          {screen === "report" && <LearningReport {...props} />}
          {screen === "learning-path" && <LearningPath {...props} />}
          {screen === "analytics" && <Analytics {...props} />}
          {screen === "profile" && <LearnerProfile {...props} />}
          {screen === "documents" && <DocumentsLibrary {...props} />}
        </ErrorBoundary>
      </div>
    </LearnerProvider>
  );
}
