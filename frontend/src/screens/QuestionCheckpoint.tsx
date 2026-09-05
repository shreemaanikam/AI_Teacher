import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const answers = [
  { id: "a", text: "Current increases." },
  { id: "b", text: "Current decreases." },
  { id: "c", text: "Current remains the same." },
  { id: "d", text: "Cannot determine." },
];

export default function QuestionCheckpoint({ navigate, currentScreen }: Props) {
  const { profile } = useLearner();
  const [selected, setSelected] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(85);
  const [submitted, setSubmitted] = useState(false);
  const [inputMode, setInputMode] = useState<"click" | "voice" | "write">("click");

  const handleSubmit = () => {
    if (!selected) return;
    setSubmitted(true);
    setTimeout(() => {
      // If student chooses 'b', they are correct. If 'a', 'c', 'd', it triggers evaluation gap.
      navigate(selected === "b" ? "evaluation-correct" : "evaluation-wrong");
    }, 600);
  };

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="min-h-screen bg-[#F9F8F5] flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 bg-[#ECFDF5] text-[#059669] border border-[#A7F3D0] text-xs font-bold px-3.5 py-1.5 rounded-full mb-4">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse-dot" />
              CHECKPOINT 3 · Ohm's Law: Resistance
            </div>
            <h1 className="font-serif text-3xl text-[#0D3B2E] tracking-tight mb-2">
              Let's check your understanding
            </h1>
            <p className="text-sm text-[#5E6D67]">
              Dr. Aria wants to verify your grasp of how resistance controls current flow.
            </p>
          </div>

          {/* Question Card */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] shadow-sm p-7 mb-5 animate-scale-in">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-xl bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center text-xs font-bold">
                  Q
                </div>
                <span className="text-xs font-semibold text-[#5E6D67]">Conceptual Question</span>
              </div>
              <span className="text-xs text-[#5E6D67]">Grounded in Chapter 4</span>
            </div>

            <p className="text-base sm:text-lg font-bold text-[#0F172A] leading-relaxed mb-6">
              What happens to current if resistance increases while voltage remains constant?
            </p>

            {/* Answer Options */}
            <div className="space-y-3">
              {answers.map((a) => {
                const isSelected = selected === a.id;
                return (
                  <button
                    key={a.id}
                    onClick={() => !submitted && setSelected(a.id)}
                    disabled={submitted}
                    className={`w-full flex items-center gap-4 p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                      isSelected
                        ? "border-[#0D3B2E] bg-[#ECFDF5] shadow-xs"
                        : "border-[#E6E4DC] bg-white hover:border-[#0D3B2E]/40 hover:bg-[#F9F8F5]"
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-xl border-2 flex items-center justify-center text-xs font-bold shrink-0 transition-all ${
                        isSelected
                          ? "border-[#0D3B2E] bg-[#0D3B2E] text-white"
                          : "border-[#E6E4DC] text-[#5E6D67]"
                      }`}
                    >
                      {a.id.toUpperCase()}
                    </div>
                    <span className={`text-sm ${isSelected ? "text-[#0D3B2E] font-bold" : "text-[#334155]"}`}>
                      {a.text}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Confidence Slider */}
          <div className="bg-white rounded-2xl border border-[#E6E4DC] p-5 mb-5 shadow-2xs">
            <div className="flex items-center justify-between mb-2 text-xs">
              <span className="font-semibold text-[#334155]">How confident are you?</span>
              <span className="font-bold text-[#0D3B2E]">{confidence}%</span>
            </div>
            <input
              type="range"
              min={10}
              max={100}
              step={5}
              value={confidence}
              onChange={(e) => setConfidence(Number(e.target.value))}
              className="w-full accent-[#0D3B2E] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-[#9CA3AF] mt-1">
              <span>Uncertain</span>
              <span>Certain</span>
            </div>
          </div>

          {/* Alternative Input Triggers */}
          <div className="flex items-center gap-3 mb-5">
            <button
              onClick={() => setInputMode("voice")}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border text-xs font-medium transition-colors ${
                inputMode === "voice" ? "border-[#0D3B2E] bg-[#ECFDF5] text-[#0D3B2E] font-bold" : "border-[#E6E4DC] bg-white text-[#5E6D67] hover:bg-[#F9F8F5]"
              }`}
            >
              <span>🎤</span>
              <span>Answer by voice</span>
            </button>
            <button
              onClick={() => setInputMode("write")}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border text-xs font-medium transition-colors ${
                inputMode === "write" ? "border-[#0D3B2E] bg-[#ECFDF5] text-[#0D3B2E] font-bold" : "border-[#E6E4DC] bg-white text-[#5E6D67] hover:bg-[#F9F8F5]"
              }`}
            >
              <span>✏️</span>
              <span>Write your response</span>
            </button>
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={!selected || submitted}
            className={`w-full py-4 rounded-xl text-sm font-bold text-[#07221A] transition-all ${
              selected && !submitted
                ? "bg-[#10B981] hover:bg-[#059669] shadow-md hover:shadow-lg cursor-pointer"
                : "bg-[#E6E4DC] text-[#9CA3AF] cursor-not-allowed"
            }`}
          >
            {submitted ? "Evaluating your response…" : "Submit Answer →"}
          </button>

          {/* Hint */}
          <div className="text-center mt-4 text-xs text-[#5E6D67]">
            💡 Hint: Recall Dr. Aria's explanation of resistance as an obstruction to flow.
          </div>
        </div>
      </div>
    </AppShell>
  );
}
