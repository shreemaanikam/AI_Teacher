import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const masteryData = [
  { name: "Voltage", value: 85, color: "#10B981" },
  { name: "Current", value: 80, color: "#34D399" },
  { name: "Resistance", value: 68, color: "#0D3B2E" },
  { name: "Ohm's Law", value: 68, color: "#8B5CF6" },
  { name: "Application", value: 60, color: "#D97706" },
];

export default function LearningReport({ navigate, currentScreen }: Props) {
  const { profile, progress } = useLearner();

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#ECFDF5] border border-[#A7F3D0] text-[#059669] text-xs font-bold mb-2">
              <span>✓</span> Lesson Complete
            </div>
            <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Learning Report</h1>
            <p className="text-xs text-[#5E6D67] mt-0.5">
              {profile.name} · Ohm's Law: Voltage & Current · {new Date().toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => alert("Downloading official PDF learning report...")}
              className="px-4 py-2 rounded-xl border border-[#E6E4DC] text-xs font-semibold text-[#334155] bg-white hover:bg-[#F5F4EE] transition-colors"
            >
              Download PDF
            </button>
            <button
              onClick={() => navigate("learning-path")}
              className="px-5 py-2 rounded-xl text-xs font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] transition-all shadow-xs"
            >
              Continue Learning →
            </button>
          </div>
        </div>

        {/* Top Score Banner & Stats Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Large Score Card */}
          <div className="bg-[#0D3B2E] text-white rounded-3xl p-6 sm:p-8 flex flex-col items-center justify-center text-center shadow-md border border-[#164E3F]">
            <div className="font-serif text-6xl font-bold text-[#A7F3D0] mb-1">
              80<span className="text-3xl text-[#D1FAE5]/60">%</span>
            </div>
            <div className="text-base font-bold text-white mb-1">Overall Mastery Score</div>
            <p className="text-xs text-[#D1FAE5]/80 max-w-xs mb-4">
              Significant leap: Resistance mastery climbed from 32% to 68% following the hydraulic pipe re-explanation.
            </p>
            <div className="flex gap-2">
              <span className="text-[10px] font-bold px-3 py-1 bg-[#10B981]/20 text-[#A7F3D0] rounded-full border border-[#10B981]/40">
                Misconception Resolved
              </span>
              <span className="text-[10px] font-bold px-3 py-1 bg-white/10 text-white rounded-full">
                {profile.level}
              </span>
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[
              { label: "Confidence", value: "85%", bg: "#ECFDF5", color: "#059669", icon: "💪" },
              { label: "Time Invested", value: "9:42", bg: "#F5F4EE", color: "#0D3B2E", icon: "⏱" },
              { label: "Questions Solved", value: "4 / 4", bg: "#ECFDF5", color: "#10B981", icon: "✅" },
              { label: "Misconceptions", value: "1 Resolved", bg: "#FFF1F2", color: "#E11D48", icon: "💡" },
              { label: "Adaptive Loops", value: "1 Triggered", bg: "#EDE9FE", color: "#8B5CF6", icon: "🔄" },
              { label: "Active Streak", value: "7 Days", bg: "#FEF3C7", color: "#D97706", icon: "🔥" },
            ].map((s) => (
              <div
                key={s.label}
                className="rounded-2xl p-4 border flex flex-col justify-between"
                style={{ backgroundColor: s.bg, borderColor: s.color + "25" }}
              >
                <div className="flex items-center gap-2">
                  <span className="text-base">{s.icon}</span>
                  <div className="text-lg font-bold" style={{ color: s.color }}>
                    {s.value}
                  </div>
                </div>
                <div className="text-xs text-[#5E6D67] font-medium mt-2">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 20: Strong Concepts vs Needs Improvement */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-base">🌟</span>
              <h3 className="font-serif text-base font-bold text-[#0D3B2E] uppercase tracking-wide">
                STRONG CONCEPTS
              </h3>
            </div>
            <div className="space-y-3">
              <div className="p-3.5 rounded-2xl bg-[#ECFDF5] border border-[#BBF7D0] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-[#0D3B2E]">Voltage (Electric Potential)</div>
                  <div className="text-[10px] text-[#5E6D67]">Mastered relationship with battery sources</div>
                </div>
                <span className="text-xs font-bold text-[#059669]">85%</span>
              </div>
              <div className="p-3.5 rounded-2xl bg-[#ECFDF5] border border-[#BBF7D0] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-[#0D3B2E]">Current Flow</div>
                  <div className="text-[10px] text-[#5E6D67]">Understands electron rate through conductors</div>
                </div>
                <span className="text-xs font-bold text-[#059669]">80%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-base">🎯</span>
              <h3 className="font-serif text-base font-bold text-[#0D3B2E] uppercase tracking-wide">
                NEEDS IMPROVEMENT
              </h3>
            </div>
            <div className="space-y-3">
              <div className="p-3.5 rounded-2xl bg-[#FEF3C7] border border-[#FDE68A] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-[#0D3B2E]">Resistance Calculations</div>
                  <div className="text-[10px] text-[#5E6D67]">Needs 2 more quantitative practice drills</div>
                </div>
                <span className="text-xs font-bold text-[#D97706]">68%</span>
              </div>
              <div className="p-3.5 rounded-2xl bg-[#FEF3C7] border border-[#FDE68A] flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-[#0D3B2E]">Ohm's Law Algebraic Transposition</div>
                  <div className="text-[10px] text-[#5E6D67]">Rearranging V = I × R into R = V / I</div>
                </div>
                <span className="text-xs font-bold text-[#D97706]">68%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Section 20: Misconception Resolution & Recharts Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Resolved Misconception Card */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold text-[#5E6D67] uppercase tracking-wide">
                  COGNITIVE RESOLUTION
                </span>
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#ECFDF5] text-[#059669]">
                  ✓ RESOLVED
                </span>
              </div>
              <h3 className="font-serif text-lg font-bold text-[#0D3B2E]">
                Resistance–Current Relationship
              </h3>
              <p className="text-xs text-[#334155] leading-relaxed mt-2">
                <strong>Initial belief:</strong> "Higher resistance increases current."
                <br />
                <strong>Intervention:</strong> Dr. Aria switched to the pipe-and-flow analogy, showing that a constricted pipe reduces water flow rate.
                <br />
                <strong>Outcome:</strong> Student successfully resolved the inverse property (I = V / R) in the follow-up check.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-[#F5F4EE] border border-[#E6E4DC] text-xs text-[#0D3B2E]">
              💡 <strong>AI Recommendation:</strong> Revise Ohm's Law and complete 2 additional practice problems.
            </div>
          </div>

          {/* Recharts Bar Chart */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-3">
            <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Mastery by Concept</h3>
            <ResponsiveContainer width="100%" height={170}>
              <BarChart data={masteryData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: "#FFF", borderRadius: 12, borderColor: "#E6E4DC", fontSize: 12 }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {masteryData.map((c) => (
                    <Cell key={c.name} fill={c.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Section 20: Next Topic & Bottom Actions */}
        <div className="rounded-3xl bg-[#0D3B2E] text-white p-6 sm:p-7 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md border border-[#164E3F]">
          <div>
            <span className="text-[10px] font-bold text-[#A7F3D0] uppercase tracking-wider">
              NEXT RECOMMENDED TOPIC
            </span>
            <h3 className="font-serif text-2xl font-bold text-white mt-1">Electrical Power (P = V × I)</h3>
            <p className="text-xs text-[#D1FAE5]/80 mt-1">
              Now that voltage, current, and resistance are clear, discover how energy is consumed in circuits.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => navigate("learning-path")}
              className="px-5 py-3 rounded-xl text-xs font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] transition-all shadow-xs cursor-pointer"
            >
              Continue Learning →
            </button>
            <button
              onClick={() => navigate("dashboard")}
              className="px-4 py-3 rounded-xl text-xs font-semibold text-white bg-white/10 hover:bg-white/20 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
