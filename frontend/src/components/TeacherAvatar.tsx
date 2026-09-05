import { useEffect, useState } from "react";

export type TeacherState =
  | "IDLE"
  | "SPEAKING"
  | "INTRODUCING"
  | "EXPLAINING"
  | "POINTING"
  | "THINKING"
  | "ASKING"
  | "LISTENING"
  | "EVALUATING"
  | "CORRECTING"
  | "ENCOURAGING"
  | "CELEBRATING"
  | "CONFUSED"
  | "EMPHASIZING";

interface TeacherAvatarProps {
  state?: TeacherState;
  isSpeaking?: boolean;
  teacherName?: string;
  teacherTitle?: string;
  size?: "sm" | "md" | "lg";
  onStateChange?: (state: TeacherState) => void;
}

export default function TeacherAvatar({
  state = "EXPLAINING",
  isSpeaking = true,
  teacherName = "Prof. Richard Davies, Ph.D.",
  teacherTitle = "Applied Physics & Circuit Theory",
  size = "md",
}: TeacherAvatarProps) {
  const [mouthOpen, setMouthOpen] = useState(false);
  const [blink, setBlink] = useState(false);
  const [headTilt, setHeadTilt] = useState(0);

  // Natural blinking interval (every 3.5 - 4.5 seconds)
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setBlink(true);
      setTimeout(() => setBlink(false), 160);
    }, 3600);
    return () => clearInterval(blinkInterval);
  }, []);

  // Natural speaking mouth visemes synchronized with playback
  useEffect(() => {
    if (!isSpeaking || state === "LISTENING") {
      setMouthOpen(false);
      return;
    }

    const mouthInterval = setInterval(() => {
      setMouthOpen((prev) => !prev);
    }, 160);
    return () => clearInterval(mouthInterval);
  }, [isSpeaking, state]);

  // Subtle head motion based on state
  useEffect(() => {
    if (state === "THINKING") setHeadTilt(-3);
    else if (state === "LISTENING") setHeadTilt(4);
    else if (state === "CELEBRATING") setHeadTilt(1);
    else if (state === "CONFUSED") setHeadTilt(-2);
    else if (state === "POINTING") setHeadTilt(-2);
    else setHeadTilt(0);
  }, [state]);

  const stateColors: Record<string, { bg: string; text: string; ring: string }> = {
    IDLE: { bg: "bg-slate-100", text: "text-slate-700", ring: "border-slate-300" },
    SPEAKING: { bg: "bg-emerald-50", text: "text-emerald-700", ring: "border-emerald-400" },
    INTRODUCING: { bg: "bg-emerald-50", text: "text-emerald-700", ring: "border-emerald-400" },
    EXPLAINING: { bg: "bg-teal-50", text: "text-teal-700", ring: "border-teal-400" },
    POINTING: { bg: "bg-cyan-50", text: "text-cyan-700", ring: "border-cyan-400" },
    THINKING: { bg: "bg-amber-50", text: "text-amber-700", ring: "border-amber-400" },
    ASKING: { bg: "bg-indigo-50", text: "text-indigo-700", ring: "border-indigo-400" },
    LISTENING: { bg: "bg-rose-50", text: "text-rose-700", ring: "border-rose-400" },
    EVALUATING: { bg: "bg-purple-50", text: "text-purple-700", ring: "border-purple-400" },
    CORRECTING: { bg: "bg-orange-50", text: "text-orange-700", ring: "border-orange-400" },
    ENCOURAGING: { bg: "bg-lime-50", text: "text-lime-700", ring: "border-lime-400" },
    CELEBRATING: { bg: "bg-emerald-100", text: "text-emerald-800", ring: "border-emerald-500" },
    CONFUSED: { bg: "bg-rose-50", text: "text-rose-700", ring: "border-rose-400" },
    EMPHASIZING: { bg: "bg-purple-50", text: "text-purple-700", ring: "border-purple-400" },
  };

  const currentColors = stateColors[state] || stateColors.EXPLAINING;

  const sizeClasses =
    size === "sm"
      ? "w-20 h-20"
      : size === "lg"
      ? "w-36 h-36 sm:w-44 sm:h-44"
      : "w-28 h-28 sm:w-32 sm:h-32";

  return (
    <div className="flex flex-col items-center select-none">
      {/* Avatar Container with Photorealistic Male Professor Presentation */}
      <div className="relative flex items-center justify-center">
        {/* Pulsing Active Speaking Radiance Rings */}
        {isSpeaking && (
          <>
            <div
              className="absolute -inset-2 rounded-full border-2 border-[#10B981] opacity-40 animate-ping pointer-events-none"
              style={{ animationDuration: "2.5s" }}
            />
            <div
              className="absolute -inset-4 rounded-full border border-[#34D399] opacity-20 animate-ping pointer-events-none"
              style={{ animationDuration: "3.5s" }}
            />
          </>
        )}

        {/* Celebration Particles */}
        {state === "CELEBRATING" && (
          <div className="absolute -top-3 -right-2 text-xl animate-bounce pointer-events-none z-20">
            ✨🎉
          </div>
        )}

        {/* Photorealistic Male Professor Portrait Frame */}
        <div
          className={`${sizeClasses} rounded-full overflow-hidden shadow-2xl border-2 border-[#10B981]/80 relative z-10 bg-gradient-to-b from-[#0F3D32] to-[#07221A] transition-transform duration-300 ring-4 ring-[#0D3B2E]/40`}
          style={{ transform: `rotate(${headTilt}deg)` }}
        >
          {/* Authentic Male Professor Portrait */}
          <img
            src="/teacher/male_professor_01.jpg"
            onError={(e) => {
              (e.target as HTMLImageElement).src = "/static/teacher/male_professor_01.jpg";
            }}
            alt={teacherName}
            className="w-full h-full object-cover object-top"
          />

          {/* Natural Eye Blink Overlay */}
          {blink && (
            <div className="absolute top-[32%] left-[28%] right-[28%] h-2.5 bg-[#38261E] rounded-full blur-[0.5px] opacity-90 transition-opacity pointer-events-none" />
          )}

          {/* Natural Mouth Aperture Viseme Overlay during Speech */}
          {isSpeaking && mouthOpen && state !== "LISTENING" && (
            <div className="absolute top-[52%] left-[45%] w-4 h-2 bg-[#2B1713] rounded-full opacity-70 blur-[0.5px] pointer-events-none" />
          )}

          {/* Academic Gradient Vignette */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#03120E]/40 via-transparent to-transparent pointer-events-none" />
        </div>
      </div>

      {/* Professor Credentials */}
      <div className="mt-2 text-center">
        <div className="text-white font-bold text-sm sm:text-base tracking-tight">{teacherName}</div>
        <div className="text-xs text-[#A7F3D0] font-medium">{teacherTitle}</div>
      </div>

      {/* Pedagogical State Badge */}
      <div className="mt-1.5 flex items-center gap-1.5">
        <span
          className={`text-[9px] uppercase tracking-wider font-extrabold px-2.5 py-0.5 rounded-full border ${currentColors.bg} ${currentColors.text} ${currentColors.ring} shadow-xs flex items-center gap-1`}
        >
          {isSpeaking && <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />}
          {state}
        </span>
      </div>

      {/* Multi-frequency Audio Equalizer Bars */}
      {isSpeaking && (
        <div className="flex gap-0.5 justify-center items-end h-4 mt-1.5">
          {[4, 10, 14, 7, 16, 9, 6, 12, 8, 4].map((h, i) => (
            <div
              key={i}
              className="w-1 rounded-full bg-[#10B981] animate-pulse"
              style={{
                height: `${h}px`,
                animationDuration: `${0.4 + (i % 3) * 0.15}s`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
