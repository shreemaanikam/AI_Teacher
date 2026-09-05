import { useEffect, useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
  correct: boolean;
}

export default function EvaluationResult({ navigate, currentScreen, correct }: Props) {
  const { profile, progress, updateProgress } = useLearner();
  const [phase, setPhase] = useState<"analyzing" | "result">("analyzing");

  useEffect(() => {
    const timer = setTimeout(() => {
      setPhase("result");
      if (!correct) {
        updateProgress({ misconceptionDetected: true });
      }
    }, 1100);
    return () => clearTimeout(timer);
  }, [correct]);

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="min-h-screen bg-[#F9F8F5] flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-xl">
          {/* Phase 1: Cognitive Analysis */}
          {phase === "analyzing" && (
            <div className="text-center py-16 animate-fade-in-up space-y-4">
              <div className="w-16 h-16 rounded-full mx-auto flex items-center justify-center bg-[#0D3B2E] text-[#A7F3D0] shadow-lg">
                <div className="w-7 h-7 border-3 border-[#A7F3D0] border-t-transparent rounded-full animate-spin" />
              </div>
              <h2 className="font-serif text-2xl font-bold text-[#0D3B2E]">Evaluating your answer…</h2>
              <p className="text-xs text-[#5E6D67] max-w-xs mx-auto">
                AI teacher is comparing response patterns with cognitive models and textbook evidence.
              </p>
            </div>
          )}

          {/* Phase 2: Evaluation Result */}
          {phase === "result" && (
            <div className="animate-scale-in space-y-6">
              {/* Header Badge */}
              <div className="text-center">
                <div
                  className={`w-16 h-16 rounded-full mx-auto mb-3 flex items-center justify-center text-3xl font-bold shadow-md ${
                    correct ? "bg-[#ECFDF5] text-[#059669]" : "bg-[#FFE4E6] text-[#E11D48]"
                  }`}
                >
                  {correct ? "✓" : "✗"}
                </div>
                <div
                  className={`text-[11px] font-bold px-3.5 py-1 rounded-full inline-block mb-2 uppercase tracking-wider ${
                    correct
                      ? "bg-[#ECFDF5] text-[#059669] border border-[#A7F3D0]"
                      : "bg-[#FFE4E6] text-[#E11D48] border border-[#FECDD3]"
                  }`}
                >
                  {correct ? "CORRECT UNDERSTANDING" : "MISCONCEPTION IDENTIFIED"}
                </div>
                <h1 className="font-serif text-2xl sm:text-3xl text-[#0D3B2E] tracking-tight">
                  {correct ? `Well done, ${profile.name}!` : "AI detected a learning gap"}
                </h1>
                <p className="text-xs text-[#5E6D67] mt-1">
                  {correct
                    ? "Your conceptual grasp of Ohm's Law matches physical reality."
                    : "The response indicates a reversal of the inverse relationship between resistance and current."}
                </p>
              </div>

              {/* Answer Comparison Card */}
              <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-sm space-y-4">
                <div className="flex items-start gap-3">
                  <div
                    className={`w-7 h-7 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 ${
                      correct ? "bg-[#ECFDF5] text-[#059669]" : "bg-[#FFE4E6] text-[#E11D48]"
                    }`}
                  >
                    {correct ? "✓" : "✗"}
                  </div>
                  <div>
                    <div className="text-[10px] font-bold text-[#9CA3AF] uppercase">YOUR ANSWER</div>
                    <div className={`text-sm font-semibold ${correct ? "text-[#059669]" : "text-[#E11D48]"}`}>
                      {correct ? "Current decreases." : '"Current increases."'}
                    </div>
                  </div>
                </div>

                {!correct && (
                  <div className="flex items-start gap-3 pt-3 border-t border-[#F5F4EE]">
                    <div className="w-7 h-7 rounded-xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center text-xs font-bold shrink-0">
                      ✓
                    </div>
                    <div>
                      <div className="text-[10px] font-bold text-[#059669] uppercase">CORRECT PRINCIPLE</div>
                      <div className="text-sm font-medium text-[#0D3B2E]">
                        Current decreases when resistance increases at constant voltage (I = V / R).
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Telemetry Metrics */}
              <div className="bg-white rounded-3xl border border-[#E6E4DC] p-5 shadow-2xs">
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-[#F9F8F5] p-3 rounded-2xl">
                    <div className="text-[10px] text-[#5E6D67]">Concept</div>
                    <div className="font-bold text-[#0D3B2E] text-sm">Resistance</div>
                  </div>
                  <div className="bg-[#F9F8F5] p-3 rounded-2xl">
                    <div className="text-[10px] text-[#5E6D67]">AI Confidence</div>
                    <div className="font-bold text-[#D97706] text-sm">91%</div>
                  </div>
                  <div className="bg-[#F9F8F5] p-3 rounded-2xl">
                    <div className="text-[10px] text-[#5E6D67]">Concept Mastery</div>
                    <div className="font-bold text-[#E11D48] text-sm">{correct ? "68%" : "32%"}</div>
                  </div>
                  <div className="bg-[#F9F8F5] p-3 rounded-2xl">
                    <div className="text-[10px] text-[#5E6D67]">Adaptive Harness Action</div>
                    <div className="font-bold text-[#0D3B2E] text-sm">{correct ? "ADVANCE" : "RE-EXPLAIN"}</div>
                  </div>
                </div>
              </div>

              {/* AI Teaching Decision Note */}
              {!correct && (
                <div className="rounded-2xl p-4 bg-[#ECFDF5] border border-[#BBF7D0]">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse-dot" />
                    <span className="text-xs font-bold text-[#0D3B2E]">
                      AI Teacher — Adaptive Decision
                    </span>
                  </div>
                  <p className="text-xs text-[#334155] leading-relaxed">
                    Rather than repeating the mathematical formula, I am immediately switching to an{" "}
                    <strong>analogy-first approach</strong> using a hydraulic pipe-and-water model to build intuitive understanding.
                  </p>
                </div>
              )}

              {/* Action Button */}
              <button
                onClick={() => navigate(correct ? "assessment" : "misconception")}
                className="w-full py-4 rounded-xl text-sm font-bold text-[#07221A] shadow-md hover:shadow-lg transition-all cursor-pointer bg-[#10B981] hover:bg-[#059669] text-center"
              >
                {correct ? "Continue to Final Assessment →" : "See What AI Detected →"}
              </button>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
