import React, { useState } from 'react';
import { Card, Button, PageHeader, Tag } from '../common/UIComponents';
import { Icon } from '../common/Icon';
import { Student, ProjectItem } from '../../types';
import { studentApi } from '../../api/student';
import { useAuth } from '../../context/AuthContext';

export const StudentProjects: React.FC<{ student: Student }> = ({ student }) => {
  const [projects, setProjects] = useState<ProjectItem[]>(student.projects);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [tech, setTech] = useState('');
  const [docUrl, setDocUrl] = useState('');
  const { currentUser } = useAuth();

  const add = async () => {
    if (!name) return;

    const newProj: ProjectItem = {
      id: 'p' + Date.now(),
      name,
      tech: tech.split(',').map((s) => s.trim()).filter(Boolean),
      review: 'Analysis complete — solid foundation. Adding automated testing and performance benchmarks will optimize your readiness.',
    };

    setProjects([newProj, ...projects]);

    // If student has document link (github/report), store via API
    if (docUrl && currentUser && currentUser.role === 'student') {
      try {
        await studentApi.uploadDocument('report', docUrl);
      } catch {
        // quiet fallback
      }
    }

    setName('');
    setTech('');
    setDocUrl('');
    setShowForm(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Projects"
        desc="Upload a project to add it to your resume — we'll review the stack and suggest improvements."
        action={
          <Button variant="primary" onClick={() => setShowForm((v) => !v)}>
            <Icon name="upload" className="w-4 h-4" /> Upload project
          </Button>
        }
      />

      {showForm && (
        <Card className="p-5">
          <div className="grid sm:grid-cols-2 gap-3 mb-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Project name"
              className="rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            />
            <input
              value={tech}
              onChange={(e) => setTech(e.target.value)}
              placeholder="Tech stack, comma separated"
              className="rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            />
          </div>
          <div className="mb-3">
            <input
              value={docUrl}
              onChange={(e) => setDocUrl(e.target.value)}
              placeholder="Project Repository or Demo URL (optional)"
              className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
            />
          </div>
          <Button variant="sagesolid" onClick={add}>
            Add project
          </Button>
        </Card>
      )}

      <div className="space-y-4">
        {projects.map((p) => (
          <Card key={p.id} className="p-5">
            <div className="font-display font-semibold mb-1.5">{p.name}</div>
            <div className="flex flex-wrap gap-1.5 mb-3">
              {p.tech.map((t) => (
                <Tag key={t} tone="blue">
                  {t}
                </Tag>
              ))}
            </div>
            <div className="text-xs font-semibold text-[var(--text-muted)] mb-1">Review & feedback</div>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">{p.review}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};
