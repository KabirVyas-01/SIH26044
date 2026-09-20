import React, { useState } from 'react';
import { Card, Button, PageHeader, Tag, VerifiedBadge, ProgressBar, SkillBar, Modal } from '../common/UIComponents';
import { ResumeScoreCard } from './StudentOverview';
import { Student } from '../../types';
import { studentApi } from '../../api/student';
import { useAuth } from '../../context/AuthContext';

export const StudentProfile: React.FC<{
  student: Student;
  onUpdateProfile?: (updated: Partial<Student>) => void;
}> = ({ student, onUpdateProfile }) => {
  const [editing, setEditing] = useState(false);
  const [college, setCollege] = useState(student.university);
  const [targetRole, setTargetRole] = useState(student.role);
  const [skillsStr, setSkillsStr] = useState(student.skills.map((s) => s.name).join(', '));
  const { currentUser } = useAuth();

  const handleSave = async () => {
    if (currentUser && currentUser.role === 'student') {
      try {
        await studentApi.updateProfile({
          college,
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
      });
    }
    setEditing(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Your profile"
        desc="What universities and industries see about your growth."
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
            <div className="flex flex-wrap gap-1.5 mt-2">
              <Tag>{student.field}</Tag>
              <Tag tone="blue">Target: {student.role}</Tag>
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

      <ResumeScoreCard student={student} />

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

      <Modal open={editing} onClose={() => setEditing(false)} title="Edit Profile">
        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">College / University</label>
            <input
              value={college}
              onChange={(e) => setCollege(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Target Role</label>
            <input
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Skills (comma separated)</label>
            <input
              value={skillsStr}
              onChange={(e) => setSkillsStr(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring"
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
