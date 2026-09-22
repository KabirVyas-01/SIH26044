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

export const ResumeScoreCard: React.FC<{ student: Student; onNavigate?: (tab: string) => void }> = ({ student, onNavigate }) => {
  const hasAudit = Boolean(student.resumeReview && student.resumeScore > 0);
  const review = student.resumeReview;

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-display font-semibold text-base">Resume score</span>
            {hasAudit ? (
              <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-sagedeep/15 text-sagedeep">
                Gemini AI Audited
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-black/5 text-[var(--text-muted)]">
                Skills Estimate
              </span>
            )}
          </div>
          {student.desiredRole && (
            <div className="text-xs text-[var(--text-muted)] mt-0.5">Target: {student.desiredRole}</div>
          )}
        </div>

        <span className="font-display text-2xl font-bold text-sagedeep">
          {student.resumeScore > 0 ? student.resumeScore : '--'}
          <span className="text-sm font-normal text-[var(--text-muted)]">/10</span>
        </span>
      </div>

      <div className="hscroll no-scrollbar mb-3">
        <div className="flex items-end gap-2 h-16 min-w-max">
          {student.resumeHistory.map((v, i) => (
            <div key={i} className="w-7 flex flex-col items-center gap-1">
              <div
                className="w-full bg-sage/70 rounded-t growbar"
                style={{ height: `${(v / 10) * 52}px` }}
              />
              <span className="text-[10px] text-[var(--text-muted)]">{v}</span>
            </div>
          ))}
        </div>
      </div>

      {hasAudit && review?.verdict && (
        <div className="p-3 rounded-xl bg-sagedeep/5 border border-sagedeep/15 text-xs text-[#2C3524] mb-3">
          <span className="font-bold text-sagedeep mr-1">AI Verdict:</span>
          <span className="italic">"{review.verdict}"</span>
        </div>
      )}

      {hasAudit && review?.missing_keywords?.length > 0 && (
        <div className="mb-3">
          <div className="text-[11px] font-semibold text-[var(--text-muted)] mb-1">Critical Missing Keywords:</div>
          <div className="flex flex-wrap gap-1">
            {review.missing_keywords.slice(0, 4).map((k: string, idx: number) => (
              <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-medium bg-rose-50 text-rose-800 border border-rose-200">
                {k}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between pt-2 border-t border-[var(--border)]">
        <p className="text-xs text-[var(--text-muted)]">
          {hasAudit ? 'Scored on engineering depth, metrics & alignment.' : 'Calculated from verified tests and project history.'}
        </p>
        {onNavigate && (
          <button
            type="button"
            onClick={() => onNavigate('aitools')}
            className="text-xs font-semibold text-sagedeep hover:underline shrink-0 ml-2"
          >
            {hasAudit ? 'Full Gap Analysis →' : 'Audit with Gemini AI →'}
          </button>
        )}
      </div>
    </Card>
  );
};

export const StudentOverview: React.FC<{ student: Student; onNavigate?: (tab: string) => void }> = ({ student, onNavigate }) => {
  const initialResumeScore = student.resumeHistory[0] || student.resumeScore;
  const improvement = (student.resumeScore - initialResumeScore).toFixed(1);

  return (
    <div className="space-y-6">
      <PageHeader
        title={student.skills.length > 0 ? `Welcome back, ${student.name.split(' ')[0]}` : `Welcome, ${student.name.split(' ')[0]}!`}
        desc={student.skills.length > 0 ? `Tracking your path toward ${student.desiredRole || student.role}.` : `Let's start by taking your initial skill test to calculate your verified score.`}
        action={student.verified ? <VerifiedBadge /> : undefined}
      />

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3">
        <StatBlock
          label="Resume score"
          value={student.resumeScore > 0 ? `${student.resumeScore}/10` : 'Pending'}
          sub={student.resumeReview ? 'Gemini AI Audited' : (student.resumeScore > 0 ? `+${improvement} since joining` : 'Audit in AI Tools')}
        />
        <StatBlock
          label="Weekly improvement"
          value={student.skills.length > 0 ? `+${student.weeklyImprovement}%` : '--'}
          sub={student.skills.length > 0 ? 'Weekly progress' : 'Awaiting activity'}
        />
        <StatBlock
          label="Potential"
          value={student.potential > 0 ? `${student.potential}/100` : '--'}
          sub={student.potential > 0 ? 'Skill potential' : 'Pending assessment'}
        />
        <StatBlock
          label="Consistency"
          value={student.consistency > 0 ? `${student.consistency}/100` : '--'}
          sub={student.consistency > 0 ? 'Daily activity' : 'Awaiting logs'}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <Card className="p-5">
          <div className="font-display font-semibold mb-4">Skill snapshot for {student.desiredRole || student.role}</div>
          {student.skills.map((s) => (
            <SkillBar key={s.name} {...s} />
          ))}
          {student.skills.length === 0 && (
            <p className="text-xs text-[var(--text-muted)]">No verified skills yet. Take an assessment to add verified skills.</p>
          )}
        </Card>

        <ResumeScoreCard student={student} onNavigate={onNavigate} />
      </div>

      <div>
        <div className="font-display font-semibold mb-3">Your growth journey</div>
        <GrowthJourney />
      </div>
    </div>
  );
};
