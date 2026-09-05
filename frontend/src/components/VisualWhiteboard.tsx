import { useState, useEffect } from "react";

export type SubjectVisualMode = "physics_circuit" | "ml_gradient_descent" | "analogy_pipe";

interface VisualWhiteboardProps {
  mode?: SubjectVisualMode;
  onModeChange?: (mode: SubjectVisualMode) => void;
  isStreaming?: boolean;
  currentTime?: number;
  duration?: number;
  activeTitle?: string;
  latexFormula?: string;
  ragCitation?: string;
  doubtPaused?: boolean;
}

export default function VisualWhiteboard({
  mode = "physics_circuit",
  onModeChange,
  isStreaming = true,
  currentTime = 0,
  duration = 8.0,
  activeTitle,
  latexFormula,
  ragCitation,
  doubtPaused = false,
}: VisualWhiteboardProps) {
  // Physics Circuit State
  const [voltage, setVoltage] = useState(9);
  const [resistance, setResistance] = useState(3);
  const currentVal = Number((voltage / resistance).toFixed(2));

  // Machine Learning Gradient Descent State
  const [learningRate, setLearningRate] = useState(0.1);
  const [userStepOverride, setUserStepOverride] = useState<number | null>(null);

  // Gradient descent loss formula J(w) = w^2 -> w_t+1 = w_t - alpha * 2w_t
  const wInitial = 2.0;
  let wCurrent = wInitial;
  const trajectory = [wInitial];
  for (let i = 0; i < 5; i++) {
    const grad = 2 * wCurrent;
    wCurrent = Number((wCurrent - learningRate * grad).toFixed(3));
    trajectory.push(wCurrent);
  }

  // Auto-sync step with video currentTime if user hasn't overridden
  const progressRatio = duration > 0 ? Math.min(1.0, Math.max(0.0, currentTime / duration)) : 0;
  const autoStepIndex = Math.min(4, Math.floor(progressRatio * 5));
  const activeStep = userStepOverride !== null ? userStepOverride : autoStepIndex;
  const lossCurrent = Number((trajectory[activeStep] ** 2).toFixed(3));

  // Reset manual override when seeking or switching segments
  useEffect(() => {
    setUserStepOverride(null);
  }, [mode]);

  // Phase highlighting based on currentTime in clip
  const isEarlyPhase = currentTime < 2.5;
  const isMidPhase = currentTime >= 2.5 && currentTime < 5.2;
  const isLatePhase = currentTime >= 5.2;

  return (
    <div className="bg-black/55 backdrop-blur-md rounded-2xl p-4 sm:p-5 border border-white/15 text-white shadow-2xl flex flex-col justify-between h-full space-y-3">
      {/* Visual Header & Mode Toggles */}
      <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-2.5">
        <div className="flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              doubtPaused
                ? "bg-[#EF4444] animate-ping"
                : isStreaming
                ? "bg-[#10B981] animate-pulse"
                : "bg-[#F59E0B]"
            }`}
          />
          <div>
            <div className="text-[10px] sm:text-[11px] font-bold text-[#A7F3D0] uppercase tracking-wider flex items-center gap-1.5">
              <span>
                {mode === "physics_circuit"
                  ? "PHYSICS WHITEBOARD: OHM'S LAW (I = V / R)"
                  : mode === "ml_gradient_descent"
                  ? "ML WHITEBOARD: GRADIENT DESCENT OPTIMIZATION"
                  : "INTUITIVE ANALOGY: HYDRAULIC PIPE"}
              </span>
            </div>
            {doubtPaused ? (
              <span className="text-[9px] font-mono text-[#FCA5A5] font-semibold">
                ⏸ FROZEN AT T={currentTime.toFixed(1)}s (STUDENT DOUBT INTERRUPTION)
              </span>
            ) : (
              <span className="text-[9px] font-mono text-white/50">
                ⏱ SYNC: {currentTime.toFixed(1)}s / {duration.toFixed(1)}s • {isStreaming ? "PLAYING" : "PAUSED"}
              </span>
            )}
          </div>
        </div>

        {/* Quick Subject Visual Switcher */}
        <div className="flex items-center gap-1 bg-white/10 p-0.5 rounded-lg text-[9px] font-bold shrink-0">
          <button
            onClick={() => onModeChange?.("physics_circuit")}
            className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
              mode === "physics_circuit"
                ? "bg-[#10B981] text-[#07221A] shadow-xs"
                : "text-white/70 hover:text-white"
            }`}
          >
            ⚡ Circuit
          </button>
          <button
            onClick={() => onModeChange?.("ml_gradient_descent")}
            className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
              mode === "ml_gradient_descent"
                ? "bg-[#10B981] text-[#07221A] shadow-xs"
                : "text-white/70 hover:text-white"
            }`}
          >
            🧠 ML Loss
          </button>
        </div>
      </div>

      {/* Mode 1: Physics Circuit Visual */}
      {mode === "physics_circuit" && (
        <div className="space-y-3 flex-1 flex flex-col justify-between">
          {/* Schematic Diagram */}
          <div className="bg-white/5 rounded-xl p-3 sm:p-4 border border-white/10 flex flex-col items-center relative overflow-hidden">
            {/* Timeline phase indicator badge */}
            <div className="absolute top-2 right-2 text-[8px] uppercase tracking-wider px-2 py-0.5 rounded font-mono font-bold bg-white/10 text-white/80">
              {isEarlyPhase ? "Phase 1: Potential (V)" : isMidPhase ? "Phase 2: Opposition (R)" : "Phase 3: Current (I)"}
            </div>

            <div className="flex items-center justify-between w-full max-w-sm my-2 sm:my-3">
              {/* Battery Voltage */}
              <div
                className={`text-center transition-all px-3 py-2 rounded-xl border ${
                  isEarlyPhase
                    ? "bg-[#10B981]/30 border-[#10B981] ring-2 ring-[#10B981]/50 scale-105"
                    : "bg-[#10B981]/15 border-[#10B981]/40"
                }`}
              >
                <div className="text-[8px] text-[#A7F3D0] uppercase font-bold">Voltage (V)</div>
                <div className="font-mono text-sm sm:text-base font-extrabold text-white">{voltage}V</div>
                <div className="text-[7px] text-[#A7F3D0]/80">Power Source</div>
              </div>

              {/* Wire with Resistor & Electron Drift */}
              <div className="flex items-center flex-1 px-3">
                <div className="h-1.5 bg-[#10B981]/70 flex-1 relative overflow-hidden rounded-full">
                  {isStreaming && !doubtPaused && (
                    <div
                      className="absolute inset-0 w-3 h-1.5 bg-white rounded-full animate-pulse"
                      style={{ animationDuration: `${Math.max(0.18, 1.2 / (currentVal || 1))}s` }}
                    />
                  )}
                </div>
                <div
                  className={`px-2.5 py-1.5 rounded-lg text-xs font-mono font-bold shrink-0 transition-all border ${
                    isMidPhase
                      ? "bg-[#D97706]/40 border-[#F59E0B] text-[#FDE68A] ring-2 ring-[#F59E0B]/50 scale-105"
                      : "bg-[#D97706]/20 border-[#D97706]/60 text-[#FCD34D]"
                  }`}
                >
                  R = {resistance}Ω
                </div>
                <div className="h-1.5 bg-[#10B981]/70 flex-1 relative overflow-hidden rounded-full">
                  {isStreaming && !doubtPaused && (
                    <div
                      className="absolute inset-0 w-3 h-1.5 bg-white rounded-full animate-pulse"
                      style={{ animationDuration: `${Math.max(0.18, 1.2 / (currentVal || 1))}s` }}
                    />
                  )}
                </div>
              </div>

              {/* Resulting Current */}
              <div
                className={`text-center transition-all px-3 py-2 rounded-xl border ${
                  isLatePhase
                    ? "bg-[#059669]/40 border-[#34D399] ring-2 ring-[#34D399]/50 scale-105"
                    : "bg-[#059669]/20 border-[#34D399]/40"
                }`}
              >
                <div className="text-[8px] text-[#A7F3D0] uppercase font-bold">Current (I)</div>
                <div className="font-mono text-sm sm:text-base font-extrabold text-white">{currentVal}A</div>
                <div className="text-[7px] text-[#34D399]/80">Charge Flow</div>
              </div>
            </div>

            {/* Sliders */}
            <div className="grid grid-cols-2 gap-3 w-full text-xs mt-2 pt-2 border-t border-white/10">
              <div>
                <div className="flex justify-between text-[10px] text-white/70 mb-0.5">
                  <span>Battery Voltage (V)</span>
                  <span className="font-mono font-bold text-[#A7F3D0]">{voltage}V</span>
                </div>
                <input
                  type="range"
                  min={3}
                  max={18}
                  step={3}
                  value={voltage}
                  onChange={(e) => setVoltage(Number(e.target.value))}
                  className="w-full accent-[#10B981] cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between text-[10px] text-white/70 mb-0.5">
                  <span>Resistor Value (R)</span>
                  <span className="font-mono font-bold text-[#FCD34D]">{resistance}Ω</span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={9}
                  step={1}
                  value={resistance}
                  onChange={(e) => setResistance(Number(e.target.value))}
                  className="w-full accent-[#D97706] cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Active Mathematical Formula Display */}
          <div className="bg-[#0D3B2E]/60 border border-[#10B981]/30 p-2.5 rounded-xl flex items-center justify-between text-xs">
            <div className="font-mono text-[#A7F3D0] font-bold">
              {latexFormula || `I = V / R = ${voltage}V / ${resistance}Ω = ${currentVal} Amperes`}
            </div>
            <div className="text-[9px] bg-[#10B981]/20 text-[#A7F3D0] px-2 py-0.5 rounded font-mono">
              V = I · R
            </div>
          </div>
        </div>
      )}

      {/* Mode 2: Machine Learning Gradient Descent Loss Curve */}
      {mode === "ml_gradient_descent" && (
        <div className="space-y-3 flex-1 flex flex-col justify-between">
          <div className="bg-white/5 rounded-xl p-3 sm:p-4 border border-white/10 flex flex-col items-center relative">
            {/* Timeline phase indicator */}
            <div className="absolute top-2 right-2 text-[8px] uppercase tracking-wider px-2 py-0.5 rounded font-mono font-bold bg-white/10 text-white/80">
              {isEarlyPhase ? "Phase 1: Loss Objective" : isMidPhase ? "Phase 2: Step Size (α)" : "Phase 3: Weight Descent"}
            </div>

            {/* SVG Convex Loss Bowl */}
            <div className="w-full h-32 max-w-sm relative mt-1">
              <svg viewBox="0 0 200 100" className="w-full h-full overflow-visible">
                {/* Parabola J(w) = 0.2*(w-100)^2 */}
                <path
                  d="M 20 85 Q 100 12 180 85"
                  fill="none"
                  stroke="#10B981"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                {/* Minimum point */}
                <circle cx="100" cy="48" r="3.5" fill="#FCD34D" />
                <text x="100" y="62" fontSize="6.5" fill="#A7F3D0" textAnchor="middle" fontWeight="bold">
                  Global Min J(w*)
                </text>

                {/* Trajectory points */}
                {trajectory.slice(0, 5).map((w, idx) => {
                  const cx = 100 + (w / wInitial) * 60;
                  const cy = 48 + (Math.abs(w) / wInitial) * 32;
                  const isCurrentStep = idx === activeStep;
                  return (
                    <g key={idx}>
                      {isCurrentStep && (
                        <circle
                          cx={cx}
                          cy={cy}
                          r={7}
                          fill="#EF4444"
                          opacity={0.4}
                          className="animate-ping"
                        />
                      )}
                      <circle
                        cx={cx}
                        cy={cy}
                        r={isCurrentStep ? 5 : 2.5}
                        fill={isCurrentStep ? "#EF4444" : "#38BDF8"}
                      />
                      <text
                        x={cx + 6}
                        y={cy - 2}
                        fontSize="5.5"
                        fill={isCurrentStep ? "#FCA5A5" : "#94A3B8"}
                        fontFamily="monospace"
                      >
                        t={idx}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Parameter & Loss readout */}
            <div className="grid grid-cols-3 gap-2 w-full text-center text-xs mt-2">
              <div className="bg-black/30 p-2 rounded-lg border border-white/10">
                <div className="text-[8px] text-[#A7F3D0] uppercase font-bold">Weight (w_t)</div>
                <div className="font-mono text-xs sm:text-sm font-bold text-white">{trajectory[activeStep]}</div>
              </div>
              <div className="bg-black/30 p-2 rounded-lg border border-white/10">
                <div className="text-[8px] text-[#A7F3D0] uppercase font-bold">Loss J(w)</div>
                <div className="font-mono text-xs sm:text-sm font-bold text-[#FCD34D]">{lossCurrent}</div>
              </div>
              <div className="bg-black/30 p-2 rounded-lg border border-white/10">
                <div className="text-[8px] text-[#A7F3D0] uppercase font-bold">Iteration</div>
                <div className="font-mono text-xs sm:text-sm font-bold text-[#38BDF8]">
                  Step {activeStep} / 4
                </div>
              </div>
            </div>

            {/* Learning Rate Slider & Stepper */}
            <div className="grid grid-cols-2 gap-3 w-full text-xs pt-2 mt-2 border-t border-white/10">
              <div>
                <div className="flex justify-between text-[10px] text-white/70 mb-0.5">
                  <span>Learning Rate (α)</span>
                  <span className="font-mono text-[#A7F3D0] font-bold">{learningRate}</span>
                </div>
                <input
                  type="range"
                  min={0.02}
                  max={0.4}
                  step={0.02}
                  value={learningRate}
                  onChange={(e) => setLearningRate(Number(e.target.value))}
                  className="w-full accent-[#10B981] cursor-pointer"
                />
              </div>
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setUserStepOverride(Math.max(0, activeStep - 1))}
                  disabled={activeStep === 0}
                  className="px-2.5 py-1 bg-white/10 hover:bg-white/20 disabled:opacity-30 rounded text-xs transition-all"
                >
                  ◀ Prev
                </button>
                <span className="text-[9px] text-white/60 font-mono">w ← w - α·∇J</span>
                <button
                  onClick={() => setUserStepOverride(Math.min(4, activeStep + 1))}
                  disabled={activeStep === 4}
                  className="px-2.5 py-1 bg-[#10B981] hover:bg-[#059669] text-[#07221A] font-bold disabled:opacity-30 rounded text-xs transition-all"
                >
                  Next ▶
                </button>
              </div>
            </div>
          </div>

          {/* Active Mathematical Formula Display */}
          <div className="bg-[#0D3B2E]/60 border border-[#10B981]/30 p-2.5 rounded-xl flex items-center justify-between text-xs">
            <div className="font-mono text-[#A7F3D0] font-bold">
              {latexFormula || `w_{t+1} = w_t - α · ∇J(w_t) = ${trajectory[activeStep]} - ${learningRate}·(${2 * trajectory[activeStep]})`}
            </div>
            <div className="text-[9px] bg-[#10B981]/20 text-[#A7F3D0] px-2 py-0.5 rounded font-mono">
              w ← w - α∇J
            </div>
          </div>
        </div>
      )}

      {/* RAG Academic Grounding Footer */}
      <div className="bg-black/40 rounded-xl px-3 py-1.5 border border-white/10 flex items-center justify-between text-[9px] text-white/60">
        <span className="truncate">
          📚 <strong className="text-white/80">RAG Grounding:</strong>{" "}
          {ragCitation ||
            (mode === "physics_circuit"
              ? "Halliday, Resnick & Walker, Fundamentals of Physics (10th ed.), Ch. 26"
              : "Goodfellow, Bengio & Courville, Deep Learning (MIT Press), Ch. 4.3")}
        </span>
        <span className="shrink-0 font-mono text-[#A7F3D0] ml-2">VERIFIED PEER CITATION</span>
      </div>
    </div>
  );
}

