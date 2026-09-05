import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const concepts = [
  { name: "Introduction & Motivation", dur: "1 min", diff: "Beginner", visual: "Physical intuition", status: "completed" },
  { name: "Voltage (Electric Potential)", dur: "2 min", diff: "Beginner", visual: "Battery diagram", status: "completed" },
  { name: "Current Flow", dur: "2 min", diff: "Beginner", visual: "Electron movement", status: "completed" },
  { name: "Resistance", dur: "2 min", diff: "Beginner", visual: "Constriction / Pipe", status: "current" },
  { name: "Ohm's Law Synthesis", dur: "2 min", diff: "Intermediate", visual: "Interactive formula + graph", status: "upcoming" },
  { name: "Real-World Application", dur: "1 min", diff: "Intermediate", visual: "Household circuits", status: "upcoming" },
];

export default function LessonPlan({ navigate, currentScreen }: Props) {
  const { profile } = useLearner();

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold text-[#059669] uppercase tracking-wider">
              DYNAMIC CURRICULUM
            </span>
            <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Your Personalized Lesson</h1>
            <p className="text-xs text-[#5E6D67] mt-0.5">
              Constructed specifically for {profile.name} · Grounded in Physics Notes.pdf
            </p>
          </div>
          <button
            onClick={() => navigate("lesson-player")}
            className="px-6 py-3 rounded-xl text-xs font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] transition-all shadow-md cursor-pointer"
          >
            Start AI Teacher →
          </button>
        </div>

        {/* Configuration Metadata Chips */}
        <div className="flex flex-wrap gap-2.5">
          {[
            { label: "Topic", value: "Ohm's Law", bg: "#F5F4EE", color: "#0D3B2E" },
            { label: "Level", value: profile.level, bg: "#ECFDF5", color: "#059669" },
            { label: "Language", value: profile.language, bg: "#ECFDF5", color: "#059669" },
            { label: "Time Limit", value: `${profile.time} min`, bg: "#FEF3C7", color: "#D97706" },
            { label: "Teaching Style", value: profile.style, bg: "#EDE9FE", color: "#8B5CF6" },
            { label: "Source Evidence", value: "Physics Notes.pdf", bg: "#F0FDF4", color: "#059669" },
          ].map((c) => (
            <div
              key={c.label}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs"
              style={{ backgroundColor: c.bg, borderColor: c.color + "30", color: c.color }}
            >
              <span className="text-[10px] opacity-70 font-semibold">{c.label}:</span>
              <span className="font-bold">{c.value}</span>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main 2 Cols: Lesson Timeline */}
          <div className="lg:col-span-2 bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-7 shadow-xs space-y-5">
            <h2 className="font-serif text-lg font-bold text-[#0D3B2E]">Lesson Timeline & Checkpoints</h2>
            <div className="space-y-3">
              {concepts.map((c, i) => {
                const isCurrent = c.status === "current";
                const isCompleted = c.status === "completed";

                return (
                  <div key={c.name} className="flex items-start gap-3.5">
                    <div className="flex flex-col items-center shrink-0">
                      <div
                        className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold border ${
                          isCurrent
                            ? "bg-[#0D3B2E] text-white border-[#0D3B2E] shadow-xs"
                            : isCompleted
                            ? "bg-[#ECFDF5] text-[#059669] border-[#A7F3D0]"
                            : "bg-[#F9F8F5] text-[#9CA3AF] border-[#E6E4DC]"
                        }`}
                      >
                        {isCompleted ? "✓" : i + 1}
                      </div>
                      {i < concepts.length - 1 && (
                        <div
                          className={`w-0.5 h-7 mt-1 ${
                            isCompleted ? "bg-[#10B981]" : "bg-[#E6E4DC]"
                          }`}
                        />
                      )}
                    </div>

                    <div
                      className={`flex-1 rounded-2xl p-4 border transition-all ${
                        isCurrent
                          ? "border-[#0D3B2E] bg-[#ECFDF5]/50 shadow-2xs"
                          : "border-[#F5F4EE] bg-[#F9F8F5]"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-[#0F172A]">{c.name}</span>
                          {isCurrent && (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#0D3B2E] text-white">
                              IN PROGRESS
                            </span>
                          )}
                        </div>
                        <span className="text-xs font-mono text-[#5E6D67]">{c.dur}</span>
                      </div>
                      <div className="flex flex-wrap gap-2 pt-1">
                        <span className="text-[10px] px-2 py-0.5 bg-white border border-[#E6E4DC] text-[#5E6D67] rounded-md">
                          {c.diff}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 bg-white border border-[#E6E4DC] text-[#5E6D67] rounded-md">
                          🎨 {c.visual}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 bg-[#ECFDF5] text-[#059669] font-semibold rounded-md border border-[#BBF7D0]">
                          Checkpoint Included
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Col: Why Personalized */}
          <div className="space-y-4">
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
              <h3 className="font-serif text-base font-bold text-[#0D3B2E]">
                Why this lesson is personalized
              </h3>
              <div className="space-y-3">
                {[
                  { label: "Target Level", value: profile.level, icon: "📚", bg: "#F5F4EE", text: "#0D3B2E" },
                  { label: "Target Language", value: `${profile.language} Voice & Captions`, icon: "🗣", bg: "#ECFDF5", text: "#059669" },
                  { label: "Weak Concept Focus", value: "Resistance (Allocated 2x visual time)", icon: "⚠️", bg: "#FFF1F2", text: "#E11D48" },
                  { label: "Cognitive Style", value: "Analogy First + Hydraulic Sim", icon: "🎨", bg: "#EDE9FE", text: "#8B5CF6" },
                  { label: "Session Constraint", value: `${profile.time} Minutes Paced`, icon: "⏱", bg: "#FEF3C7", text: "#D97706" },
                ].map((r) => (
                  <div key={r.label} className="flex items-center gap-3 p-3 rounded-2xl" style={{ backgroundColor: r.bg }}>
                    <span className="text-base">{r.icon}</span>
                    <div>
                      <div className="text-[10px] font-bold uppercase" style={{ color: r.text + "99" }}>
                        {r.label}
                      </div>
                      <div className="text-xs font-bold" style={{ color: r.text }}>
                        {r.value}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Teacher Rationale */}
            <div className="rounded-3xl p-5 bg-[#0D3B2E] text-white shadow-xs space-y-2">
              <div className="flex items-center gap-2">
                <span>🤖</span>
                <span className="text-xs font-bold text-[#A7F3D0]">Harness Strategy</span>
              </div>
              <p className="text-xs text-[#D1FAE5] leading-relaxed">
                "Resistance is identified as your primary cognitive bottleneck. We have restructured the syllabus to front-load intuitive physical metaphors before introducing algebraic Ohm's Law formulas."
              </p>
            </div>

            <button
              onClick={() => navigate("lesson-player")}
              className="w-full py-4 rounded-xl text-sm font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] shadow-md hover:shadow-lg transition-all cursor-pointer text-center"
            >
              Start AI Teacher Now →
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
