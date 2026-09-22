import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  PageHeader,
  StatBlock,
  Tag,
  EmptyState,
  VerifiedBadge,
  Modal,
  ProgressBar,
} from '../common/UIComponents';
import { Company, Student, University, BackendPosting, BackendApplicant } from '../../types';
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
  const [shortlistedIds, setShortlistedIds] = useState<(string | number)[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);

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

  const toggleShortlist = (id: string | number) => {
    setShortlistedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Search results"
        desc={`${matches.length} student${matches.length !== 1 ? 's' : ''} match your current requirements.`}
      />
      <div className="grid sm:grid-cols-2 gap-4">
        {matches.map((s) => (
          <Card key={s.id} className="p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between gap-3 mb-2">
                <div
                  className="flex items-center gap-2 cursor-pointer"
                  onClick={() => setSelectedStudent(s)}
                >
                  <div className="w-8 h-8 rounded-full bg-mutedsage/60 flex items-center justify-center text-xs font-bold">
                    {s.name[0]}
                  </div>
                  <div>
                    <div className="text-sm font-semibold flex items-center gap-1.5 hover:text-sagedeep">
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
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-[var(--border)] flex-wrap justify-between">
              <div className="flex items-center gap-2">
                <Button
                  variant={shortlistedIds.includes(s.id) ? "sagesolid" : "outline"}
                  className={shortlistedIds.includes(s.id) ? "text-xs py-1.5 px-3" : "border-sagedeep text-sagedeep text-xs py-1.5 px-3"}
                  onClick={() => toggleShortlist(s.id)}
                >
                  {shortlistedIds.includes(s.id) ? "Shortlisted ✓" : "Shortlist"}
                </Button>
                <Button
                  variant="ghost"
                  className="text-xs py-1.5 px-2.5 text-[var(--text-muted)] hover:text-black"
                  onClick={() => setSelectedStudent(s)}
                >
                  View Details
                </Button>
              </div>
              <Button
                variant={connections.includes(s.id) ? "sagesolid" : "outline"}
                className={
                  "text-xs py-1.5 px-2.5 " +
                  (connections.includes(s.id) ? "" : "border-[var(--border)] text-[var(--text-muted)]")
                }
                onClick={() => toggle(s)}
              >
                {connections.includes(s.id) ? "Connected" : "Connect"}
              </Button>
            </div>
          </Card>
        ))}
      </div>
      {matches.length === 0 && (
        <EmptyState text="No students match these requirements yet — try loosening a filter." />
      )}

      {selectedStudent && (
        <Modal
          open={!!selectedStudent}
          onClose={() => setSelectedStudent(null)}
          wide={true}
          title="Candidate Profile"
        >
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-mutedsage/70 flex items-center justify-center font-display text-lg font-bold">
                  {selectedStudent.name[0]}
                </div>
                <div>
                  <div className="font-display text-lg font-semibold flex items-center gap-2">
                    {selectedStudent.name} <VerifiedBadge small />
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">{selectedStudent.university}</div>
                  <div className="text-xs text-[var(--text-muted)] mt-0.5">{selectedStudent.field}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-[var(--text-muted)]">Resume Score</div>
                <div className="text-lg font-bold text-sagedeep">{selectedStudent.resumeScore}/10</div>
              </div>
            </div>

            <div>
              <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                Verified Skill Scores
              </div>
              <div className="grid sm:grid-cols-2 gap-2">
                {selectedStudent.skills.map((k) => (
                  <div key={k.name} className="p-2.5 rounded-xl bg-black/[0.02] border border-[var(--border)]">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-semibold">{k.name}</span>
                      <span className="font-mono text-sagedeep font-bold">{k.score}%</span>
                    </div>
                    <ProgressBar value={k.score} />
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center text-xs p-3 rounded-xl bg-black/[0.02] border border-[var(--border)]">
              <div>
                <span className="text-[var(--text-muted)] block">Discipline</span>
                <span className="font-bold text-sm">{selectedStudent.discipline}/100</span>
              </div>
              <div>
                <span className="text-[var(--text-muted)] block">Consistency</span>
                <span className="font-bold text-sm">{selectedStudent.consistency}/100</span>
              </div>
              <div>
                <span className="text-[var(--text-muted)] block">Potential</span>
                <span className="font-bold text-sm">{selectedStudent.potential}/100</span>
              </div>
            </div>

            <div className="pt-3 border-t border-[var(--border)] flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setSelectedStudent(null)}>
                Close
              </Button>
              <Button
                variant={shortlistedIds.includes(selectedStudent.id) ? "sagesolid" : "primary"}
                onClick={() => toggleShortlist(selectedStudent.id)}
              >
                {shortlistedIds.includes(selectedStudent.id) ? "Shortlisted ✓" : "Shortlist Candidate"}
              </Button>
            </div>
          </div>
        </Modal>
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

export const IndustryApplications: React.FC = () => {
  const [postings, setPostings] = useState<BackendPosting[]>([]);
  const [applicants, setApplicants] = useState<(BackendApplicant & { posting_title?: string })[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplicant, setSelectedApplicant] = useState<(BackendApplicant & { posting_title?: string }) | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const { currentUser } = useAuth();

  useEffect(() => {
    let isMounted = true;
    const loadData = async () => {
      setLoading(true);
      try {
        const postRes = await industryApi.getMyPostings();
        const postList = postRes?.postings || [];
        if (isMounted) setPostings(postList);

        let collected: (BackendApplicant & { posting_title?: string })[] = [];
        if (postList.length > 0) {
          for (const p of postList) {
            try {
              const appRes = await industryApi.getApplicants(p.id);
              if (appRes?.applicants && appRes.applicants.length > 0) {
                const withTitle = appRes.applicants.map((a) => ({
                  ...a,
                  posting_title: p.title,
                }));
                collected = [...collected, ...withTitle];
              }
            } catch {
              // ignore
            }
          }
        }

        // If no applicants in live DB yet, seed with realistic mock applicants from STUDENTS
        if (collected.length === 0) {
          const sampleRoles = postList.length > 0 ? postList.map((p) => p.title) : ['Cloud Engineer Associate', 'Full Stack Developer', 'Data Science Intern'];
          collected = STUDENTS.map((s, idx) => ({
            application_id: 200 + idx,
            student_id: typeof s.id === 'number' ? s.id : idx + 1,
            name: s.name,
            email: `${s.name.toLowerCase().replace(/\s+/g, '.')}@university.edu`,
            college: s.university,
            skills: s.skills.map((k) => k.name).join(', '),
            status: (idx === 0 ? 'shortlisted' : 'applied') as 'applied' | 'shortlisted' | 'rejected' | 'selected',
            applied_date: 'Today',
            verification_status: 'verified',
            is_university_verified: true,
            verified_skills: s.skills.map((k) => ({ skill_name: k.name, percentage: k.score })),
            github_url: 'https://github.com',
            leetcode_url: 'https://leetcode.com',
            resume_url: '#',
            posting_title: sampleRoles[idx % sampleRoles.length],
          }));
        }

        if (isMounted) setApplicants(collected);
      } catch {
        // fallback
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadData();
    return () => {
      isMounted = false;
    };
  }, [currentUser]);

  const handleUpdateStatus = async (
    applicationId: number,
    newStatus: 'shortlisted' | 'selected' | 'rejected' | 'applied'
  ) => {
    setActionLoadingId(applicationId);
    setApplicants((prev) =>
      prev.map((a) => (a.application_id === applicationId ? { ...a, status: newStatus as any } : a))
    );
    if (selectedApplicant && selectedApplicant.application_id === applicationId) {
      setSelectedApplicant((prev) => (prev ? { ...prev, status: newStatus as any } : null));
    }

    try {
      if (newStatus === 'shortlisted' || newStatus === 'selected' || newStatus === 'rejected') {
        await industryApi.updateApplicantStatus(applicationId, newStatus);
      }
    } catch {
      // optimistic update maintained
    } finally {
      setActionLoadingId(null);
    }
  };

  const total = applicants.length;
  const shortlistedCount = applicants.filter((a) => a.status === 'shortlisted').length;
  const selectedCount = applicants.filter((a) => a.status === 'selected').length;
  const pendingCount = applicants.filter((a) => a.status === 'applied').length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Applicant Tracking & Applications"
        desc="Review candidates who applied to your job and internship openings, inspect technical scores, and manage shortlists."
      />

      <div className="grid sm:grid-cols-4 gap-3">
        <StatBlock label="Total Applicants" value={total} />
        <StatBlock label="Under Review" value={pendingCount} />
        <StatBlock label="Shortlisted" value={shortlistedCount} />
        <StatBlock label="Selected / Hired" value={selectedCount} />
      </div>

      {loading ? (
        <Card className="p-8 text-center text-xs text-[var(--text-muted)]">
          Loading applicants…
        </Card>
      ) : applicants.length === 0 ? (
        <EmptyState text="No applications received yet for your postings." />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {applicants.map((app) => {
            const isShortlisted = app.status === 'shortlisted';
            const isSelected = app.status === 'selected';
            const isRejected = app.status === 'rejected';

            return (
              <Card key={app.application_id} className="p-5 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div
                      className="flex items-center gap-2.5 cursor-pointer"
                      onClick={() => setSelectedApplicant(app)}
                    >
                      <div className="w-10 h-10 rounded-full bg-mutedsage/60 flex items-center justify-center text-sm font-bold">
                        {app.name[0]}
                      </div>
                      <div>
                        <div className="text-sm font-semibold flex items-center gap-1.5 hover:text-sagedeep">
                          {app.name} <VerifiedBadge small />
                        </div>
                        <div className="text-xs text-[var(--text-muted)]">{app.college}</div>
                      </div>
                    </div>
                    <div>
                      {isShortlisted ? (
                        <Tag tone="sage">Shortlisted ✓</Tag>
                      ) : isSelected ? (
                        <Tag tone="sage">Selected 🎉</Tag>
                      ) : isRejected ? (
                        <Tag tone="rose">Rejected</Tag>
                      ) : (
                        <Tag tone="blue">Under Review</Tag>
                      )}
                    </div>
                  </div>

                  <div className="text-xs font-semibold text-black bg-black/[0.03] px-3 py-1.5 rounded-lg border border-[var(--border)] mb-3">
                    Applied for: <span className="text-sagedeep">{app.posting_title || 'Software Engineering Role'}</span>
                  </div>

                  {app.verified_skills && app.verified_skills.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {app.verified_skills.map((vs) => (
                        <Tag key={vs.skill_name} tone={vs.percentage >= 70 ? 'sage' : 'amber'}>
                          {vs.skill_name} {Math.round(vs.percentage)}%
                        </Tag>
                      ))}
                    </div>
                  )}

                  <div className="text-[11px] text-[var(--text-muted)] flex items-center gap-2 mb-2">
                    <span>✉ {app.email}</span>
                    {app.applied_date && <span>· 📅 {app.applied_date}</span>}
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-3 border-t border-[var(--border)] flex-wrap justify-between">
                  <div className="flex items-center gap-2">
                    <Button
                      variant={isShortlisted ? "sagesolid" : "outline"}
                      className={isShortlisted ? "text-xs py-1.5 px-3" : "border-sagedeep text-sagedeep text-xs py-1.5 px-3"}
                      disabled={actionLoadingId === app.application_id}
                      onClick={() =>
                        handleUpdateStatus(
                          app.application_id,
                          isShortlisted ? 'applied' : 'shortlisted'
                        )
                      }
                    >
                      {isShortlisted ? "Shortlisted ✓" : "Shortlist"}
                    </Button>
                    <Button
                      variant="ghost"
                      className="text-xs py-1.5 px-2.5 text-[var(--text-muted)] hover:text-black"
                      onClick={() => setSelectedApplicant(app)}
                    >
                      View Details
                    </Button>
                  </div>

                  {isSelected ? (
                    <Tag tone="sage">Hired</Tag>
                  ) : (
                    <Button
                      variant="outline"
                      className="text-xs py-1 px-2 border-emerald-600 text-emerald-700 hover:bg-emerald-50"
                      onClick={() => handleUpdateStatus(app.application_id, 'selected')}
                    >
                      Select
                    </Button>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {selectedApplicant && (
        <Modal
          open={!!selectedApplicant}
          onClose={() => setSelectedApplicant(null)}
          wide={true}
          title="Applicant Details"
        >
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-mutedsage/70 flex items-center justify-center font-display text-lg font-bold">
                  {selectedApplicant.name[0]}
                </div>
                <div>
                  <div className="font-display text-lg font-semibold flex items-center gap-2">
                    {selectedApplicant.name} <VerifiedBadge small />
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">{selectedApplicant.college}</div>
                  <div className="text-xs text-[var(--text-muted)] mt-0.5">{selectedApplicant.email}</div>
                  {selectedApplicant.university_roll_no && (
                    <div className="text-xs font-mono text-[var(--text-muted)] mt-0.5">
                      Roll No: {selectedApplicant.university_roll_no}
                    </div>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-[var(--text-muted)] mb-1">Status</div>
                {selectedApplicant.status === 'shortlisted' ? (
                  <Tag tone="sage">Shortlisted ✓</Tag>
                ) : selectedApplicant.status === 'selected' ? (
                  <Tag tone="sage">Selected 🎉</Tag>
                ) : selectedApplicant.status === 'rejected' ? (
                  <Tag tone="rose">Rejected</Tag>
                ) : (
                  <Tag tone="blue">Under Review</Tag>
                )}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-black/[0.02] border border-[var(--border)] text-xs">
              <span className="font-semibold text-black">Applied for Opening: </span>
              <span className="font-medium text-sagedeep">{selectedApplicant.posting_title || 'Technical Role'}</span>
            </div>

            <div>
              <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                Verified Skill Assessments
              </div>
              <div className="grid sm:grid-cols-2 gap-2">
                {selectedApplicant.verified_skills && selectedApplicant.verified_skills.length > 0 ? (
                  selectedApplicant.verified_skills.map((vs) => (
                    <div key={vs.skill_name} className="p-2.5 rounded-xl bg-black/[0.02] border border-[var(--border)]">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="font-semibold">{vs.skill_name}</span>
                        <span className="font-mono text-sagedeep font-bold">{Math.round(vs.percentage)}%</span>
                      </div>
                      <ProgressBar value={vs.percentage} />
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-[var(--text-muted)]">No verified assessment records available.</p>
                )}
              </div>
            </div>

            <div className="flex flex-wrap gap-3 pt-2 text-xs font-semibold">
              {selectedApplicant.resume_url && (
                <a href={selectedApplicant.resume_url} target="_blank" rel="noreferrer" className="text-sagedeep hover:underline">
                  📄 Candidate Resume ↗
                </a>
              )}
              {selectedApplicant.github_url && (
                <a href={selectedApplicant.github_url} target="_blank" rel="noreferrer" className="text-deepblue hover:underline">
                  💻 GitHub Profile ↗
                </a>
              )}
              {selectedApplicant.leetcode_url && (
                <a href={selectedApplicant.leetcode_url} target="_blank" rel="noreferrer" className="text-amber-700 hover:underline">
                  ⚡ LeetCode Profile ↗
                </a>
              )}
            </div>

            <div className="pt-3 border-t border-[var(--border)] flex justify-between items-center flex-wrap gap-2">
              <Button variant="ghost" onClick={() => setSelectedApplicant(null)}>
                Close
              </Button>
              <div className="flex items-center gap-2">
                <Button
                  variant={selectedApplicant.status === 'rejected' ? "outline" : "outline"}
                  className="text-xs py-1.5 px-3 border-rose-300 text-rose-700 hover:bg-rose-50"
                  onClick={() => handleUpdateStatus(selectedApplicant.application_id, 'rejected')}
                >
                  Reject
                </Button>
                <Button
                  variant={selectedApplicant.status === 'selected' ? "sagesolid" : "outline"}
                  className="text-xs py-1.5 px-3 border-emerald-600 text-emerald-700 hover:bg-emerald-50"
                  onClick={() => handleUpdateStatus(selectedApplicant.application_id, 'selected')}
                >
                  Select Candidate
                </Button>
                <Button
                  variant={selectedApplicant.status === 'shortlisted' ? "sagesolid" : "primary"}
                  onClick={() =>
                    handleUpdateStatus(
                      selectedApplicant.application_id,
                      selectedApplicant.status === 'shortlisted' ? 'applied' : 'shortlisted'
                    )
                  }
                >
                  {selectedApplicant.status === 'shortlisted' ? "Shortlisted ✓" : "Shortlist Candidate"}
                </Button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
