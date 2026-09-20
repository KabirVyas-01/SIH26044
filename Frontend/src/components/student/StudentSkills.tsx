import React, { useState } from 'react';
import { Card, Button, SkillBar, PageHeader } from '../common/UIComponents';
import { SkillTestModal } from './SkillTestModal';
import { Student } from '../../types';

export const StudentSkills: React.FC<{
  student: Student;
  onUpdateSkill?: (skillName: string, score: number) => void;
}> = ({ student, onUpdateSkill }) => {
  const [role, setRole] = useState(student.role);
  const [testSkill, setTestSkill] = useState<string | null>(null);

  const handleTestPassed = (skillName: string, score: number) => {
    if (onUpdateSkill) {
      onUpdateSkill(skillName, score);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Skills & assessment"
        desc="See how your current skills compare to what your target role actually requires."
      />
      <Card className="p-5">
        <label className="text-xs font-semibold text-[var(--text-muted)]">Desired job role</label>
        <div className="flex flex-col sm:flex-row gap-3 mt-1.5">
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="flex-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
          />
          <Button variant="sagesolid">Check readiness</Button>
        </div>
      </Card>

      <Card className="p-5">
        <div className="font-display font-semibold mb-4">Skill gap for {role}</div>
        {student.skills.map((s) => (
          <div key={s.name} className="flex items-center gap-4 mb-2">
            <div className="flex-1">
              <SkillBar {...s} />
            </div>
            <Button
              variant="outline"
              className="text-xs px-3 py-2 border-sagedeep text-sagedeep shrink-0"
              onClick={() => setTestSkill(s.name)}
            >
              Take test
            </Button>
          </div>
        ))}
        {student.skills.length === 0 && (
          <p className="text-xs text-[var(--text-muted)]">No skills logged yet.</p>
        )}
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
