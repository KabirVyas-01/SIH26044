import React, { useState, useEffect } from 'react';
import { PortalShell } from '../common/PortalShell';
import {
  AcademicianOverview,
  AcademicianPublish,
  AcademicianPapers,
  AcademicianDiscuss,
} from './AcademicianComponents';
import { ACADEMICIANS } from '../../data/mockData';
import { Academician, ResearchPaper } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { academicianApi } from '../../api/academician';

const ACAD_TABS = [
  { key: 'overview', label: 'Profile',          icon: 'user' },
  { key: 'publish',  label: 'Publish Research', icon: 'upload' },
  { key: 'papers',   label: 'My Papers',        icon: 'book' },
  { key: 'discuss',  label: 'Discussions',      icon: 'msg' },
];

export const AcademicianPortal: React.FC<{ go: (page: string) => void }> = ({ go }) => {
  const [active, setActive] = useState('overview');
  const { currentUser } = useAuth();
  const [papers, setPapers] = useState<ResearchPaper[]>(ACADEMICIANS[0].papers);

  useEffect(() => {
    const fetchPostings = async () => {
      if (currentUser && currentUser.role === 'academician') {
        try {
          const res = await academicianApi.getMyPostings();
          if (res && res.postings && res.postings.length > 0) {
            const mapped: ResearchPaper[] = res.postings.map((p) => ({
              id: p.id,
              title: p.title,
              field: p.required_skills || 'Computer Science',
              desc: p.description,
              discussions: [],
            }));
            setPapers(mapped);
          }
        } catch {
          // fallback
        }
      }
    };

    fetchPostings();
  }, [currentUser]);

  const acad: Academician = {
    ...ACADEMICIANS[0],
    name: currentUser?.name || ACADEMICIANS[0].name,
    field: currentUser?.expertise_domain || ACADEMICIANS[0].field,
    papers,
  };

  const renderView = () => {
    switch (active) {
      case 'overview':
        return <AcademicianOverview acad={acad} />;
      case 'publish':
        return <AcademicianPublish papers={papers} setPapers={setPapers} />;
      case 'papers':
        return <AcademicianPapers papers={papers} />;
      case 'discuss':
        return <AcademicianDiscuss papers={papers} setPapers={setPapers} />;
      default:
        return <AcademicianOverview acad={acad} />;
    }
  };

  return (
    <PortalShell
      portalKey="academician"
      tabs={ACAD_TABS}
      active={active}
      setActive={setActive}
      go={go}
      subtitle={acad.name}
    >
      {renderView()}
    </PortalShell>
  );
};
