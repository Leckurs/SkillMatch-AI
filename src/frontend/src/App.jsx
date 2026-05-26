import { useState } from "react";

function App() {
  const [resume, setResume] = useState(null)
  const [jobDescription, setJobDescription] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit() {
    setLoading(true)
    const formData = new FormData()
    formData.append("resume", resume)
    formData.append("job_description", jobDescription)

    const response = await fetch("http://localhost:8000/analyse", {
      method: "POST",
      body: formData
    })

    const data = await response.json()
    setResult(data)
    setLoading(false)
  }

  return(
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-8">
      <div className="bg-white rounded-xl shadow p-8 w-full max-w-lg">
      <h1 className="text-2xl font-bold mb-6">SkillMatch Analyser</h1>
      <div className="mb-4"> 
        <label className="block text-sm font-medium mb-1">Upload Resume (PDF or DOCX)</label>
        <input type="file" accept=".pdf,.docx" onChange={e => setResume(e.target.files[0])}></input>
      </div>
      <div className="mb-6">
        <label className="block text-sm font-medium mb-1">Job Description</label>
        <textarea
        className="w-full border rounded-lg p-3 text-sm"
        rows={5}
        placeholder="Paste the job description here..."
        value={jobDescription}
        onChange={e => setJobDescription(e.target.value)}
        ></textarea>
         </div>
        <button
          className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700"
          onClick={handleSubmit}
          disabled={!resume || !jobDescription}
          >
            {loading ? "Analysing..." : "Analyse"}
          </button>
          {result && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-lg font-bold">Fit Score: {result.fit_score}%</p>
              <p className="mt-2 text-sm font-medium">Matched Skills: {result.matched_skills.join(", ")}</p>
              <p className="mt-1 text-sm font-medium">Missing Skills: {result.missing_skills.join(", ")}</p>
              <p className="mt-2 text-sm text-gray-500">{result.summary}</p>
              </div>

  )}
      </div>
      </div>
  )
}

export default App