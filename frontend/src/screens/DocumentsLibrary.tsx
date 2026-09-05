import { useState } from "react";
import AppShell from "../components/AppShell";
import type { Screen } from "../types";
import { useLearner } from "../context/LearnerContext";

interface Props {
  navigate: (s: Screen) => void;
  currentScreen: Screen;
}

export default function DocumentsLibrary({ navigate, currentScreen }: Props) {
  const { documents } = useLearner();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");

  const filtered = documents.filter(
    (d) =>
      d.name.toLowerCase().includes(search.toLowerCase()) &&
      (filter === "All" || d.status === filter.toLowerCase())
  );

  return (
    <AppShell navigate={navigate} currentScreen={currentScreen}>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold text-[#059669] uppercase tracking-wider">
              GROUNDED SOURCE REPOSITORY
            </span>
            <h1 className="font-serif text-3xl text-[#0D3B2E] font-bold">Documents Library</h1>
            <p className="text-xs text-[#5E6D67] mt-0.5">
              {documents.length} documents uploaded · {documents.filter((d) => d.status === "grounded").length} fully indexed for AI teaching
            </p>
          </div>
          <button
            onClick={() => navigate("create-lesson")}
            className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#0D3B2E] hover:bg-[#07221A] transition-all shadow-xs cursor-pointer"
          >
            + Upload Document
          </button>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex items-center gap-2.5 flex-1 bg-white border border-[#E6E4DC] rounded-2xl px-4 py-2.5 text-xs shadow-2xs">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#5E6D67" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search documents by title, chapter or subject…"
              className="flex-1 text-[#0F172A] focus:outline-none bg-transparent"
            />
          </div>

          <div className="flex gap-2">
            {["All", "Grounded", "Processing", "Error"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                  filter === f
                    ? "bg-[#0D3B2E] text-white border-[#0D3B2E] shadow-2xs"
                    : "bg-white text-[#334155] border-[#E6E4DC] hover:border-[#0D3B2E]/40 hover:bg-[#F5F4EE]"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Documents Table */}
        <div className="bg-white rounded-3xl border border-[#E6E4DC] shadow-xs overflow-hidden">
          <div className="hidden sm:grid grid-cols-[2fr_80px_60px_70px_100px_90px_80px] gap-2 px-6 py-3.5 bg-[#F9F8F5] border-b border-[#E6E4DC] text-[10px] font-bold text-[#5E6D67] uppercase tracking-wider">
            <span>Document</span>
            <span>Format</span>
            <span>Pages</span>
            <span>Concepts</span>
            <span>RAG Status</span>
            <span>Last Used</span>
            <span className="text-right">Action</span>
          </div>

          <div className="divide-y divide-[#F5F4EE]">
            {filtered.map((doc) => {
              const isGrounded = doc.status === "grounded";
              const isProcessing = doc.status === "processing";
              const isError = doc.status === "error";

              return (
                <div
                  key={doc.name}
                  className="grid grid-cols-1 sm:grid-cols-[2fr_80px_60px_70px_100px_90px_80px] gap-2 px-6 py-4 items-center hover:bg-[#F9F8F5] transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-[#ECFDF5] text-[#059669] flex items-center justify-center text-base font-bold shrink-0">
                      📄
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#0D3B2E]">{doc.name}</div>
                      <div className="text-[10px] text-[#5E6D67]">
                        {doc.size} · {doc.chapters} chapters
                      </div>
                    </div>
                  </div>

                  <span className="text-xs text-[#5E6D67] hidden sm:block">{doc.type}</span>
                  <span className="text-xs text-[#5E6D67] hidden sm:block">{doc.pages}</span>
                  <span className="text-xs text-[#5E6D67] hidden sm:block">{doc.concepts}</span>

                  <div>
                    <span
                      className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${
                        isGrounded
                          ? "bg-[#ECFDF5] text-[#059669] border border-[#A7F3D0]"
                          : isProcessing
                          ? "bg-[#FEF3C7] text-[#D97706] border border-[#FDE68A]"
                          : "bg-[#FFE4E6] text-[#E11D48] border border-[#FECDD3]"
                      }`}
                    >
                      {isGrounded ? "✓ Grounded" : isProcessing ? "⏳ Ingesting" : "⚠ Error"}
                    </span>
                  </div>

                  <span className="text-xs text-[#5E6D67] hidden sm:block">{doc.lastUsed}</span>

                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => navigate("document-processing")}
                      className="px-3 py-1 rounded-lg bg-[#ECFDF5] hover:bg-[#D1FAE5] text-[#059669] text-xs font-bold transition-colors"
                    >
                      Open
                    </button>
                    {isError && (
                      <button
                        onClick={() => navigate("document-processing")}
                        className="px-2 py-1 rounded-lg bg-[#FFE4E6] hover:bg-[#FECDD3] text-[#E11D48] text-xs font-bold transition-colors"
                      >
                        Retry
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {filtered.length === 0 && (
            <div className="p-12 text-center text-xs text-[#5E6D67]">
              No documents matched your search filter.
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
