import React, { useState, useEffect } from 'react';
import { PortalShell } from '../common/PortalShell';
import { StudentOverview } from './StudentOverview';
import { StudentSkills } from './StudentSkills';
import { StudentRoadmap, StudentDaily } from './StudentRoadmap';
import { StudentAITools, StudentField } from './StudentAITools';
import { StudentOpportunities } from './StudentOpportunities';
import { StudentApplications } from './StudentApplications';
import { StudentProjects } from './StudentProjects';
import { StudentProfile } from './StudentProfile';
import { SkillTestModal } from './SkillTestModal';
import { Student, SkillItem } from '../../types';
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
  { key: 'applications',  label: 'Applications',      icon: 'checkc' },
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
            const verifiedList = p.verified_skills || [];
            const verifiedMap = new Map<string, number>();
            verifiedList.forEach((s: any) => {
              verifiedMap.set(s.skill_name.toLowerCase(), Math.round(s.percentage));
            });

            // Parse student's declared skills from profile (e.g. "React, SQL, Java")
            const declaredNames: string[] = p.skills
              ? p.skills.split(',').map((s: string) => s.trim()).filter(Boolean)
              : [];

            // Combine declared skills and any verified skills
            const combinedSkillMap = new Map<string, SkillItem>();

            // 1. Add student's declared skills
            declaredNames.forEach((name: string) => {
              const lower = name.toLowerCase();
              const score = verifiedMap.get(lower) ?? 0;
              combinedSkillMap.set(lower, {
                name: name,
                score: score,
                min: 70,
                isVerified: score >= 70,
              });
            });

            // 2. Also add any verified skills not in declared list
            verifiedList.forEach((s: any) => {
              const lower = s.skill_name.toLowerCase();
              if (!combinedSkillMap.has(lower)) {
                combinedSkillMap.set(lower, {
                  name: s.skill_name,
                  score: Math.round(s.percentage),
                  min: 70,
                  isVerified: Math.round(s.percentage) >= 70,
                });
              }
            });

            const allSkills = Array.from(combinedSkillMap.values());
            const verifiedSkillsCount = allSkills.filter((s) => s.isVerified).length;

            // Prioritize genuine Gemini ATS score from SQLite if available; fallback to skill tests count
            const realResumeScore =
              p.resume_score && p.resume_score > 0
                ? +Number(p.resume_score).toFixed(1)
                : verifiedSkillsCount > 0
                ? +(Math.min(10, 4.0 + verifiedSkillsCount * 1.5)).toFixed(1)
                : 0;

            const realPotential =
              verifiedSkillsCount > 0
                ? Math.min(100, 50 + verifiedSkillsCount * 12)
                : 0;

            setStudent((prev) => ({
              ...prev,
              id: p.id,
              name: p.name || currentUser.name || prev.name,
              university: p.college || prev.university,
              verified: p.is_verified || false,
              skills: allSkills,
              resumeScore: realResumeScore,
              potential: realPotential,
              desiredRole: p.desired_role || prev.desiredRole,
              resumeReview: p.resume_review_parsed || p.resume_review,
              resumeText: p.resume_text || prev.resumeText,
              githubUrl: p.github_url || prev.githubUrl,
              leetcodeUrl: p.leetcode_url || prev.leetcodeUrl,
              resumeUrl: p.resume_url || prev.resumeUrl,
              universityRollNo: p.university_roll_no || prev.universityRollNo,
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

      // Preserve existing genuine Gemini score if already computed
      const newResumeScore =
        prev.resumeScore > 0
          ? prev.resumeScore
          : +(Math.min(10, 4.0 + updatedSkills.length * 1.5)).toFixed(1);
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

  const handleUpdateResume = (score: number, review: any, text: string, role?: string) => {
    setStudent((prev) => ({
      ...prev,
      resumeScore: score,
      resumeReview: review,
      resumeText: text,
      desiredRole: role || prev.desiredRole,
      resumeHistory: [...prev.resumeHistory.slice(1), score],
    }));
  };

  const handleUpdateProfile = (updates: Partial<Student>) => {
    setStudent((prev) => ({ ...prev, ...updates }));
  };

  const renderView = () => {
    switch (active) {
      case 'overview':
        return <StudentOverview student={student} onNavigate={(t) => setActive(t)} />;
      case 'skills':
        return <StudentSkills student={student} onUpdateSkill={handleUpdateSkill} />;
      case 'roadmap':
        return <StudentRoadmap student={student} onNavigate={(t) => setActive(t)} />;
      case 'daily':
        return <StudentDaily student={student} />;
      case 'aitools':
        return <StudentAITools student={student} onUpdateResume={handleUpdateResume} />;
      case 'field':
        return <StudentField />;
      case 'opportunities':
        return <StudentOpportunities />;
      case 'applications':
        return <StudentApplications onBrowseOpportunities={() => setActive('opportunities')} />;
      case 'projects':
        return <StudentProjects student={student} />;
      case 'profile':
        return (
          <StudentProfile
            student={student}
            onUpdateProfile={handleUpdateProfile}
            onNavigate={(t) => setActive(t)}
          />
        );
      default:
        return <StudentOverview student={student} onNavigate={(t) => setActive(t)} />;
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
      {/* Dynamic Skill Verification Banner based on Student's Actual Skills */}
      {!student.skills.some((s) => s.isVerified || s.score >= 70) && (
        <div className="mb-6 p-4 rounded-2xl bg-amber-50 border border-amber-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3.5">
          <div className="flex-1">
            <div className="text-sm font-bold text-amber-900 flex items-center gap-1.5">
              <span>⚡</span> Action Required: Verify your first technical skill
            </div>
            <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">
              {student.skills.length > 0
                ? 'Select one of your registered skills below to take a 10-minute assessment, earn your verified badge, and calculate your resume score:'
                : 'Take an assessment in your primary skill to earn your verified badge and calculate your real resume score:'}
            </p>

            {/* If student declared skills, show their actual skills as buttons */}
            {student.skills.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 mt-2.5">
                {student.skills.map((s) => (
                  <button
                    key={s.name}
                    type="button"
                    onClick={() => setOnboardingSkill(s.name)}
                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white border border-amber-300 text-amber-900 hover:bg-amber-100 hover:border-amber-400 shadow-sm transition"
                  >
                    Verify {s.name} →
                  </button>
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-1.5 mt-2.5">
                {['React', 'SQL', 'Java', 'Python', 'Web Development'].map((sk) => (
                  <button
                    key={sk}
                    type="button"
                    onClick={() => setOnboardingSkill(sk)}
                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white border border-amber-300 text-amber-900 hover:bg-amber-100 transition shadow-sm"
                  >
                    Verify {sk} →
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {renderView()}

      {/* Quick Launch Assessment Modal */}
      <SkillTestModal
        open={!!onboardingSkill}
        skill={onboardingSkill}
        onClose={() => setOnboardingSkill(null)}
        onSuccess={handleUpdateSkill}
      />
    </PortalShell>
  );
};
