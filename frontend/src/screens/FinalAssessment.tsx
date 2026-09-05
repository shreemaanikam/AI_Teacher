import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const questions = [
  {
    q: "What does Ohm's Law state in algebraic form?",
    options: ["V = I × R", "R = V + I", "I = V + R", "V = I / R"],
    correct: 0,
  },
  {
    q: "A direct circuit has V = 12V and R = 4Ω. What is the current flowing?",
    options: ["2A", "3A", "4A", "48A"],
    correct: 1,
  },
  {
    q: "If resistance doubles while voltage remains constant, the current will:",
    options: ["Double", "Stay the same", "Halve", "Quadruple"],
    correct: 2,
  },
];

export default function FinalAssessment({ navigate, currentScreen }: Props) {
  const { profile } = useLearner();
  const [qIndex, setQIndex] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>([null, null, null]);
  const [selected, setSelected] = useState<number | null>(null);
  const [timeLeft] = useState(300); // 5 mins
  const [confidence, setConfidence] = useState(85);

  const q = questions[qIndex];
  const progressPercent = ((qIndex + 1) / questions.length) * 100;

  const handleNext = () => {
    const newAnswers = [...answers];
    newAnswers[qIndex] = selected;
    setAnswers(newAnswers);
    setSelected(null);
    if (qIndex < questions.length - 1) {
      setQIndex(qIndex + 1);
    } else {
      navigate("report");
    }
  };

  const mins = Math.floor(timeLeft / 60);
  const secs = timeLeft % 60;

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="min-h-screen bg-[#F9F8F5] py-10 px-4">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#ECFDF5] text-[#059669] text-[10px] font-bold uppercase mb-1">
                <span>✓</span> Evaluation Phase
              </div>
              <h1 className="font-serif text-2xl text-[#0D3B2E] font-bold">Final Assessment</h1>
              <p className="text-xs text-[#5E6D67]">Ohm's Law · Physics · {profile.level}</p>
            </div>
            <div className="flex items-center gap-2 bg-white border border-[#E6E4DC] rounded-2xl px-4 py-2 text-xs font-mono font-bold text-[#0D3B2E] shadow-2xs">
              <span>⏱</span>
              <span>
                {mins}:{secs.toString().padStart(2, "0")}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-[#5E6D67] font-medium">
              <span>Question {qIndex + 1} of {questions.length}</span>
              <span>{Math.round(progressPercent)}%</span>
            </div>
            <div className="h-2 bg-[#E6E4DC] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#0D3B2E] rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* Question Card */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] shadow-sm p-7 space-y-6 animate-fade-in-up">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center text-xs font-bold">
                  Q{qIndex + 1}
                </div>
                <span className="text-xs font-semibold text-[#5E6D67]">Multiple Choice Question</span>
              </div>
              <span className="text-xs text-[#5E6D67]">Physics · Ohm's Law</span>
            </div>

            <p className="text-base sm:text-lg font-bold text-[#0F172A] leading-relaxed">
              {q.q}
            </p>

            <div className="space-y-3">
              {q.options.map((opt, i) => {
                const isSelected = selected === i;
                return (
                  <button
                    key={i}
                    onClick={() => setSelected(i)}
                    className={`w-full flex items-center gap-4 p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                      isSelected
                        ? "border-[#0D3B2E] bg-[#ECFDF5] shadow-xs"
                        : "border-[#E6E4DC] bg-white hover:border-[#0D3B2E]/40 hover:bg-[#F9F8F5]"
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-xl border-2 flex items-center justify-center text-xs font-bold shrink-0 ${
                        isSelected
                          ? "border-[#0D3B2E] bg-[#0D3B2E] text-white"
                          : "border-[#E6E4DC] text-[#5E6D67]"
                      }`}
                    >
                      {String.fromCharCode(65 + i)}
                    </div>
                    <span className={`text-sm ${isSelected ? "text-[#0D3B2E] font-bold" : "text-[#334155]"}`}>
                      {opt}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Confidence Slider */}
          <div className="bg-white rounded-2xl border border-[#E6E4DC] p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-2 text-xs">
              <span className="font-semibold text-[#334155]">Confidence in this answer</span>
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
          </div>

          {/* Navigation Actions */}
          <div className="flex gap-3">
            {qIndex > 0 && (
              <button
                onClick={() => {
                  setQIndex(qIndex - 1);
                  setSelected(answers[qIndex - 1]);
                }}
                className="px-6 py-3 rounded-xl border border-[#E6E4DC] text-xs font-bold text-[#334155] hover:bg-[#F5F4EE] transition-colors"
              >
                ← Back
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={selected === null}
              className={`flex-1 py-3.5 rounded-xl text-xs font-bold text-[#07221A] transition-all ${
                selected !== null
                  ? "bg-[#10B981] hover:bg-[#059669] shadow-md hover:shadow-lg cursor-pointer"
                  : "bg-[#E6E4DC] text-[#9CA3AF] cursor-not-allowed"
              }`}
            >
              {qIndex < questions.length - 1 ? "Next Question →" : "Submit Assessment →"}
            </button>
          </div>

          {/* Nav Dots */}
          <div className="flex gap-2 justify-center">
            {questions.map((_, i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full transition-all ${
                  i < qIndex
                    ? "bg-[#10B981]"
                    : i === qIndex
                    ? "bg-[#0D3B2E] scale-125"
                    : "bg-[#E6E4DC]"
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
