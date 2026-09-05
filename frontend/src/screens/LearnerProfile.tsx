import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

export default function LearnerProfile({ navigate, currentScreen }: Props) {
  const { profile, updateProfile, progress } = useLearner();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(profile.name);
  const [language, setLanguage] = useState(profile.language);
  const [style, setStyle] = useState(profile.style);
  const [depth, setDepth] = useState(profile.depth);
  const [level, setLevel] = useState(profile.level);
  const [time, setTime] = useState(profile.time);

  const handleSave = () => {
    updateProfile({
      name,
      language,
      style,
      depth,
      level,
      time,
    });
    setEditing(false);
  };

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-[#059669] uppercase tracking-wider">
              COGNITIVE PROFILE & MEMORY
            </span>
            <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Learner Profile</h1>
            <p className="text-xs text-[#5E6D67] mt-0.5">
              Personalized cognitive memory and preferences for {profile.name}
            </p>
          </div>
          <button
            onClick={() => {
              if (editing) handleSave();
              else setEditing(true);
            }}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer ${
              editing
                ? "bg-[#10B981] hover:bg-[#059669] text-[#07221A]"
                : "bg-white border border-[#E6E4DC] text-[#0D3B2E] hover:bg-[#F5F4EE]"
            }`}
          >
            {editing ? "Save Changes ✓" : "Edit Preferences"}
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Avatar & Summary Card */}
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-7 shadow-xs text-center flex flex-col items-center justify-between space-y-4">
            <div className="w-full space-y-3">
              <div className="w-20 h-20 rounded-full bg-[#0D3B2E] text-[#A7F3D0] mx-auto flex items-center justify-center text-3xl font-bold shadow-md border-2 border-[#10B981]/30">
                {name[0] || "A"}
              </div>

              {editing ? (
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="text-xl font-bold text-[#0D3B2E] text-center border-b-2 border-[#10B981] focus:outline-none bg-transparent w-full"
                />
              ) : (
                <h2 className="text-xl font-bold text-[#0D3B2E]">{name}</h2>
              )}

              <p className="text-xs text-[#5E6D67]">
                AI Innovation Hackathon Demo Learner · Grade 11 Physics
              </p>

              <div className="pt-2">
                <span className="text-[10px] font-bold px-3 py-1 rounded-full bg-[#ECFDF5] text-[#059669] border border-[#A7F3D0]">
                  Grounded in Physics Notes.pdf
                </span>
              </div>
            </div>

            <div className="w-full pt-4 border-t border-[#F5F4EE] space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-[#5E6D67]">Overall Mastery</span>
                <span className="text-[#0D3B2E] font-bold">{progress.overallMastery}%</span>
              </div>
              <div className="h-2 bg-[#F5F4EE] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#0D3B2E] rounded-full transition-all duration-700"
                  style={{ width: `${progress.overallMastery}%` }}
                />
              </div>
            </div>
          </div>

          {/* Preferences & Cognitive Memory */}
          <div className="lg:col-span-2 space-y-6">
            {/* Preferences Grid */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
              <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Learning Preferences</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-3.5 rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC]">
                  <div className="text-[10px] text-[#5E6D67] font-bold uppercase">Language</div>
                  {editing ? (
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="mt-1 w-full bg-white border border-[#E6E4DC] rounded-xl px-3 py-1 text-xs font-bold text-[#0D3B2E]"
                    >
                      {["English", "Hindi", "Tamil", "Hinglish"].map((l) => (
                        <option key={l}>{l}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-sm font-bold text-[#0D3B2E] mt-1">🇮🇳 {language}</div>
                  )}
                </div>

                <div className="p-3.5 rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC]">
                  <div className="text-[10px] text-[#5E6D67] font-bold uppercase">Teaching Style</div>
                  {editing ? (
                    <select
                      value={style}
                      onChange={(e) => setStyle(e.target.value)}
                      className="mt-1 w-full bg-white border border-[#E6E4DC] rounded-xl px-3 py-1 text-xs font-bold text-[#0D3B2E]"
                    >
                      {["Visual", "Simple Examples", "Analogy First", "Technical", "Interactive"].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-sm font-bold text-[#0D3B2E] mt-1">🎨 {style}</div>
                  )}
                </div>

                <div className="p-3.5 rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC]">
                  <div className="text-[10px] text-[#5E6D67] font-bold uppercase">Education Level</div>
                  {editing ? (
                    <select
                      value={level}
                      onChange={(e) => setLevel(e.target.value)}
                      className="mt-1 w-full bg-white border border-[#E6E4DC] rounded-xl px-3 py-1 text-xs font-bold text-[#0D3B2E]"
                    >
                      {["Beginner", "Intermediate", "Advanced"].map((lv) => (
                        <option key={lv}>{lv}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-sm font-bold text-[#0D3B2E] mt-1">📚 {level}</div>
                  )}
                </div>

                <div className="p-3.5 rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC]">
                  <div className="text-[10px] text-[#5E6D67] font-bold uppercase">Lesson Depth</div>
                  {editing ? (
                    <select
                      value={depth}
                      onChange={(e) => setDepth(e.target.value)}
                      className="mt-1 w-full bg-white border border-[#E6E4DC] rounded-xl px-3 py-1 text-xs font-bold text-[#0D3B2E]"
                    >
                      {["Quick Overview", "Balanced", "Deep Dive"].map((d) => (
                        <option key={d}>{d}</option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-sm font-bold text-[#0D3B2E] mt-1">⚡ {depth}</div>
                  )}
                </div>
              </div>
            </div>

            {/* Cognitive Memory & Concepts */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
              <h3 className="font-serif text-base font-bold text-[#0D3B2E]">
                Explicit Cognitive Model
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="text-[10px] font-bold text-[#059669] uppercase">STRONG CONCEPTS</div>
                  {["Voltage Potential (85%)", "Direct Current flow", "Closed circuit loops"].map((c) => (
                    <div key={c} className="flex items-center gap-2 text-xs text-[#0F172A]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                      <span>{c}</span>
                    </div>
                  ))}
                </div>

                <div className="space-y-2">
                  <div className="text-[10px] font-bold text-[#E11D48] uppercase">NEEDS REINFORCEMENT</div>
                  {["Resistance calculations (68%)", "Algebraic formulation (R = V/I)"].map((c) => (
                    <div key={c} className="flex items-center gap-2 text-xs text-[#0F172A]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#E11D48]" />
                      <span>{c}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Resolved Misconception Card */}
              <div className="p-4 rounded-2xl bg-[#ECFDF5] border border-[#BBF7D0] space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-[#059669] uppercase">
                    RESOLVED MISCONCEPTION RECORD
                  </span>
                  <span className="text-[10px] font-bold text-[#059669]">Sep 4, 2026</span>
                </div>
                <div className="text-xs font-semibold text-[#0D3B2E]">
                  Inverse property of Resistance (I = V / R)
                </div>
                <p className="text-[11px] text-[#5E6D67]">
                  Corrected intuition that higher resistance increases current using hydraulic pipe narrowing analogy.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
