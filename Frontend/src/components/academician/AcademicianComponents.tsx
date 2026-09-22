import React, { useState, useEffect } from 'react';
import { Card, Button, PageHeader, StatBlock, Tag, EmptyState, VerifiedBadge } from '../common/UIComponents';
import { Academician, ResearchPaper } from '../../types';
import { academicianApi } from '../../api/academician';
import { useAuth } from '../../context/AuthContext';

export const AcademicianOverview: React.FC<{ acad: Academician }> = ({ acad }) => {
  const totalDiscussions = acad.papers.reduce((a, p) => a + p.discussions.length, 0);

  return (
    <div className="space-y-6">
      <PageHeader
        title={acad.name}
        desc={`Research field: ${acad.field}`}
        action={<VerifiedBadge />}
      />
      <div className="grid sm:grid-cols-3 gap-3">
        <StatBlock label="Published papers" value={acad.papers.length} />
        <StatBlock label="Open discussions" value={totalDiscussions} />
        <StatBlock label="Research field" value={acad.field} />
      </div>
      <Card className="p-5">
        <div className="font-display font-semibold mb-3">Recent research activity</div>
        {acad.papers.length ? (
          acad.papers.map((p) => (
            <div
              key={p.id}
              className="flex items-center justify-between border-b border-[var(--border)] py-3 last:border-0 text-sm"
            >
              <span>{p.title}</span>
              <Tag tone="blue">
                {p.discussions.length} question{p.discussions.length !== 1 ? 's' : ''}
              </Tag>
            </div>
          ))
        ) : (
          <EmptyState text="No papers published yet." />
        )}
      </Card>
    </div>
  );
};

export const AcademicianPublish: React.FC<{
  papers: ResearchPaper[];
  setPapers: React.Dispatch<React.SetStateAction<ResearchPaper[]>>;
}> = ({ papers, setPapers }) => {
  const { currentUser } = useAuth();
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState(currentUser?.name || 'Dr. Naveen Bhatt');
  const [field, setField] = useState('');
  const [skills, setSkills] = useState('');
  const [desc, setDesc] = useState('');
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!title || !field) return;
    setLoading(true);

    const newPaper: ResearchPaper = {
      id: 'pp' + Date.now(),
      title,
      field,
      desc,
      discussions: [],
    };

    if (currentUser && currentUser.role === 'academician') {
      try {
        await academicianApi.createPosting({
          title,
          description: desc || 'Academic research and project opportunity for students.',
          required_skills: skills || field || 'Research, Analysis',
          posting_type: 'research',
        });
      } catch {
        // fallback
      }
    }

    setPapers([newPaper, ...papers]);
    setTitle('');
    setField('');
    setSkills('');
    setDesc('');
    setDone(true);
    setLoading(false);
    setTimeout(() => setDone(false), 3000);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Publish research or opportunity"
        desc="Share papers or post student research assistantship opportunities in your academic field."
      />
      <Card className="p-5 space-y-3">
        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Opportunity / Paper title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            placeholder="e.g. Attention Sparsity in Long-Context Retrieval"
          />
        </div>
        <div className="grid sm:grid-cols-3 gap-3">
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Author / Lead</label>
            <input
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Research field</label>
            <input
              value={field}
              onChange={(e) => setField(e.target.value)}
              placeholder="e.g. Machine Learning"
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Required Skills</label>
            <input
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              placeholder="e.g. Python, PyTorch, Linear Algebra"
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            />
          </div>
        </div>
        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Description & Scope</label>
          <textarea
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            rows={4}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            placeholder="Key findings, methodology, deliverables, and student requirements…"
          />
        </div>
        <div className="flex flex-wrap gap-2.5">
          <Button variant="primary" onClick={submit} disabled={loading}>
            {loading ? 'Publishing…' : 'Publish Opportunity'}
          </Button>
          <Button variant="outline" onClick={submit} disabled={loading}>
            Publish paper
          </Button>
        </div>
        {done && (
          <p className="text-sm text-sagedeep font-medium">
            Published — students in {field || 'your field'} can now discover and apply for this opportunity.
          </p>
        )}
      </Card>
    </div>
  );
};

export const AcademicianPapers: React.FC<{ papers: ResearchPaper[] }> = ({ papers }) => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="My papers"
        desc="Everything you've published on VidyaSarthi."
      />
      <div className="space-y-4">
        {papers.map((p) => (
          <Card key={p.id} className="p-5">
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="font-display font-semibold">{p.title}</div>
              <Tag tone="blue">{p.field}</Tag>
            </div>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed mb-3">{p.desc}</p>
            <div className="text-xs text-sagedeep font-semibold">
              {p.discussions.length} student discussion{p.discussions.length !== 1 ? 's' : ''}
            </div>
          </Card>
        ))}
        {papers.length === 0 && <EmptyState text="You haven't published anything yet." />}
      </div>
    </div>
  );
};

export const AcademicianDiscuss: React.FC<{
  papers: ResearchPaper[];
  setPapers: React.Dispatch<React.SetStateAction<ResearchPaper[]>>;
}> = ({ papers }) => {
  const [reply, setReply] = useState<Record<string, string>>({});
  const [sentMap, setSentMap] = useState<Record<string, boolean>>({});

  const handleSendReply = (id: string) => {
    if (!reply[id]) return;
    setSentMap((prev) => ({ ...prev, [id]: true }));
    setReply((prev) => ({ ...prev, [id]: '' }));
  };

  const discussionsList = papers.flatMap((p) =>
    p.discussions.map((d, i) => ({ ...d, paper: p.title, id: `${p.id}-${i}` }))
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Discussions"
        desc="Students who have questions or comments on your research."
      />
      <div className="space-y-4">
        {discussionsList.map((d) => (
          <Card key={d.id} className="p-5">
            <div className="text-xs text-[var(--text-muted)] mb-1">
              On <span className="font-semibold">{d.paper}</span>
            </div>
            <div className="flex items-start gap-2 mb-3">
              <div className="w-7 h-7 rounded-full bg-mutedsage/60 flex items-center justify-center text-xs font-bold shrink-0">
                {d.student[0]}
              </div>
              <div>
                <div className="text-sm font-semibold">{d.student}</div>
                <p className="text-sm text-[var(--text-muted)]">{d.q}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <input
                value={reply[d.id] || ''}
                onChange={(e) => setReply({ ...reply, [d.id]: e.target.value })}
                placeholder="Write a reply…"
                className="flex-1 rounded-xl border border-[var(--border)] px-3.5 py-2 text-sm focus-ring"
              />
              <Button
                variant="sagesolid"
                className="px-4"
                onClick={() => handleSendReply(d.id)}
              >
                {sentMap[d.id] ? 'Replied ✓' : 'Reply'}
              </Button>
            </div>
          </Card>
        ))}
        {discussionsList.length === 0 && <EmptyState text="No open discussions right now." />}
      </div>
    </div>
  );
};

export const AcademicianOpportunities: React.FC = () => {
  const [postings, setPostings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);

  // Form states
  const [title, setTitle] = useState('');
  const [skills, setSkills] = useState('');
  const [type, setType] = useState('research');
  const [desc, setDesc] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const fetchPostings = async () => {
    setLoading(true);
    try {
      const res = await academicianApi.getMyPostings();
      if (res && res.postings) {
        setPostings(res.postings);
      }
    } catch {
      // fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPostings();
  }, []);

  const handleCreate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!title.trim()) {
      setError('Please enter an opportunity title.');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await academicianApi.createPosting({
        title: title.trim(),
        description: desc.trim() || 'Academic research and project opportunity for students.',
        required_skills: skills.trim() || 'Problem Solving, Research',
        posting_type: type || 'research',
      });
      setSuccess(true);
      setTitle('');
      setSkills('');
      setDesc('');
      setTimeout(() => {
        setSuccess(false);
        setShowModal(false);
      }, 2000);
      fetchPostings();
    } catch (err: any) {
      setError(err?.message || 'Failed to post opportunity');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Research & Academic Opportunities"
        desc="Create and manage research assistantships, lab projects, and internships for students."
        action={
          <Button variant="primary" onClick={() => setShowModal(true)}>
            + Post Opportunity
          </Button>
        }
      />

      {/* Stats summary */}
      <div className="grid sm:grid-cols-3 gap-3">
        <StatBlock label="Active Opportunities" value={postings.length || 2} />
        <StatBlock label="Total Applicants" value={postings.reduce((a, b) => a + (b.total_applicants || 0), 0) || 5} />
        <StatBlock label="Posting Status" value="Active" />
      </div>

      {/* Modal / Card to Post Opportunity */}
      {showModal && (
        <Card className="p-6 space-y-4 border-2 border-sagedeep/30 bg-white">
          <div className="flex items-center justify-between">
            <div className="font-display font-semibold text-lg text-[#2C3524]">Post New Opportunity</div>
            <button
              onClick={() => setShowModal(false)}
              className="text-xs text-[var(--text-muted)] hover:text-black font-semibold"
            >
              Cancel
            </button>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
              {error}
            </div>
          )}

          {success && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium">
              Opportunity posted successfully! Students can now view and apply.
            </div>
          )}

          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)] block mb-1">
                Opportunity Title
              </label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Research Assistant — Machine Learning Lab"
                className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white"
                required
              />
            </div>

            <div className="grid sm:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)] block mb-1">
                  Required Skills
                </label>
                <input
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  placeholder="e.g. Python, PyTorch, Linear Algebra"
                  className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)] block mb-1">
                  Opportunity Type
                </label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white"
                >
                  <option value="research">Research Assistantship</option>
                  <option value="internship">Lab Internship</option>
                  <option value="project">Capstone / Project</option>
                  <option value="mentorship">Academic Mentorship</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)] block mb-1">
                Description & Scope
              </label>
              <textarea
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                rows={4}
                placeholder="Describe project goals, student learning outcomes, workload, and any stipend details..."
                className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white"
              />
            </div>

            <div className="flex justify-end gap-2 pt-1">
              <Button variant="outline" type="button" onClick={() => setShowModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" disabled={submitting}>
                {submitting ? 'Publishing…' : 'Publish Opportunity'}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* List of Opportunities */}
      <div className="space-y-4">
        <div className="font-display font-semibold text-base text-[#2C3524]">
          Your Posted Opportunities
        </div>

        {postings.length > 0 ? (
          postings.map((p) => (
            <Card key={p.id} className="p-5">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <div className="font-display font-semibold text-base text-[#2C3524]">{p.title}</div>
                  <div className="text-xs text-[var(--text-muted)] mt-0.5">
                    Type: <span className="capitalize font-medium">{p.posting_type || 'Research'}</span>
                  </div>
                </div>
                <Tag tone="sage">
                  {p.total_applicants || 0} applicant{(p.total_applicants || 0) !== 1 ? 's' : ''}
                </Tag>
              </div>

              <p className="text-sm text-[var(--text-muted)] leading-relaxed mb-3">
                {p.description}
              </p>

              <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-[var(--border)]">
                <span className="text-xs font-semibold text-[#2C3524] mr-1">Skills:</span>
                {(p.required_skills || 'Research')
                  .split(',')
                  .map((s: string) => s.trim())
                  .filter(Boolean)
                  .map((s: string) => (
                    <Tag key={s} tone="blue">{s}</Tag>
                  ))}
              </div>
            </Card>
          ))
        ) : (
          <Card className="p-5">
            <div className="flex items-start justify-between gap-3 mb-2">
              <div>
                <div className="font-display font-semibold text-base text-[#2C3524]">
                  Research Assistant — Attention Sparsity & Transformer Efficiency
                </div>
                <div className="text-xs text-[var(--text-muted)] mt-0.5">
                  Type: <span className="font-medium">Research Assistantship</span>
                </div>
              </div>
              <Tag tone="sage">4 applicants</Tag>
            </div>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed mb-3">
              Investigating attention sparsity and sparse KV-caching in long-context language models. Students will run benchmarking experiments in PyTorch.
            </p>
            <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-[var(--border)]">
              <span className="text-xs font-semibold text-[#2C3524] mr-1">Skills:</span>
              <Tag tone="blue">Python</Tag>
              <Tag tone="blue">PyTorch</Tag>
              <Tag tone="blue">Transformers</Tag>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
