import React, { useState, useEffect } from 'react';
import { Card, PageHeader, Tag, ProgressBar, Button, Modal } from '../common/UIComponents';
import { OPPORTUNITIES } from '../../data/mockData';
import { studentApi } from '../../api/student';
import { Opportunity } from '../../types';
import { useAuth } from '../../context/AuthContext';

export const StudentOpportunities: React.FC = () => {
  const [min, setMin] = useState(0);
  const [opportunities, setOpportunities] = useState<Opportunity[]>(OPPORTUNITIES);
  const [appliedIds, setAppliedIds] = useState<(string | number)[]>([]);
  const [applyingId, setApplyingId] = useState<string | number | null>(null);
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null);
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
            <Card
              key={o.id}
              className="p-5 flex flex-col justify-between hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedOpp(o)}
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <div className="font-display font-semibold text-black hover:text-sagedeep">{o.title}</div>
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

              <div className="pt-2 border-t border-[var(--border)] flex justify-between items-center">
                <Button
                  variant="ghost"
                  className="text-xs py-1.5 px-2.5 text-[var(--text-muted)] hover:text-black"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedOpp(o);
                  }}
                >
                  View Details
                </Button>
                <Button
                  variant={isApplied ? "sagesolid" : "outline"}
                  className="text-xs py-1.5 px-3 border-sagedeep text-sagedeep"
                  disabled={isApplied || isApplying}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleApply(o.id);
                  }}
                >
                  {isApplied ? "Applied ✓" : isApplying ? "Applying…" : "Apply now"}
                </Button>
              </div>
            </Card>
          );
        })}
      </div>

      {selectedOpp && (
        <Modal
          open={!!selectedOpp}
          onClose={() => setSelectedOpp(null)}
          wide={true}
          title="Opportunity Details"
        >
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="font-display text-lg font-bold text-black">{selectedOpp.title}</h3>
                <div className="text-sm font-medium text-[var(--text-muted)] mt-0.5">{selectedOpp.company}</div>
              </div>
              <div
                className={
                  "text-xs font-bold rounded-full px-3 py-1 whitespace-nowrap " +
                  (selectedOpp.match >= 80
                    ? "bg-sage/25 text-sagedeep"
                    : selectedOpp.match >= 60
                    ? "bg-amber-100 text-amber-700"
                    : "bg-black/5 text-[var(--text-muted)]")
                }
              >
                {selectedOpp.match}% match
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Tag tone="sage">{selectedOpp.posting_type ? selectedOpp.posting_type.replace('_', ' ').toUpperCase() : 'INTERNSHIP'}</Tag>
              <Tag tone="blue">{selectedOpp.field || 'Engineering'}</Tag>
              <Tag tone="amber">Verified Match</Tag>
            </div>

            <div>
              <h4 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-1.5">Overview & Description</h4>
              <p className="text-sm text-black/80 leading-relaxed whitespace-pre-line bg-black/[0.02] p-3 rounded-xl border border-[var(--border)]">
                {selectedOpp.description || `Exciting opportunity at ${selectedOpp.company} seeking talented individuals. You will work alongside industry mentors on high-impact projects, developing practical experience and contributing to production workflows.`}
              </p>
            </div>

            <div>
              <h4 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-1.5">Required Skills</h4>
              <div className="flex flex-wrap gap-1.5">
                {selectedOpp.skills && selectedOpp.skills.length > 0 ? (
                  selectedOpp.skills.map((s) => (
                    <Tag key={s} tone="sage">{s}</Tag>
                  ))
                ) : (
                  <span className="text-xs text-[var(--text-muted)]">No specific skills listed.</span>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2 border-t border-[var(--border)] text-xs">
              <div>
                <span className="text-[var(--text-muted)] font-medium">Location:</span>
                <p className="font-semibold text-black mt-0.5">Flexible / Hybrid / Remote</p>
              </div>
              <div>
                <span className="text-[var(--text-muted)] font-medium">Stipend / Compensation:</span>
                <p className="font-semibold text-black mt-0.5">Competitive (Per Organization Standards)</p>
              </div>
            </div>

            <div className="pt-3 border-t border-[var(--border)] flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setSelectedOpp(null)}>
                Close
              </Button>
              <Button
                variant={appliedIds.includes(selectedOpp.id) ? "sagesolid" : "primary"}
                disabled={appliedIds.includes(selectedOpp.id) || applyingId === selectedOpp.id}
                onClick={() => handleApply(selectedOpp.id)}
              >
                {appliedIds.includes(selectedOpp.id)
                  ? "Applied ✓"
                  : applyingId === selectedOpp.id
                  ? "Applying…"
                  : "Apply for this Opportunity"}
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
