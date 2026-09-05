import { useState, useEffect } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const steps = [
  { id: "upload", label: "UPLOAD", desc: "File received & checksum verified", icon: "⬆" },
  { id: "validate", label: "VALIDATE", desc: "Format & integrity checked (PDF v1.7)", icon: "🛡" },
  { id: "extract", label: "EXTRACT", desc: "Parsing text, equations & diagrams", icon: "⚙" },
  { id: "detect", label: "DETECT CONCEPTS", desc: "Found 18 physical concepts in 6 chapters", icon: "🔍" },
  { id: "chunk", label: "CHUNK", desc: "Semantic splitting into teachable units", icon: "✂" },
  { id: "index", label: "INDEX", desc: "Vector indexing into knowledge graph", icon: "📑" },
  { id: "ready", label: "READY", desc: "Fully grounded for Dr. Aria AI teaching", icon: "✓" },
];

export default function DocumentProcessing({ navigate, currentScreen }: Props) {
  const { profile } = useLearner();
  const [activeStep, setActiveStep] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    steps.forEach((_, i) => {
      timers.push(setTimeout(() => setActiveStep(i + 1), (i + 1) * 500));
    });
    timers.push(setTimeout(() => setDone(true), steps.length * 500 + 200));
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <span className="text-xs font-bold text-[#059669] uppercase tracking-wider">
            RAG INGESTION PIPELINE
          </span>
          <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Document Processing & Grounding</h1>
          <p className="text-xs text-[#5E6D67] mt-0.5">
            Extracting semantic concepts and evidence references from your source material.
          </p>
        </div>

        {/* File Card */}
        <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center text-xl font-bold">
              📄
            </div>
            <div>
              <div className="font-bold text-[#0F172A] text-sm sm:text-base">Physics Notes.pdf</div>
              <div className="flex flex-wrap gap-3 text-xs text-[#5E6D67] mt-0.5">
                <span>PDF · 2.4 MB</span>
                <span>•</span>
                <span>24 pages</span>
                <span>•</span>
                <span>6 chapters</span>
                <span>•</span>
                <span>18 concepts</span>
              </div>
            </div>
          </div>
          <div>
            {done ? (
              <span className="flex items-center gap-1.5 text-xs font-bold text-[#059669] bg-[#ECFDF5] border border-[#A7F3D0] px-3.5 py-1.5 rounded-full">
                <span>✓</span> Grounded by Source
              </span>
            ) : (
              <span className="text-xs font-bold text-[#D97706] bg-[#FEF3C7] px-3.5 py-1.5 rounded-full">
                Processing…
              </span>
            )}
          </div>
        </div>

        {/* Section 11: 7-Stage Visual Pipeline */}
        <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 sm:p-7 shadow-xs space-y-4">
          <h2 className="font-serif text-base font-bold text-[#0D3B2E] mb-2">Ingestion & Indexing Timeline</h2>
          <div className="space-y-4">
            {steps.map((step, i) => {
              const state = i < activeStep ? "done" : i === activeStep ? "active" : "pending";
              return (
                <div key={step.id} className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold transition-all ${
                        state === "done"
                          ? "bg-[#ECFDF5] text-[#059669] border border-[#BBF7D0]"
                          : state === "active"
                          ? "bg-[#0D3B2E] text-white animate-pulse"
                          : "bg-[#F5F4EE] text-[#9CA3AF]"
                      }`}
                    >
                      {state === "done" ? "✓" : step.icon}
                    </div>
                    {i < steps.length - 1 && (
                      <div
                        className={`w-0.5 h-7 mt-1 transition-all duration-500 ${
                          state === "done" ? "bg-[#10B981]" : "bg-[#E6E4DC]"
                        }`}
                      />
                    )}
                  </div>

                  <div className="flex-1 pb-3">
                    <div
                      className={`text-xs font-bold transition-colors ${
                        state === "done"
                          ? "text-[#059669]"
                          : state === "active"
                          ? "text-[#0D3B2E]"
                          : "text-[#9CA3AF]"
                      }`}
                    >
                      {step.label}
                    </div>
                    <div className="text-xs text-[#5E6D67]">{step.desc}</div>
                    {state === "active" && (
                      <div className="mt-2 h-1.5 w-40 bg-[#E6E4DC] rounded-full overflow-hidden">
                        <div className="h-full bg-[#0D3B2E] rounded-full animate-pulse" style={{ width: "65%" }} />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Grounded Evidence Preview */}
        {done && (
          <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4 animate-fade-in-up">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-base font-bold text-[#0D3B2E]">Grounded Evidence Preview</h3>
              <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-[#ECFDF5] text-[#059669]">
                ✓ Ready for Lesson Planner
              </span>
            </div>

            <div className="space-y-3">
              {[
                {
                  page: "Page 48",
                  chapter: "Chapter 4 — Voltage",
                  text: "Voltage is the electrical potential difference between two points in a circuit, measured in Volts (V). It represents the energy required to move a unit charge.",
                },
                {
                  page: "Page 51",
                  chapter: "Chapter 4 — Current",
                  text: "Electric current is the rate of flow of electric charge through a conductor, measured in Amperes (A). Directed from positive to negative terminal conventionally.",
                },
                {
                  page: "Page 53",
                  chapter: "Chapter 4 — Resistance",
                  text: "Resistance is the opposition to current flow in a conductor, measured in Ohms (Ω). Higher resistance reduces current flow proportionally at constant voltage (I = V / R).",
                },
              ].map((ev) => (
                <div key={ev.page} className="p-4 rounded-2xl bg-[#F9F8F5] border border-[#E6E4DC] flex gap-3 text-xs">
                  <span className="font-bold text-[#0D3B2E] bg-white border border-[#E6E4DC] px-2 py-1 rounded-lg h-fit">
                    {ev.page}
                  </span>
                  <div>
                    <div className="font-bold text-[#059669] mb-0.5">{ev.chapter}</div>
                    <p className="text-[#334155] leading-relaxed">{ev.text}</p>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={() => navigate("lesson-plan")}
              className="w-full py-4 rounded-xl text-sm font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] shadow-md hover:shadow-lg transition-all cursor-pointer text-center"
            >
              View Personalized Lesson Plan →
            </button>
          </div>
        )}
      </div>
    </AppShell>
  );
}
