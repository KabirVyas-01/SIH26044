import React, { useState } from 'react';
import {
  Card,
  Button,
  PageHeader,
  StatBlock,
  Tag,
  EmptyState,
  VerifiedBadge,
} from '../common/UIComponents';
import { Company, Student, University } from '../../types';
import { STUDENTS, UNIVERSITIES } from '../../data/mockData';
import { industryApi } from '../../api/industry';
import { useAuth } from '../../context/AuthContext';

export const IndustryOverview: React.FC<{ company: Company }> = ({ company }) => {
  const { currentUser } = useAuth();
  const [showPostModal, setShowPostModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSkills, setNewSkills] = useState('');
  const [newType, setNewType] = useState('job');
  const [roles, setRoles] = useState(company.roles);
  const [loading, setLoading] = useState(false);

  const handleCreatePosting = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newSkills) return;
    setLoading(true);

    if (currentUser && currentUser.role === 'industry') {
      try {
        await industryApi.createPosting({
          title: newTitle,
          description: newDesc || `${newTitle} opening at ${company.name}`,
          required_skills: newSkills,
          posting_type: newType,
        });
      } catch {
        // fallback
      }
    }

    const newRole = {
      id: 'r' + Date.now(),
      title: newTitle,
      skills: newSkills.split(',').map((s) => ({ name: s.trim(), min: 70 })),
    };

    setRoles([newRole, ...roles]);
    setNewTitle('');
    setNewDesc('');
    setNewSkills('');
    setShowPostModal(false);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={company.name}
        desc={`${company.field} · hiring on VidyaSarthi`}
        action={
          <Button variant="primary" onClick={() => setShowPostModal((v) => !v)}>
            + Post new opportunity
          </Button>
        }
      />

      <div className="grid sm:grid-cols-3 gap-3">
        <StatBlock label="Open roles" value={roles.length} />
        <StatBlock label="Candidates matched" value={STUDENTS.length} />
        <StatBlock label="Universities in network" value={UNIVERSITIES.length} />
      </div>

      {showPostModal && (
        <Card className="p-5">
          <form onSubmit={handleCreatePosting} className="space-y-3">
            <div className="font-display font-semibold">Post a Job or Internship</div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">Role Title</label>
              <input
                required
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Cloud Engineer Associate"
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring"
              />
            </div>
            <div className="grid sm:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">Type</label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white"
                >
                  <option value="job">Full-time Job</option>
                  <option value="internship">Internship</option>
                  <option value="project">Project</option>
                  <option value="apprenticeship">Apprenticeship</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">Required Skills (comma separated)</label>
                <input
                  required
                  value={newSkills}
                  onChange={(e) => setNewSkills(e.target.value)}
                  placeholder="e.g. Python, Docker, AWS"
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring"
                />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">Description</label>
              <textarea
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                rows={3}
                placeholder="Role responsibilities and requirements…"
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring"
              />
            </div>
            <div className="flex gap-2">
              <Button variant="sagesolid" type="submit" disabled={loading}>
                {loading ? 'Posting…' : 'Publish Role'}
              </Button>
              <Button variant="ghost" type="button" onClick={() => setShowPostModal(false)}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      <Card className="p-5">
        <div className="font-display font-semibold mb-4">Open roles</div>
        <div className="space-y-3">
          {roles.map((r) => (
            <div
              key={r.id}
              className="flex items-center justify-between border-b border-[var(--border)] pb-3 last:border-0 last:pb-0"
            >
              <div>
                <div className="text-sm font-semibold">{r.title}</div>
                <div className="flex gap-1.5 mt-1">
                  {r.skills.map((s) => (
                    <Tag key={s.name}>
                      {s.name} ≥ {s.min}%
                    </Tag>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

interface IndustryFilterState {
  skill: string;
  minSkill: number;
  minPotential: number;
  field: string;
  university: string;
}

export const IndustryFilters: React.FC<{
  filters: IndustryFilterState;
  setFilters: React.Dispatch<React.SetStateAction<IndustryFilterState>>;
}> = ({ filters, setFilters }) => {
  const skillOpts = [...new Set(STUDENTS.flatMap((s) => s.skills.map((k) => k.name)))];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Requirements & filters"
        desc="Set what you're looking for — results update on the Search Results tab."
      />
      <Card className="p-5 space-y-5">
        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Skill</label>
          <select
            value={filters.skill}
            onChange={(e) => setFilters({ ...filters, skill: e.target.value })}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white"
          >
            <option value="">Any skill</option>
            {skillOpts.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <div className="flex justify-between text-xs font-semibold text-[var(--text-muted)] mb-1">
            <span>Minimum skill percentage</span>
            <span>{filters.minSkill}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={filters.minSkill}
            onChange={(e) => setFilters({ ...filters, minSkill: +e.target.value })}
            className="w-full accent-[#4B5A3A]"
          />
        </div>
        <div>
          <div className="flex justify-between text-xs font-semibold text-[var(--text-muted)] mb-1">
            <span>Minimum potential</span>
            <span>{filters.minPotential}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={filters.minPotential}
            onChange={(e) => setFilters({ ...filters, minPotential: +e.target.value })}
            className="w-full accent-[#4B5A3A]"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Field of work</label>
          <select
            value={filters.field}
            onChange={(e) => setFilters({ ...filters, field: e.target.value })}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white"
          >
            <option value="">Any field</option>
            {[...new Set(STUDENTS.map((s) => s.field))].map((f) => (
              <option key={f}>{f}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">University priority</label>
          <select
            value={filters.university}
            onChange={(e) => setFilters({ ...filters, university: e.target.value })}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring bg-white"
          >
            <option value="">Any university</option>
            {UNIVERSITIES.map((u) => (
              <option key={u.id}>{u.name}</option>
            ))}
          </select>
        </div>
      </Card>
    </div>
  );
};

export const IndustryResults: React.FC<{
  filters: IndustryFilterState;
  connections: (string | number)[];
  setConnections: React.Dispatch<React.SetStateAction<(string | number)[]>>;
}> = ({ filters, connections, setConnections }) => {
  const matches = STUDENTS.filter((s) => {
    const skillOk =
      !filters.skill ||
      s.skills.some((k) => k.name === filters.skill && k.score >= filters.minSkill);
    const potOk = s.potential >= filters.minPotential;
    const fieldOk = !filters.field || s.field === filters.field;
    const uniOk = !filters.university || s.university === filters.university;
    return skillOk && potOk && fieldOk && uniOk;
  });

  const toggle = (s: Student) =>
    setConnections((prev) =>
      prev.includes(s.id) ? prev.filter((id) => id !== s.id) : [...prev, s.id]
    );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Search results"
        desc={`${matches.length} student${matches.length !== 1 ? 's' : ''} match your current requirements.`}
      />
      <div className="grid sm:grid-cols-2 gap-4">
        {matches.map((s) => (
          <Card key={s.id} className="p-5">
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-mutedsage/60 flex items-center justify-center text-xs font-bold">
                  {s.name[0]}
                </div>
                <div>
                  <div className="text-sm font-semibold flex items-center gap-1.5">
                    {s.name} <VerifiedBadge small />
                  </div>
                  <div className="text-[11px] text-[var(--text-muted)]">{s.university}</div>
                </div>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5 mb-3">
              {s.skills.map((k) => (
                <Tag key={k.name} tone={k.score >= k.min ? 'sage' : 'amber'}>
                  {k.name} {k.score}%
                </Tag>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs mb-3">
              <div>
                <span className="text-[var(--text-muted)]">Potential</span>{' '}
                <span className="font-semibold">{s.potential}</span>
              </div>
              <div>
                <span className="text-[var(--text-muted)]">Resume score</span>{' '}
                <span className="font-semibold">{s.resumeScore}/10</span>
              </div>
            </div>
            <Button
              variant={connections.includes(s.id) ? "sagesolid" : "outline"}
              className={
                connections.includes(s.id) ? "" : "border-sagedeep text-sagedeep"
              }
              onClick={() => toggle(s)}
            >
              {connections.includes(s.id) ? "Connected" : "Connect"}
            </Button>
          </Card>
        ))}
      </div>
      {matches.length === 0 && (
        <EmptyState text="No students match these requirements yet — try loosening a filter." />
      )}

      <div className="pt-2">
        <div className="font-display font-semibold mb-3">Matching universities</div>
        <div className="grid sm:grid-cols-2 gap-3">
          {UNIVERSITIES.filter((u) => !filters.university || u.name === filters.university).map(
            (u) => (
              <Card key={u.id} className="p-4">
                <div className="text-sm font-semibold">{u.name}</div>
                <div className="text-xs text-[var(--text-muted)]">
                  {u.city} · avg skill {u.avgSkill}/100
                </div>
              </Card>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export const IndustryConnections: React.FC<{ connections: (string | number)[] }> = ({
  connections,
}) => {
  const list = STUDENTS.filter((s) => connections.includes(s.id));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Connections"
        desc="Students and companies you're connected with."
      />
      {list.length === 0 ? (
        <EmptyState text="No connections yet — connect with students from Search Results." />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {list.map((s) => (
            <Card key={s.id} className="p-4 flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-mutedsage/60 flex items-center justify-center text-xs font-bold">
                {s.name[0]}
              </div>
              <div>
                <div className="text-sm font-semibold">{s.name}</div>
                <div className="text-xs text-[var(--text-muted)]">
                  {s.field} · {s.university}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
