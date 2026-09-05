import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const masteryData = [
  { week: "W1", mastery: 55 },
  { week: "W2", mastery: 60 },
  { week: "W3", mastery: 65 },
  { week: "W4", mastery: 70 },
  { week: "W5", mastery: 75 },
  { week: "W6", mastery: 79 },
  { week: "W7", mastery: 82 },
];

const conceptData = [
  { name: "Voltage", value: 85, color: "#10B981" },
  { name: "Current", value: 72, color: "#34D399" },
  { name: "Resistance", value: 32, color: "#E11D48" },
  { name: "Ohm's Law", value: 68, color: "#8B5CF6" },
  { name: "Circuits", value: 55, color: "#D97706" },
];

const recentAssessments = [
  { topic: "Voltage Basics", score: 90, date: "Today", status: "complete" },
  { topic: "Current Flow", score: 78, date: "Yesterday", status: "complete" },
  { topic: "Resistance", score: 45, date: "2 days ago", status: "needs-review" },
];

export default function Dashboard({ navigate, currentScreen }: Props) {
  const { profile, progress } = useLearner();
  const [insightModalOpen, setInsightModalOpen] = useState(false);
  const [chartPeriod, setChartPeriod] = useState<"1W" | "1M" | "All">("1W");

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-8">
        {/* Top Greeting Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#ECFDF5] border border-[#A7F3D0] text-[11px] font-semibold text-[#059669] mb-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse-dot" />
              Round 2 AI Innovation Hackathon Demo · Active Session
            </div>
            <h1 className="font-serif text-3xl lg:text-4xl text-[#0D3B2E] tracking-tight">
              Good morning, {profile.name}
            </h1>
            <p className="text-sm text-[#5E6D67] mt-0.5">
              Your AI teacher is ready to continue where you left off.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("learning-path")}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-[#0D3B2E] bg-white border border-[#E6E4DC] hover:bg-[#F5F4EE] transition-colors"
            >
              View Learning Path
            </button>
            <button
              onClick={() => navigate("create-lesson")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-[#0D3B2E] hover:bg-[#07221A] transition-all shadow-xs"
            >
              <span>+</span>
              <span>New Lesson</span>
            </button>
          </div>
        </div>

        {/* SECTION 5: SCREENSHOT REFERENCE — MAIN HERO CARD */}
        <div className="rounded-3xl bg-gradient-to-br from-[#0D3B2E] via-[#092920] to-[#061D16] text-white p-6 sm:p-8 relative overflow-hidden shadow-lg border border-[#164E3F]/40">
          {/* Subtle background glow & mesh pattern */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#10B981]/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-[#A7F3D0]/5 rounded-full blur-2xl pointer-events-none" />

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
            <div className="lg:col-span-2 space-y-4">
              {/* Section label */}
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold tracking-wider uppercase text-[#A7F3D0] bg-[#164E3F]/70 px-3 py-1 rounded-full border border-[#34D399]/30">
                  CONTINUE WHERE YOU LEFT OFF
                </span>
                <span className="text-xs text-[#D1FAE5]/70">· In Progress</span>
              </div>

              {/* Large lesson title */}
              <h2 className="font-serif text-3xl sm:text-4xl text-white tracking-tight leading-snug">
                Ohm's Law: Voltage & Current
              </h2>

              <p className="text-sm text-[#D1FAE5]/90 max-w-xl leading-relaxed">
                Explore how electric potential pushes electrons through a conductor and how current responds to varying electrical resistance in direct circuits.
              </p>

              {/* Metadata chips */}
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <span className="text-xs px-3 py-1 rounded-xl bg-white/10 text-white border border-white/15 backdrop-blur-xs font-medium">
                  Physics
                </span>
                <span className="text-xs px-3 py-1 rounded-xl bg-white/10 text-white border border-white/15 backdrop-blur-xs font-medium">
                  6 min remaining
                </span>
                <span className="text-xs px-3 py-1 rounded-xl bg-white/10 text-white border border-white/15 backdrop-blur-xs font-medium">
                  {profile.level}
                </span>
                <span className="text-xs px-3 py-1 rounded-xl bg-[#10B981]/20 text-[#A7F3D0] border border-[#10B981]/30 font-medium">
                  🇮🇳 {profile.language}
                </span>
              </div>

              {/* Lesson progress bar */}
              <div className="pt-2 max-w-md">
                <div className="flex justify-between text-xs text-[#A7F3D0] font-semibold mb-1.5">
                  <span>Lesson Progress</span>
                  <span>62%</span>
                </div>
                <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-[#34D399] to-[#10B981] rounded-full transition-all duration-700" style={{ width: "62%" }} />
                </div>
              </div>

              {/* Primary CTA */}
              <div className="pt-2">
                <button
                  onClick={() => navigate("lesson-player")}
                  className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-[#07221A] text-sm font-bold shadow-md hover:shadow-lg transition-all cursor-pointer"
                >
                  <span>Resume lesson</span>
                  <span>→</span>
                </button>
              </div>
            </div>

            {/* Next Up card inside Hero */}
            <div className="rounded-2xl bg-white/10 backdrop-blur-md p-5 border border-white/15 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold tracking-wider uppercase text-[#A7F3D0]">NEXT UP</span>
                <span className="text-[10px] text-white/60">Checkpoint 3</span>
              </div>
              <div className="text-base font-semibold text-white">Resistance: Pipe & Flow Model</div>
              <p className="text-xs text-white/80 leading-relaxed">
                A visual simulation mapping water pressure to voltage and pipe diameter to electrical resistance.
              </p>
              <div className="pt-2 flex items-center justify-between text-xs text-[#A7F3D0]">
                <span>Analogy First</span>
                <button
                  onClick={() => navigate("lesson-player")}
                  className="font-semibold underline underline-offset-4 hover:text-white"
                >
                  Preview Concept
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 6: SCREENSHOT REFERENCE — PERSONALIZED RECOMMENDATIONS ("CHOSEN FOR YOU") */}
        <div className="space-y-4">
          <div>
            <span className="text-xs font-bold tracking-wider uppercase text-[#059669]">CHOSEN FOR YOU</span>
            <h2 className="font-serif text-2xl text-[#0D3B2E] tracking-tight mt-0.5">Keep the momentum going</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Card 1: BUILD YOUR FOUNDATION */}
            <div
              onClick={() => navigate("lesson-player")}
              className="bg-white rounded-2xl p-6 border border-[#E6E4DC] hover:border-[#0D3B2E]/40 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-[#059669] bg-[#ECFDF5] px-2.5 py-1 rounded-full">
                  BUILD YOUR FOUNDATION
                </span>
                <h3 className="font-serif text-lg font-bold text-[#0D3B2E] mt-3 group-hover:text-[#059669] transition-colors">
                  Resistance, made intuitive
                </h3>
                <p className="text-xs text-[#5E6D67] mt-2 leading-relaxed">
                  A visual 12-minute lesson before you move into circuit combinations.
                </p>
              </div>
              <div className="flex items-center justify-between pt-4 border-t border-[#F5F4EE] mt-4 text-xs font-medium text-[#5E6D67]">
                <div className="flex items-center gap-3">
                  <span>⏱ 12 min</span>
                  <span>•</span>
                  <span>Beginner</span>
                </div>
                <span className="text-[#0D3B2E] font-bold group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>

            {/* Card 2: QUICK PRACTICE */}
            <div
              onClick={() => navigate("question")}
              className="bg-white rounded-2xl p-6 border border-[#E6E4DC] hover:border-[#0D3B2E]/40 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-[#D97706] bg-[#FEF3C7] px-2.5 py-1 rounded-full">
                  QUICK PRACTICE
                </span>
                <h3 className="font-serif text-lg font-bold text-[#0D3B2E] mt-3 group-hover:text-[#D97706] transition-colors">
                  Voltage vs. current
                </h3>
                <p className="text-xs text-[#5E6D67] mt-2 leading-relaxed">
                  You hesitated here last time. Try three questions with instant feedback.
                </p>
              </div>
              <div className="flex items-center justify-between pt-4 border-t border-[#F5F4EE] mt-4 text-xs font-medium text-[#5E6D67]">
                <div className="flex items-center gap-3">
                  <span>⏱ 6 min</span>
                  <span>•</span>
                  <span>3 questions</span>
                </div>
                <span className="text-[#0D3B2E] font-bold group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>

            {/* Card 3: UP NEXT */}
            <div
              onClick={() => navigate("lesson-plan")}
              className="bg-white rounded-2xl p-6 border border-[#E6E4DC] hover:border-[#0D3B2E]/40 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-[#8B5CF6] bg-[#EDE9FE] px-2.5 py-1 rounded-full">
                  UP NEXT
                </span>
                <h3 className="font-serif text-lg font-bold text-[#0D3B2E] mt-3 group-hover:text-[#8B5CF6] transition-colors">
                  Series circuit lab
                </h3>
                <p className="text-xs text-[#5E6D67] mt-2 leading-relaxed">
                  Apply Ohm's law in a guided, interactive circuit experiment.
                </p>
              </div>
              <div className="flex items-center justify-between pt-4 border-t border-[#F5F4EE] mt-4 text-xs font-medium text-[#5E6D67]">
                <div className="flex items-center gap-3">
                  <span>⏱ 18 min</span>
                  <span>•</span>
                  <span>Interactive</span>
                </div>
                <span className="text-[#0D3B2E] font-bold group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 7: SCREENSHOT REFERENCE — "YOUR CURRENT PATH" & LEARNING INSIGHT */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Path Timeline */}
          <div className="lg:col-span-2 bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-7 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-[#F5F4EE] gap-2">
              <div>
                <span className="text-[10px] font-bold tracking-wider uppercase text-[#5E6D67]">YOUR CURRENT PATH</span>
                <h3 className="font-serif text-xl font-bold text-[#0D3B2E]">Electricity fundamentals</h3>
                <p className="text-xs text-[#5E6D67]">4 of 9 concepts explored</p>
              </div>
              <button
                onClick={() => navigate("learning-path")}
                className="text-xs font-semibold text-[#0D3B2E] hover:text-[#059669] flex items-center gap-1.5"
              >
                <span>View full learning path</span>
                <span>→</span>
              </button>
            </div>

            {/* Path Timeline Items */}
            <div className="divide-y divide-[#F5F4EE] pt-2">
              {/* Concept 1 */}
              <div className="py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center text-sm font-bold">
                    ✓
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-[#0F172A]">Electric charge</div>
                    <div className="text-xs text-[#5E6D67]">Mastery 94% · Fundamental concepts</div>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#ECFDF5] text-[#059669]">
                  Secure
                </span>
              </div>

              {/* Concept 2 (Current) */}
              <div className="py-3.5 flex items-center justify-between bg-[#ECFDF5]/50 -mx-6 px-6 rounded-xl">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center text-xs font-bold">
                    2
                  </div>
                  <div>
                    <div className="text-sm font-bold text-[#0D3B2E] flex items-center gap-2">
                      <span>Voltage & current</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#0D3B2E] text-white">
                        CURRENT
                      </span>
                    </div>
                    <div className="text-xs text-[#5E6D67]">In progress · 62% mastery · Dr. Aria live</div>
                  </div>
                </div>
                <button
                  onClick={() => navigate("lesson-player")}
                  className="text-xs font-bold text-[#059669] hover:underline"
                >
                  Resume →
                </button>
              </div>

              {/* Concept 3 */}
              <div className="py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-[#F5F4EE] text-[#0D3B2E] flex items-center justify-center text-xs font-bold">
                    3
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-[#0F172A]">Resistance</div>
                    <div className="text-xs text-[#5E6D67]">Weak concept (32%) · Adaptive visual ready</div>
                  </div>
                </div>
                <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-[#F5F4EE] text-[#5E6D67]">
                  Ready when you are
                </span>
              </div>

              {/* Concept 4 */}
              <div className="py-3.5 flex items-center justify-between opacity-60">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-[#F5F4EE] text-[#9CA3AF] flex items-center justify-center text-xs font-bold">
                    🔒
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-[#0F172A]">Series circuits</div>
                    <div className="text-xs text-[#5E6D67]">Requires mastery of Resistance</div>
                  </div>
                </div>
                <span className="text-xs font-medium text-[#9CA3AF]">
                  Complete Resistance first
                </span>
              </div>
            </div>
          </div>

          {/* Right Col: Dark Green Learning Insight Card */}
          <div className="rounded-3xl bg-[#0D3B2E] text-white p-6 sm:p-7 flex flex-col justify-between shadow-xs border border-[#164E3F]">
            <div className="space-y-4">
              <div className="w-9 h-9 rounded-xl bg-[#10B981]/20 text-[#A7F3D0] flex items-center justify-center text-lg">
                💡
              </div>
              <h3 className="font-serif text-2xl text-white tracking-tight leading-snug">
                YOU LEARN FASTEST when ideas are shown visually before the formula.
              </h3>
              <p className="text-xs text-[#D1FAE5]/90 leading-relaxed">
                Based on your recent lessons, we'll lead with diagrams and examples, then introduce the math.
              </p>
            </div>

            <div className="pt-6 border-t border-[#164E3F] mt-6 flex items-center justify-between">
              <button
                onClick={() => setInsightModalOpen(true)}
                className="text-xs text-[#A7F3D0] hover:text-white underline underline-offset-4 cursor-pointer font-medium"
              >
                Why am I seeing this?
              </button>
              <button
                onClick={() => navigate("profile")}
                className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors"
              >
                Adjust style
              </button>
            </div>
          </div>
        </div>

        {/* SECTION 9: KPI METRICS & ANALYTICS */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Overall Mastery", value: `${progress.overallMastery}%`, change: "+3%", icon: "📊", color: "#059669", bg: "#ECFDF5" },
            { label: "Current Streak", value: `${progress.streak} days`, change: "Best: 12", icon: "🔥", color: "#D97706", bg: "#FEF3C7" },
            { label: "Average Score", value: "87%", change: "+5%", icon: "⭐", color: "#10B981", bg: "#ECFDF5" },
            { label: "Lessons Completed", value: "12", change: "This week: 3", icon: "✅", color: "#0D3B2E", bg: "#F5F4EE" },
          ].map((m) => (
            <div key={m.label} className="bg-white rounded-2xl p-5 border border-[#E6E4DC] shadow-2xs">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xl">{m.icon}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full font-bold" style={{ backgroundColor: m.bg, color: m.color }}>
                  {m.change}
                </span>
              </div>
              <div className="text-2xl font-bold tracking-tight text-[#0D3B2E]">{m.value}</div>
              <div className="text-xs text-[#5E6D67] mt-0.5">{m.label}</div>
            </div>
          ))}
        </div>

        {/* Charts & Focus Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recharts Mastery AreaChart */}
          <div className="lg:col-span-2 bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-serif text-lg font-bold text-[#0D3B2E]">Mastery Progress</h3>
                <p className="text-xs text-[#5E6D67]">Overall learning retention trend over 7 weeks</p>
              </div>
              <div className="flex gap-1 bg-[#F5F4EE] p-1 rounded-xl">
                {(["1W", "1M", "All"] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setChartPeriod(t)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                      chartPeriod === t ? "bg-white text-[#0D3B2E] shadow-2xs" : "text-[#5E6D67] hover:text-[#0D3B2E]"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <ResponsiveContainer width="100%" height={170}>
              <AreaChart data={masteryData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="forestGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="week" tick={{ fontSize: 11, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <YAxis domain={[40, 100]} tick={{ fontSize: 11, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#FFFFFF",
                    borderColor: "#E6E4DC",
                    borderRadius: 12,
                    fontSize: 12,
                    color: "#0D3B2E",
                    boxShadow: "0 4px 12px rgba(13,59,46,0.08)",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="mastery"
                  stroke="#0D3B2E"
                  strokeWidth={2.5}
                  fill="url(#forestGrad)"
                  dot={{ r: 4, fill: "#10B981" }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Weak Concept Focus Area */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-base">⚠️</span>
                <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Focus Area</h3>
              </div>
              <div className="rounded-2xl p-4 bg-[#FFF1F2] border border-[#FFE4E6]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-sm font-bold text-[#E11D48]">Resistance</span>
                  <span className="text-xs font-bold px-2 py-0.5 bg-[#FFE4E6] text-[#E11D48] rounded-full">
                    32% Mastery
                  </span>
                </div>
                <p className="text-xs text-[#5E6D67] leading-relaxed">
                  AI detected a misconception about the inverse relationship between resistance and current. An analogy-first re-explanation is prepared.
                </p>
              </div>
            </div>

            <button
              onClick={() => navigate("lesson-player")}
              className="w-full mt-4 py-2.5 bg-[#E11D48] hover:bg-[#BE123C] text-white text-xs font-bold rounded-xl transition-colors shadow-xs"
            >
              Fix This Now →
            </button>
          </div>
        </div>

        {/* Insight Explanation Modal */}
        {insightModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-fade-in-up">
            <div className="w-full max-w-md bg-white rounded-3xl p-6 shadow-2xl border border-[#E6E4DC] space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xl">🧠</span>
                  <h3 className="font-serif text-lg font-bold text-[#0D3B2E]">Cognitive Model Insight</h3>
                </div>
                <button
                  onClick={() => setInsightModalOpen(false)}
                  className="text-xs font-bold text-[#5E6D67] hover:text-[#0D3B2E]"
                >
                  ✕
                </button>
              </div>
              <p className="text-xs text-[#334155] leading-relaxed">
                During your last 3 sessions, our adaptive engine observed that you answered questions <strong>73% faster</strong> and made <strong>60% fewer errors</strong> when concepts were introduced with physical or hydraulic analogies before showing algebraic equations.
              </p>
              <div className="p-3 bg-[#ECFDF5] rounded-xl border border-[#BBF7D0] text-xs text-[#059669]">
                ✓ Personalization active: <strong>Analogy First + Circuit Visualization</strong>
              </div>
              <button
                onClick={() => setInsightModalOpen(false)}
                className="w-full py-2.5 rounded-xl text-xs font-bold text-white bg-[#0D3B2E] hover:bg-[#07221A] transition-colors"
              >
                Got it
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
