import React, { useState, useEffect } from 'react';
import { PortalShell } from '../common/PortalShell';
import { StudentOverview } from './StudentOverview';
import { StudentSkills } from './StudentSkills';
import { StudentRoadmap, StudentDaily } from './StudentRoadmap';
import { StudentAITools, StudentField } from './StudentAITools';
import { StudentOpportunities } from './StudentOpportunities';
import { StudentProjects } from './StudentProjects';
import { StudentProfile } from './StudentProfile';
import { SkillTestModal } from './SkillTestModal';
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

  // Fresh, clean initial state for newly registered students (Zero fake mock data!)
  const [student, setStudent] = useState<Student>({
    id: currentUser?.id || 'new',
    name: currentUser?.name || 'Student',
    university: currentUser?.college || 'University',
    field: 'Computer Science & Engineering',
    role: 'Full Stack Developer',
    resumeScore: 0,
    potential: 0,
    discipline: 0,
    punctuality: 0,
    consistency: 0,
    weeklyImprovement: 0,
    verified: false,
    resumeHistory: [0],
    dailyLog: [],
    projects: [],
    skills: [], // Starts truly empty!
  });

  const [onboardingSkill, setOnboardingSkill] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealProfile = async () => {
      if (currentUser && currentUser.role === 'student') {
        try {
          const res = await studentApi.getProfile();
          if (res && res.profile) {
            const p = res.profile;
            const realSkills = (p.verified_skills || []).map((s: any) => ({
              name: s.skill_name,
              score: Math.round(s.percentage),
              min: 70,
            }));

            // Calculate real resume score out of 10 based on actual verified skills
            const realResumeScore =
              realSkills.length > 0
                ? +(Math.min(10, 4.0 + realSkills.length * 1.5)).toFixed(1)
                : 0;

            const realPotential =
              realSkills.length > 0
                ? Math.min(100, 50 + realSkills.length * 12)
                : 0;

            setStudent((prev) => ({
              ...prev,
              id: p.id,
              name: p.name || currentUser.name || prev.name,
              university: p.college || prev.university,
              verified: p.is_verified || false,
              skills: realSkills, // Empty [] if new student, real skills if tests taken!
              resumeScore: realResumeScore,
              potential: realPotential,
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

      const newResumeScore = +(Math.min(10, 4.0 + updatedSkills.length * 1.5)).toFixed(1);
      const newPotential = Math.min(100, 50 + updatedSkills.length * 12);

      return {
        ...prev,
        skills: updatedSkills,
        resumeScore: newResumeScore,
        potential: newPotential,
        verified: true,
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
      subtitle={student.university}
    >
      {/* Onboarding Banner for New Students with 0 Verified Skills */}
      {student.skills.length === 0 && (
        <div className="mb-6 p-4 rounded-2xl bg-amber-50 border border-amber-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <div className="text-sm font-semibold text-amber-900">
              ⚡ Action Required: Complete your Initial Skill Assessment
            </div>
            <p className="text-xs text-amber-700 mt-0.5">
              Your profile currently has 0 verified skills. Take your first 5-question test to earn your verified badge and calculate your real resume score!
            </p>
          </div>
          <button
            type="button"
            onClick={() => setOnboardingSkill('Python')}
            className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold shrink-0 shadow-sm"
          >
            Start Python Assessment →
          </button>
        </div>
      )}

      {renderView()}

      {/* Quick Launch Assessment Modal */}
      <SkillTestModal
        open={!!onboardingSkill}
        skill={onboardingSkill || 'Python'}
        onClose={() => setOnboardingSkill(null)}
        onSuccess={handleUpdateSkill}
      />
    </PortalShell>
  );
};
