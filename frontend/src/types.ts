export interface Candidate {
  id: string;
  name: string;
  title: string;
  years_experience: number;
  location: string;
  work_mode: string[];
  skills: string[];
  domains: string[];
  summary: string;
  current_company?: string;
  linkedin?: string;
}

export interface ParsedJD {
  role_title: string;
  seniority: string;
  min_years_experience: number;
  max_years_experience: number;
  must_have_skills: string[];
  nice_to_have_skills: string[];
  domains: string[];
  location?: string | null;
  work_mode: string[];
  responsibilities: string[];
  raw_jd: string;
}

export interface ScoreBreakdown {
  skills_score: number;
  experience_score: number;
  domain_score: number;
  location_score: number;
  semantic_score: number;
}

export interface MatchedCandidate {
  candidate: Candidate;
  match_score: number;
  breakdown: ScoreBreakdown;
  matched_must_have: string[];
  missing_must_have: string[];
  matched_nice_to_have: string[];
  explanation: string;
}

export interface ScoutResponse {
  parsed_jd: ParsedJD;
  matches: MatchedCandidate[];
  total_candidates_considered: number;
  llm_mode: string;
}
