import React, { useState } from 'react';
import { PortalShell } from '../common/PortalShell';
import {
  IndustryOverview,
  IndustryFilters,
  IndustryResults,
  IndustryApplications,
  IndustryConnections,
} from './IndustryComponents';
import { COMPANIES } from '../../data/mockData';
import { useAuth } from '../../context/AuthContext';

const IND_TABS = [
  { key: 'overview',     label: 'Dashboard',              icon: 'home' },
  { key: 'filters',      label: 'Requirements & Filters', icon: 'filter' },
  { key: 'results',      label: 'Search Results',         icon: 'search' },
  { key: 'applications', label: 'Applications',           icon: 'users' },
  { key: 'connections',  label: 'Connections',            icon: 'link' },
];

export const IndustryPortal: React.FC<{ go: (page: string) => void }> = ({ go }) => {
  const [active, setActive] = useState('overview');
  const [filters, setFilters] = useState({
    skill: '',
    minSkill: 0,
    minPotential: 0,
    field: '',
    university: '',
  });
  const [connections, setConnections] = useState<(string | number)[]>([]);
  const { currentUser } = useAuth();
  const baseCompany = COMPANIES[0];

  const company = {
    ...baseCompany,
    name: currentUser?.name || baseCompany.name,
  };

  const renderView = () => {
    switch (active) {
      case 'overview':
        return <IndustryOverview company={company} />;
      case 'filters':
        return <IndustryFilters filters={filters} setFilters={setFilters} />;
      case 'results':
        return (
          <IndustryResults
            filters={filters}
            connections={connections}
            setConnections={setConnections}
          />
        );
      case 'applications':
        return <IndustryApplications />;
      case 'connections':
        return <IndustryConnections connections={connections} />;
      default:
        return <IndustryOverview company={company} />;
    }
  };

  return (
    <PortalShell
      portalKey="industry"
      tabs={IND_TABS}
      active={active}
      setActive={setActive}
      go={go}
      subtitle={company.name}
    >
      {renderView()}
    </PortalShell>
  );
};
