import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

export default function Landing({ navigate }: Props) {
  const { profile } = useLearner();

  return (
    <div className="min-h-screen bg-[#F9F8F5] text-[#0F172A] flex flex-col justify-between">
      {/* Top Navbar */}
      <header className="bg-white border-b border-[#E6E4DC] px-6 lg:px-12 py-4 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center font-bold text-sm shadow-xs">
            ✦
          </div>
          <div>
            <div className="text-sm font-bold text-[#0D3B2E]">Aster AI</div>
            <div className="text-[10px] text-[#5E6D67] font-semibold uppercase tracking-wider">Teacher of the Future</div>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-xs font-semibold text-[#5E6D67]">
          <a href="#how-it-works" className="hover:text-[#0D3B2E] transition-colors">Cognitive Loop</a>
          <a href="#features" className="hover:text-[#0D3B2E] transition-colors">Features</a>
          <a href="#pedagogy" className="hover:text-[#0D3B2E] transition-colors">Adaptive Intelligence</a>
        </nav>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("dashboard")}
            className="text-xs font-semibold text-[#0D3B2E] hover:text-[#059669] px-3.5 py-2 transition-colors cursor-pointer"
          >
            Launch Demo
          </button>
          <button
            onClick={() => navigate("onboarding")}
            className="text-xs font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] px-5 py-2.5 rounded-xl shadow-xs transition-all cursor-pointer"
          >
            Get Started →
          </button>
        </div>
      </header>

      {/* Main Hero */}
      <main className="max-w-6xl mx-auto px-6 py-16 lg:py-24 space-y-16">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 bg-[#ECFDF5] text-[#059669] border border-[#A7F3D0] text-xs font-bold px-4 py-1.5 rounded-full">
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse-dot" />
            AI Innovation Hackathon 2026 Round 2 · Autonomous Pedagogical System
          </div>

          <h1 className="font-serif text-4xl sm:text-6xl text-[#0D3B2E] tracking-tight leading-[1.15]">
            An AI Teacher That<br />
            <span className="italic text-[#059669]">Adapts When You Misunderstand</span>
          </h1>

          <p className="text-base sm:text-lg text-[#334155] leading-relaxed max-w-2xl mx-auto">
            This is <strong>not a chatbot</strong>. Your AI teacher plans a personalized syllabus from your textbooks, lectures with audio and live diagrams, diagnoses misconceptions with 91% confidence, and dynamically switches teaching strategies.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <button
              onClick={() => navigate("dashboard")}
              className="px-8 py-4 rounded-xl bg-[#0D3B2E] hover:bg-[#07221A] text-white text-sm font-bold shadow-md hover:shadow-lg transition-all cursor-pointer"
            >
              Resume Demo as {profile.name} →
            </button>
            <button
              onClick={() => navigate("onboarding")}
              className="px-7 py-4 rounded-xl bg-white border border-[#E6E4DC] hover:border-[#0D3B2E]/40 text-[#0D3B2E] text-sm font-bold transition-colors cursor-pointer"
            >
              Start New Onboarding
            </button>
          </div>
        </div>

        {/* Cognitive Loop Diagram Banner */}
        <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-8 shadow-sm space-y-6" id="how-it-works">
          <div className="text-center max-w-xl mx-auto space-y-1">
            <span className="text-[10px] font-bold text-[#059669] uppercase tracking-wider">
              CORE PEDAGOGICAL ENGINE
            </span>
            <h2 className="font-serif text-2xl font-bold text-[#0D3B2E]">The 8-Stage Cognitive Loop</h2>
            <p className="text-xs text-[#5E6D67]">
              Continuous feedback ensures learning mastery before advancing
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5 text-center text-xs">
            {[
              { step: "1", title: "UNDERSTAND", desc: "Profile & context", icon: "🧠" },
              { step: "2", title: "PLAN", desc: "Adaptive syllabus", icon: "📋" },
              { step: "3", title: "EXPLAIN", desc: "Dr. Aria lecture", icon: "🗣" },
              { step: "4", title: "DEMONSTRATE", desc: "Circuit simulator", icon: "🎨" },
              { step: "5", title: "QUESTION", desc: "Checkpoint test", icon: "❓" },
              { step: "6", title: "EVALUATE", desc: "Misconception audit", icon: "🔍" },
              { step: "7", title: "ADAPT", desc: "Hydraulic analogy", icon: "🔄" },
              { step: "8", title: "CONTINUE", desc: "Mastery secured", icon: "✓" },
            ].map((s) => (
              <div key={s.step} className="p-3.5 rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC] flex flex-col items-center justify-between">
                <span className="text-xl mb-1">{s.icon}</span>
                <div className="text-[11px] font-bold text-[#0D3B2E]">{s.title}</div>
                <div className="text-[10px] text-[#5E6D67] mt-0.5">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6" id="features">
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center text-xl">
              📄
            </div>
            <h3 className="font-serif text-lg font-bold text-[#0D3B2E]">Source Grounded (RAG)</h3>
            <p className="text-xs text-[#5E6D67] leading-relaxed">
              Upload your own syllabus or textbook. Every sentence, checkpoint question, and formula is cited directly back to chapters and pages with zero hallucination.
            </p>
          </div>

          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#FFF1F2] text-[#E11D48] flex items-center justify-center text-xl">
              💡
            </div>
            <h3 className="font-serif text-lg font-bold text-[#0D3B2E]">Misconception Detection</h3>
            <p className="text-xs text-[#5E6D67] leading-relaxed">
              When a student answers incorrectly, the AI doesn't just grade it wrong. It diagnoses the underlying cognitive misunderstanding and explains what belief caused the error.
            </p>
          </div>

          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center text-xl">
              🔄
            </div>
            <h3 className="font-serif text-lg font-bold text-[#0D3B2E]">Dynamic Re-Teaching</h3>
            <p className="text-xs text-[#5E6D67] leading-relaxed">
              Automatically pivots teaching strategy from technical formulas to hydraulic pipe-and-flow physical simulations to rebuild conceptual intuition.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#E6E4DC] bg-white py-6 px-6 text-center text-xs text-[#5E6D67]">
        Aster AI Teacher of the Future · AI Innovation Hackathon 2026 Round 2 · Adaptive Cognitive Architecture
      </footer>
    </div>
  );
}
