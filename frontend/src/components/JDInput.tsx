import { useState } from "react";
import { SAMPLE_JDS } from "../samples";

interface Props {
  onScout: (jd: string, topK: number) => void;
  loading: boolean;
}

export function JDInput({ onScout, loading }: Props) {
  const [jd, setJd] = useState(SAMPLE_JDS[0].text);
  const [topK, setTopK] = useState(8);

  return (
    <div className="bg-white border hairline rounded-3xl p-6 md:p-8 shadow-card">
      <div className="flex flex-wrap items-start justify-between gap-4 mb-5">
        <div>
          <h2 className="font-display text-xl font-bold text-ink-900">
            Job Description
          </h2>
          <p className="text-sm text-ink-500 mt-0.5">
            Paste a JD and let the agent find your top matches.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {SAMPLE_JDS.map((s) => (
            <button
              key={s.label}
              onClick={() => setJd(s.text)}
              disabled={loading}
              className="text-xs px-3 py-1.5 rounded-full bg-cream-100 hover:bg-olive-100 hover:text-olive-800 border hairline text-ink-700 transition disabled:opacity-50"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <textarea
        value={jd}
        onChange={(e) => setJd(e.target.value)}
        rows={14}
        placeholder="Paste your job description here…"
        className="w-full bg-cream-50 text-ink-900 placeholder-ink-400 rounded-2xl border hairline focus:border-olive-500 focus:ring-4 focus:ring-olive-200/50 outline-none p-5 font-mono text-sm leading-relaxed transition"
      />

      <div className="flex flex-wrap items-center justify-between gap-4 mt-5">
        <label className="flex items-center gap-3 text-sm text-ink-700">
          <span className="font-medium">Top results:</span>
          <input
            type="range"
            min={3}
            max={15}
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value))}
            className="accent-olive-700"
          />
          <span className="font-bold text-ink-900 w-6 text-center">
            {topK}
          </span>
        </label>

        <button
          onClick={() => onScout(jd, topK)}
          disabled={loading || jd.trim().length < 20}
          className="btn-dark px-6 py-3 rounded-full text-sm font-semibold inline-flex items-center gap-2"
        >
          {loading ? (
            <>
              <svg
                className="w-4 h-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeOpacity="0.25"
                  strokeWidth="3"
                />
                <path
                  d="M12 2a10 10 0 0 1 10 10"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
              </svg>
              Scouting…
            </>
          ) : (
            <>
              Scout Candidates
              <svg
                className="w-4 h-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
