import { useState } from "react";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const steps = ["Profile", "Preferences", "Goals", "Review"];

export default function Onboarding({ navigate }: Props) {
  const { profile, updateProfile } = useLearner();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    name: profile.name,
    level: profile.level,
    language: profile.language,
    goal: profile.goal,
    knowledge: profile.knowledge,
    style: profile.style,
    time: profile.time,
    depth: profile.depth,
  });

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const ChipGroup = ({
    options,
    value,
    onChange,
  }: {
    options: string[];
    value: string;
    onChange: (v: string) => void;
  }) => (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button
          key={o}
          type="button"
          onClick={() => onChange(o)}
          className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
            value === o
              ? "bg-[#0D3B2E] text-white border-[#0D3B2E] shadow-2xs"
              : "bg-white text-[#334155] border-[#E6E4DC] hover:border-[#0D3B2E]/40 hover:bg-[#F5F4EE]"
          }`}
        >
          {o}
        </button>
      ))}
    </div>
  );

  const handleFinish = () => {
    updateProfile(form);
    navigate("dashboard");
  };

  return (
    <div className="min-h-screen bg-[#F9F8F5] flex items-center justify-center py-12 px-4 text-[#0F172A]">
      <div className="w-full max-w-xl space-y-6">
        {/* Brand Header */}
        <div className="flex items-center gap-3 justify-center">
          <div className="w-9 h-9 rounded-xl bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center font-bold text-sm shadow-xs">
            ✦
          </div>
          <div className="text-center">
            <div className="text-sm font-bold text-[#0D3B2E]">Aster AI</div>
            <div className="text-[10px] text-[#5E6D67] font-semibold uppercase">Learner Onboarding</div>
          </div>
        </div>

        {/* Step Progress Indicators */}
        <div className="flex items-center gap-2">
          {steps.map((s, i) => (
            <div key={s} className="flex-1 space-y-1 text-center">
              <div
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  i <= step ? "bg-[#0D3B2E]" : "bg-[#E6E4DC]"
                }`}
              />
              <span className={`text-[10px] font-bold ${i <= step ? "text-[#0D3B2E]" : "text-[#9CA3AF]"}`}>
                {s}
              </span>
            </div>
          ))}
        </div>

        {/* Wizard Card */}
        <div className="bg-white rounded-3xl border border-[#E6E4DC] shadow-sm p-7 sm:p-8 space-y-6 animate-fade-in-up">
          {/* Step 0: Profile */}
          {step === 0 && (
            <div className="space-y-5">
              <div>
                <h2 className="font-serif text-2xl font-bold text-[#0D3B2E]">What should Dr. Aria call you?</h2>
                <p className="text-xs text-[#5E6D67] mt-0.5">Let's configure your learner identity</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Student Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => set("name", e.target.value)}
                  className="w-full border border-[#E6E4DC] rounded-xl px-4 py-2.5 text-sm text-[#0F172A] focus:outline-none focus:border-[#0D3B2E]"
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Education Level</label>
                <ChipGroup options={["Beginner", "Intermediate", "Advanced"]} value={form.level} onChange={(v) => set("level", v)} />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Preferred Language</label>
                <ChipGroup options={["English", "Hindi", "Tamil", "Hinglish"]} value={form.language} onChange={(v) => set("language", v)} />
              </div>
            </div>
          )}

          {/* Step 1: Preferences */}
          {step === 1 && (
            <div className="space-y-5">
              <div>
                <h2 className="font-serif text-2xl font-bold text-[#0D3B2E]">How do you learn best?</h2>
                <p className="text-xs text-[#5E6D67] mt-0.5">Your teacher adapts delivery to this preference</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Teaching Strategy</label>
                <ChipGroup
                  options={["Visual", "Simple Examples", "Analogy First", "Technical", "Interactive"]}
                  value={form.style}
                  onChange={(v) => set("style", v)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Available Time Per Session</label>
                <div className="flex gap-2 flex-wrap">
                  {["5", "10", "20", "30", "60"].map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => set("time", t)}
                      className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                        form.time === t
                          ? "bg-[#0D3B2E] text-white border-[#0D3B2E]"
                          : "bg-white text-[#334155] border-[#E6E4DC] hover:border-[#0D3B2E]/40 hover:bg-[#F5F4EE]"
                      }`}
                    >
                      {t} min
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Target Depth</label>
                <ChipGroup options={["Quick Overview", "Balanced", "Deep Dive"]} value={form.depth} onChange={(v) => set("depth", v)} />
              </div>
            </div>
          )}

          {/* Step 2: Goals */}
          {step === 2 && (
            <div className="space-y-5">
              <div>
                <h2 className="font-serif text-2xl font-bold text-[#0D3B2E]">What is your primary learning goal?</h2>
                <p className="text-xs text-[#5E6D67] mt-0.5">Helps the syllabus generator sequence concepts</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Goal Description</label>
                <textarea
                  value={form.goal}
                  onChange={(e) => set("goal", e.target.value)}
                  rows={2}
                  className="w-full border border-[#E6E4DC] rounded-xl px-4 py-2.5 text-sm text-[#0F172A] focus:outline-none focus:border-[#0D3B2E] resize-none"
                  placeholder="e.g. Master Physics fundamentals and circuit analysis"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#5E6D67] uppercase mb-1.5">Existing Knowledge</label>
                <textarea
                  value={form.knowledge}
                  onChange={(e) => set("knowledge", e.target.value)}
                  rows={2}
                  className="w-full border border-[#E6E4DC] rounded-xl px-4 py-2.5 text-sm text-[#0F172A] focus:outline-none focus:border-[#0D3B2E] resize-none"
                  placeholder="e.g. Basic understanding of batteries and wires"
                />
              </div>
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && (
            <div className="space-y-5">
              <div>
                <h2 className="font-serif text-2xl font-bold text-[#0D3B2E]">Review Your Cognitive Profile</h2>
                <p className="text-xs text-[#5E6D67] mt-0.5">You can edit these preferences at any time in Settings</p>
              </div>

              <div className="rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC] divide-y divide-[#F5F4EE] text-xs">
                {[
                  ["Student Name", form.name],
                  ["Level", form.level],
                  ["Language", `🇮🇳 ${form.language}`],
                  ["Strategy", form.style],
                  ["Pacing", `${form.time} Minutes / Lesson`],
                  ["Depth", form.depth],
                  ["Goal", form.goal],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between py-2.5 px-4">
                    <span className="font-bold text-[#5E6D67]">{k}</span>
                    <span className="font-semibold text-[#0D3B2E]">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step Navigation Buttons */}
          <div className="flex items-center gap-3 pt-4 border-t border-[#F5F4EE]">
            {step > 0 && (
              <button
                type="button"
                onClick={() => setStep((s) => s - 1)}
                className="px-5 py-3 rounded-xl border border-[#E6E4DC] text-xs font-bold text-[#334155] hover:bg-[#F5F4EE] transition-colors"
              >
                Back
              </button>
            )}
            <button
              type="button"
              onClick={() => (step < steps.length - 1 ? setStep((s) => s + 1) : handleFinish())}
              className="flex-1 py-3.5 rounded-xl text-xs font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] transition-all shadow-xs cursor-pointer text-center"
            >
              {step < steps.length - 1 ? "Continue →" : "Save Profile & Enter Dashboard →"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
