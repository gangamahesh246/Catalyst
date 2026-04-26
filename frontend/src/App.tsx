import { useState } from "react";
import { JDInput } from "./components/JDInput";
import { ParsedJDCard } from "./components/ParsedJDCard";
import { CandidateCard } from "./components/CandidateCard";
import type { ScoutResponse } from "./types";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScoutResponse | null>(null);

  const handleScout = async (jd: string, topK: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/scout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jd_text: jd, top_k: topK }),
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(`Request failed (${res.status}): ${detail}`);
      }
      const data: ScoutResponse = await res.json();
      setResult(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="max-w-6xl mx-auto w-full px-5 md:px-8 pt-10 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-olive-700 flex items-center justify-center shadow-card">
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#f7f5ed"
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </div>
          <div>
            <h1 className="font-display text-3xl md:text-4xl font-bold tracking-tight text-ink-900">
              Talent Scouting Agent
            </h1>
            <p className="text-sm text-ink-500 mt-0.5">
              JD in · ranked, explainable shortlist out · in seconds.
            </p>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-5 md:px-8 pb-16 grid grid-cols-1 lg:grid-cols-5 gap-6">
        <section className="lg:col-span-3 space-y-6">
          <JDInput onScout={handleScout} loading={loading} />
          {error && (
            <div className="bg-rose-50 border border-rose-200 rounded-2xl p-4 text-rose-800 text-sm shadow-card">
              {error}
            </div>
          )}
          {result && (
            <ParsedJDCard
              jd={result.parsed_jd}
              llmMode={result.llm_mode}
              totalCandidates={result.total_candidates_considered}
            />
          )}
        </section>

        <section className="lg:col-span-2">
          <div className="lg:sticky lg:top-6">
            <div className="flex items-baseline justify-between mb-4">
              <h2 className="font-display text-xl font-bold text-ink-900">
                Ranked Shortlist
              </h2>
              {result && (
                <span className="text-xs text-ink-500 font-medium">
                  {result.matches.length} candidates
                </span>
              )}
            </div>

            {!result && !loading && (
              <div className="bg-white border hairline rounded-3xl p-8 text-center shadow-card">
                <div className="w-12 h-12 mx-auto rounded-2xl bg-olive-100 text-olive-700 flex items-center justify-center mb-4">
                  <svg
                    width="22"
                    height="22"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.3-4.3" />
                  </svg>
                </div>
                <h3 className="font-display text-lg font-bold text-ink-900">
                  Awaiting your JD
                </h3>
                <p className="text-sm text-ink-500 mt-1">
                  Paste a job description on the left and hit{" "}
                  <span className="text-olive-700 font-semibold">
                    Scout Candidates
                  </span>
                  .
                </p>
              </div>
            )}

            {loading && (
              <div className="bg-white border hairline rounded-3xl p-8 text-center shadow-card animate-pulse">
                <div className="text-4xl mb-3">🔍</div>
                <h3 className="font-display text-lg font-bold text-ink-900">
                  Scouting…
                </h3>
                <p className="text-sm text-ink-500 mt-1">
                  Parsing the JD, retrieving candidates, scoring matches.
                </p>
              </div>
            )}

            {result && (
              <div className="space-y-3 max-h-[calc(100vh-160px)] overflow-y-auto pr-1">
                {result.matches.map((m, idx) => (
                  <CandidateCard
                    key={m.candidate.id}
                    match={m}
                    rank={idx + 1}
                  />
                ))}
              </div>
            )}
          </div>
        </section>
      </main>

      <footer className="text-center text-ink-400 text-xs pb-6">
        Talent Scouting Agent · single-agent prototype · TF-IDF retrieval +
        multi-dimensional scoring + LLM explanations
      </footer>
    </div>
  );
}
