import type { ParsedJD } from "../types";

interface Props {
  jd: ParsedJD;
  llmMode: string;
  totalCandidates: number;
}

function Pill({
  children,
  tone = "default",
}: {
  children: React.ReactNode;
  tone?: "default" | "must" | "nice" | "domain";
}) {
  const tones: Record<string, string> = {
    default: "bg-cream-100 border-cream-300 text-ink-700",
    must: "bg-olive-100 border-olive-300 text-olive-800",
    nice: "bg-amber-50 border-amber-200 text-amber-800",
    domain: "bg-emerald-50 border-emerald-200 text-emerald-800",
  };
  return (
    <span
      className={`inline-flex items-center text-xs font-medium px-2.5 py-1 rounded-full border ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

export function ParsedJDCard({ jd, llmMode, totalCandidates }: Props) {
  return (
    <div className="bg-white border hairline rounded-3xl p-6 shadow-card">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-olive-700 font-semibold">
            Parsed JD
          </div>
          <h3 className="font-display text-xl font-bold text-ink-900 mt-1">
            What the agent extracted
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`text-xs font-medium px-2.5 py-1 rounded-full border ${
              llmMode === "gemini"
                ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                : "bg-amber-50 border-amber-200 text-amber-800"
            }`}
          >
            LLM: {llmMode}
          </span>
          <span className="text-xs font-medium px-2.5 py-1 rounded-full border bg-cream-100 border-cream-300 text-ink-700">
            Pool: {totalCandidates}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
        <div>
          <div className="text-[11px] uppercase tracking-wider text-ink-400 font-semibold mb-1">
            Role
          </div>
          <div className="text-ink-900 font-semibold">{jd.role_title}</div>
          <div className="text-ink-500 text-sm capitalize mt-0.5">
            {jd.seniority} · {jd.min_years_experience}–{jd.max_years_experience} yrs
          </div>
        </div>
        <div>
          <div className="text-[11px] uppercase tracking-wider text-ink-400 font-semibold mb-1">
            Location & Mode
          </div>
          <div className="text-ink-900">{jd.location || "Unspecified"}</div>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {jd.work_mode.map((w) => (
              <Pill key={w}>{w}</Pill>
            ))}
            {jd.work_mode.length === 0 && (
              <span className="text-ink-400 text-sm">No mode specified</span>
            )}
          </div>
        </div>
      </div>

      <div className="mt-5">
        <div className="text-[11px] uppercase tracking-wider text-ink-400 font-semibold mb-2">
          Must-have skills
        </div>
        <div className="flex flex-wrap gap-1.5">
          {jd.must_have_skills.length === 0 && (
            <span className="text-ink-400 text-sm">None detected</span>
          )}
          {jd.must_have_skills.map((s) => (
            <Pill key={s} tone="must">
              {s}
            </Pill>
          ))}
        </div>
      </div>

      {jd.nice_to_have_skills.length > 0 && (
        <div className="mt-4">
          <div className="text-[11px] uppercase tracking-wider text-ink-400 font-semibold mb-2">
            Nice-to-have skills
          </div>
          <div className="flex flex-wrap gap-1.5">
            {jd.nice_to_have_skills.map((s) => (
              <Pill key={s} tone="nice">
                {s}
              </Pill>
            ))}
          </div>
        </div>
      )}

      {jd.domains.length > 0 && (
        <div className="mt-4">
          <div className="text-[11px] uppercase tracking-wider text-ink-400 font-semibold mb-2">
            Domains
          </div>
          <div className="flex flex-wrap gap-1.5">
            {jd.domains.map((d) => (
              <Pill key={d} tone="domain">
                {d}
              </Pill>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
