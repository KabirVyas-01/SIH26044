import React from 'react';
import { Card, StatBlock, SkillBar, PageHeader, VerifiedBadge } from '../common/UIComponents';
import { Student } from '../../types';

export const GrowthJourney: React.FC = () => {
  const steps = [
    { t: 'What should I learn?', d: 'Based on your desired role and current skill gaps.' },
    { t: 'Am I ready?', d: 'Based on skill tests, resume score, and projects.' },
    { t: 'Where do I fit?', d: 'Based on matching internships and job openings.' },
  ];
  return (
    <div className="grid sm:grid-cols-3 gap-4">
      {steps.map((s, i) => (
        <Card key={s.t} className="p-4">
          <div className="text-xs font-semibold text-sagedeep mb-2">Step {i + 1}</div>
          <div className="font-display font-semibold mb-1.5">{s.t}</div>
          <p className="text-xs text-[var(--text-muted)] leading-relaxed">{s.d}</p>
        </Card>
      ))}
    </div>
  );
};

export const ResumeScoreCard: React.FC<{ student: Student }> = ({ student }) => {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="font-display font-semibold">Resume score</div>
        <span className="font-display text-2xl">
          {student.resumeScore}
          <span className="text-sm text-[var(--text-muted)]">/10</span>
        </span>
      </div>
      <div className="hscroll no-scrollbar">
        <div className="flex items-end gap-2 h-20 min-w-max">
          {student.resumeHistory.map((v, i) => (
            <div key={i} className="w-7 flex flex-col items-center gap-1">
              <div
                className="w-full bg-sage/70 rounded-t growbar"
                style={{ height: (v / 10) * 64 + "px" }}
              />
              <span className="text-[10px] text-[var(--text-muted)]">{v}</span>
            </div>
          ))}
        </div>
      </div>
      <p className="text-xs text-[var(--text-muted)] mt-3">
        Improves as you clear skill tests, learn new skills and add stronger projects.
      </p>
    </Card>
  );
};

export const StudentOverview: React.FC<{ student: Student }> = ({ student }) => {
  const initialResumeScore = student.resumeHistory[0] || student.resumeScore;
  const improvement = (student.resumeScore - initialResumeScore).toFixed(1);

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome back, ${student.name.split(' ')[0]}`}
        desc={`Tracking your path toward ${student.role}.`}
        action={student.verified ? <VerifiedBadge /> : undefined}
      />

      <div className="grid sm:grid-cols-4 gap-3">
        <StatBlock
          label="Resume score"
          value={student.resumeScore + "/10"}
          sub={"+" + improvement + " since joining"}
        />
        <StatBlock label="Weekly improvement" value={"+" + student.weeklyImprovement + "%"} />
        <StatBlock label="Potential" value={student.potential + "/100"} />
        <StatBlock label="Consistency" value={student.consistency + "/100"} />
      </div>

      <Card className="p-5">
        <div className="font-display font-semibold mb-4">Skill snapshot for {student.role}</div>
        {student.skills.map((s) => (
          <SkillBar key={s.name} {...s} />
        ))}
        {student.skills.length === 0 && (
          <p className="text-xs text-[var(--text-muted)]">No verified skills yet. Take an assessment to add verified skills.</p>
        )}
      </Card>

      <div>
        <div className="font-display font-semibold mb-3">Your growth journey</div>
        <GrowthJourney />
      </div>
    </div>
  );
};
