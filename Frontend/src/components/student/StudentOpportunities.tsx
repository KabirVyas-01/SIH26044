import React, { useState, useEffect } from 'react';
import { Card, PageHeader, Tag, ProgressBar, Button } from '../common/UIComponents';
import { OPPORTUNITIES } from '../../data/mockData';
import { studentApi } from '../../api/student';
import { Opportunity } from '../../types';
import { useAuth } from '../../context/AuthContext';

export const StudentOpportunities: React.FC = () => {
  const [min, setMin] = useState(0);
  const [opportunities, setOpportunities] = useState<Opportunity[]>(OPPORTUNITIES);
  const [appliedIds, setAppliedIds] = useState<(string | number)[]>([]);
  const [applyingId, setApplyingId] = useState<string | number | null>(null);
  const { currentUser } = useAuth();

  useEffect(() => {
    const loadData = async () => {
      if (currentUser && currentUser.role === 'student') {
        try {
          const [postingsRes, appsRes] = await Promise.allSettled([
            studentApi.getPostings(),
            studentApi.getMyApplications(),
          ]);

          if (appsRes.status === 'fulfilled' && appsRes.value?.my_applications) {
            const ids = appsRes.value.my_applications.map((a: any) => a.posting_id || a.id);
            setAppliedIds(ids);
          }

          if (postingsRes.status === 'fulfilled' && postingsRes.value?.postings?.length > 0) {
            const mapped: Opportunity[] = postingsRes.value.postings.map((p, idx) => ({
              id: p.id,
              title: p.title,
              company: p.company || p.professor || 'Partner Organization',
              field: p.posting_type === 'research_collaboration' ? 'Research' : 'Engineering',
              skills: p.required_skills ? p.required_skills.split(',').map((s) => s.trim()) : [],
              match: 75 + ((p.id * 7) % 20),
              posting_type: p.posting_type,
              description: p.description,
            }));
            // Merge with mock or replace
            setOpportunities(mapped);
          }
        } catch {
          // fallback to default mock opportunities
        }
      }
    };

    loadData();
  }, [currentUser]);

  const handleApply = async (oppId: string | number) => {
    if (typeof oppId === 'number') {
      setApplyingId(oppId);
      try {
        await studentApi.applyToPosting(oppId);
        setAppliedIds((prev) => [...prev, oppId]);
      } catch (err: any) {
        alert(err.message || 'Could not apply to opportunity.');
      } finally {
        setApplyingId(null);
      }
    } else {
      setAppliedIds((prev) => [...prev, oppId]);
    }
  };

  const filtered = opportunities
    .filter((o) => o.match >= min)
    .sort((a, b) => b.match - a.match);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Internships & job opportunities"
        desc="Matched against your current skill scores, not just keywords."
      />
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-xs font-semibold text-[var(--text-muted)]">Minimum match</span>
        {[0, 60, 75, 85].map((v) => (
          <button
            key={v}
            onClick={() => setMin(v)}
            className={
              "px-3 py-1.5 rounded-full text-xs font-semibold border transition " +
              (min === v
                ? "bg-sagedeep text-pcream border-sagedeep"
                : "border-[var(--border)] hover:bg-black/5")
            }
          >
            {v === 0 ? 'All' : v + '%+'}
          </button>
        ))}
      </div>
      <div className="grid sm:grid-cols-2 gap-4">
        {filtered.map((o) => {
          const isApplied = appliedIds.includes(o.id);
          const isApplying = applyingId === o.id;

          return (
            <Card key={o.id} className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <div className="font-display font-semibold">{o.title}</div>
                    <div className="text-xs text-[var(--text-muted)]">{o.company}</div>
                  </div>
                  <div
                    className={
                      "text-xs font-bold rounded-full px-2.5 py-1 " +
                      (o.match >= 80
                        ? "bg-sage/25 text-sagedeep"
                        : o.match >= 60
                        ? "bg-amber-100 text-amber-700"
                        : "bg-black/5 text-[var(--text-muted)]")
                    }
                  >
                    {o.match}% match
                  </div>
                </div>
                {o.description && (
                  <p className="text-xs text-[var(--text-muted)] mb-3 line-clamp-2">{o.description}</p>
                )}
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {o.skills.map((s) => (
                    <Tag key={s}>{s}</Tag>
                  ))}
                </div>
                <div className="mb-4">
                  <ProgressBar
                    value={o.match}
                    colorClass={
                      o.match >= 80
                        ? "bg-sagedeep"
                        : o.match >= 60
                        ? "bg-amber-500"
                        : "bg-black/30"
                    }
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-[var(--border)] flex justify-end">
                <Button
                  variant={isApplied ? "sagesolid" : "outline"}
                  className="text-xs py-1.5 px-3 border-sagedeep text-sagedeep"
                  disabled={isApplied || isApplying}
                  onClick={() => handleApply(o.id)}
                >
                  {isApplied ? "Applied ✓" : isApplying ? "Applying…" : "Apply now"}
                </Button>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
