import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

export default function CreateLesson({ navigate, currentScreen }: Props) {
  const { profile, updateProfile, addDocument } = useLearner();
  const [prompt, setPrompt] = useState("Teach me Ohm's Law and Circuit Resistance from the beginning.");
  const [level, setLevel] = useState(profile.level);
  const [language, setLanguage] = useState(profile.language);
  const [style, setStyle] = useState(profile.style);
  const [time, setTime] = useState(profile.time);
  const [depth, setDepth] = useState(profile.depth);
  const [goal, setGoal] = useState("Understand fundamentals and solve circuit problems");
  const [fileState, setFileState] = useState<"empty" | "uploading" | "uploaded">("empty");
  const [dragging, setDragging] = useState(false);

  const handleUpload = () => {
    setFileState("uploading");
    setTimeout(() => {
      setFileState("uploaded");
      addDocument({
        name: "Uploaded Material — Physics.pdf",
        type: "PDF",
        pages: 18,
        chapters: 4,
        concepts: 14,
        status: "grounded",
        lastUsed: "Just now",
        size: "3.2 MB",
      });
    }, 1500);
  };

  const handleCreate = () => {
    updateProfile({
      level,
      language,
      style,
      time,
      depth,
      goal,
    });
    navigate("document-processing");
  };

  const ChipRow = ({
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
          className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
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

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <span className="text-xs font-bold text-[#059669] uppercase tracking-wider">
            LESSON CREATION STUDIO
          </span>
          <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Create a Personalized Lesson</h1>
          <p className="text-xs text-[#5E6D67] mt-0.5">
            Choose a topic or upload your syllabus, notes, or textbook chapters to ground your AI teacher.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left 3 Cols: Option A (Upload) & Option B (Topic Input) */}
          <div className="lg:col-span-3 space-y-6">
            {/* OPTION B: Topic Input */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center text-sm font-bold">
                  💬
                </div>
                <div>
                  <h2 className="font-serif text-base font-bold text-[#0D3B2E]">Option B: Teach Me a Topic</h2>
                  <p className="text-xs text-[#5E6D67]">Describe what you want to master in natural language</p>
                </div>
              </div>

              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={3}
                className="w-full border border-[#E6E4DC] rounded-2xl px-4 py-3 text-sm text-[#0F172A] bg-[#F9F8F5] focus:outline-none focus:border-[#0D3B2E] focus:bg-white resize-none transition-colors"
                placeholder="Teach me Ohm's Law and Circuit Resistance from the beginning..."
              />

              <div className="flex flex-wrap gap-2">
                {[
                  "Ohm's Law",
                  "Newton's Third Law",
                  "Photosynthesis Cycle",
                  "Binary Search Trees",
                  "Electromagnetic Induction",
                ].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setPrompt(`Teach me ${s} from the beginning with visual analogies.`)}
                    className="px-3 py-1 rounded-full text-xs text-[#5E6D67] bg-[#F5F4EE] hover:bg-[#ECFDF5] hover:text-[#059669] font-medium transition-colors"
                  >
                    + {s}
                  </button>
                ))}
              </div>
            </div>

            {/* OPTION A: Upload Material */}
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-[#F5F4EE] text-[#0D3B2E] flex items-center justify-center text-sm font-bold">
                    📄
                  </div>
                  <div>
                    <h2 className="font-serif text-base font-bold text-[#0D3B2E]">Option A: Upload Study Material</h2>
                    <p className="text-xs text-[#5E6D67]">PDF, DOCX, PPTX, research paper, notes, textbook</p>
                  </div>
                </div>
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#ECFDF5] text-[#059669]">
                  RAG Grounding
                </span>
              </div>

              {fileState === "empty" && (
                <div
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragging(true);
                  }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragging(false);
                    handleUpload();
                  }}
                  onClick={handleUpload}
                  className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
                    dragging
                      ? "border-[#059669] bg-[#ECFDF5]"
                      : "border-[#E6E4DC] hover:border-[#0D3B2E] hover:bg-[#F9F8F5]"
                  }`}
                >
                  <div className="text-3xl mb-2">📥</div>
                  <div className="text-sm font-bold text-[#0D3B2E]">
                    Click to browse or drop your learning documents here
                  </div>
                  <div className="text-xs text-[#5E6D67] mt-1">
                    Supports PDF, DOC, DOCX, PPT, PPTX up to 50MB
                  </div>
                </div>
              )}

              {fileState === "uploading" && (
                <div className="p-4 rounded-2xl border border-[#E6E4DC] bg-[#F9F8F5] space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center font-bold">
                      📄
                    </div>
                    <div className="flex-1">
                      <div className="text-xs font-bold text-[#0D3B2E]">Physics Notes.pdf</div>
                      <div className="text-[10px] text-[#5E6D67]">Uploading & validating format…</div>
                    </div>
                  </div>
                  <div className="h-1.5 bg-[#E6E4DC] rounded-full overflow-hidden">
                    <div className="h-full bg-[#059669] rounded-full animate-pulse" style={{ width: "70%" }} />
                  </div>
                </div>
              )}

              {fileState === "uploaded" && (
                <div className="p-4 rounded-2xl border border-[#BBF7D0] bg-[#ECFDF5] flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-[#DCFCE7] text-[#059669] flex items-center justify-center font-bold">
                      ✓
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#0D3B2E]">Physics Notes.pdf</div>
                      <div className="text-[10px] text-[#5E6D67]">24 pages · 6 chapters · Ready for RAG extraction</div>
                    </div>
                  </div>
                  <span className="text-xs font-bold text-[#059669]">Grounded ✓</span>
                </div>
              )}
            </div>
          </div>

          {/* Right 2 Cols: Lesson Configuration */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-3xl border border-[#E6E4DC] p-6 shadow-xs space-y-4">
              <h2 className="font-serif text-base font-bold text-[#0D3B2E]">Configuration</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-[#5E6D67] mb-2 uppercase">Education Level</label>
                  <ChipRow options={["Beginner", "Intermediate", "Advanced"]} value={level} onChange={setLevel} />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#5E6D67] mb-2 uppercase">Delivery Language</label>
                  <ChipRow options={["English", "Hindi", "Tamil", "Hinglish"]} value={language} onChange={setLanguage} />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#5E6D67] mb-2 uppercase">Time Budget</label>
                  <div className="flex gap-2 flex-wrap">
                    {["5", "10", "20", "30", "60"].map((t) => (
                      <button
                        key={t}
                        type="button"
                        onClick={() => setTime(t)}
                        className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                          time === t
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
                  <label className="block text-xs font-bold text-[#5E6D67] mb-2 uppercase">Teaching Style</label>
                  <ChipRow
                    options={["Visual", "Simple Examples", "Analogy First", "Technical", "Interactive"]}
                    value={style}
                    onChange={setStyle}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#5E6D67] mb-2 uppercase">Desired Depth</label>
                  <ChipRow options={["Quick Overview", "Balanced", "Deep Dive"]} value={depth} onChange={setDepth} />
                </div>
              </div>
            </div>

            {/* Summary Box */}
            <div className="rounded-2xl p-4 bg-[#ECFDF5] border border-[#BBF7D0] space-y-2">
              <div className="text-xs font-bold text-[#0D3B2E]">Personalization Preview</div>
              <div className="flex flex-wrap gap-1.5 text-[10px]">
                {[level, `🇮🇳 ${language}`, `${time}m`, style, depth].map((tag) => (
                  <span key={tag} className="px-2.5 py-1 rounded-full bg-white border border-[#A7F3D0] text-[#059669] font-semibold">
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Primary CTA */}
            <button
              type="button"
              onClick={handleCreate}
              className="w-full py-4 rounded-xl text-sm font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] shadow-md hover:shadow-lg transition-all cursor-pointer text-center"
            >
              Create Personalized Lesson →
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
