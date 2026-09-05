import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const masteryOverTime = [
  { date: "Sep 1", mastery: 52 },
  { date: "Sep 2", mastery: 58 },
  { date: "Sep 3", mastery: 61 },
  { date: "Sep 4", mastery: 68 },
  { date: "Sep 5", mastery: 72 },
  { date: "Sep 6", mastery: 78 },
  { date: "Sep 7", mastery: 82 },
];

const assessmentScores = [
  { topic: "Voltage", score: 90 },
  { topic: "Current", score: 80 },
  { topic: "Resistance", score: 68 },
  { topic: "Ohm's Law", score: 68 },
];

const timeSpent = [
  { day: "Mon", mins: 15 },
  { day: "Tue", mins: 22 },
  { day: "Wed", mins: 12 },
  { day: "Thu", mins: 18 },
  { day: "Fri", mins: 25 },
  { day: "Sat", mins: 10 },
  { day: "Sun", mins: 20 },
];

export default function Analytics({ navigate, currentScreen }: Props) {
  const { profile, progress } = useLearner();
  const [filterPeriod, setFilterPeriod] = useState<"7D" | "1M" | "All">("7D");

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold text-[#059669] uppercase tracking-wider">
              TELEMETRY & COGNITIVE PROGRESS
            </span>
            <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Analytics</h1>
            <p className="text-xs text-[#5E6D67] mt-0.5">
              Comprehensive performance & concept retention telemetry for {profile.name}
            </p>
          </div>
          <div className="flex gap-1 bg-white border border-[#E6E4DC] p-1 rounded-xl shadow-2xs">
            {(["7D", "1M", "All"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setFilterPeriod(t)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  filterPeriod === t ? "bg-[#0D3B2E] text-white" : "text-[#5E6D67] hover:text-[#0D3B2E]"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Overall Mastery", value: `${progress.overallMastery}%`, change: "+12% this week", color: "#059669", bg: "#ECFDF5", icon: "📈" },
            { label: "Lessons Done", value: "12", change: "+3 this week", color: "#0D3B2E", bg: "#F5F4EE", icon: "📚" },
            { label: "Learning Streak", value: `${progress.streak} Days`, change: "Best: 12 days", color: "#D97706", bg: "#FEF3C7", icon: "🔥" },
            { label: "Misconceptions", value: "3 Diagnosed", change: "3 of 3 resolved", color: "#10B981", bg: "#ECFDF5", icon: "🧠" },
          ].map((k) => (
            <div key={k.label} className="bg-white rounded-3xl border border-[#E6E4DC] p-5 shadow-2xs">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xl">{k.icon}</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: k.bg, color: k.color }}>
                  {k.change}
                </span>
              </div>
              <div className="text-2xl font-bold text-[#0D3B2E] tracking-tight">{k.value}</div>
              <div className="text-xs text-[#5E6D67] mt-0.5">{k.label}</div>
            </div>
          ))}
        </div>

        {/* Charts: Mastery Trend & Assessment Scores */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Mastery Trend */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-3">
            <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Mastery Progression Over Time</h3>
            <ResponsiveContainer width="100%" height={170}>
              <AreaChart data={masteryOverTime} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="anaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <YAxis domain={[40, 100]} tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: "#FFF", borderRadius: 12, borderColor: "#E6E4DC", fontSize: 12 }} />
                <Area type="monotone" dataKey="mastery" stroke="#0D3B2E" strokeWidth={2.5} fill="url(#anaGrad)" dot={{ r: 4, fill: "#10B981" }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Assessment Scores */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-3">
            <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Assessment Scores by Concept</h3>
            <ResponsiveContainer width="100%" height={170}>
              <BarChart data={assessmentScores} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <XAxis dataKey="topic" tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: "#FFF", borderRadius: 12, borderColor: "#E6E4DC", fontSize: 12 }} />
                <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                  {assessmentScores.map((d, i) => (
                    <Cell key={i} fill={d.score >= 80 ? "#10B981" : d.score >= 60 ? "#0D3B2E" : "#E11D48"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Time Spent & Learning Streak Heatmap */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-3">
            <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Time Spent (minutes / day)</h3>
            <ResponsiveContainer width="100%" height={150}>
              <BarChart data={timeSpent} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="day" tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#5E6D67" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: "#FFF", borderRadius: 12, borderColor: "#E6E4DC", fontSize: 12 }} />
                <Bar dataKey="mins" fill="#0D3B2E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-base font-bold text-[#0D3B2E]">28-Day Activity Heatmap</h3>
              <span className="text-xs font-bold text-[#059669]">7 Days Active</span>
            </div>
            <div className="grid grid-cols-7 gap-1.5">
              {[...Array(28)].map((_, i) => (
                <div
                  key={i}
                  className={`h-6 rounded-md transition-all ${
                    i >= 21
                      ? "bg-[#10B981]"
                      : i % 3 === 0
                      ? "bg-[#0D3B2E]/60"
                      : i % 2 === 0
                      ? "bg-[#A7F3D0]"
                      : "bg-[#F5F4EE]"
                  }`}
                  title={`Day ${i + 1}`}
                />
              ))}
            </div>
            <div className="flex items-center gap-3 p-3.5 rounded-2xl bg-[#ECFDF5] border border-[#BBF7D0]">
              <span className="text-2xl">🔥</span>
              <div>
                <div className="text-xs font-bold text-[#0D3B2E]">Active 7-Day Consistency Streak</div>
                <div className="text-[10px] text-[#5E6D67]">Learner retention increases by 40% with daily 10-minute micro-lessons.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
