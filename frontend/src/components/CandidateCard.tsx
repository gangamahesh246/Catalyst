import { useState } from "react";
import type { MatchedCandidate } from "../types";

interface Props {
  match: MatchedCandidate;
  rank: number;
}

function ScoreRing({ value }: { value: number }) {
  const r = 30;
  const c = 2 * Math.PI * r;
  const offset = c - (Math.max(0, Math.min(100, value)) / 100) * c;
  const tone =
    value >= 75
      ? "stroke-olive-600"
      : value >= 55
      ? "stroke-olive-400"
      : "stroke-amber-500";
  return (
    <div className="relative w-[78px] h-[78px] shrink-0">
      <svg viewBox="0 0 80 80" className="w-full h-full -rotate-90">
        <circle
          cx="40"
          cy="40"
          r={r}
          className="stroke-cream-200"
          strokeWidth="8"
          fill="none"
        />
        <circle
          cx="40"
          cy="40"
          r={r}
          className={tone}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          fill="none"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center flex-col">
        <span className="text-lg font-bold text-ink-900 leading-none">
          {Math.round(value)}
        </span>
        <span className="text-[9px] text-ink-400 mt-0.5 font-semibold uppercase tracking-wider">
          match
        </span>
      </div>
    </div>
  );
}

function Bar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-ink-500 w-20 shrink-0 font-medium">
        {label}
      </span>
      <div className="flex-1 h-2 bg-cream-200 rounded-full overflow-hidden">
        <div
          className="h-full score-bar rounded-full"
          style={{ width: `${Math.max(2, Math.min(100, value))}%` }}
        />
      </div>
      <span className="text-xs text-ink-700 w-9 text-right font-semibold">
        {Math.round(value)}
      </span>
    </div>
  );
}

export function CandidateCard({ match, rank }: Props) {
  const [open, setOpen] = useState(rank === 1);
  const c = match.candidate;
  const b = match.breakdown;

  return (
    <div className="bg-white border hairline rounded-3xl p-5 shadow-card hover:shadow-cardHover transition">
      <div className="flex items-start gap-4">
        <ScoreRing value={match.match_score} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-olive-100 text-olive-800 font-bold tracking-wider">
              #{rank}
            </span>
            <h4 className="text-ink-900 font-bold truncate">{c.name}</h4>
            <span className="text-ink-400 text-sm">·</span>
            <span className="text-ink-700 text-sm font-medium">{c.title}</span>
          </div>
          <div className="text-xs text-ink-500 mt-1">
            {c.years_experience} yrs · {c.location}
            {c.current_company && ` · @ ${c.current_company}`}
          </div>
          <p className="text-sm text-ink-700 mt-3 leading-relaxed">
            {match.explanation}
          </p>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {match.matched_must_have.map((s) => (
          <span
            key={s}
            className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 font-medium"
          >
            ✓ {s}
          </span>
        ))}
        {match.missing_must_have.map((s) => (
          <span
            key={s}
            className="text-xs px-2 py-0.5 rounded-full bg-rose-50 border border-rose-200 text-rose-800 font-medium"
          >
            ✗ {s}
          </span>
        ))}
        {match.matched_nice_to_have.map((s) => (
          <span
            key={s}
            className="text-xs px-2 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 font-medium"
          >
            ★ {s}
          </span>
        ))}
      </div>

      <button
        onClick={() => setOpen((v) => !v)}
        className="mt-3 text-xs font-semibold text-olive-700 hover:text-olive-900 transition"
      >
        {open ? "Hide details ▲" : "Show breakdown ▼"}
      </button>

      {open && (
        <div className="mt-4 space-y-2.5 border-t hairline pt-4">
          <Bar label="Skills" value={b.skills_score} />
          <Bar label="Experience" value={b.experience_score} />
          <Bar label="Domain" value={b.domain_score} />
          <Bar label="Location" value={b.location_score} />
          <Bar label="Semantic" value={b.semantic_score} />

          <div className="mt-4">
            <div className="text-[11px] uppercase tracking-wider text-ink-400 font-semibold mb-1.5">
              Profile summary
            </div>
            <p className="text-sm text-ink-700 leading-relaxed">{c.summary}</p>
          </div>

          <div className="mt-3">
            <div className="text-[11px] uppercase tracking-wider text-ink-400 font-semibold mb-1.5">
              All skills
            </div>
            <div className="flex flex-wrap gap-1">
              {c.skills.map((s) => (
                <span
                  key={s}
                  className="text-xs px-2 py-0.5 rounded-full bg-cream-100 border hairline text-ink-700"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
