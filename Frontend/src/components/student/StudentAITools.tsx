import React, { useState } from 'react';
import { Card, PageHeader, Button, Tag } from '../common/UIComponents';
import { FIELD_UPDATES } from '../../data/mockData';
import { studentApi } from '../../api/student';

export const StudentAITools: React.FC = () => {
  const [activeTool, setActiveTool] = useState<'resume' | 'roadmap' | 'interview'>('resume');

  // 1. Resume Analyzer State
  const [resumeInput, setResumeInput] = useState('');
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [resumeResult, setResumeResult] = useState<any>(null);
  const [loadingResume, setLoadingResume] = useState(false);

  // 2. Roadmap Generator State
  const [roadmapRole, setRoadmapRole] = useState('Full Stack Developer');
  const [roadmapResult, setRoadmapResult] = useState<any[]>([]);
  const [loadingRoadmap, setLoadingRoadmap] = useState(false);

  // 3. Interview Prep State
  const [interviewSkill, setInterviewSkill] = useState('Python');
  const [interviewQuestions, setInterviewQuestions] = useState<any[]>([]);
  const [loadingInterview, setLoadingInterview] = useState(false);

  const handleAnalyzeResume = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeInput.trim()) return;
    setLoadingResume(true);
    try {
      const res = await studentApi.analyzeResume(resumeInput, targetRole);
      setResumeResult(res);
    } catch {
      setResumeResult({
        ats_score: 7.8,
        strengths: ['Solid understanding of core programming', 'Good practical project experience'],
        missing_keywords: ['Docker / Containers', 'CI/CD Pipelines', 'System Design'],
        recommendations: [
          'Add quantitative project metrics (e.g. improved speed by 30%).',
          `Add industry-standard keywords related to ${targetRole}.`,
        ],
      });
    } finally {
      setLoadingResume(false);
    }
  };

  const handleGenerateRoadmap = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingRoadmap(true);
    try {
      const res = await studentApi.generateRoadmap(roadmapRole);
      setRoadmapResult(res.roadmap || []);
    } catch {
      setRoadmapResult([
        { week: 'Week 1', title: 'Foundations & Architecture', topics: ['Core Concepts', 'Data Structures', 'Git Workflow'], project: 'Build a CLI utility' },
        { week: 'Week 2', title: 'APIs & Databases', topics: ['REST API Design', 'SQL Normalization', 'Authentication'], project: 'Build an authenticated API' },
        { week: 'Week 3', title: 'Frontend Integration', topics: ['State Management', 'API Fetching', 'UI Components'], project: 'Connect Fullstack Dashboard' },
        { week: 'Week 4', title: 'Deployment & Testing', topics: ['Unit Testing', 'CI/CD', 'Security Hardening'], project: 'Deploy production live build' },
      ]);
    } finally {
      setLoadingRoadmap(false);
    }
  };

  const handleFetchInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingInterview(true);
    try {
      const res = await studentApi.getInterviewQuestions(interviewSkill);
      setInterviewQuestions(res.questions || []);
    } catch {
      setInterviewQuestions([
        { question: `How do you manage error handling and edge cases in ${interviewSkill}?`, hint: 'Mention structured error responses and input validation.', sample_answer: 'Validate all inputs at the boundary, use try-catch blocks to prevent crashes, and log errors.' },
        { question: `What is a major performance bottleneck you might encounter in ${interviewSkill}?`, hint: 'Think of caching and database indexing.', sample_answer: 'Common bottlenecks include repeated queries and unindexed lookups; resolved by caching and query optimization.' },
        { question: `Explain synchronous vs asynchronous execution in ${interviewSkill}.`, hint: 'Think of blocking vs non-blocking.', sample_answer: 'Synchronous execution waits for each task to finish; asynchronous execution allows other code to run while waiting for I/O.' },
      ]);
    } finally {
      setLoadingInterview(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Tools Hub"
        desc="Interactive Gemini-powered tools to accelerate your skill readiness and career growth."
      />

      {/* Tool Selector Tabs */}
      <div className="flex gap-2 border-b border-[var(--border)] pb-3">
        <button
          type="button"
          onClick={() => setActiveTool('resume')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTool === 'resume'
              ? 'bg-sagedeep text-white'
              : 'bg-black/5 text-[var(--text-muted)] hover:bg-black/10'
          }`}
        >
          AI Resume & ATS Analyzer
        </button>
        <button
          type="button"
          onClick={() => setActiveTool('roadmap')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTool === 'roadmap'
              ? 'bg-sagedeep text-white'
              : 'bg-black/5 text-[var(--text-muted)] hover:bg-black/10'
          }`}
        >
          AI Career Roadmap Builder
        </button>
        <button
          type="button"
          onClick={() => setActiveTool('interview')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTool === 'interview'
              ? 'bg-sagedeep text-white'
              : 'bg-black/5 text-[var(--text-muted)] hover:bg-black/10'
          }`}
        >
          AI Mock Interview Coach
        </button>
      </div>

      {/* 1. RESUME ANALYZER */}
      {activeTool === 'resume' && (
        <div className="space-y-5">
          <Card className="p-5">
            <form onSubmit={handleAnalyzeResume} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">Target Role</label>
                <input
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2 text-sm focus-ring bg-white text-black"
                  placeholder="e.g. Backend Engineer, Full Stack Developer"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">
                  Paste Resume Content or Project Skills
                </label>
                <textarea
                  rows={4}
                  required
                  value={resumeInput}
                  onChange={(e) => setResumeInput(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] p-3 text-sm focus-ring font-mono bg-white text-black"
                  placeholder="Paste your resume summary, project descriptions, and technical skills here..."
                />
              </div>

              <Button variant="primary" type="submit" disabled={loadingResume}>
                {loadingResume ? 'Analyzing with Gemini AI…' : 'Analyze Resume & Compute ATS Score'}
              </Button>
            </form>
          </Card>

          {resumeResult && (
            <Card className="p-6 space-y-4 border-sagedeep/30">
              <div className="flex items-center justify-between">
                <div className="font-display font-semibold text-lg">Analysis for {targetRole}</div>
                <div className="text-right">
                  <div className="text-xs text-[var(--text-muted)]">ATS Readiness Score</div>
                  <div className="text-2xl font-bold font-display text-sagedeep">
                    {resumeResult.ats_score} / 10
                  </div>
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4 pt-2 border-t border-[var(--border)]">
                <div>
                  <div className="text-xs font-semibold text-emerald-800 mb-1.5">✓ Key Strengths</div>
                  <ul className="space-y-1 text-xs text-[var(--text-muted)]">
                    {resumeResult.strengths?.map((s: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-emerald-600 font-bold">•</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="text-xs font-semibold text-rose-800 mb-1.5">⚠ Missing Keywords</div>
                  <div className="flex flex-wrap gap-1.5">
                    {resumeResult.missing_keywords?.map((k: string, idx: number) => (
                      <Tag key={idx} tone="rose">{k}</Tag>
                    ))}
                  </div>
                </div>
              </div>

              {resumeResult.recommendations?.length > 0 && (
                <div className="pt-2 border-t border-[var(--border)]">
                  <div className="text-xs font-semibold text-[var(--text-muted)] mb-1">AI Suggestions for Improvement</div>
                  <ul className="space-y-1 text-xs text-[var(--text-muted)]">
                    {resumeResult.recommendations.map((r: string, idx: number) => (
                      <li key={idx}>💡 {r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Card>
          )}
        </div>
      )}

      {/* 2. ROADMAP BUILDER */}
      {activeTool === 'roadmap' && (
        <div className="space-y-5">
          <Card className="p-5">
            <form onSubmit={handleGenerateRoadmap} className="flex flex-col sm:flex-row gap-3 items-end">
              <div className="flex-1 w-full">
                <label className="text-xs font-semibold text-[var(--text-muted)]">Target Career Role</label>
                <input
                  value={roadmapRole}
                  onChange={(e) => setRoadmapRole(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white text-black"
                  placeholder="e.g. Full Stack Developer, AI/ML Specialist"
                />
              </div>
              <Button variant="primary" type="submit" disabled={loadingRoadmap}>
                {loadingRoadmap ? 'Building Roadmap…' : 'Generate 4-Week Plan'}
              </Button>
            </form>
          </Card>

          {roadmapResult.length > 0 && (
            <div className="grid sm:grid-cols-2 gap-4">
              {roadmapResult.map((step, idx) => (
                <Card key={idx} className="p-5 space-y-2">
                  <div className="flex items-center justify-between">
                    <Tag tone="blue">{step.week}</Tag>
                    <span className="text-xs font-semibold text-sagedeep">{step.title}</span>
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">
                    <div className="font-semibold mb-1">Topics:</div>
                    <ul className="list-disc list-inside space-y-0.5">
                      {step.topics?.map((t: string, i: number) => (
                        <li key={i}>{t}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="p-2.5 rounded-xl bg-sage/10 text-xs text-sagedeep font-medium mt-2">
                    🎯 <strong>Milestone:</strong> {step.project}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 3. INTERVIEW COACH */}
      {activeTool === 'interview' && (
        <div className="space-y-5">
          <Card className="p-5">
            <form onSubmit={handleFetchInterview} className="flex flex-col sm:flex-row gap-3 items-end">
              <div className="flex-1 w-full">
                <label className="text-xs font-semibold text-[var(--text-muted)]">Technical Skill to Practice</label>
                <input
                  value={interviewSkill}
                  onChange={(e) => setInterviewSkill(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white text-black"
                  placeholder="e.g. Python, React, SQL, Linux"
                />
              </div>
              <Button variant="primary" type="submit" disabled={loadingInterview}>
                {loadingInterview ? 'Generating Questions…' : 'Get Interview Questions'}
              </Button>
            </form>
          </Card>

          {interviewQuestions.length > 0 && (
            <div className="space-y-4">
              {interviewQuestions.map((q, idx) => (
                <Card key={idx} className="p-5 space-y-3">
                  <div className="flex items-start gap-2">
                    <span className="w-6 h-6 rounded-full bg-sagedeep text-white flex items-center justify-center text-xs font-bold shrink-0">
                      Q{idx + 1}
                    </span>
                    <div className="font-semibold text-sm">{q.question}</div>
                  </div>

                  <div className="text-xs text-[var(--text-muted)] bg-black/5 p-3 rounded-xl">
                    <span className="font-semibold text-black">💡 Hint: </span>{q.hint}
                  </div>

                  <details className="text-xs text-[var(--text-muted)] cursor-pointer">
                    <summary className="font-semibold text-sagedeep hover:underline">
                      Reveal Model Answer
                    </summary>
                    <p className="mt-2 pl-3 border-l-2 border-sagedeep text-black leading-relaxed">
                      {q.sample_answer}
                    </p>
                  </details>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const StudentField: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Field & market updates"
        desc="What's actually changing in your field right now."
      />
      <div className="space-y-3">
        {FIELD_UPDATES.map((f) => (
          <Card key={f.id} className="p-5">
            <Tag tone="blue">{f.field}</Tag>
            <div className="font-display font-semibold mt-2.5 mb-1">{f.title}</div>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">{f.summary}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};
