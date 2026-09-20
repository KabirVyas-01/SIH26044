import React, { useState } from 'react';
import { Card, Button, StatBlock, PageHeader, Tag, ProgressBar } from '../common/UIComponents';
import { Icon } from '../common/Icon';
import { SkillTestModal } from './SkillTestModal';
import { ROADMAP } from '../../data/mockData';
import { Student } from '../../types';

export const StudentRoadmap: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Learning roadmap"
        desc="A focused path from your current skill level to where your target role needs you to be."
      />
      <div className="space-y-4">
        {ROADMAP.map((r) => (
          <Card key={r.skill} className="p-5">
            <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
              <div className="font-display font-semibold">{r.skill}</div>
              <Tag>{r.weeks} weeks</Tag>
            </div>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-xs text-[var(--text-muted)] w-10">{r.from}</span>
              <ProgressBar value={r.from} colorClass="bg-amber-500" />
              <Icon name="arrowr" className="w-3.5 h-3.5 text-[var(--text-muted)] shrink-0" />
              <ProgressBar value={r.to} />
              <span className="text-xs text-[var(--text-muted)] w-10">{r.to}</span>
            </div>
            <div className="grid sm:grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-sage/10 border border-sage/30 p-3">
                <div className="text-xs font-semibold text-sagedeep mb-1">Free resource</div>
                {r.free}
              </div>
              <div className="rounded-xl bg-black/5 p-3">
                <div className="text-xs font-semibold text-[var(--text-muted)] mb-1">Paid resource</div>
                {r.paid}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const StudentDaily: React.FC<{ student: Student }> = ({ student }) => {
  const [log, setLog] = useState(student.dailyLog);
  const [topic, setTopic] = useState('');
  const [hours, setHours] = useState('');
  const [testOpen, setTestOpen] = useState(false);

  const submit = () => {
    if (!topic) return;
    setLog([{ date: 'Today', topic, hours: hours || 1 }, ...log]);
    setTopic('');
    setHours('');
    setTestOpen(true);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Daily learning update"
        desc="Log what you worked on today — a short AI-generated check confirms you actually understood it."
      />

      <Card className="p-5">
        <div className="font-display font-semibold mb-3">Today's learning</div>
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. JavaScript Arrays"
            className="flex-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
          />
          <input
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            placeholder="Hours"
            type="number"
            min="0"
            step="0.5"
            className="sm:w-28 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
          />
          <Button variant="primary" onClick={submit}>
            Submit
          </Button>
        </div>
      </Card>

      <div className="grid sm:grid-cols-4 gap-3">
        <StatBlock label="Discipline" value={student.discipline} />
        <StatBlock label="Punctuality" value={student.punctuality} />
        <StatBlock label="Consistency" value={student.consistency} />
        <StatBlock label="Potential" value={student.potential} />
      </div>

      <Card className="p-5">
        <div className="font-display font-semibold mb-4">Recent activity</div>
        <div className="space-y-3">
          {log.map((l, i) => (
            <div
              key={i}
              className="flex items-center justify-between gap-3 text-sm border-b border-[var(--border)] pb-3 last:border-0 last:pb-0"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="text-xs text-[var(--text-muted)] w-14 shrink-0">{l.date}</span>
                <span className="truncate">{l.topic}</span>
              </div>
              <span className="text-xs text-[var(--text-muted)] shrink-0">{l.hours}h</span>
            </div>
          ))}
        </div>
      </Card>
      <SkillTestModal open={testOpen} onClose={() => setTestOpen(false)} skill={topic || 'today’s topic'} />
    </div>
  );
};
