import React, { useEffect, useRef, useState } from "react";

export type TeacherState =
  | "INTRODUCING"
  | "EXPLAINING"
  | "POINTING"
  | "THINKING"
  | "ASKING"
  | "LISTENING"
  | "EVALUATING"
  | "CORRECTING"
  | "ENCOURAGING"
  | "CELEBRATING";

export interface TeachingSegment {
  id: string;
  title: string;
  teacherState: TeacherState;
  duration: number;
  videoUrl: string;
  audioUrl: string;
  script: string;
  whiteboardData?: {
    voltage?: number;
    resistance?: number;
    current?: number;
    learningRate?: number;
    stepIndex?: number;
    weight?: number;
    loss?: number;
    highlight?: string;
  };
}

export const PHYSICS_DEMO_SEGMENTS: TeachingSegment[] = [
  {
    id: "seg_01_intro",
    title: "Welcome & Electric Potential",
    teacherState: "INTRODUCING",
    duration: 6.2,
    videoUrl: "/static/teacher-avatar/generated/physics/seg_01_intro.mp4",
    audioUrl: "/static/teacher-avatar/generated/physics/seg_01_intro.wav",
    script:
      "Good morning class. Today we will explore Ohm's Law, which forms the cornerstone of circuit theory.",
    whiteboardData: { voltage: 9, resistance: 3, current: 3, highlight: "voltage" },
  },
  {
    id: "seg_02_voltage",
    title: "Understanding Voltage (Potential Difference)",
    teacherState: "EXPLAINING",
    duration: 7.87,
    videoUrl: "/static/teacher-avatar/generated/physics/seg_02_voltage.mp4",
    audioUrl: "/static/teacher-avatar/generated/physics/seg_02_voltage.wav",
    script:
      "Voltage, or electric potential difference, is the electrical pressure from a power source that pushes electrons through a conducting loop.",
    whiteboardData: { voltage: 12, resistance: 3, current: 4, highlight: "voltage" },
  },
  {
    id: "seg_03_current",
    title: "Understanding Current (Flow of Charge)",
    teacherState: "EXPLAINING",
    duration: 8.41,
    videoUrl: "/static/teacher-avatar/generated/physics/seg_03_current.mp4",
    audioUrl: "/static/teacher-avatar/generated/physics/seg_03_current.wav",
    script:
      "Current is the rate at which electric charge flows past a point in a circuit, measured in amperes, where one ampere equals one coulomb per second.",
    whiteboardData: { voltage: 9, resistance: 3, current: 3, highlight: "current" },
  },
  {
    id: "seg_04_resistance",
    title: "Understanding Electrical Resistance",
    teacherState: "EXPLAINING",
    duration: 7.62,
    videoUrl: "/static/teacher-avatar/generated/physics/seg_04_resistance.mp4",
    audioUrl: "/static/teacher-avatar/generated/physics/seg_04_resistance.wav",
    script:
      "Resistance is the opposition to the flow of electrical charge. When electrons drift through a conductor, they collide with lattice ions.",
    whiteboardData: { voltage: 9, resistance: 6, current: 1.5, highlight: "resistance" },
  },
  {
    id: "seg_05_formula",
    title: "The Master Equation: I = V / R",
    teacherState: "POINTING",
    duration: 9.86,
    videoUrl: "/static/teacher-avatar/generated/physics/seg_05_formula.mp4",
    audioUrl: "/static/teacher-avatar/generated/physics/seg_05_formula.wav",
    script:
      "Using Ohm's Law, the current I in amperes equals voltage V divided by resistance R. Notice the direct proportionality to voltage and inverse relationship with resistance.",
    whiteboardData: { voltage: 9, resistance: 3, current: 3, highlight: "formula" },
  },
  {
    id: "seg_06_example",
    title: "Worked Numerical Circuit Example",
    teacherState: "EXPLAINING",
    duration: 7.69,
    videoUrl: "/static/teacher-avatar/generated/physics/seg_06_example.mp4",
    audioUrl: "/static/teacher-avatar/generated/physics/seg_06_example.wav",
    script:
      "For example, if our battery supplies nine volts across a three ohm resistor, the resulting current is exactly three amperes.",
    whiteboardData: { voltage: 9, resistance: 3, current: 3, highlight: "calculation" },
  },
];

export const ML_DEMO_SEGMENTS: TeachingSegment[] = [
  {
    id: "seg_01_intro",
    title: "Welcome & Optimization Foundations",
    teacherState: "INTRODUCING",
    duration: 8.18,
    videoUrl: "/static/teacher-avatar/generated/machine-learning/seg_01_intro.mp4",
    audioUrl: "/static/teacher-avatar/generated/machine-learning/seg_01_intro.wav",
    script:
      "Welcome back. Today we examine Gradient Descent, the foundational first-order optimization algorithm that powers modern machine learning.",
    whiteboardData: { learningRate: 0.1, stepIndex: 0, weight: 2.0, loss: 4.0, highlight: "loss_surface" },
  },
  {
    id: "seg_02_loss_surface",
    title: "The Objective & Loss Surface J(w)",
    teacherState: "EXPLAINING",
    duration: 9.42,
    videoUrl: "/static/teacher-avatar/generated/machine-learning/seg_02_loss_surface.mp4",
    audioUrl: "/static/teacher-avatar/generated/machine-learning/seg_02_loss_surface.wav",
    script:
      "Our objective is to minimize a loss function J of theta, which measures the difference between model predictions and true ground truth targets across parameter space.",
    whiteboardData: { learningRate: 0.1, stepIndex: 1, weight: 1.6, loss: 2.56, highlight: "loss_surface" },
  },
  {
    id: "seg_03_learning_rate",
    title: "Learning Rate (Step Size Alpha)",
    teacherState: "EXPLAINING",
    duration: 9.74,
    videoUrl: "/static/teacher-avatar/generated/machine-learning/seg_03_learning_rate.mp4",
    audioUrl: "/static/teacher-avatar/generated/machine-learning/seg_03_learning_rate.wav",
    script:
      "The learning rate alpha controls our step size. If alpha is too small, convergence takes forever; if too large, the updates will oscillate or diverge.",
    whiteboardData: { learningRate: 0.1, stepIndex: 2, weight: 1.28, loss: 1.64, highlight: "learning_rate" },
  },
  {
    id: "seg_04_gradient_direction",
    title: "Gradient Vector & Steepest Descent",
    teacherState: "POINTING",
    duration: 9.44,
    videoUrl: "/static/teacher-avatar/generated/machine-learning/seg_04_gradient_direction.mp4",
    audioUrl: "/static/teacher-avatar/generated/machine-learning/seg_04_gradient_direction.wav",
    script:
      "The gradient vector points in the direction of steepest ascent on the loss surface. Therefore, to minimize error, we take steps in the negative gradient direction.",
    whiteboardData: { learningRate: 0.1, stepIndex: 3, weight: 1.024, loss: 1.05, highlight: "gradient_direction" },
  },
  {
    id: "seg_05_update_rule",
    title: "Parameter Update Rule: w_t+1 = w_t - alpha * grad",
    teacherState: "POINTING",
    duration: 8.34,
    videoUrl: "/static/teacher-avatar/generated/machine-learning/seg_05_update_rule.mp4",
    audioUrl: "/static/teacher-avatar/generated/machine-learning/seg_05_update_rule.wav",
    script:
      "Here is the master parameter update equation: theta at t plus one equals theta at t minus alpha times the gradient of the loss function.",
    whiteboardData: { learningRate: 0.1, stepIndex: 4, weight: 0.819, loss: 0.67, highlight: "update_rule" },
  },
  {
    id: "seg_06_example",
    title: "Model Training & Convergence Example",
    teacherState: "EXPLAINING",
    duration: 8.13,
    videoUrl: "/static/teacher-avatar/generated/machine-learning/seg_06_example.mp4",
    audioUrl: "/static/teacher-avatar/generated/machine-learning/seg_06_example.wav",
    script:
      "In training deep neural networks and linear models, repeated mini-batch gradient descent iteratively drives weights toward the global or local minimum.",
    whiteboardData: { learningRate: 0.1, stepIndex: 4, weight: 0.819, loss: 0.67, highlight: "convergence" },
  },
];

interface TeacherVideoPlayerProps {
  segments?: TeachingSegment[];
  segmentIndex?: number;
  onSegmentChange?: (index: number) => void;
  teacherState?: TeacherState;
  onStateChange?: (state: TeacherState) => void;
  isPlaying?: boolean;
  onPlayPause?: (playing: boolean) => void;
  speed?: "1x" | "1.25x" | "1.5x";
  onSpeedChange?: (speed: "1x" | "1.25x" | "1.5x") => void;
  isMuted?: boolean;
  onMuteToggle?: () => void;
  showCaptions?: boolean;
  onToggleCaptions?: () => void;
  onAskDoubt?: () => void;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onWhiteboardSync?: (data: TeachingSegment["whiteboardData"]) => void;
}

export default function TeacherVideoPlayer({
  segments,
  segmentIndex = 0,
  onSegmentChange,
  teacherState: parentTeacherState,
  onStateChange,
  isPlaying = true,
  onPlayPause,
  speed = "1x",
  onSpeedChange,
  isMuted = false,
  onMuteToggle,
  showCaptions = true,
  onToggleCaptions,
  onAskDoubt,
  onTimeUpdate,
  onWhiteboardSync,
}: TeacherVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const segmentList = segments && segments.length > 0 ? segments : PHYSICS_DEMO_SEGMENTS;
  const activeSegment = segmentList[segmentIndex] || segmentList[0];

  const [currentSec, setCurrentSec] = useState(0);
  const [durationSec, setDurationSec] = useState(activeSegment.duration || 7.58);
  const [videoError, setVideoError] = useState(false);
  const [volume, setVolume] = useState(1.0);
  const [autoplayBlocked, setAutoplayBlocked] = useState(false);
  const [isPlayingAudioTest, setIsPlayingAudioTest] = useState(false);
  const [lessonStarted, setLessonStarted] = useState(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("start") === "1" || params.get("autostart") === "true") return true;
    }
    return false;
  });

  const currentState = parentTeacherState || activeSegment.teacherState;
  const currentVideoUrl = isPlayingAudioTest
    ? "/static/teacher/teacher_video_audio_test.mp4"
    : activeSegment.videoUrl;

  // Sync whiteboard data when segment changes
  useEffect(() => {
    if (activeSegment.whiteboardData && onWhiteboardSync) {
      onWhiteboardSync(activeSegment.whiteboardData);
    }
  }, [segmentIndex, segmentList]);

  // Video playback speed effect
  useEffect(() => {
    const rate = speed === "1.5x" ? 1.5 : speed === "1.25x" ? 1.25 : 1.0;
    if (videoRef.current) videoRef.current.playbackRate = rate;
    if (audioRef.current) audioRef.current.playbackRate = rate;
  }, [speed]);

  // Handle Playback & Autoplay policy
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.volume = volume;
      if (isPlaying) {
        videoRef.current.muted = isMuted;
        const playPromise = videoRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setAutoplayBlocked(false);
            })
            .catch((err) => {
              console.warn("Autoplay with audio restricted by browser policy:", err);
              setAutoplayBlocked(true);
              if (videoRef.current) {
                videoRef.current.muted = true;
                videoRef.current.play().catch(() => {});
              }
            });
        }
      } else {
        videoRef.current.pause();
      }
    }
    if (audioRef.current) {
      audioRef.current.volume = volume;
      if (isPlaying) {
        audioRef.current.play().catch(() => {});
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying, segmentIndex, isMuted, volume, isPlayingAudioTest]);

  // Volume & Mute synchronization
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.muted = isMuted;
      videoRef.current.volume = volume;
    }
    if (audioRef.current) {
      audioRef.current.muted = isMuted;
      audioRef.current.volume = volume;
    }
  }, [isMuted, volume]);

  const handleEnableAudio = () => {
    setAutoplayBlocked(false);
    if (videoRef.current) {
      videoRef.current.muted = false;
      videoRef.current.volume = volume > 0 ? volume : 1.0;
      videoRef.current.play().catch(() => {});
    }
    if (audioRef.current) {
      audioRef.current.muted = false;
      audioRef.current.volume = volume > 0 ? volume : 1.0;
      audioRef.current.play().catch(() => {});
    }
    if (isMuted && onMuteToggle) {
      onMuteToggle();
    }
  };

  const handleStartLesson = () => {
    setLessonStarted(true);
    setAutoplayBlocked(false);
    if (onPlayPause) onPlayPause(true);
    if (videoRef.current) {
      videoRef.current.muted = false;
      videoRef.current.volume = volume > 0 ? volume : 1.0;
      videoRef.current.play().catch(() => {});
    }
    if (audioRef.current) {
      audioRef.current.muted = false;
      audioRef.current.volume = volume > 0 ? volume : 1.0;
      audioRef.current.play().catch(() => {});
    }
    if (isMuted && onMuteToggle) {
      onMuteToggle();
    }
  };

  const handleToggleAudioTest = () => {
    setIsPlayingAudioTest((prev) => !prev);
    handleEnableAudio();
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const cur = videoRef.current.currentTime;
      const dur = videoRef.current.duration || activeSegment.duration;
      setCurrentSec(cur);
      setDurationSec(dur);
      if (onTimeUpdate) onTimeUpdate(cur, dur);
    }
  };

  const handleVideoEnded = () => {
    // Transition to next segment automatically or checkpoint if on question
    if (segmentIndex < PHYSICS_DEMO_SEGMENTS.length - 1) {
      if (onSegmentChange) onSegmentChange(segmentIndex + 1);
    } else {
      if (onPlayPause) onPlayPause(false);
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickPos = (e.clientX - rect.left) / rect.width;
    const newTime = clickPos * durationSec;
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setCurrentSec(newTime);
    }
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const stateBadges: Record<
    TeacherState,
    { label: string; color: string; bg: string; border: string; desc: string }
  > = {
    INTRODUCING: {
      label: "Introducing Concept",
      color: "text-emerald-300",
      bg: "bg-emerald-950/80",
      border: "border-emerald-500/40",
      desc: "Welcoming students and outlining lecture objectives",
    },
    EXPLAINING: {
      label: "Explaining Mechanism",
      color: "text-teal-300",
      bg: "bg-teal-950/80",
      border: "border-teal-500/40",
      desc: "Active lecture mode with synchronized lip articulation",
    },
    POINTING: {
      label: "Whiteboard Focus",
      color: "text-cyan-300",
      bg: "bg-cyan-950/80",
      border: "border-cyan-500/40",
      desc: "Directing student focus to the circuit formula I = V / R",
    },
    THINKING: {
      label: "Formulating Analogy",
      color: "text-amber-300",
      bg: "bg-amber-950/80",
      border: "border-amber-500/40",
      desc: "Pondering an intuitive hydraulic pipe analogy",
    },
    ASKING: {
      label: "Diagnostic Checkpoint",
      color: "text-indigo-300",
      bg: "bg-indigo-950/80",
      border: "border-indigo-500/40",
      desc: "Posing a formative question to test understanding",
    },
    LISTENING: {
      label: "Listening to Student",
      color: "text-rose-300",
      bg: "bg-rose-950/80",
      border: "border-rose-500/40",
      desc: "Attentive paused state awaiting student doubt query",
    },
    EVALUATING: {
      label: "Evaluating Response",
      color: "text-purple-300",
      bg: "bg-purple-950/80",
      border: "border-purple-500/40",
      desc: "Analyzing student response for misconceptions",
    },
    CORRECTING: {
      label: "Empathetic Correction",
      color: "text-orange-300",
      bg: "bg-orange-950/80",
      border: "border-orange-500/40",
      desc: "Clarifying invalid assumptions with contrastive examples",
    },
    ENCOURAGING: {
      label: "Encouraging Progress",
      color: "text-lime-300",
      bg: "bg-lime-950/80",
      border: "border-lime-500/40",
      desc: "Affirming intellectual effort and critical thinking",
    },
    CELEBRATING: {
      label: "Mastery Achieved",
      color: "text-yellow-300",
      bg: "bg-yellow-950/80",
      border: "border-yellow-500/40",
      desc: "Celebrating conceptual mastery and topic completion",
    },
  };

  const currentBadge = stateBadges[currentState] || stateBadges.EXPLAINING;

  return (
    <div className="flex flex-col h-full w-full bg-[#03120E] text-white select-none rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
      {/* Top Media Bar: Professor Bio + Live Status Badges */}
      <div className="bg-[#07221A] px-4 py-2.5 flex items-center justify-between border-b border-white/10">
        <div className="flex items-center gap-3">
          {/* Small Professor Thumbnail */}
          <div className="relative w-8 h-8 rounded-full overflow-hidden border border-[#10B981]/60 shrink-0">
            <img
              src="/teacher/male_professor_01.jpg"
              onError={(e) => {
                (e.target as HTMLImageElement).src = "/static/teacher/male_professor_01.jpg";
              }}
              alt="Prof. Richard Davies"
              className="w-full h-full object-cover object-top"
            />
            {isPlaying && (
              <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-[#10B981] ring-1 ring-black animate-pulse" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-xs sm:text-sm text-[#F9F8F5] tracking-tight">
                Prof. Richard Davies, Ph.D.
              </span>
              <span className="text-[9px] bg-[#10B981]/20 text-[#A7F3D0] border border-[#10B981]/40 px-1.5 py-0.5 rounded font-medium">
                Applied Physics
              </span>
            </div>
            <p className="text-[10px] text-[#A7F3D0]/80">
              AI Teacher Video · Cambridge Curriculum
            </p>
          </div>
        </div>

        {/* Dynamic Pedagogical State Badge */}
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold border backdrop-blur-md shadow-xs ${currentBadge.bg} ${currentBadge.border} ${currentBadge.color}`}
          title={currentBadge.desc}
        >
          <span className="w-2 h-2 rounded-full bg-current animate-ping" style={{ animationDuration: "2s" }} />
          <span>{currentBadge.label}</span>
        </div>
      </div>

      {/* Center Video Stage with Deterministic Fallback */}
      <div className="teacher-video relative flex-1 min-h-[280px] sm:min-h-[380px] aspect-video bg-[#03120E] flex items-center justify-center overflow-hidden" data-testid="teacher-video">
        {/* Visual Background Lighting */}
        <div className="absolute inset-0 bg-radial-gradient from-[#0F3D32]/60 via-[#07221A] to-[#03120E] pointer-events-none" />

        {/* Clear Start Lesson Hero Overlay if not yet started */}
        {!lessonStarted && (
          <div className="absolute inset-0 z-40 bg-[#03120E]/85 backdrop-blur-xs flex flex-col items-center justify-center p-4 sm:p-6 text-center">
            <div className="max-w-sm bg-[#07221A] border-2 border-[#10B981]/60 rounded-2xl p-6 shadow-2xl space-y-4">
              <div className="w-14 h-14 rounded-full bg-[#10B981]/20 border-2 border-[#10B981] flex items-center justify-center mx-auto text-2xl text-[#10B981]">
                ▶
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-bold text-white">Start Interactive Lesson</h3>
                <p className="text-xs text-[#A7F3D0] mt-1">
                  Prof. Richard Davies, Ph.D. · Applied Physics
                </p>
              </div>
              <button
                onClick={handleStartLesson}
                className="w-full py-3.5 px-6 rounded-xl bg-[#10B981] hover:bg-[#059669] text-[#07221A] font-extrabold text-sm shadow-xl transition-all transform hover:scale-105 active:scale-95 cursor-pointer flex items-center justify-center gap-2"
              >
                <span>▶</span>
                <span>Start Lesson</span>
              </button>
              <p className="text-[10px] text-white/60">
                🔊 Starts video lecture with audible professor voice
              </p>
            </div>
          </div>
        )}

        {/* Floating Unmute / Enable Audio Prompt if autoplay with sound restricted */}
        {lessonStarted && (autoplayBlocked || isMuted) && isPlaying && (
          <button
            onClick={handleEnableAudio}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 flex items-center gap-2.5 px-6 py-3.5 rounded-2xl bg-[#10B981] hover:bg-[#059669] text-[#07221A] font-extrabold text-sm shadow-2xl border-2 border-white/20 transition-all hover:scale-105 active:scale-95 cursor-pointer animate-pulse"
          >
            <span className="text-xl">🔊</span>
            <span>Click to Enable Teacher Audio</span>
          </button>
        )}

        {/* Audio Test Active Notification Banner */}
        {isPlayingAudioTest && (
          <div className="absolute top-3 right-4 z-20 flex items-center gap-2 bg-amber-500/90 text-black px-3 py-1 rounded-full text-[11px] font-bold shadow-lg">
            <span>⚡ AUDIO TEST RUNNING</span>
            <button
              onClick={handleToggleAudioTest}
              className="text-xs bg-black/20 hover:bg-black/40 px-1.5 py-0.5 rounded cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        {/* Primary Video Element */}
        {!videoError ? (
          <video
            ref={videoRef}
            src={currentVideoUrl}
            className="w-full h-full object-contain relative z-10 transition-opacity duration-300"
            playsInline
            preload="metadata"
            autoPlay={isPlaying && lessonStarted}
            muted={isMuted}
            onTimeUpdate={handleTimeUpdate}
            onEnded={handleVideoEnded}
            onError={() => {
              console.warn("Primary MP4 failed, falling back to photorealistic portrait + synchronized audio.");
              setVideoError(true);
            }}
          />
        ) : (
          /* Deterministic Graceful Fallback: Photorealistic High-Res Portrait + Synchronized Audio */
          <div className="relative w-full h-full flex flex-col items-center justify-center p-4 z-10">
            <audio
              ref={audioRef}
              src={activeSegment.audioUrl}
              autoPlay={isPlaying}
              muted={isMuted}
              onTimeUpdate={() => {
                if (audioRef.current) {
                  const cur = audioRef.current.currentTime;
                  const dur = audioRef.current.duration || activeSegment.duration;
                  setCurrentSec(cur);
                  setDurationSec(dur);
                  if (onTimeUpdate) onTimeUpdate(cur, dur);
                }
              }}
              onEnded={handleVideoEnded}
            />

            {/* Photorealistic Portrait with Clean Audio Waveform */}
            <div className="relative w-52 h-52 sm:w-64 sm:h-64 rounded-2xl overflow-hidden shadow-2xl border-2 border-[#10B981]/50 bg-[#0D3B2E]">
              <img
                src="/teacher/male_professor_01.jpg"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = "/static/teacher/male_professor_01.jpg";
                }}
                alt="Prof. Richard Davies"
                className="w-full h-full object-cover object-top"
              />

              {/* Active Audio Waveform Indicator */}
              {isPlaying && (
                <div className="absolute bottom-2 left-3 right-3 flex items-center justify-center gap-1 bg-black/70 backdrop-blur-xs py-1.5 rounded-lg border border-white/10">
                  <span className="text-[10px] text-[#A7F3D0] font-mono mr-1">AUDIO STREAM</span>
                  {[0.4, 0.8, 0.6, 1.0, 0.5, 0.9, 0.3].map((h, i) => (
                    <span
                      key={i}
                      className="w-1 bg-[#10B981] rounded-full animate-pulse"
                      style={{
                        height: `${Math.max(4, h * 16)}px`,
                        animationDuration: `${0.3 + i * 0.1}s`,
                      }}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Live Subtitles / Caption Overlay */}
        {showCaptions && (
          <div
            className="teacher-caption absolute bottom-4 left-4 right-4 z-20 pointer-events-none flex justify-center"
            data-testid="teacher-caption"
            style={{
              position: "absolute",
              left: "16px",
              right: "16px",
              bottom: "16px",
              width: "auto",
              maxWidth: "calc(100% - 32px)",
              boxSizing: "border-box",
            }}
          >
            <div
              className="teacher-caption-inner bg-black/85 backdrop-blur-md px-4 py-2.5 rounded-xl border border-white/10 shadow-lg text-center w-full max-w-2xl h-auto pointer-events-auto"
              style={{
                width: "100%",
                maxWidth: "672px",
                height: "auto",
                minHeight: "auto",
                maxHeight: "none",
                whiteSpace: "normal",
                wordWrap: "break-word",
                overflowWrap: "break-word",
                wordBreak: "break-word",
                boxSizing: "border-box",
                overflow: "visible",
              }}
            >
              <p
                className="teacher-caption-text text-white text-xs sm:text-sm font-medium leading-relaxed whitespace-normal break-words h-auto"
                style={{
                  margin: 0,
                  whiteSpace: "normal",
                  wordWrap: "break-word",
                  overflowWrap: "break-word",
                  wordBreak: "break-word",
                  overflow: "visible",
                  textOverflow: "clip",
                  height: "auto",
                  minHeight: "auto",
                  maxHeight: "none",
                }}
              >
                "{isPlayingAudioTest ? "Hello. Today we will learn this concept step by step." : activeSegment.script}"
              </p>
            </div>
          </div>
        )}

        {/* Watermark / Attribution */}
        <div className="absolute top-3 left-4 z-20 flex items-center gap-2">
          <span className="flex items-center gap-1.5 text-[10px] font-bold text-white bg-emerald-600 px-2.5 py-0.5 rounded-full shadow-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            AI TEACHER VIDEO
          </span>
          <span className="text-[10px] font-semibold text-[#A7F3D0] bg-black/40 px-2.5 py-0.5 rounded-full border border-white/10 backdrop-blur-xs">
            {isPlayingAudioTest ? "Diagnostic Sound Test (24kHz AAC)" : activeSegment.title}
          </span>
        </div>
      </div>

      {/* Integrated Scrubber & Timing Bar */}
      <div className="bg-[#07221A] px-4 pt-2 border-t border-white/10">
        <div className="flex items-center justify-between text-[10px] text-white/60 mb-1 font-mono">
          <span>{formatTime(currentSec)}</span>
          <span className="text-[#A7F3D0] font-bold">
            {isPlayingAudioTest ? "Sound Verification Test" : `Segment ${segmentIndex + 1} of ${PHYSICS_DEMO_SEGMENTS.length}`}
          </span>
          <span>{formatTime(durationSec)}</span>
        </div>
        <div
          onClick={handleSeek}
          className="h-2 bg-white/10 rounded-full cursor-pointer overflow-hidden relative group"
        >
          <div
            className="h-full bg-gradient-to-r from-[#059669] to-[#10B981] rounded-full transition-all group-hover:brightness-125"
            style={{ width: `${Math.min(100, (currentSec / (durationSec || 1)) * 100)}%` }}
          />
        </div>
      </div>

      {/* Control Actions & Segment Switcher Bar */}
      <div className="bg-[#07221A] px-4 py-3 flex flex-wrap items-center justify-between gap-2.5">
        {/* Left: Play/Pause, Ask Doubt, Sound Toggle, Volume Slider */}
        <div className="flex items-center gap-2">
          {/* Play / Pause */}
          <button
            onClick={() => {
              if (!lessonStarted) setLessonStarted(true);
              if (onPlayPause) onPlayPause(!isPlaying);
            }}
            className="w-9 h-9 rounded-xl bg-[#10B981] hover:bg-[#059669] text-[#07221A] flex items-center justify-center text-sm font-bold transition-all shadow-md cursor-pointer active:scale-95"
            title={isPlaying ? "Pause Video" : "Play Video"}
          >
            {isPlaying ? "⏸" : "▶"}
          </button>

          {/* Ask Doubt Interruption Button */}
          <button
            onClick={onAskDoubt}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-all shadow-md cursor-pointer animate-pulse active:scale-95"
            title="Interrupt teacher to ask a question"
          >
            <span>✋</span>
            <span>Ask Doubt</span>
          </button>

          {/* Explicit Sound On / Mute Toggle Button */}
          <button
            onClick={() => {
              if (onMuteToggle) onMuteToggle();
              if (isMuted) setAutoplayBlocked(false);
            }}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer border shadow-xs ${
              isMuted
                ? "bg-rose-950/80 border-rose-500/50 text-rose-300 hover:bg-rose-900/80"
                : "bg-emerald-950/80 border-emerald-500/50 text-emerald-300 hover:bg-emerald-900/80"
            }`}
            title={isMuted ? "Unmute Teacher Voice" : "Mute Teacher Voice"}
          >
            <span>{isMuted ? "🔇 Mute" : "🔊 Sound On"}</span>
          </button>

          {/* Volume Control Group */}
          <div className="flex items-center gap-1.5 bg-black/40 px-2 py-1 rounded-xl border border-white/10">
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={isMuted ? 0 : volume}
              onChange={(e) => {
                const newVol = parseFloat(e.target.value);
                setVolume(newVol);
                if (videoRef.current) videoRef.current.volume = newVol;
                if (audioRef.current) audioRef.current.volume = newVol;
                if (newVol > 0 && isMuted && onMuteToggle) {
                  onMuteToggle();
                  setAutoplayBlocked(false);
                }
              }}
              className="w-14 sm:w-16 h-1.5 bg-white/20 rounded-lg appearance-none cursor-pointer accent-[#10B981]"
              title={`Volume: ${Math.round((isMuted ? 0 : volume) * 100)}%`}
            />
          </div>

          {/* Dedicated Instant Audio Test Button */}
          <button
            onClick={handleToggleAudioTest}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-[10px] font-bold transition-all cursor-pointer border shadow-xs ${
              isPlayingAudioTest
                ? "bg-amber-500 text-black border-amber-400 animate-pulse"
                : "bg-[#10B981]/15 text-[#A7F3D0] border-[#10B981]/40 hover:bg-[#10B981]/30"
            }`}
            title="Test teacher audio playback immediately"
          >
            <span>{isPlayingAudioTest ? "⏹ Stop Test" : "⚡ Test Sound"}</span>
          </button>
        </div>

        {/* Center: Segment Navigation */}
        <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/10 overflow-x-auto max-w-xs sm:max-w-none">
          {PHYSICS_DEMO_SEGMENTS.map((seg, idx) => (
            <button
              key={seg.id}
              onClick={() => {
                if (isPlayingAudioTest) setIsPlayingAudioTest(false);
                if (onSegmentChange) onSegmentChange(idx);
                if (onStateChange) onStateChange(seg.teacherState);
              }}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer whitespace-nowrap ${
                segmentIndex === idx && !isPlayingAudioTest
                  ? "bg-[#10B981] text-[#07221A] shadow-xs"
                  : "text-white/60 hover:text-white hover:bg-white/5"
              }`}
              title={seg.title}
            >
              {idx === 0
                ? "1. Intro"
                : idx === 1
                ? "2. Resistance"
                : idx === 2
                ? "3. Formula"
                : idx === 3
                ? "4. Example"
                : idx === 4
                ? "5. Checkpoint"
                : "6. Doubt"}
            </button>
          ))}
        </div>

        {/* Right: Speed, Captions Toggle */}
        <div className="flex items-center gap-1.5">
          {/* Speed Selector */}
          <div className="flex items-center gap-0.5 bg-black/40 p-0.5 rounded-lg text-[10px] font-bold border border-white/10">
            {(["1x", "1.25x", "1.5x"] as const).map((s) => (
              <button
                key={s}
                onClick={() => onSpeedChange && onSpeedChange(s)}
                className={`px-1.5 py-0.5 rounded transition-all cursor-pointer ${
                  speed === s ? "bg-[#10B981] text-[#07221A]" : "text-white/60 hover:text-white"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Subtitles CC Toggle */}
          <button
            onClick={onToggleCaptions}
            className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer border ${
              showCaptions
                ? "bg-[#10B981] text-[#07221A] border-[#10B981]"
                : "bg-black/40 text-white/50 border-white/10 hover:text-white"
            }`}
            title="Toggle Subtitles"
          >
            CC
          </button>
        </div>
      </div>
    </div>
  );
}
