import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const nodes = [
  { id: 1, label: "Physics Fundamentals", mastery: 92, status: "completed", tier: "Foundation", dur: "10m" },
  { id: 2, label: "Electric Charge", mastery: 94, status: "completed", tier: "Foundation", dur: "12m" },
  { id: 3, label: "Voltage (Potential)", mastery: 85, status: "completed", tier: "Core Concepts", dur: "15m" },
  { id: 4, label: "Current Flow", mastery: 80, status: "completed", tier: "Core Concepts", dur: "15m" },
  { id: 5, label: "Resistance", mastery: 68, status: "current", tier: "Core Concepts", dur: "15m" },
  { id: 6, label: "Ohm's Law", mastery: 68, status: "completed", tier: "Laws & Formulae", dur: "18m" },
  { id: 7, label: "Circuit Analysis", mastery: 55, status: "recommended", tier: "Advanced", dur: "20m" },
  { id: 8, label: "Electrical Power", mastery: 0, status: "recommended", tier: "Advanced", dur: "15m" },
  { id: 9, label: "Capacitors in DC", mastery: 0, status: "locked", tier: "Expert", dur: "25m" },
  { id: 10, label: "Inductors & AC", mastery: 0, status: "locked", tier: "Expert", dur: "30m" },
];

export default function LearningPath({ navigate, currentScreen }: Props) {
  const { profile } = useLearner();

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold text-[#059669] uppercase tracking-wider">
              ROADMAP
            </span>
            <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Your Learning Path</h1>
            <p className="text-xs text-[#5E6D67] mt-0.5">
              Personalized concept progression for {profile.name} · Physics Curriculum
            </p>
          </div>
          <button
            onClick={() => navigate("lesson-player")}
            className="px-5 py-2.5 rounded-xl text-xs font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] transition-all shadow-xs cursor-pointer"
          >
            Resume Active Concept →
          </button>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#ECFDF5] border border-[#A7F3D0] text-[#059669] font-semibold">
            <span>✓</span> Completed (Mastered)
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#0D3B2E] text-white font-semibold">
            <span>●</span> Current Active
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#EDE9FE] border border-[#DDD6FE] text-[#8B5CF6] font-semibold">
            <span>✦</span> Recommended Next
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#F5F4EE] border border-[#E6E4DC] text-[#9CA3AF]">
            <span>🔒</span> Locked
          </div>
        </div>

        {/* Learning Path Tree */}
        <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-8 shadow-sm space-y-8">
          {[
            { tier: "Foundation", items: nodes.filter((n) => n.tier === "Foundation") },
            { tier: "Core Concepts", items: nodes.filter((n) => n.tier === "Core Concepts") },
            { tier: "Laws & Formulae", items: nodes.filter((n) => n.tier === "Laws & Formulae") },
            { tier: "Advanced", items: nodes.filter((n) => n.tier === "Advanced") },
            { tier: "Expert", items: nodes.filter((n) => n.tier === "Expert") },
          ].map((section, idx) => (
            <div key={section.tier} className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-bold text-[#5E6D67] uppercase tracking-wider bg-[#F5F4EE] px-3 py-1 rounded-full">
                  LEVEL {idx + 1} · {section.tier}
                </span>
                <div className="h-px bg-[#F5F4EE] flex-1" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {section.items.map((item) => {
                  const isCurrent = item.status === "current";
                  const isCompleted = item.status === "completed";
                  const isRecommended = item.status === "recommended";
                  const isLocked = item.status === "locked";

                  return (
                    <div
                      key={item.id}
                      onClick={() => !isLocked && navigate("lesson-player")}
                      className={`p-5 rounded-2xl border transition-all flex flex-col justify-between ${
                        isCurrent
                          ? "bg-[#0D3B2E] text-white border-[#0D3B2E] shadow-md cursor-pointer"
                          : isCompleted
                          ? "bg-[#ECFDF5] border-[#A7F3D0] text-[#0D3B2E] hover:shadow-xs cursor-pointer"
                          : isRecommended
                          ? "bg-white border-[#8B5CF6]/50 hover:border-[#8B5CF6] text-[#0F172A] hover:shadow-xs cursor-pointer"
                          : "bg-[#F9F8F5] border-[#E6E4DC] text-[#9CA3AF] cursor-not-allowed opacity-60"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-base">
                          {isCompleted ? "✓" : isCurrent ? "▶" : isRecommended ? "✦" : "🔒"}
                        </span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            isCurrent
                              ? "bg-white/20 text-[#A7F3D0]"
                              : isCompleted
                              ? "bg-[#DCFCE7] text-[#059669]"
                              : isRecommended
                              ? "bg-[#EDE9FE] text-[#8B5CF6]"
                              : "bg-[#F5F4EE] text-[#9CA3AF]"
                          }`}
                        >
                          {item.dur}
                        </span>
                      </div>

                      <div>
                        <div className="text-sm font-bold tracking-tight">{item.label}</div>
                        {item.mastery > 0 && (
                          <div className="mt-2 space-y-1">
                            <div className="flex justify-between text-[10px] font-semibold opacity-80">
                              <span>Mastery</span>
                              <span>{item.mastery}%</span>
                            </div>
                            <div className="h-1.5 bg-black/10 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${isCurrent ? "bg-[#10B981]" : "bg-[#059669]"}`}
                                style={{ width: `${item.mastery}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
