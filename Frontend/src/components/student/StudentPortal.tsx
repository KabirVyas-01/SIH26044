import React, { useState, useEffect } from 'react';
import { PortalShell } from '../common/PortalShell';
import { StudentOverview } from './StudentOverview';
import { StudentSkills } from './StudentSkills';
import { StudentRoadmap, StudentDaily } from './StudentRoadmap';
import { StudentAITools, StudentField } from './StudentAITools';
import { StudentOpportunities } from './StudentOpportunities';
import { StudentProjects } from './StudentProjects';
import { StudentProfile } from './StudentProfile';
import { STUDENTS } from '../../data/mockData';
import { Student } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { studentApi } from '../../api/student';

const STUDENT_TABS = [
  { key: 'overview',      label: 'Overview',          icon: 'home' },
  { key: 'skills',        label: 'Skills & Tests',    icon: 'target' },
  { key: 'roadmap',       label: 'Learning Roadmap',  icon: 'compass' },
  { key: 'daily',         label: 'Daily Learning',    icon: 'calendar' },
  { key: 'aitools',       label: 'AI Tools Hub',      icon: 'zap' },
  { key: 'field',         label: 'Field Updates',     icon: 'bars' },
  { key: 'opportunities', label: 'Opportunities',     icon: 'briefcase' },
  { key: 'projects',      label: 'Projects',          icon: 'file' },
  { key: 'profile',       label: 'Profile',           icon: 'user' },
];

export const StudentPortal: React.FC<{ go: (page: string) => void }> = ({ go }) => {
  const [active, setActive] = useState('overview');
  const { currentUser } = useAuth();
  const [student, setStudent] = useState<Student>(STUDENTS[0]);

  useEffect(() => {
    const fetchRealProfile = async () => {
      if (currentUser && currentUser.role === 'student') {
        try {
          const res = await studentApi.getProfile();
          if (res && res.profile) {
            const p = res.profile;
            setStudent((prev) => ({
              ...prev,
              id: p.id,
              name: p.name || prev.name,
              university: p.college || prev.university,
              verified: p.is_verified,
              skills: p.verified_skills && p.verified_skills.length > 0
                ? p.verified_skills.map((s: any) => ({
                    name: s.skill_name,
                    score: Math.round(s.percentage),
                    min: 70,
                  }))
                : prev.skills,
            }));
          }
        } catch {
          // fallback
        }
      }
    };

    fetchRealProfile();
  }, [currentUser]);

  const handleUpdateSkill = (skillName: string, score: number) => {
    setStudent((prev) => {
      const exists = prev.skills.some((s) => s.name.toLowerCase() === skillName.toLowerCase());
      const updatedSkills = exists
        ? prev.skills.map((s) =>
            s.name.toLowerCase() === skillName.toLowerCase() ? { ...s, score } : s
          )
        : [...prev.skills, { name: skillName, score, min: 70 }];

      return {
        ...prev,
        skills: updatedSkills,
        resumeScore: Math.min(10, +(prev.resumeScore + 0.3).toFixed(1)),
        potential: Math.min(100, prev.potential + 2),
      };
    });
  };

  const handleUpdateProfile = (updates: Partial<Student>) => {
    setStudent((prev) => ({ ...prev, ...updates }));
  };

  const renderView = () => {
    switch (active) {
      case 'overview':
        return <StudentOverview student={student} />;
      case 'skills':
        return <StudentSkills student={student} onUpdateSkill={handleUpdateSkill} />;
      case 'roadmap':
        return <StudentRoadmap />;
      case 'daily':
        return <StudentDaily student={student} />;
      case 'aitools':
        return <StudentAITools />;
      case 'field':
        return <StudentField />;
      case 'opportunities':
        return <StudentOpportunities />;
      case 'projects':
        return <StudentProjects student={student} />;
      case 'profile':
        return <StudentProfile student={student} onUpdateProfile={handleUpdateProfile} />;
      default:
        return <StudentOverview student={student} />;
    }
  };

  return (
    <PortalShell
      portalKey="student"
      tabs={STUDENT_TABS}
      active={active}
      setActive={setActive}
      go={go}
      subtitle={student.name}
    >
      {renderView()}
    </PortalShell>
  );
};
