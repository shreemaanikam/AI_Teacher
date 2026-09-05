import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
  showQuestion: boolean;
}

const followUpAnswers = [
  { id: "a", text: "Current increases." },
  { id: "b", text: "Current stays the same." },
  { id: "c", text: "Current decreases." },
  { id: "d", text: "The voltage also changes." },
];

export default function AdaptiveReteaching({ navigate, currentScreen, showQuestion }: Props) {
  const { profile, progress, updateProgress } = useLearner();
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [correct, setCorrect] = useState<boolean | null>(null);
  const [pipeConstriction, setPipeConstriction] = useState<"low" | "high">("high");

  const handleSubmit = () => {
    if (!selected) return;
    const isCorrect = selected === "c";
    setCorrect(isCorrect);
    setSubmitted(true);
    if (isCorrect) {
      updateProgress({
        resistanceMastery: 68,
        overallMastery: 86,
        misconceptionResolved: true,
      });
      setTimeout(() => navigate("assessment"), 1600);
    }
  };

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
        {/* Header Badges */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-[#0D3B2E] text-white">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse-dot" />
            ADAPTIVE TEACHING HARNESS
          </div>
          <div className="px-3 py-1 rounded-full text-xs font-semibold bg-[#ECFDF5] text-[#059669] border border-[#A7F3D0]">
            ✨ Strategy Switch: Analogy First + Hydraulic Simulation
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main 2 Cols: Pipe Analogy & Interactive Simulation */}
          <div className="lg:col-span-2 space-y-6">
            {/* Analogy Explanation Card */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-7 shadow-sm space-y-5 animate-fade-in-up">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🪣</span>
                <div>
                  <h2 className="font-serif text-2xl font-bold text-[#0D3B2E]">
                    The Pipe & Water Flow Model
                  </h2>
                  <p className="text-xs text-[#5E6D67]">Visualizing the inverse relationship naturally</p>
                </div>
              </div>

              <p className="text-sm text-[#334155] leading-relaxed">
                Imagine an electric circuit as a water pipe system:
              </p>

              <div className="grid grid-cols-3 gap-3 text-center text-xs">
                <div className="p-3 rounded-2xl bg-[#ECFDF5] border border-[#A7F3D0]">
                  <div className="text-[10px] font-bold text-[#059669] uppercase">VOLTAGE</div>
                  <div className="font-bold text-[#0D3B2E] mt-1">Water Pressure</div>
                  <div className="text-[10px] text-[#5E6D67] mt-0.5">The push</div>
                </div>
                <div className="p-3 rounded-2xl bg-[#FFF1F2] border border-[#FECDD3]">
                  <div className="text-[10px] font-bold text-[#E11D48] uppercase">RESISTANCE</div>
                  <div className="font-bold text-[#0F172A] mt-1">Narrow Pipe</div>
                  <div className="text-[10px] text-[#5E6D67] mt-0.5">The obstacle</div>
                </div>
                <div className="p-3 rounded-2xl bg-[#F0FDF4] border border-[#BBF7D0]">
                  <div className="text-[10px] font-bold text-[#059669] uppercase">CURRENT</div>
                  <div className="font-bold text-[#0D3B2E] mt-1">Flow Rate</div>
                  <div className="text-[10px] text-[#5E6D67] mt-0.5">Gallons / sec</div>
                </div>
              </div>

              {/* Interactive Hydraulic Simulation Box */}
              <div className="rounded-2xl bg-[#F5F4EE] border border-[#E6E4DC] p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#0D3B2E] uppercase">
                    Interactive Pipe Simulation
                  </span>
                  <div className="flex gap-1 bg-white p-1 rounded-xl border border-[#E6E4DC]">
                    <button
                      onClick={() => setPipeConstriction("low")}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-colors ${
                        pipeConstriction === "low"
                          ? "bg-[#0D3B2E] text-white"
                          : "text-[#5E6D67] hover:text-[#0D3B2E]"
                      }`}
                    >
                      Low Resistance (Wide)
                    </button>
                    <button
                      onClick={() => setPipeConstriction("high")}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-colors ${
                        pipeConstriction === "high"
                          ? "bg-[#E11D48] text-white"
                          : "text-[#5E6D67] hover:text-[#0D3B2E]"
                      }`}
                    >
                      High Resistance (Narrow)
                    </button>
                  </div>
                </div>

                {/* Animated Pipe Graphic */}
                <div className="bg-white rounded-xl p-5 border border-[#E6E4DC] flex items-center justify-center">
                  {pipeConstriction === "low" ? (
                    <div className="w-full flex items-center gap-2">
                      <div className="h-14 flex-1 bg-[#D1FAE5] rounded-l-xl border-y-2 border-l-2 border-[#10B981] flex items-center justify-center text-xs font-bold text-[#059669]">
                        Wide Pipe (Low R)
                      </div>
                      <div className="h-14 w-16 bg-[#A7F3D0] border-y-2 border-[#10B981] flex items-center justify-center text-[10px] font-bold text-[#0D3B2E]">
                        R = 1Ω
                      </div>
                      <div className="h-14 flex-1 bg-[#D1FAE5] rounded-r-xl border-y-2 border-r-2 border-[#10B981] flex items-center justify-center text-xs font-bold text-[#059669]">
                        🌊 Heavy Flow (I = 9A)
                      </div>
                    </div>
                  ) : (
                    <div className="w-full flex items-center gap-1">
                      <div className="h-14 flex-1 bg-[#FFE4E6] rounded-l-xl border-y-2 border-l-2 border-[#F43F5E] flex items-center justify-center text-xs font-bold text-[#E11D48]">
                        Incoming Pressure
                      </div>
                      <div className="h-5 w-20 bg-[#F43F5E] text-white flex items-center justify-center text-[10px] font-bold rounded-sm shadow-xs">
                        Constricted (R=9Ω)
                      </div>
                      <div className="h-14 flex-1 bg-[#FFE4E6] rounded-r-xl border-y-2 border-r-2 border-[#F43F5E] flex items-center justify-center text-xs font-bold text-[#E11D48]">
                        💧 Trickle Flow (I = 1A)
                      </div>
                    </div>
                  )}
                </div>

                <div className="text-center text-xs font-mono font-bold text-[#0D3B2E]">
                  {pipeConstriction === "low"
                    ? "R is low → Resistance to flow is small → CURRENT IS HIGH!"
                    : "R is high → Pipe is tightly constricted → CURRENT DROPS!"}
                </div>
              </div>
            </div>

            {/* Concrete Numerical Scenarios */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-sm space-y-3">
              <div className="flex items-center gap-2">
                <span>⚡</span>
                <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Concrete Calculations</h3>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { scenario: "V = 9V, R = 3Ω", result: "I = 3A", label: "Baseline", bg: "#F5F4EE", text: "#0D3B2E" },
                  { scenario: "V = 9V, R = 9Ω", result: "I = 1A", label: "Resistance Triples", bg: "#FFF1F2", text: "#E11D48" },
                  { scenario: "V = 9V, R = 1Ω", result: "I = 9A", label: "Resistance Drops", bg: "#ECFDF5", text: "#059669" },
                ].map((ex) => (
                  <div
                    key={ex.label}
                    className="p-3.5 rounded-2xl border text-center"
                    style={{ backgroundColor: ex.bg, borderColor: ex.text + "30" }}
                  >
                    <div className="text-[10px] font-bold uppercase mb-1" style={{ color: ex.text }}>
                      {ex.label}
                    </div>
                    <div className="text-xs text-[#5E6D67] mb-1">{ex.scenario}</div>
                    <div className="font-mono text-base font-bold" style={{ color: ex.text }}>
                      {ex.result}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Section 17: Follow-Up Re-Evaluation Question */}
            {showQuestion && (
              <div className="bg-white rounded-3xl border-2 border-[#0D3B2E] shadow-md p-6 sm:p-7 space-y-4 animate-scale-in">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-xl bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center text-xs font-bold">
                    Q
                  </div>
                  <span className="text-xs font-bold text-[#0D3B2E]">Follow-up Understanding Check</span>
                </div>

                <p className="text-base font-bold text-[#0F172A]">
                  If voltage stays the same and resistance becomes larger, what happens to current?
                </p>

                <div className="space-y-2.5">
                  {followUpAnswers.map((a) => {
                    let btnStyle = "border-[#E6E4DC] bg-white hover:border-[#0D3B2E] hover:bg-[#F9F8F5]";
                    if (submitted) {
                      if (a.id === "c") btnStyle = "border-[#059669] bg-[#ECFDF5]";
                      else if (a.id === selected && a.id !== "c") btnStyle = "border-[#E11D48] bg-[#FFF1F2]";
                      else btnStyle = "border-[#E6E4DC] bg-[#F5F4EE] opacity-50";
                    } else if (selected === a.id) {
                      btnStyle = "border-[#0D3B2E] bg-[#ECFDF5] font-bold";
                    }

                    return (
                      <button
                        key={a.id}
                        onClick={() => !submitted && setSelected(a.id)}
                        disabled={submitted}
                        className={`w-full flex items-center gap-3 p-3.5 rounded-2xl border text-left transition-all ${btnStyle} ${
                          !submitted ? "cursor-pointer" : "cursor-default"
                        }`}
                      >
                        <div
                          className={`w-7 h-7 rounded-xl border-2 flex items-center justify-center text-xs font-bold shrink-0 ${
                            submitted && a.id === "c"
                              ? "border-[#059669] bg-[#059669] text-white"
                              : submitted && a.id === selected && a.id !== "c"
                              ? "border-[#E11D48] bg-[#E11D48] text-white"
                              : selected === a.id
                              ? "border-[#0D3B2E] bg-[#0D3B2E] text-white"
                              : "border-[#E6E4DC] text-[#5E6D67]"
                          }`}
                        >
                          {submitted && a.id === "c" ? "✓" : submitted && a.id === selected ? "✗" : a.id.toUpperCase()}
                        </div>
                        <span className="text-sm text-[#0F172A]">{a.text}</span>
                      </button>
                    );
                  })}
                </div>

                {submitted && correct && (
                  <div className="p-4 rounded-2xl bg-[#ECFDF5] border border-[#BBF7D0] text-center animate-scale-in">
                    <span className="text-sm font-bold text-[#059669]">
                      🎉 Misconception Resolved! Resistance mastery upgraded: 32% → 68%
                    </span>
                  </div>
                )}

                <button
                  onClick={handleSubmit}
                  disabled={!selected || submitted}
                  className={`w-full py-3.5 rounded-xl text-sm font-bold text-[#07221A] transition-all ${
                    selected && !submitted
                      ? "bg-[#10B981] hover:bg-[#059669] shadow-md cursor-pointer"
                      : "bg-[#E6E4DC] text-[#9CA3AF] cursor-not-allowed"
                  }`}
                >
                  {submitted ? (correct ? "Proceeding to assessment…" : "Try again") : "Submit Re-Evaluation →"}
                </button>
              </div>
            )}

            {!showQuestion && (
              <button
                onClick={() => navigate("adaptive-question")}
                className="w-full py-4 rounded-xl text-sm font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] shadow-lg hover:shadow-xl transition-all cursor-pointer text-center"
              >
                Take the Follow-up Question →
              </button>
            )}
          </div>

          {/* Right Col: Adaptive State Comparison & Mastery Delta */}
          <div className="space-y-4">
            {/* Strategy Switch Card */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-5 shadow-xs space-y-3">
              <span className="text-[10px] font-bold text-[#5E6D67] uppercase">TEACHING HARNESS</span>
              <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Strategy Transition</h3>
              <div className="space-y-2">
                <div className="p-3 rounded-xl bg-[#F9F8F5] border border-[#E6E4DC] text-xs">
                  <div className="text-[10px] text-[#9CA3AF] font-bold">PREVIOUS</div>
                  <div className="font-medium text-[#0F172A] mt-0.5">Formula First (I = V / R)</div>
                </div>
                <div className="flex justify-center text-[#059669] text-sm">↓</div>
                <div className="p-3 rounded-xl bg-[#ECFDF5] border border-[#A7F3D0] text-xs">
                  <div className="text-[10px] text-[#059669] font-bold">ADAPTED NOW</div>
                  <div className="font-bold text-[#0D3B2E] mt-0.5">Pipe Analogy + Visual Simulator</div>
                </div>
              </div>
            </div>

            {/* Live Mastery Meter */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-5 shadow-xs space-y-3">
              <span className="text-[10px] font-bold text-[#5E6D67] uppercase">COGNITIVE MODEL</span>
              <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Mastery Progression</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-[#5E6D67]">Before Re-explanation</span>
                  <span className="font-bold text-[#E11D48]">32%</span>
                </div>
                <div className="h-2 bg-[#F5F4EE] rounded-full overflow-hidden">
                  <div className="h-full bg-[#E11D48] rounded-full" style={{ width: "32%" }} />
                </div>

                <div className="flex justify-between text-xs pt-1">
                  <span className="text-[#5E6D67]">Target Post-Adaptation</span>
                  <span className="font-bold text-[#059669]">68%</span>
                </div>
                <div className="h-2 bg-[#F5F4EE] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#059669] rounded-full transition-all duration-1000"
                    style={{ width: showQuestion && correct ? "68%" : "32%" }}
                  />
                </div>
              </div>
            </div>

            {/* AI Teacher Rationale */}
            <div className="rounded-3xl p-5 bg-[#0D3B2E] text-white space-y-2 shadow-xs">
              <div className="flex items-center gap-2">
                <span className="text-sm">👩‍🏫</span>
                <span className="text-xs font-bold text-[#A7F3D0]">Dr. Aria Note</span>
              </div>
              <p className="text-xs text-[#D1FAE5] leading-relaxed">
                "Hydraulic analogies reduce abstract cognitive load by 73%. Once you see the constricted pipe, the inverse relationship is permanently secured."
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
