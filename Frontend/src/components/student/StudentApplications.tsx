import React, { useState, useEffect } from 'react';
import { Card, PageHeader, Tag, Button, EmptyState, StatBlock } from '../common/UIComponents';
import { studentApi } from '../../api/student';
import { useAuth } from '../../context/AuthContext';

export interface StudentApplicationItem {
  id: number;
  posting_id?: number;
  title: string;
  posting_type?: string;
  company_name?: string;
  professor_name?: string;
  description?: string;
  required_skills?: string;
  status: 'applied' | 'shortlisted' | 'rejected' | 'selected' | string;
  applied_date?: string;
}

export const StudentApplications: React.FC<{ onBrowseOpportunities?: () => void }> = ({
  onBrowseOpportunities,
}) => {
  const [applications, setApplications] = useState<StudentApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();

  const fetchApplications = async () => {
    if (currentUser && currentUser.role === 'student') {
      try {
        const res = await studentApi.getMyApplications();
        if (res && res.my_applications) {
          setApplications(res.my_applications);
        }
      } catch {
        // fallback
      } finally {
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [currentUser]);

  const totalCount = applications.length;
  const shortlistedCount = applications.filter((a) => a.status === 'shortlisted').length;
  const appliedCount = applications.filter((a) => a.status === 'applied').length;
  const selectedCount = applications.filter((a) => a.status === 'selected').length;

  const renderStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'shortlisted':
        return <Tag tone="sage">Shortlisted ✓</Tag>;
      case 'selected':
        return <Tag tone="sage">Selected 🎉</Tag>;
      case 'rejected':
        return <Tag tone="rose">Not Selected</Tag>;
      default:
        return <Tag tone="blue">Under Review</Tag>;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Applications"
        desc="Track real-time status of your job, internship, and research applications."
      />

      <div className="grid sm:grid-cols-4 gap-3">
        <StatBlock label="Total Applications" value={totalCount} />
        <StatBlock label="Under Review" value={appliedCount} />
        <StatBlock label="Shortlisted" value={shortlistedCount} />
        <StatBlock label="Offers / Selected" value={selectedCount} />
      </div>

      {loading ? (
        <Card className="p-8 text-center text-xs text-[var(--text-muted)]">
          Loading your submitted applications…
        </Card>
      ) : applications.length === 0 ? (
        <div className="space-y-4">
          <EmptyState text="You haven't submitted any applications yet. Explore openings matched to your skills!" />
          {onBrowseOpportunities && (
            <div className="text-center">
              <Button variant="primary" onClick={onBrowseOpportunities}>
                Browse Opportunities →
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app) => (
            <Card key={app.id} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h4 className="font-display font-semibold text-base text-black">{app.title}</h4>
                  {renderStatusBadge(app.status)}
                  <Tag tone="amber">
                    {app.posting_type ? app.posting_type.replace('_', ' ').toUpperCase() : 'OPPORTUNITY'}
                  </Tag>
                </div>
                <div className="text-xs text-[var(--text-muted)] flex items-center gap-2 flex-wrap">
                  <span>🏢 {app.company_name || app.professor_name || 'Partner Host'}</span>
                  {app.applied_date && <span>· 📅 Applied {app.applied_date}</span>}
                </div>
                {app.required_skills && (
                  <div className="flex flex-wrap gap-1 mt-1 pt-1">
                    {app.required_skills.split(',').map((s) => (
                      <Tag key={s.trim()}>{s.trim()}</Tag>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
