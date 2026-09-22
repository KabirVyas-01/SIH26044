import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  PageHeader,
  StatBlock,
  Tag,
  ProgressBar,
  SkillBar,
  Modal,
  SearchInput,
  EmptyState,
  VerifiedBadge,
} from '../common/UIComponents';
import { University, Student } from '../../types';
import { instituteApi } from '../../api/institute';
import { useAuth } from '../../context/AuthContext';

export const StudentDetailModal: React.FC<{
  student: Student | null;
  onClose: () => void;
  onGuide: (student: Student) => void;
}> = ({ student, onClose, onGuide }) => {
  return (
    <Modal open={!!student} onClose={onClose} title={student ? student.name : ''} wide>
      {student && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 flex-wrap">
            <VerifiedBadge small />
            <Tag>{student.field}</Tag>
            <Tag tone="blue">{student.university}</Tag>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <div className="text-xs font-semibold text-[var(--text-muted)] mb-2">Skills</div>
              {student.skills.map((s) => (
                <SkillBar key={s.name} {...s} />
              ))}
            </div>
            <div>
              <div className="text-xs font-semibold text-[var(--text-muted)] mb-2">Growth signals</div>
              {[
                ['Potential', student.potential],
                ['Discipline', student.discipline],
                ['Consistency', student.consistency],
              ].map(([l, v]) => (
                <div key={l as string} className="mb-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span>{l}</span>
                    <span className="text-[var(--text-muted)]">{v}/100</span>
                  </div>
                  <ProgressBar value={v as number} colorClass="bg-deepblue" />
                </div>
              ))}
            </div>
          </div>
          <Button
            variant="primary"
            className="w-full"
            onClick={() => onGuide(student)}
          >
            Suggest a roadmap
          </Button>
        </div>
      )}
    </Modal>
  );
};

export const GuidanceModal: React.FC<{
  student: Student | null;
  onClose: () => void;
}> = ({ student, onClose }) => {
  const [msg, setMsg] = useState('');
  const [sent, setSent] = useState(false);

  useEffect(() => {
    setMsg('');
    setSent(false);
  }, [student]);

  return (
    <Modal open={!!student} onClose={onClose} title={student ? `Guide ${student.name}` : ''}>
      {student && !sent && (
        <div className="space-y-3">
          <p className="text-sm text-[var(--text-muted)]">
            Suggest a focus area based on {student.name.split(' ')[0]}'s current skill gaps.
          </p>
          <textarea
            value={msg}
            onChange={(e) => setMsg(e.target.value)}
            rows={4}
            placeholder="e.g. Focus on closing the TypeScript gap before applying to frontend roles."
            className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
          />
          <Button variant="primary" className="w-full" onClick={() => setSent(true)}>
            Send roadmap suggestion
          </Button>
        </div>
      )}
      {sent && (
        <p className="text-sm text-sagedeep font-medium py-4 text-center">
          Sent — {student ? student.name.split(' ')[0] : 'Student'} will see this on their dashboard.
        </p>
      )}
    </Modal>
  );
};

export const UniversityOverview: React.FC<{ uni: University; students: Student[] }> = ({
  uni,
  students,
}) => {
  const { currentUser } = useAuth();
  const [liveStats, setLiveStats] = useState<{
    enrolled_students?: number;
    verified_students?: number;
    average_skill_score?: number;
  } | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      if (currentUser && currentUser.role === 'institute') {
        try {
          const res = await instituteApi.getDashboard();
          if (res?.institute_stats) {
            setLiveStats(res.institute_stats);
          }
        } catch {
          // fallback
        }
      }
    };
    fetchStats();
  }, [currentUser]);

  const avg =
    liveStats?.average_skill_score ||
    Math.round(
      students.reduce(
        (a, s) =>
          a + (s.skills.length > 0 ? s.skills.reduce((x, k) => x + k.score, 0) / s.skills.length : 0),
        0
      ) / (students.length || 1)
    );

  const totalCount = liveStats?.enrolled_students || students.length;

  return (
    <div className="space-y-6">
      <PageHeader
        title={uni.name}
        desc={`${uni.city} · ${uni.students.toLocaleString()} enrolled students`}
      />
      <div className="grid sm:grid-cols-4 gap-3">
        <StatBlock
          label="Students on VidyaSarthi"
          value={totalCount}
          sub={liveStats ? "live database" : "demo sample"}
        />
        <StatBlock label="Avg. skill score" value={avg} />
        <StatBlock label="Weekly improvement" value={"+" + uni.improvement + "%"} />
        <StatBlock label="Verified profiles" value="100%" />
      </div>
      <Card className="p-5">
        <div className="font-display font-semibold mb-4">Skill distribution by field</div>
        <div className="space-y-3">
          {[...new Set(students.map((s) => s.field))].map((f) => {
            const grp = students.filter((s) => s.field === f);
            const a = Math.round(
              grp.reduce(
                (x, s) =>
                  x + (s.skills.length > 0 ? s.skills.reduce((y, k) => y + k.score, 0) / s.skills.length : 0),
                0
              ) / (grp.length || 1)
            );
            return (
              <div key={f}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium">{f}</span>
                  <span className="text-[var(--text-muted)]">
                    {a}/100 avg · {grp.length} students
                  </span>
                </div>
                <ProgressBar value={a} />
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

export const UniversityDirectory: React.FC<{ students: Student[] }> = ({ students }) => {
  const [q, setQ] = useState('');
  const [minPotential, setMinPotential] = useState(0);
  const [field, setField] = useState('All');
  const [selected, setSelected] = useState<Student | null>(null);
  const [guiding, setGuiding] = useState<Student | null>(null);

  const fields = ['All', ...new Set(students.map((s) => s.field))];

  const filtered = students.filter(
    (s) =>
      s.name.toLowerCase().includes(q.toLowerCase()) &&
      s.potential >= minPotential &&
      (field === 'All' || s.field === field)
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Student directory"
        desc="Filter by skill, potential and improvement to find who needs guidance."
      />
      <Card className="p-4 space-y-3">
        <SearchInput value={q} onChange={setQ} placeholder="Search students…" />
        <div className="flex flex-wrap gap-3 items-center">
          <select
            value={field}
            onChange={(e) => setField(e.target.value)}
            className="rounded-xl border border-[var(--border)] px-3 py-2 text-xs focus-ring bg-white"
          >
            {fields.map((f) => (
              <option key={f}>{f}</option>
            ))}
          </select>
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-[var(--text-muted)]">Min potential</span>
            {[0, 60, 75].map((v) => (
              <button
                key={v}
                onClick={() => setMinPotential(v)}
                className={
                  "px-3 py-1.5 rounded-full font-semibold border " +
                  (minPotential === v
                    ? "bg-sagedeep text-pcream border-sagedeep"
                    : "border-[var(--border)] hover:bg-black/5")
                }
              >
                {v === 0 ? 'Any' : v + '+'}
              </button>
            ))}
          </div>
        </div>
      </Card>
      <div className="hscroll">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 min-w-[280px]">
          {filtered.map((s) => (
            <button key={s.id} onClick={() => setSelected(s)} className="text-left">
              <Card className="p-4 h-full hover:border-sagedeep transition">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-8 rounded-full bg-mutedsage/60 flex items-center justify-center text-xs font-bold">
                    {s.name[0]}
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-semibold truncate">{s.name}</div>
                    <div className="text-[11px] text-[var(--text-muted)] truncate">{s.field}</div>
                  </div>
                </div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-[var(--text-muted)]">Potential</span>
                  <span className="font-semibold">{s.potential}</span>
                </div>
                <ProgressBar value={s.potential} colorClass="bg-deepblue" height="h-1.5" />
              </Card>
            </button>
          ))}
        </div>
      </div>
      {filtered.length === 0 && <EmptyState text="No students match these filters." />}

      <StudentDetailModal
        student={selected}
        onClose={() => setSelected(null)}
        onGuide={(s) => {
          setSelected(null);
          setGuiding(s);
        }}
      />
      <GuidanceModal student={guiding} onClose={() => setGuiding(null)} />
    </div>
  );
};

export const UniversityGuidance: React.FC<{ students: Student[] }> = ({ students }) => {
  const [guiding, setGuiding] = useState<Student | null>(null);
  const needHelp = [...students].sort((a, b) => a.potential - b.potential).slice(0, 4);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Roadmap & guidance"
        desc="Students who could benefit most from a suggested focus area right now."
      />
      <div className="space-y-3">
        {needHelp.map((s) => {
          const lowestGap = s.skills.reduce(
            (m, k) => (k.min - k.score > m.g ? { n: k.name, g: k.min - k.score } : m),
            { n: 'General', g: -99 }
          );

          return (
            <Card key={s.id} className="p-4 flex items-center justify-between gap-3 flex-wrap">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-mutedsage/60 flex items-center justify-center text-xs font-bold">
                  {s.name[0]}
                </div>
                <div>
                  <div className="text-sm font-semibold">{s.name}</div>
                  <div className="text-xs text-[var(--text-muted)]">
                    Lowest gap: {lowestGap.n}
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                className="border-sagedeep text-sagedeep text-xs px-3 py-2"
                onClick={() => setGuiding(s)}
              >
                Suggest roadmap
              </Button>
            </Card>
          );
        })}
      </div>
      <GuidanceModal student={guiding} onClose={() => setGuiding(null)} />
    </div>
  );
};
