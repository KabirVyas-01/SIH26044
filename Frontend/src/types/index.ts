export type UserRole = 'student' | 'academician' | 'institute' | 'industry';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  college?: string;
  university_roll_no?: string;
  expertise_domain?: string;
  qualification?: string;
  desired_role?: string;
  skills?: string;
  resume_url?: string;
  prior_experience?: string;
  github_url?: string;
  leetcode_url?: string;
  industry_domain?: string;
  city?: string;
  website_url?: string;
  contact_person?: string;
  admin_tpo_contact?: string;
  department?: string;
  profile_url?: string;
}

export interface SkillItem {
  name: string;
  score: number;
  min: number;
}

export interface DailyLogItem {
  date: string;
  topic: string;
  hours: number | string;
}

export interface ProjectItem {
  id: string;
  name: string;
  tech: string[];
  review: string;
}

export interface Student {
  id: string | number;
  name: string;
  university: string;
  field: string;
  role: string;
  resumeScore: number;
  potential: number;
  discipline: number;
  punctuality: number;
  consistency: number;
  weeklyImprovement: number;
  verified: boolean;
  resumeHistory: number[];
  dailyLog: DailyLogItem[];
  projects: ProjectItem[];
  skills: SkillItem[];
  qualification?: string;
  desiredRole?: string;
  resumeUrl?: string;
  priorExperience?: string;
  githubUrl?: string;
  leetcodeUrl?: string;
  universityRollNo?: string;
}

export interface University {
  id: string | number;
  name: string;
  students: number;
  avgSkill: number;
  improvement: number;
  city: string;
}

export interface CompanyRole {
  id: string;
  title: string;
  skills: { name: string; min: number }[];
}

export interface Company {
  id: string | number;
  name: string;
  field: string;
  roles: CompanyRole[];
}

export interface AITool {
  id: string;
  name: string;
  category: string;
  desc: string;
  use: string;
}

export interface FieldUpdate {
  id: string;
  field: string;
  title: string;
  summary: string;
}

export interface Opportunity {
  id: string | number;
  title: string;
  company: string;
  field: string;
  skills: string[];
  match: number;
  posting_type?: string;
  description?: string;
}

export interface RoadmapItem {
  skill: string;
  from: number;
  to: number;
  weeks: number;
  free: string;
  paid: string;
}

export interface PaperDiscussion {
  student: string;
  q: string;
}

export interface ResearchPaper {
  id: string | number;
  title: string;
  field: string;
  desc: string;
  discussions: PaperDiscussion[];
}

export interface Academician {
  id: string | number;
  name: string;
  field: string;
  papers: ResearchPaper[];
}

export interface NotificationItem {
  id: string;
  text: string;
}

export interface BackendPosting {
  id: number;
  title: string;
  description: string;
  required_skills: string;
  posting_type: string;
  company?: string;
  professor?: string;
  created_at: string;
  total_applicants?: number;
}

export interface BackendApplicant {
  application_id: number;
  status: 'applied' | 'shortlisted' | 'rejected' | 'selected';
  applied_date: string;
  student_id: number;
  name: string;
  email: string;
  college: string;
  skills: string;
  github_url?: string;
  leetcode_url?: string;
  resume_url?: string;
  university_roll_no?: string;
  verification_status: string;
  is_university_verified?: boolean;
  verified_skills?: { skill_name: string; percentage: number }[];
  documents?: { document_type: string; file_url: string }[];
}

export interface BackendAssessmentQuestion {
  id: number;
  skill_name: string;
  question_text: string;
  options: { [key: string]: string };
}
