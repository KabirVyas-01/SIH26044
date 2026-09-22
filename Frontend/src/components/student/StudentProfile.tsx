import React, { useState, useEffect } from 'react';
import { Card, Button, PageHeader, Tag, VerifiedBadge, ProgressBar, SkillBar, Modal } from '../common/UIComponents';
import { ResumeScoreCard } from './StudentOverview';
import { Student } from '../../types';
import { studentApi } from '../../api/student';
import { useAuth } from '../../context/AuthContext';

export const StudentProfile: React.FC<{
  student: Student;
  onUpdateProfile?: (updated: Partial<Student>) => void;
  onNavigate?: (tab: string) => void;
}> = ({ student, onUpdateProfile, onNavigate }) => {
  const [editing, setEditing] = useState(false);
  const [college, setCollege] = useState(student.university);
  const [targetRole, setTargetRole] = useState(student.desiredRole || student.role);
  const [qualification, setQualification] = useState(student.qualification || student.field || '');
  const [universityRollNo, setUniversityRollNo] = useState(student.universityRollNo || '');
  const [resumeUrl, setResumeUrl] = useState(student.resumeUrl || '');
  const [priorExperience, setPriorExperience] = useState(student.priorExperience || '');
  const [githubUrl, setGithubUrl] = useState(student.githubUrl || '');
  const [leetcodeUrl, setLeetcodeUrl] = useState(student.leetcodeUrl || '');
  const [skillsStr, setSkillsStr] = useState(student.skills.map((s) => s.name).join(', '));
  const [apps, setApps] = useState<any[]>([]);
  const { currentUser } = useAuth();

  useEffect(() => {
    let isMounted = true;
    studentApi.getMyApplications().then((res) => {
      if (isMounted && res?.my_applications) {
        setApps(res.my_applications);
      }
    }).catch(() => {});
    return () => { isMounted = false; };
  }, []);

  const handleSave = async () => {
    if (currentUser && currentUser.role === 'student') {
      try {
        await studentApi.updateProfile({
          college,
          desired_role: targetRole,
          qualification,
          university_roll_no: universityRollNo,
          resume_url: resumeUrl,
          prior_experience: priorExperience,
          github_url: githubUrl,
          leetcode_url: leetcodeUrl,
          skills: skillsStr,
        });
      } catch {
        // fallback
      }
    }
    if (onUpdateProfile) {
      onUpdateProfile({
        university: college,
        role: targetRole,
        desiredRole: targetRole,
        field: qualification,
        qualification,
        universityRollNo,
        resumeUrl,
        priorExperience,
        githubUrl,
        leetcodeUrl,
      });
    }
    setEditing(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Your profile"
        desc="What universities and industries see about your growth and qualifications."
      />
      <Card className="p-6">
        <div className="flex items-start gap-4 flex-wrap">
          <div className="w-16 h-16 rounded-full bg-mutedsage/70 flex items-center justify-center font-display text-xl">
            {student.name[0]}
          </div>
          <div className="flex-1 min-w-[200px]">
            <div className="flex items-center gap-2 flex-wrap">
              <div className="font-display text-xl font-semibold">{student.name}</div>
              {student.verified && <VerifiedBadge small />}
            </div>
            <div className="text-sm text-[var(--text-muted)]">{student.university}</div>
            {student.universityRollNo && (
              <div className="text-xs text-[var(--text-muted)] mt-0.5 font-mono">
                Roll No: {student.universityRollNo}
              </div>
            )}
            <div className="flex flex-wrap gap-1.5 mt-2">
              <Tag>{student.qualification || student.field}</Tag>
              <Tag tone="blue">Target: {student.desiredRole || student.role}</Tag>
            </div>

            {/* Profile & Portfolio Links */}
            <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-[var(--border)] text-xs font-semibold">
              {student.resumeUrl && (
                <a
                  href={student.resumeUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-sagedeep hover:underline"
                >
                  📄 View Resume ↗
                </a>
              )}
              {student.githubUrl && (
                <a
                  href={student.githubUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-deepblue hover:underline"
                >
                  💻 GitHub Profile ↗
                </a>
              )}
              {student.leetcodeUrl && (
                <a
                  href={student.leetcodeUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-amber-700 hover:underline"
                >
                  ⚡ LeetCode Profile ↗
                </a>
              )}
            </div>
          </div>
          <Button
            variant="outline"
            className="border-sagedeep text-sagedeep"
            onClick={() => setEditing(true)}
          >
            Edit profile
          </Button>
        </div>
      </Card>

      {/* Qualifications & Experience Block */}
      <Card className="p-5">
        <div className="font-display font-semibold mb-3">Education & Experience Summary</div>
        <div className="grid sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1">
            <span className="font-semibold text-[var(--text-muted)] uppercase tracking-wider text-[10px]">
              Educational Qualification
            </span>
            <p className="text-sm font-medium">{student.qualification || 'Not specified'}</p>
          </div>
          <div className="space-y-1">
            <span className="font-semibold text-[var(--text-muted)] uppercase tracking-wider text-[10px]">
              Desired Career Role
            </span>
            <p className="text-sm font-medium">{student.desiredRole || student.role}</p>
          </div>
          <div className="sm:col-span-2 space-y-1 pt-2 border-t border-[var(--border)]">
            <span className="font-semibold text-[var(--text-muted)] uppercase tracking-wider text-[10px]">
              Prior Experience, Internships & Projects
            </span>
            <p className="text-sm leading-relaxed text-[var(--text-muted)]">
              {student.priorExperience || 'No prior experience details provided.'}
            </p>
          </div>
        </div>
      </Card>

      <ResumeScoreCard student={student} />

      {/* My Submitted Applications */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="font-display font-semibold">My Applications</div>
          {onNavigate && (
            <button
              type="button"
              onClick={() => onNavigate('applications')}
              className="text-xs text-sagedeep font-semibold hover:underline"
            >
              View all applications ({apps.length}) →
            </button>
          )}
        </div>
        {apps.length === 0 ? (
          <p className="text-xs text-[var(--text-muted)]">
            No active applications yet. Browse opportunities to apply!
          </p>
        ) : (
          <div className="space-y-2.5">
            {apps.slice(0, 4).map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between p-3 rounded-xl bg-black/[0.02] border border-[var(--border)]"
              >
                <div>
                  <div className="text-sm font-semibold text-black">{a.title}</div>
                  <div className="text-xs text-[var(--text-muted)]">
                    {a.company_name || a.professor_name || 'Organization'} · {a.applied_date || 'Recently applied'}
                  </div>
                </div>
                <Tag tone={a.status === 'shortlisted' || a.status === 'selected' ? 'sage' : 'blue'}>
                  {a.status === 'shortlisted' ? 'Shortlisted ✓' : a.status === 'selected' ? 'Selected 🎉' : 'Under Review'}
                </Tag>
              </div>
            ))}
          </div>
        )}
      </Card>

      <div className="grid sm:grid-cols-2 gap-4">
        <Card className="p-5">
          <div className="font-display font-semibold mb-3">Growth transparency</div>
          {[
            ['Discipline', student.discipline],
            ['Punctuality', student.punctuality],
            ['Consistency', student.consistency],
            ['Potential', student.potential],
          ].map(([l, v]) => (
            <div key={l as string} className="mb-3">
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium">{l}</span>
                <span className="text-[var(--text-muted)]">{v}/100</span>
              </div>
              <ProgressBar value={v as number} />
            </div>
          ))}
        </Card>

        <Card className="p-5">
          <div className="font-display font-semibold mb-3">Skills</div>
          {student.skills.map((s) => (
            <SkillBar key={s.name} {...s} />
          ))}
          {student.skills.length === 0 && (
            <p className="text-xs text-[var(--text-muted)]">No verified skills recorded yet.</p>
          )}
        </Card>
      </div>

      <Modal open={editing} onClose={() => setEditing(false)} wide={true} title="Edit Profile">
        <div className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">College / University</label>
              <input
                value={college}
                onChange={(e) => setCollege(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">University Roll No.</label>
              <input
                value={universityRollNo}
                onChange={(e) => setUniversityRollNo(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">Educational Qualification</label>
              <input
                value={qualification}
                onChange={(e) => setQualification(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">Target / Desired Role</label>
              <input
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">Resume URL / Link</label>
              <input
                type="url"
                value={resumeUrl}
                onChange={(e) => setResumeUrl(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">Skills (comma separated)</label>
              <input
                value={skillsStr}
                onChange={(e) => setSkillsStr(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">GitHub Profile URL</label>
              <input
                type="url"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">LeetCode Profile URL</label>
              <input
                type="url"
                value={leetcodeUrl}
                onChange={(e) => setLeetcodeUrl(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              />
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Prior Experience & Projects</label>
            <textarea
              rows={2}
              value={priorExperience}
              onChange={(e) => setPriorExperience(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
            />
          </div>
          <Button variant="primary" className="w-full mt-2" onClick={handleSave}>
            Save Changes
          </Button>
        </div>
      </Modal>
    </div>
  );
};
