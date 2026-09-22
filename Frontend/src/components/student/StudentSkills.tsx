import React, { useState } from 'react';
import { Card, Button, PageHeader } from '../common/UIComponents';
import { SkillTestModal } from './SkillTestModal';
import { Student } from '../../types';

export const StudentSkills: React.FC<{
  student: Student;
  onUpdateSkill?: (skillName: string, score: number) => void;
}> = ({ student, onUpdateSkill }) => {
  const [role, setRole] = useState(student.desiredRole || student.role || 'Software Engineer');
  const [testSkill, setTestSkill] = useState<string | null>(null);
  const [newSkillInput, setNewSkillInput] = useState('');

  const handleTestPassed = (skillName: string, score: number) => {
    if (onUpdateSkill) {
      onUpdateSkill(skillName, score);
    }
  };

  const verifiedCount = student.skills.filter((s) => s.isVerified || s.score >= 70).length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Skills & Assessment"
        desc="Verify your declared technical skills, evaluate your target role readiness, and earn verified badges for recruiters."
      />

      {/* Target Role Card */}
      <Card className="p-5">
        <label className="text-xs font-semibold text-[var(--text-muted)]">Target Role for Skill Evaluation</label>
        <div className="flex flex-col sm:flex-row gap-3 mt-1.5">
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="flex-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            placeholder="e.g. Full Stack Developer, AI Engineer"
          />
          <Button variant="sagesolid" className="text-xs sm:text-sm">Save Role</Button>
        </div>
      </Card>

      {/* Skills List with Verification Status */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-[var(--border)]">
          <div>
            <div className="font-display font-semibold text-base">Your Skills & Verification Badges</div>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">
              Score 70% or higher in the 10-minute technical assessment to earn a verified credential.
            </p>
          </div>
          <div className="text-xs font-bold px-2.5 py-1 rounded-full bg-deepblue/10 text-deepblue shrink-0">
            {verifiedCount} of {student.skills.length} Verified
          </div>
        </div>

        {student.skills.map((s) => {
          const isVerified = s.isVerified || s.score >= 70;
          return (
            <div
              key={s.name}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 mb-2.5 rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="font-bold text-sm text-[var(--text-main)]">{s.name}</span>
                  {isVerified ? (
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">
                      ✓ Verified ({s.score}%)
                    </span>
                  ) : (
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-300">
                      Pending Test
                    </span>
                  )}
                </div>

                {/* Progress bar */}
                <div className="w-full bg-black/10 dark:bg-white/10 rounded-full h-2 overflow-hidden max-w-md">
                  <div
                    className={`h-full rounded-full transition-all ${isVerified ? 'bg-sagedeep' : 'bg-amber-500'}`}
                    style={{ width: `${s.score || 0}%` }}
                  />
                </div>
              </div>

              <Button
                variant={isVerified ? 'outline' : 'primary'}
                className={`text-xs px-3.5 py-2 shrink-0 ${!isVerified ? 'bg-amber-600 hover:bg-amber-700 text-white' : ''}`}
                onClick={() => setTestSkill(s.name)}
              >
                {isVerified ? 'Retake Test' : `Verify ${s.name} →`}
              </Button>
            </div>
          );
        })}

        {student.skills.length === 0 && (
          <p className="text-xs text-[var(--text-muted)] py-4 text-center">
            No skills added to your profile yet. Add your skills below to get started!
          </p>
        )}

        {/* Add & Test a New Skill Input */}
        <div className="mt-4 pt-3.5 border-t border-[var(--border)]">
          <label className="text-xs font-semibold text-[var(--text-muted)] block mb-1.5">
            Want to test another skill? (e.g. React, Docker, SQL, Java, C++, TypeScript)
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Enter skill name…"
              value={newSkillInput}
              onChange={(e) => setNewSkillInput(e.target.value)}
              className="flex-1 rounded-xl border border-[var(--border)] px-3.5 py-2 text-sm focus-ring bg-white text-black"
            />
            <Button
              variant="sagesolid"
              className="text-xs sm:text-sm px-4 py-2 shrink-0"
              disabled={!newSkillInput.trim()}
              onClick={() => {
                const trimmed = newSkillInput.trim();
                if (trimmed) {
                  setTestSkill(trimmed);
                  setNewSkillInput('');
                }
              }}
            >
              Start Assessment →
            </Button>
          </div>
        </div>
      </Card>

      <SkillTestModal
        open={!!testSkill}
        onClose={() => setTestSkill(null)}
        skill={testSkill}
        onSuccess={handleTestPassed}
      />
    </div>
  );
};
