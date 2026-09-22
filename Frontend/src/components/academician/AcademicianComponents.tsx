import React, { useState } from 'react';
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
          description: desc || 'Academic research collaboration opportunity',
          required_skills: field,
          posting_type: 'research_collaboration',
        });
      } catch {
        // fallback
      }
    }

    setPapers([newPaper, ...papers]);
    setTitle('');
    setField('');
    setDesc('');
    setDone(true);
    setLoading(false);
    setTimeout(() => setDone(false), 3000);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Publish a research paper"
        desc="Help this reach students and academicians working in the same field."
      />
      <Card className="p-5 space-y-3">
        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Paper title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            placeholder="e.g. Attention Sparsity in Long-Context Retrieval"
          />
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Author</label>
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
        </div>
        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Description</label>
          <textarea
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            rows={4}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            placeholder="Key findings, methodology, and abstract…"
          />
        </div>
        <Button variant="primary" onClick={submit} disabled={loading}>
          {loading ? 'Publishing…' : 'Publish paper'}
        </Button>
        {done && (
          <p className="text-sm text-sagedeep font-medium">
            Published — students in {field || 'your field'} can now discover it.
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
