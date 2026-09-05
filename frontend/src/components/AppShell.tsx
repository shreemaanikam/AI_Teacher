import { ReactNode, useState, useEffect } from "react";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  children: ReactNode;
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

const navItems: { label: string; icon: string; screen: Screen; badge?: string }[] = [
  { label: "Home", icon: "⌂", screen: "dashboard" },
  { label: "Learn", icon: "▶", screen: "lesson-player", badge: "Live" },
  { label: "Library", icon: "◱", screen: "documents" },
  { label: "Progress", icon: "⌖", screen: "learning-path" },
  { label: "Analytics", icon: "⋯", screen: "analytics" },
];

export default function AppShell({ children, navigate, currentScreen }: Props) {
  const { profile, updateProfile, progress } = useLearner();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [languageMenuOpen, setLanguageMenuOpen] = useState(false);

  // Keyboard shortcut for Cmd/Ctrl + K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setSearchOpen(false);
        setProfileMenuOpen(false);
        setNotificationsOpen(false);
        setLanguageMenuOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const searchResults = [
    { title: "Ohm's Law: Voltage & Current", desc: "Physics · Current active lesson", screen: "lesson-player" as Screen },
    { title: "Resistance & Circuit Flow", desc: "Physics · Analogy-first module", screen: "lesson-player" as Screen },
    { title: "Physics Notes.pdf", desc: "Grounded Document · 24 pages", screen: "document-processing" as Screen },
    { title: "Concept Mastery Roadmap", desc: "Learning Path · 4 of 9 explored", screen: "learning-path" as Screen },
    { title: "Learning Analytics & Scores", desc: "7-day streak · 82% mastery", screen: "analytics" as Screen },
  ].filter(item => item.title.toLowerCase().includes(searchQuery.toLowerCase()) || item.desc.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="flex min-h-screen bg-[#F9F8F5] text-[#0F172A]">
      {/* Search Modal */}
      {searchOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-[#07221A]/40 backdrop-blur-sm p-4 animate-fade-in-up">
          <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-[#E5E7EB] overflow-hidden">
            <div className="flex items-center px-4 py-3.5 border-b border-[#F3F4F6] gap-3">
              <span className="text-[#0D3B2E] text-lg font-bold">🔍</span>
              <input
                autoFocus
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search anything you're learning, concepts, documents..."
                className="w-full text-sm text-[#0F172A] focus:outline-none bg-transparent"
              />
              <span className="text-[10px] font-semibold bg-[#F3F4F6] text-[#6B7280] px-2 py-1 rounded-md">ESC</span>
            </div>
            <div className="p-2 max-h-72 overflow-y-auto">
              {searchResults.length > 0 ? (
                searchResults.map((res) => (
                  <button
                    key={res.title}
                    onClick={() => {
                      navigate(res.screen);
                      setSearchOpen(false);
                    }}
                    className="w-full text-left p-3 hover:bg-[#ECFDF5] rounded-xl flex items-center justify-between group transition-all"
                  >
                    <div>
                      <div className="text-sm font-semibold text-[#0D3B2E] group-hover:text-[#07221A]">{res.title}</div>
                      <div className="text-xs text-[#5E6D67]">{res.desc}</div>
                    </div>
                    <span className="text-xs text-[#10B981] opacity-0 group-hover:opacity-100 font-medium">Jump →</span>
                  </button>
                ))
              ) : (
                <div className="p-6 text-center text-xs text-[#5E6D67]">No results found for "{searchQuery}"</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/30 backdrop-blur-xs lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-screen z-40 w-64 bg-white border-r border-[#E6E4DC] flex flex-col transition-transform duration-200 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
        style={{ boxShadow: "1px 0 3px 0 rgba(13,59,46,0.03)" }}
      >
        {/* Brand Header */}
        <div className="px-6 py-5 border-b border-[#F5F4EE]">
          <button
            onClick={() => {
              navigate("dashboard");
              setSidebarOpen(false);
            }}
            className="flex items-center gap-3 w-full text-left group"
          >
            <div className="w-9 h-9 rounded-xl bg-[#0D3B2E] text-white flex items-center justify-center font-bold text-sm shadow-sm group-hover:bg-[#07221A] transition-colors">
              <span className="text-[#A7F3D0]">✦</span>
            </div>
            <div>
              <div className="text-sm font-bold tracking-tight text-[#0D3B2E] leading-tight">Aster AI</div>
              <div className="text-[10px] font-medium tracking-wide uppercase text-[#5E6D67] leading-tight">Teacher of the Future</div>
            </div>
          </button>
        </div>

        {/* Primary Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const active =
              currentScreen === item.screen ||
              (item.screen === "lesson-player" &&
                [
                  "lesson-player",
                  "question",
                  "evaluation-wrong",
                  "evaluation-correct",
                  "misconception",
                  "adaptive",
                  "adaptive-question",
                  "assessment",
                ].includes(currentScreen)) ||
              (item.screen === "documents" && ["documents", "document-processing"].includes(currentScreen)) ||
              (item.screen === "learning-path" && ["learning-path", "report"].includes(currentScreen)) ||
              (item.screen === "dashboard" && currentScreen === "dashboard");

            return (
              <button
                key={item.label}
                onClick={() => {
                  navigate(item.screen);
                  setSidebarOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  active
                    ? "bg-[#0D3B2E] text-white shadow-xs font-semibold"
                    : "text-[#334155] hover:bg-[#F5F4EE] hover:text-[#0D3B2E]"
                }`}
              >
                <span className={`text-base w-5 text-center ${active ? "text-[#A7F3D0]" : "text-[#5E6D67]"}`}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
                {item.badge && !active && (
                  <span className="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#ECFDF5] text-[#059669]">
                    {item.badge}
                  </span>
                )}
                {active && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-[#A7F3D0]" />}
              </button>
            );
          })}
        </nav>

        {/* Bottom Actions & User Profile */}
        <div className="p-3 border-t border-[#F5F4EE] space-y-2">
          {/* Create Lesson CTA */}
          <button
            onClick={() => {
              navigate("create-lesson");
              setSidebarOpen(false);
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-white bg-[#0D3B2E] hover:bg-[#07221A] transition-all shadow-xs"
          >
            <span className="text-sm">+</span>
            <span>New Lesson</span>
          </button>

          {/* Settings Nav Item */}
          <button
            onClick={() => {
              navigate("profile");
              setSidebarOpen(false);
            }}
            className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-medium transition-all ${
              currentScreen === "profile"
                ? "bg-[#ECFDF5] text-[#0D3B2E] font-semibold"
                : "text-[#5E6D67] hover:bg-[#F5F4EE] hover:text-[#0D3B2E]"
            }`}
          >
            <span className="text-sm w-5 text-center">⚙</span>
            <span>Settings</span>
          </button>

          {/* User Profile Summary */}
          <div
            onClick={() => {
              navigate("profile");
              setSidebarOpen(false);
            }}
            className="flex items-center gap-3 p-2.5 rounded-xl bg-[#F9F8F5] border border-[#E6E4DC] hover:border-[#0D3B2E]/30 cursor-pointer transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center text-xs font-bold shrink-0">
              {profile.name[0] || "A"}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-[#0F172A] truncate">{profile.name}</div>
              <div className="text-[10px] text-[#5E6D67] truncate">Curious learner · {profile.language}</div>
            </div>
            <span className="text-xs text-[#9CA3AF]">›</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Top Bar */}
        <header className="bg-white/90 backdrop-blur-md border-b border-[#E6E4DC] h-16 flex items-center px-6 gap-4 sticky top-0 z-20">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden w-9 h-9 flex items-center justify-center rounded-xl border border-[#E5E7EB] hover:bg-[#F5F4EE] text-[#0D3B2E]"
          >
            ☰
          </button>

          {/* Large Search Field */}
          <div className="flex-1 max-w-lg">
            <button
              onClick={() => setSearchOpen(true)}
              className="w-full flex items-center justify-between bg-[#F9F8F5] border border-[#E6E4DC] hover:border-[#0D3B2E]/40 rounded-xl px-4 py-2 text-xs text-[#5E6D67] transition-all cursor-pointer shadow-2xs"
            >
              <div className="flex items-center gap-2.5">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#5E6D67" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.35-4.35" />
                </svg>
                <span className="text-xs">Search anything you're learning…</span>
              </div>
              <div className="hidden sm:flex items-center gap-1 bg-white border border-[#E6E4DC] rounded-md px-1.5 py-0.5 text-[10px] font-medium text-[#5E6D67]">
                <span>⌘</span>
                <span>K</span>
              </div>
            </button>
          </div>

          {/* Right-Side Utilities */}
          <div className="ml-auto flex items-center gap-3">
            {/* Language Selector Dropdown */}
            <div className="relative">
              <button
                onClick={() => setLanguageMenuOpen(!languageMenuOpen)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#E6E4DC] bg-white text-xs font-medium text-[#0D3B2E] hover:bg-[#F9F8F5] transition-colors"
              >
                <span>🇮🇳</span>
                <span>{profile.language}</span>
                <span className="text-[10px] text-[#5E6D67]">▾</span>
              </button>
              {languageMenuOpen && (
                <div className="absolute right-0 mt-2 w-36 bg-white rounded-xl shadow-lg border border-[#E5E7EB] py-1 z-30 animate-scale-in">
                  {["English", "Hindi", "Tamil", "Hinglish"].map((lang) => (
                    <button
                      key={lang}
                      onClick={() => {
                        updateProfile({ language: lang });
                        setLanguageMenuOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-xs hover:bg-[#ECFDF5] transition-colors flex items-center justify-between ${
                        profile.language === lang ? "font-bold text-[#0D3B2E]" : "text-[#334155]"
                      }`}
                    >
                      <span>{lang}</span>
                      {profile.language === lang && <span className="text-[#10B981]">✓</span>}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Notification Bell */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="w-9 h-9 flex items-center justify-center rounded-xl border border-[#E6E4DC] hover:bg-[#F9F8F5] text-[#5E6D67] transition-colors relative"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                  <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                </svg>
                <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#E11D48]" />
              </button>
              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-[#E5E7EB] p-3 z-30 animate-scale-in">
                  <div className="flex items-center justify-between pb-2 border-b border-[#F3F4F6] mb-2">
                    <span className="text-xs font-bold text-[#0D3B2E]">Notifications</span>
                    <span className="text-[10px] text-[#10B981] font-semibold">2 unread</span>
                  </div>
                  <div className="space-y-2">
                    <div className="p-2 rounded-xl bg-[#FFF1F2] border border-[#FFE4E6] text-xs">
                      <div className="font-semibold text-[#E11D48] text-[11px]">Misconception Diagnosed</div>
                      <div className="text-[10px] text-[#5E6D67] mt-0.5">Resistance & Current relationship review ready.</div>
                    </div>
                    <div className="p-2 rounded-xl bg-[#ECFDF5] border border-[#BBF7D0] text-xs">
                      <div className="font-semibold text-[#059669] text-[11px]">Document Grounded</div>
                      <div className="text-[10px] text-[#5E6D67] mt-0.5">Physics Notes.pdf indexed into 18 concepts.</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className="flex items-center gap-2.5 p-1 rounded-xl hover:bg-[#F5F4EE] transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-[#0D3B2E] text-[#A7F3D0] flex items-center justify-center text-xs font-bold shadow-xs">
                  {profile.name[0] || "A"}
                </div>
                <div className="hidden md:block text-left">
                  <div className="text-xs font-semibold text-[#0F172A] leading-tight">{profile.name}</div>
                  <div className="text-[10px] text-[#5E6D67] leading-tight">Curious learner</div>
                </div>
                <span className="hidden md:inline text-[10px] text-[#5E6D67]">▾</span>
              </button>

              {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-2xl shadow-xl border border-[#E5E7EB] py-2 z-30 animate-scale-in">
                  <div className="px-4 py-2 border-b border-[#F3F4F6]">
                    <div className="text-xs font-bold text-[#0D3B2E]">{profile.name}</div>
                    <div className="text-[10px] text-[#5E6D67]">{profile.level} · {profile.language}</div>
                  </div>
                  <button
                    onClick={() => {
                      navigate("profile");
                      setProfileMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 text-xs font-medium text-[#334155] hover:bg-[#F9F8F5] flex items-center gap-2"
                  >
                    <span>👤</span> View Profile
                  </button>
                  <button
                    onClick={() => {
                      navigate("profile");
                      setProfileMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 text-xs font-medium text-[#334155] hover:bg-[#F9F8F5] flex items-center gap-2"
                  >
                    <span>⚙</span> Preferences
                  </button>
                  <button
                    onClick={() => {
                      navigate("learning-path");
                      setProfileMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 text-xs font-medium text-[#334155] hover:bg-[#F9F8F5] flex items-center gap-2"
                  >
                    <span>⌖</span> Learning Path
                  </button>
                  <div className="border-t border-[#F3F4F6] mt-1 pt-1">
                    <button
                      onClick={() => {
                        navigate("landing");
                        setProfileMenuOpen(false);
                      }}
                      className="w-full text-left px-4 py-2 text-xs font-medium text-[#E11D48] hover:bg-[#FFF1F2] flex items-center gap-2"
                    >
                      <span>🚪</span> Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 overflow-auto bg-[#F9F8F5]">
          {children}
        </main>
      </div>
    </div>
  );
}
