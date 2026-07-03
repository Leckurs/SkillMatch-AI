import { useState } from "react";
import {
  Upload,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";

function ScoreCircle({ score }) {
  const radius = 80;
  const stroke = 10;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset =
    circumference - (score / 100) * circumference;

  const color =
    score >= 70
      ? "#22c55e"
      : score >= 40
      ? "#eab308"
      : "#ef4444";

  return (
    <div className="flex justify-center">
      <div className="relative">
        <svg height={radius * 2} width={radius * 2}>
          <circle
            stroke="#334155"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />

          <circle
            stroke={color}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={`${circumference} ${circumference}`}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            style={{
              transform: "rotate(-90deg)",
              transformOrigin: "50% 50%",
              transition: "stroke-dashoffset 0.8s ease",
            }}
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-3xl font-bold"
            style={{ color }}
          >
            {score}%
          </span>

          <span className="text-xs text-slate-400">
            Match Score
          </span>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

async function handleSubmit() {
  setLoading(true);

  try {
    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    console.time("request");

    const response = await fetch(
      "http://localhost:8000/analyse",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    console.timeEnd("request");

    setResult(data);
  } catch (error) {
    console.error(error);
  } finally {
    setLoading(false);
  }
}

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#0f172a] flex items-center justify-center p-6 relative overflow-hidden">

      {/* Glow Effects */}
      <div className="absolute -top-48 -left-48 w-[1000px] h-[1000px] bg-cyan-400/25 blur-[220px] rounded-full"></div>

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 blur-[180px] rounded-full"></div>

      <div className="absolute -bottom-48 -right-48 w-[1000px] h-[1000px] bg-purple-500/25 blur-[220px] rounded-full"></div>

      <div className="relative w-full max-w-4xl rounded-3xl border border-white/20 bg-slate-800/50 backdrop-blur-xl p-8 shadow-2xl text-white">

        {/* Header */}
        <h1 className="text-5xl font-bold text-center tracking-tight mb-3">
          SkillMatch AI
        </h1>

        <p className="text-center text-slate-300 text-lg mb-10">
          University Project: AI-powered resume and job compatibility analysis web-app
        </p>

        {/* Upload */}
        <div className="mb-8">
          <label className="block mb-3 text-lg font-semibold text-center">
            Upload Resume
          </label>

          <div className="border border-dashed border-slate-500 rounded-2xl p-8 text-center hover:border-cyan-400 hover:bg-white/5 transition">

            <Upload
              className="mx-auto mb-4 text-cyan-400"
              size={40}
            />

            <label className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-cyan-500/20 text-cyan-300 cursor-pointer hover:bg-cyan-500/30 transition">
              <Upload size={18} />
              Choose Resume

              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) =>
                  setResume(e.target.files[0])
                }
                className="hidden"
              />
            </label>

            {resume ? (
              <p className="mt-4 text-green-400 text-sm break-all">
                {resume.name}
              </p>
            ) : (
              <p className="mt-4 text-slate-400 text-sm">
                PDF or DOCX supported
              </p>
            )}
          </div>
        </div>

        {/* Job Description */}
        <div className="mb-8">
          <label className="block mb-3 text-lg font-semibold">
            Job Description
          </label>

          <textarea
            className="w-full bg-slate-900/70 border border-slate-600 rounded-xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
            rows={6}
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) =>
              setJobDescription(e.target.value)
            }
          />
        </div>

        {/* Button */}
        <button
          className="w-full bg-gradient-to-r from-cyan-500 to-purple-500 text-white py-4 rounded-xl font-semibold hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2"
          onClick={handleSubmit}
          disabled={!resume || !jobDescription || loading}
        >
          {loading ? (
            <>
              <Loader2
                size={18}
                className="animate-spin"
              />
              Analysing...
            </>
          ) : (
            <>
              <Sparkles size={18} />
              Analyse Match
            </>
          )}
        </button>

        {/* Results */}
        {result && (
          <div className="mt-10 p-6 bg-slate-900/40 border border-white/10 rounded-2xl">

            <h2 className="text-2xl font-bold text-center mb-6">
              Analysis Result
            </h2>

            <ScoreCircle score={result.fit_score} />

            {/* Matched Skills */}
            <div className="mt-8 mb-6">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle
                  size={18}
                  className="text-green-400"
                />
                <span className="font-semibold">
                  Matched Skills
                </span>
              </div>

              <div className="flex flex-wrap gap-2">
                {result.matched_skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 rounded-full bg-green-500/20 text-green-300 text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle
                  size={18}
                  className="text-red-400"
                />
                <span className="font-semibold">
                  Missing Skills
                </span>
              </div>

            <div className="flex flex-wrap gap-2">
              {result.missing_skills.map((skill) => (
                <span key={skill} className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-sm">
                    {skill}
                  </span>
                  {result.learning_resources && result.learning_resources[skill] && (
                    
                      <a href={result.learning_resources[skill]}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-cyan-400 hover:text-cyan-300 underline"
                    >
                      Learn →
                    </a>
                  )}
                </span>
              ))}
            </div>
            </div>

            {/* Suggested Job Titles */}
            {result.suggested_titles && result.suggested_titles.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={18} className="text-yellow-400" />
                  <span className="font-semibold">Suggested Job Titles</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.suggested_titles.map((item) => (
                    <span key={item.title} className="flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-300 text-sm">
                      {item.title} — {item.match}%
                    </span>
                  ))}
    </div>
  </div>
)}

            {/* Resume Feedback */}
            {result.feedback && result.feedback.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={18} className="text-cyan-400" />
                  <span className="font-semibold">Resume Feedback</span>
                </div>
                <ul className="space-y-2">
                  {result.feedback.map((tip, index) => (
                    <li key={index} className="flex items-start gap-2 text-slate-300 text-sm">
                      <span className="text-cyan-400 mt-0.5">•</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Summary */}
            <div className="border-t border-white/10 pt-5">
              <h3 className="font-semibold mb-3">
                AI Summary
              </h3>

              <p className="text-slate-300 leading-relaxed">
                {result.summary}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;