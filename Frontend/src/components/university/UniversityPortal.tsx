import React, { useState } from 'react';
import { PortalShell } from '../common/PortalShell';
import {
  UniversityOverview,
  UniversityDirectory,
  UniversityGuidance,
} from './UniversityComponents';
import { UNIVERSITIES, STUDENTS } from '../../data/mockData';
import { useAuth } from '../../context/AuthContext';

const UNI_TABS = [
  { key: 'overview',  label: 'Dashboard',        icon: 'home' },
  { key: 'directory', label: 'Student Directory', icon: 'users' },
  { key: 'guidance',  label: 'Guidance',         icon: 'compass' },
];

export const UniversityPortal: React.FC<{ go: (page: string) => void }> = ({ go }) => {
  const [active, setActive] = useState('overview');
  const { currentUser } = useAuth();
  const baseUni = UNIVERSITIES[2];

  const uni = {
    ...baseUni,
    name: currentUser?.name || baseUni.name,
  };

  const students = STUDENTS.filter(
    (s) => !currentUser || currentUser.role !== 'institute' || s.university.includes(uni.name.split(' ')[0]) || true
  );

  const renderView = () => {
    switch (active) {
      case 'overview':
        return <UniversityOverview uni={uni} students={students} />;
      case 'directory':
        return <UniversityDirectory students={students} />;
      case 'guidance':
        return <UniversityGuidance students={students} />;
      default:
        return <UniversityOverview uni={uni} students={students} />;
    }
  };

  return (
    <PortalShell
      portalKey="university"
      tabs={UNI_TABS}
      active={active}
      setActive={setActive}
      go={go}
      subtitle={uni.name}
    >
      {renderView()}
    </PortalShell>
  );
};
