import React, { useState } from 'react';
import { Card, PageHeader, SearchInput, Tag, EmptyState } from '../common/UIComponents';
import { AI_TOOLS, FIELD_UPDATES } from '../../data/mockData';

export const StudentAITools: React.FC = () => {
  const [q, setQ] = useState('');
  const filtered = AI_TOOLS.filter((t) =>
    (t.name + t.desc + t.use + t.category).toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI tools hub"
        desc="Discover → understand → use. Search by the task you're trying to do."
      />
      <SearchInput
        value={q}
        onChange={setQ}
        placeholder="Search by task, e.g. “summarise a lecture”"
      />
      <div className="grid sm:grid-cols-2 gap-4">
        {filtered.map((t) => (
          <Card key={t.id} className="p-5">
            <div className="flex items-center justify-between mb-2">
              <div className="font-display font-semibold">{t.name}</div>
              <Tag tone="blue">{t.category}</Tag>
            </div>
            <p className="text-sm text-[var(--text-muted)] mb-2 leading-relaxed">{t.desc}</p>
            <p className="text-xs bg-sage/10 border border-sage/30 rounded-lg px-3 py-2 text-sagedeep">
              {t.use}
            </p>
          </Card>
        ))}
        {filtered.length === 0 && <EmptyState text="No AI tools match that task yet." />}
      </div>
    </div>
  );
};

export const StudentField: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Field & market updates"
        desc="What's actually changing in your field right now."
      />
      <div className="space-y-3">
        {FIELD_UPDATES.map((f) => (
          <Card key={f.id} className="p-5">
            <Tag tone="blue">{f.field}</Tag>
            <div className="font-display font-semibold mt-2.5 mb-1">{f.title}</div>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">{f.summary}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};
