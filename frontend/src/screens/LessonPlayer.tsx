import { useState, useEffect } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";
import TeacherVideoPlayer, {
  PHYSICS_DEMO_SEGMENTS,
  ML_DEMO_SEGMENTS,
  TeacherState,
} from "../components/TeacherVideoPlayer";
import VisualWhiteboard, { SubjectVisualMode } from "../components/VisualWhiteboard";
import DoubtInterruptionModal from "../components/DoubtInterruptionModal";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const PHYSICS_TIMELINE = [
  { id: 0, name: "1. Intro", status: "completed", dur: "6.2s" },
  { id: 1, name: "2. Voltage", status: "current", dur: "7.9s" },
  { id: 2, name: "3. Current", status: "upcoming", dur: "8.4s" },
  { id: 3, name: "4. Resistance", status: "upcoming", dur: "7.6s" },
  { id: 4, name: "5. Formula", status: "upcoming", dur: "9.9s" },
  { id: 5, name: "6. Circuit Ex", status: "upcoming", dur: "7.7s" },
];

const ML_TIMELINE = [
  { id: 0, name: "1. Intro", status: "completed", dur: "8.2s" },
  { id: 1, name: "2. Loss J(w)", status: "current", dur: "9.4s" },
  { id: 2, name: "3. Step (α)", status: "upcoming", dur: "9.7s" },
  { id: 3, name: "4. Gradient", status: "upcoming", dur: "9.4s" },
  { id: 4, name: "5. Update", status: "upcoming", dur: "8.3s" },
  { id: 5, name: "6. Converge", status: "upcoming", dur: "8.1s" },
];

const stateFlow = ["TEACH", "QUESTION", "EVALUATE", "ADAPT", "ASSESS"] as const;

export default function LessonPlayer({ navigate, currentScreen }: Props) {
  const { profile, progress } = useLearner();
  const [playing, setPlaying] = useState(true);
  const [muted, setMuted] = useState(false);
  const [speed, setSpeed] = useState<"1x" | "1.25x" | "1.5x">("1x");
  const [captions, setCaptions] = useState(true);
  const [currentState] = useState<typeof stateFlow[number]>("TEACH");

  // Subject selector: "physics" or "machine-learning"
  const [selectedSubject, setSelectedSubject] = useState<"physics" | "machine-learning">("physics");

  // Segment index: default 0 (or from query param seg)
  const [segmentIndex, setSegmentIndex] = useState(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const s = params.get("seg");
      if (s) return Math.max(0, parseInt(s, 10));
    }
    return 0;
  });

  // Stage layout view mode: "split" | "video_only" | "whiteboard_only"
  const [stageView, setStageView] = useState<"split" | "video_only" | "whiteboard_only">("split");

  // Avatar & Pedagogical Teacher State
  const [teacherState, setTeacherState] = useState<TeacherState>("INTRODUCING");
  const [visualMode, setVisualMode] = useState<SubjectVisualMode>("physics_circuit");
  const [currentTimeSec, setCurrentTimeSec] = useState(0);
  const [totalDurationSec, setTotalDurationSec] = useState(7.58);

  // Live Doubt Interruption State
  const [doubtModalOpen, setDoubtModalOpen] = useState(false);
  const [pausedTimestamp, setPausedTimestamp] = useState(0);
  const [savedSegmentBeforeDoubt, setSavedSegmentBeforeDoubt] = useState(0);
  const [teacherExplanationNotice, setTeacherExplanationNotice] = useState<string | null>(null);

  const currentSegments = selectedSubject === "machine-learning" ? ML_DEMO_SEGMENTS : PHYSICS_DEMO_SEGMENTS;
  const currentTimeline = selectedSubject === "machine-learning" ? ML_TIMELINE : PHYSICS_TIMELINE;
  const activeSegment = currentSegments[segmentIndex] || currentSegments[0];

  // Sync teacher state when segment changes
  useEffect(() => {
    if (activeSegment) {
      setTeacherState(activeSegment.teacherState);
    }
  }, [segmentIndex, selectedSubject]);

  // Handle Subject Switch
  const handleSwitchSubject = (subj: "physics" | "machine-learning") => {
    setSelectedSubject(subj);
    setVisualMode(subj === "machine-learning" ? "ml_gradient_descent" : "physics_circuit");
    setSegmentIndex(0);
    setCurrentTimeSec(0);
  };

  // Handle Doubt Interruption
  const handleTriggerDoubt = () => {
    setPlaying(false);
    setTeacherState("LISTENING");
    setPausedTimestamp(currentTimeSec);
    setSavedSegmentBeforeDoubt(segmentIndex);
    setDoubtModalOpen(true);
  };

  // Handle Resume Lesson
  const handleResumeLesson = () => {
    setDoubtModalOpen(false);
    setTeacherState("EXPLAINING");
    setPlaying(true);
  };

  // Pedagogical Controls
  const handleSimplerExplanation = () => {
    setTeacherState("THINKING");
    setTeacherExplanationNotice(
      selectedSubject === "physics"
        ? "Adapting explanation: Using intuitive water pipe hydraulic analogy."
        : "Adapting explanation: Using intuitive rolling ball on a curved valley floor."
    );
    setTimeout(() => {
      setTeacherState("EXPLAINING");
    }, 1200);
  };

  const handleAnotherExample = () => {
    setTeacherState("THINKING");
    setTeacherExplanationNotice(
      selectedSubject === "physics"
        ? "Generating practical example: Incandescent filament heating and tungsten resistivity."
        : "Generating practical example: Linear regression fitting on housing prices dataset."
    );
    setTimeout(() => {
      setSegmentIndex(5); // Example segment
      setTeacherState("EXPLAINING");
    }, 1200);
  };

  const handleShowVisually = () => {
    setTeacherState("POINTING");
    setTeacherExplanationNotice(
      selectedSubject === "physics"
        ? "Directing focus to whiteboard circuit schematic and I = V / R derivation."
        : "Directing focus to 3D loss surface bowl and negative gradient direction."
    );
    setSegmentIndex(4); // Formula / update rule segment
  };

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="flex flex-col min-h-screen bg-[#F9F8F5]">
        {/* Top Context & Subject Switcher Header */}
        <div className="bg-white border-b border-[#E6E4DC] px-4 sm:px-6 py-2.5 flex flex-wrap items-center justify-between gap-3">
          {/* Breadcrumb Context */}
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-[#0D3B2E]">
              {selectedSubject === "physics" ? "Physics (PH101)" : "Machine Learning (CS229)"}
            </span>
            <span className="text-[#9CA3AF]">›</span>
            <span className="text-[#5E6D67]">
              {selectedSubject === "physics" ? "Ohm's Law" : "Gradient Descent"}
            </span>
            <span className="text-[#9CA3AF]">›</span>
            <span className="font-bold text-[#059669] bg-[#ECFDF5] px-2 py-0.5 rounded-md">
              {activeSegment.title}
            </span>
          </div>

          {/* Subject Switcher Buttons */}
          <div className="flex items-center gap-2">
            <div className="flex items-center bg-[#F5F4EE] p-1 rounded-xl border border-[#E6E4DC] text-xs font-bold shadow-2xs">
              <button
                onClick={() => handleSwitchSubject("physics")}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
                  selectedSubject === "physics"
                    ? "bg-[#0D3B2E] text-white shadow-xs"
                    : "text-[#5E6D67] hover:text-[#0D3B2E]"
                }`}
              >
                <span>⚡</span>
                <span>Physics: Ohm's Law</span>
              </button>
              <button
                onClick={() => handleSwitchSubject("machine-learning")}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
                  selectedSubject === "machine-learning"
                    ? "bg-[#0D3B2E] text-white shadow-xs"
                    : "text-[#5E6D67] hover:text-[#0D3B2E]"
                }`}
              >
                <span>🧠</span>
                <span>ML: Gradient Descent</span>
              </button>
            </div>

            {/* Stage View Toggle */}
            <div className="flex items-center bg-[#F5F4EE] p-0.5 rounded-lg border border-[#E6E4DC] text-[10px] font-bold">
              <button
                onClick={() => setStageView("split")}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  stageView === "split"
                    ? "bg-[#0D3B2E] text-white shadow-xs"
                    : "text-[#5E6D67] hover:text-[#0D3B2E]"
                }`}
                title="Split Stage: Professor Video + Interactive Whiteboard"
              >
                Split Stage
              </button>
              <button
                onClick={() => setStageView("video_only")}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  stageView === "video_only"
                    ? "bg-[#0D3B2E] text-white shadow-xs"
                    : "text-[#5E6D67] hover:text-[#0D3B2E]"
                }`}
                title="Full Professor Video"
              >
                Professor Video
              </button>
              <button
                onClick={() => setStageView("whiteboard_only")}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  stageView === "whiteboard_only"
                    ? "bg-[#0D3B2E] text-white shadow-xs"
                    : "text-[#5E6D67] hover:text-[#0D3B2E]"
                }`}
                title="Full Whiteboard View"
              >
                Whiteboard
              </button>
            </div>

            {/* Cognitive Pipeline Steps */}
            <div className="hidden sm:flex items-center gap-1 overflow-x-auto">
              {stateFlow.map((s) => {
                const isActive = s === currentState;
                return (
                  <div
                    key={s}
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold transition-all ${
                      isActive
                        ? "bg-[#0D3B2E] text-white shadow-xs"
                        : "bg-[#F5F4EE] text-[#5E6D67]"
                    }`}
                  >
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />}
                    <span>{s}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Notice Banner */}
        {teacherExplanationNotice && (
          <div className="bg-[#ECFDF5] border-b border-[#A7F3D0] px-6 py-2 flex items-center justify-between text-xs text-[#065F46]">
            <span>💡 <strong>Pedagogical Action:</strong> {teacherExplanationNotice}</span>
            <button
              onClick={() => setTeacherExplanationNotice(null)}
              className="text-[#065F46] hover:text-black ml-4 font-bold"
            >
              ✕
            </button>
          </div>
        )}

        {/* Main Stage: Dedicated Media & Whiteboard Area */}
        <div className="flex-1 flex flex-col bg-[#07221A] p-3 sm:p-5 lg:p-6 w-full">
          <div className="max-w-7xl w-full mx-auto flex-1 flex flex-col justify-between">
            {/* Split Stage or Single View */}
            <div className="flex-1 mb-4">
              {stageView === "split" && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-stretch">
                  {/* Left Column: Photorealistic Male AI Professor Video Player */}
                  <div className="teacher-video-container flex flex-col h-full min-h-[380px] sm:min-h-[440px]">
                    <TeacherVideoPlayer
                      segments={currentSegments}
                      segmentIndex={segmentIndex}
                      onSegmentChange={(idx) => setSegmentIndex(idx)}
                      teacherState={teacherState}
                      onStateChange={(st) => setTeacherState(st)}
                      isPlaying={playing && !doubtModalOpen}
                      onPlayPause={(p) => setPlaying(p)}
                      speed={speed}
                      onSpeedChange={(s) => setSpeed(s)}
                      isMuted={muted}
                      onMuteToggle={() => setMuted(!muted)}
                      showCaptions={captions}
                      onToggleCaptions={() => setCaptions(!captions)}
                      onAskDoubt={handleTriggerDoubt}
                      onTimeUpdate={(c, d) => {
                        setCurrentTimeSec(c);
                        setTotalDurationSec(d);
                      }}
                    />
                  </div>

                  {/* Right Column: Subject-Aware Interactive Whiteboard */}
                  <div className="flex flex-col h-full min-h-[380px] sm:min-h-[440px]">
                    <VisualWhiteboard
                      mode={visualMode}
                      onModeChange={(m) => setVisualMode(m)}
                      isStreaming={playing && !doubtModalOpen}
                      currentTime={currentTimeSec}
                      duration={totalDurationSec}
                      activeTitle={activeSegment.title}
                      latexFormula={
                        selectedSubject === "machine-learning"
                          ? "w_{t+1} = w_t - α · ∇J(w_t)"
                          : `I = V / R = ${activeSegment.whiteboardData?.voltage || 9}V / ${activeSegment.whiteboardData?.resistance || 3}Ω = ${activeSegment.whiteboardData?.current || 3}A`
                      }
                      ragCitation={
                        selectedSubject === "machine-learning"
                          ? "Goodfellow, Bengio & Courville, Deep Learning (MIT Press), Ch. 4.3"
                          : "Halliday, Resnick & Walker, Fundamentals of Physics (10th ed.), Ch. 26"
                      }
                      doubtPaused={doubtModalOpen}
                    />
                  </div>
                </div>
              )}

              {stageView === "video_only" && (
                <div className="h-full min-h-[480px] max-w-4xl mx-auto">
                  <TeacherVideoPlayer
                    segments={currentSegments}
                    segmentIndex={segmentIndex}
                    onSegmentChange={(idx) => setSegmentIndex(idx)}
                    teacherState={teacherState}
                    onStateChange={(st) => setTeacherState(st)}
                    isPlaying={playing && !doubtModalOpen}
                    onPlayPause={(p) => setPlaying(p)}
                    speed={speed}
                    onSpeedChange={(s) => setSpeed(s)}
                    isMuted={muted}
                    onMuteToggle={() => setMuted(!muted)}
                    showCaptions={captions}
                    onToggleCaptions={() => setCaptions(!captions)}
                    onAskDoubt={handleTriggerDoubt}
                    onTimeUpdate={(c, d) => {
                      setCurrentTimeSec(c);
                      setTotalDurationSec(d);
                    }}
                  />
                </div>
              )}

              {stageView === "whiteboard_only" && (
                <div className="h-full min-h-[480px] max-w-4xl mx-auto">
                  <VisualWhiteboard
                    mode={visualMode}
                    onModeChange={(m) => setVisualMode(m)}
                    isStreaming={playing && !doubtModalOpen}
                    currentTime={currentTimeSec}
                    duration={totalDurationSec}
                    activeTitle={activeSegment.title}
                    latexFormula={
                      selectedSubject === "machine-learning"
                        ? "w_{t+1} = w_t - α · ∇J(w_t)"
                        : `I = V / R = ${activeSegment.whiteboardData?.voltage || 9}V / ${activeSegment.whiteboardData?.resistance || 3}Ω = ${activeSegment.whiteboardData?.current || 3}A`
                    }
                    ragCitation={
                      selectedSubject === "machine-learning"
                        ? "Goodfellow, Bengio & Courville, Deep Learning (MIT Press), Ch. 4.3"
                        : "Halliday, Resnick & Walker, Fundamentals of Physics (10th ed.), Ch. 26"
                    }
                    doubtPaused={doubtModalOpen}
                  />
                </div>
              )}
            </div>

            {/* Stage Footer: Pedagogical Actions Bar */}
            <div className="bg-[#03120E] rounded-xl border border-white/10 px-4 py-3 flex flex-wrap items-center justify-between gap-3 text-white">
              {/* Pedagogical Control Shortcuts: Play | Ask Doubt | Simpler | Example | Checkpoint */}
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => setPlaying(!playing)}
                  className="px-3.5 py-1.5 rounded-lg bg-[#10B981] hover:bg-[#059669] text-[#07221A] text-xs font-bold transition-all cursor-pointer shadow-xs active:scale-95 flex items-center gap-1.5"
                  title={playing ? "Pause Lesson" : "Play Lesson"}
                >
                  <span>{playing ? "⏸" : "▶"}</span>
                  <span>{playing ? "Pause" : "Play"}</span>
                </button>
                <button
                  onClick={handleTriggerDoubt}
                  className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-all cursor-pointer shadow-xs active:scale-95 flex items-center gap-1.5 animate-pulse"
                  title="Interrupt lesson to ask a doubt"
                >
                  <span>✋</span>
                  <span>Ask Doubt</span>
                </button>
                <button
                  onClick={handleSimplerExplanation}
                  className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold transition-all cursor-pointer shadow-xs active:scale-95 flex items-center gap-1"
                  title="Explain in simpler terms with analogy"
                >
                  <span>💡</span>
                  <span>Simpler</span>
                </button>
                <button
                  onClick={handleAnotherExample}
                  className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold transition-all cursor-pointer shadow-xs active:scale-95 flex items-center gap-1"
                  title="Provide another worked example"
                >
                  <span>🔍</span>
                  <span>Example</span>
                </button>
                <button
                  onClick={() => navigate("question")}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 border border-amber-500/50 text-amber-300 hover:bg-amber-500/30 text-xs font-bold transition-all cursor-pointer shadow-xs active:scale-95 flex items-center gap-1"
                  title="Jump to checkpoint question"
                >
                  <span>⚡</span>
                  <span>Checkpoint</span>
                </button>
              </div>

              {/* Source Grounding Tag */}
              <div className="text-[10px] text-[#A7F3D0]/90 bg-white/5 px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-1.5">
                <span>📄 Grounded in:</span>
                <span className="font-semibold text-white">
                  {selectedSubject === "machine-learning"
                    ? "CIT Machine Learning (AD5305) & Goodfellow Ch. 4.3"
                    : "Fundamentals of Physics (Walker, Halliday, Resnick) Ch. 26"}
                </span>
              </div>
            </div>

            {/* Bottom Timeline */}
            <div className="bg-white rounded-xl border border-[#E6E4DC] px-4 py-3 mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-[#0D3B2E] uppercase tracking-wider">
                  {selectedSubject === "physics"
                    ? "Ohm's Law Master Lecture Trajectory (6 Core Segments)"
                    : "Gradient Descent Optimization Trajectory (6 Core Segments)"}
                </span>
                <span className="text-[10px] text-[#5E6D67]">Click any segment to jump</span>
              </div>
              <div className="flex gap-2 overflow-x-auto pb-1">
                {currentTimeline.map((t) => {
                  const isCurrent = t.id === segmentIndex;
                  return (
                    <button
                      key={t.id}
                      onClick={() => {
                        setSegmentIndex(t.id);
                        setCurrentTimeSec(0);
                      }}
                      className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-xs shrink-0 transition-all cursor-pointer ${
                        isCurrent
                          ? "bg-[#0D3B2E] border-[#0D3B2E] text-white font-bold shadow-xs scale-102"
                          : t.id < segmentIndex
                          ? "bg-[#ECFDF5] border-[#BBF7D0] text-[#059669]"
                          : "bg-[#F9F8F5] border-[#E6E4DC] text-[#5E6D67] hover:bg-white"
                      }`}
                    >
                      {t.id < segmentIndex && <span>✓</span>}
                      <span>{t.name}</span>
                      <span className="opacity-70 text-[10px]">{t.dur}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Docked Lesson Intelligence & Telemetry Section */}
            <div className="mt-4 bg-white rounded-2xl border border-[#E6E4DC] p-5 shadow-xs">
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#F5F4EE]">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#10B981] animate-pulse" />
                  <span className="text-xs font-bold text-[#0D3B2E] uppercase tracking-wide">
                    Live Pedagogical Telemetry & Cognitive State
                  </span>
                </div>
                <div className="text-[10px] text-[#5E6D67] font-medium">
                  Real-time synchronization between Teacher Harness, RAG, and Whiteboard
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Col 1: Professor Profile */}
                <div className="rounded-xl p-3.5 bg-[#F9F8F5] border border-[#E6E4DC] flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl overflow-hidden border border-[#10B981]/50 shrink-0">
                    <img
                      src="/teacher/male_professor_01.jpg"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = "/static/teacher/male_professor_01.jpg";
                      }}
                      alt="Prof. Richard Davies"
                      className="w-full h-full object-cover object-top"
                    />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-[#0D3B2E]">Prof. Richard Davies, Ph.D.</div>
                    <div className="text-[10px] text-[#059669] font-medium">
                      Photorealistic Adult Male Professor
                    </div>
                    <div className="text-[9px] text-[#5E6D67]">
                      Natural Male Voice · Viseme Synchronized
                    </div>
                  </div>
                </div>

                {/* Col 2: Active Cognitive State */}
                <div className="rounded-xl p-3.5 bg-[#ECFDF5] border border-[#BBF7D0]">
                  <div className="text-[10px] font-bold text-[#059669] mb-0.5">ACTIVE COGNITIVE STATE</div>
                  <div className="text-sm font-bold text-[#0D3B2E]">{teacherState}</div>
                  <div className="text-[10px] text-[#5E6D67] mt-0.5">
                    {teacherState === "INTRODUCING"
                      ? "Welcoming class and establishing baseline electrical concepts."
                      : teacherState === "EXPLAINING"
                      ? "Explaining resistance and electron collision physics."
                      : teacherState === "POINTING"
                      ? "Highlighting the fundamental relationship formula I = V / R."
                      : teacherState === "THINKING"
                      ? "Formulating an intuitive real-world hydraulic analogy."
                      : teacherState === "ASKING"
                      ? "Presenting diagnostic checkpoint question to assess mastery."
                      : teacherState === "LISTENING"
                      ? "Listening attentively to student doubt question."
                      : "Active educational interaction."}
                  </div>
                </div>

                {/* Col 3: Checkpoint Action */}
                <div className="rounded-xl p-3.5 bg-[#FEF3C7] border border-[#FDE68A] flex flex-col justify-between">
                  <div>
                    <div className="text-[10px] font-bold text-[#D97706] mb-0.5">⚡ CHECKPOINT READY</div>
                    <div className="text-xs text-[#0F172A] font-medium">
                      Test Ohm's Law comprehension with conceptual question
                    </div>
                  </div>
                  <button
                    onClick={() => navigate("question")}
                    className="mt-2 py-2 px-3 rounded-lg text-xs font-bold text-[#07221A] bg-[#10B981] hover:bg-[#059669] transition-all shadow-xs cursor-pointer text-center"
                  >
                    Take Checkpoint Question →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Doubt Interruption Modal */}
        <DoubtInterruptionModal
          isOpen={doubtModalOpen}
          onClose={() => setDoubtModalOpen(false)}
          pausedTimestampSeconds={pausedTimestamp}
          currentConcept={activeSegment.title}
          onResumeLesson={handleResumeLesson}
          onAnswerResolved={(doubt, answer) => {
            setTeacherExplanationNotice(`Resolved Doubt: "${doubt.slice(0, 45)}..."`);
            // Switch to Segment 5 (Doubt Response) where Prof. Davies explains!
            setSegmentIndex(5);
            setTeacherState("EXPLAINING");
            setPlaying(true);
          }}
        />
      </div>
    </AppShell>
  );
}
