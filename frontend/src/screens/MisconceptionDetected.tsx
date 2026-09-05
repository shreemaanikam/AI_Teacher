import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

export default function MisconceptionDetected({ navigate, currentScreen }: Props) {
  const { profile } = useLearner();

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="min-h-screen bg-[#F9F8F5] py-10 px-4">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Header Warning */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 bg-[#FFE4E6] text-[#E11D48] border border-[#FECDD3] text-xs font-bold px-4 py-1.5 rounded-full mb-3 animate-scale-in">
              <span className="w-2 h-2 rounded-full bg-[#E11D48] animate-pulse-dot" />
              MISCONCEPTION DETECTED · Confidence 91%
            </div>
            <h1 className="font-serif text-3xl sm:text-4xl text-[#0D3B2E] tracking-tight mb-2 animate-fade-in-up">
              AI detected a learning gap
            </h1>
            <p className="text-[#5E6D67] text-sm max-w-md mx-auto">
              Your response indicates an intuitive belief that higher resistance allows more current to flow.
            </p>
          </div>

          {/* Belief vs Truth Comparison */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-[#FFF1F2] rounded-3xl border-2 border-[#FFE4E6] p-6 shadow-2xs">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-xl bg-[#FFE4E6] text-[#E11D48] flex items-center justify-center font-bold text-sm">
                  ✗
                </div>
                <span className="text-xs font-bold text-[#E11D48] uppercase tracking-wide">
                  STUDENT BELIEF
                </span>
              </div>
              <div className="text-base font-bold text-[#0F172A] leading-snug">
                "Higher resistance increases current."
              </div>
              <div className="text-xs text-[#E11D48] mt-2">Repeated conceptual misconception</div>
            </div>

            <div className="bg-[#ECFDF5] rounded-3xl border-2 border-[#A7F3D0] p-6 shadow-2xs">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-xl bg-[#DCFCE7] text-[#059669] flex items-center justify-center font-bold text-sm">
                  ✓
                </div>
                <span className="text-xs font-bold text-[#059669] uppercase tracking-wide">
                  PHYSICAL PRINCIPLE
                </span>
              </div>
              <div className="text-base font-bold text-[#0D3B2E] leading-snug">
                Higher resistance impedes current, reducing flow.
              </div>
              <div className="text-xs text-[#059669] mt-2">Inverse relationship (I = V / R)</div>
            </div>
          </div>

          {/* Section 16: Teaching Harness Decision Grid */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-7 shadow-sm space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-[#F5F4EE]">
              <div>
                <span className="text-[10px] font-bold text-[#5E6D67] uppercase tracking-wider">
                  COGNITIVE HARNESS
                </span>
                <h3 className="font-serif text-lg font-bold text-[#0D3B2E]">Teaching Decision Breakdown</h3>
              </div>
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#ECFDF5] text-[#059669]">
                Live Diagnostic
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3.5 rounded-2xl bg-[#FFF1F2] border border-[#FFE4E6]">
                <div className="text-[10px] text-[#9CA3AF] uppercase font-bold">Concept</div>
                <div className="font-bold text-[#E11D48] text-sm mt-0.5">Resistance</div>
              </div>
              <div className="p-3.5 rounded-2xl bg-[#FEF3C7] border border-[#FDE68A]">
                <div className="text-[10px] text-[#9CA3AF] uppercase font-bold">AI Confidence</div>
                <div className="font-bold text-[#D97706] text-sm mt-0.5">91%</div>
              </div>
              <div className="p-3.5 rounded-2xl bg-[#F5F4EE] border border-[#E6E4DC]">
                <div className="text-[10px] text-[#9CA3AF] uppercase font-bold">Action Switch</div>
                <div className="font-bold text-[#0D3B2E] text-xs mt-0.5">
                  <span className="line-through text-[#9CA3AF]">ADVANCE</span> → RE-EXPLAIN
                </div>
              </div>
              <div className="p-3.5 rounded-2xl bg-[#ECFDF5] border border-[#BBF7D0]">
                <div className="text-[10px] text-[#9CA3AF] uppercase font-bold">Strategy</div>
                <div className="font-bold text-[#059669] text-sm mt-0.5">Analogy First</div>
              </div>
            </div>

            {/* Strategy Comparison */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-4 rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC]">
                <div className="text-[10px] font-bold text-[#9CA3AF] uppercase mb-1">PREVIOUS APPROACH</div>
                <div className="text-sm font-semibold text-[#0F172A] mb-1">Technical Formula Presentation</div>
                <p className="text-xs text-[#5E6D67] leading-relaxed">
                  Presented equation I = V / R with circuit diagrams. Resulted in mathematical abstraction gap.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-[#ECFDF5] border border-[#BBF7D0]">
                <div className="text-[10px] font-bold text-[#059669] uppercase mb-1">ADAPTED APPROACH</div>
                <div className="text-sm font-bold text-[#0D3B2E] mb-1">Hydraulic Pipe-and-Water Analogy</div>
                <p className="text-xs text-[#334155] leading-relaxed">
                  Visualizing current as water flow and resistance as pipe constriction creates immediate physical intuition.
                </p>
              </div>
            </div>
          </div>

          {/* Section 16: Adaptive Process Visual Flow */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-sm space-y-4">
            <h3 className="text-xs font-bold text-[#5E6D67] uppercase tracking-wider">
              Adaptive Feedback Loop
            </h3>
            <div className="flex items-center gap-2 overflow-x-auto pb-2 text-xs">
              {[
                { label: "Answer", icon: "💬", active: true },
                { label: "Evaluate", icon: "⚙️", active: true },
                { label: "Misconception", icon: "⚠️", active: true },
                { label: "Update State", icon: "🧠", active: true },
                { label: "Re-explain", icon: "🔄", active: true },
                { label: "New Analogy", icon: "🪣", active: false },
                { label: "New Visual", icon: "🎨", active: false },
                { label: "New Question", icon: "❓", active: false },
              ].map((step, idx) => (
                <div key={step.label} className="flex items-center gap-1.5 shrink-0">
                  <div
                    className={`px-3 py-2 rounded-xl border text-center flex items-center gap-1.5 font-semibold ${
                      step.active
                        ? "bg-[#0D3B2E] text-white border-[#0D3B2E]"
                        : "bg-[#F9F8F5] text-[#5E6D67] border-[#E6E4DC]"
                    }`}
                  >
                    <span>{step.icon}</span>
                    <span className="text-[11px]">{step.label}</span>
                  </div>
                  {idx < 7 && <span className="text-[#9CA3AF] text-xs font-bold">→</span>}
                </div>
              ))}
            </div>
          </div>

          {/* AI Decision Note */}
          <div className="rounded-3xl p-5 bg-[#0D3B2E] text-white shadow-md border border-[#164E3F] space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-base">👩‍🏫</span>
              <span className="text-xs font-bold text-[#A7F3D0]">Dr. Aria — AI Teacher</span>
            </div>
            <p className="text-xs sm:text-sm text-[#D1FAE5] leading-relaxed">
              "Alex, don't worry! This is one of the most common stumbling blocks in physics. Let's step away from the circuit formula and look at water flowing through a garden hose. Once you see the physical picture, the math will feel effortless."
            </p>
          </div>

          {/* Primary Action Button */}
          <button
            onClick={() => navigate("adaptive")}
            className="w-full py-4 rounded-xl text-sm font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] shadow-lg hover:shadow-xl transition-all cursor-pointer text-center"
          >
            Learn This Differently →
          </button>
        </div>
      </div>
    </AppShell>
  );
}
