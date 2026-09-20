import {
  University,
  Company,
  AITool,
  FieldUpdate,
  Student,
  Opportunity,
  RoadmapItem,
  ResearchPaper,
  Academician,
  NotificationItem,
} from '../types';

export const UNIVERSITIES: University[] = [
  { id: 'u1', name: 'Ashgrove Institute of Technology', students: 2140, avgSkill: 68, improvement: 12, city: 'Pune' },
  { id: 'u2', name: 'Meridian State University', students: 3380, avgSkill: 61, improvement: 8, city: 'Coimbatore' },
  { id: 'u3', name: 'North Ridge College of Engineering', students: 1520, avgSkill: 74, improvement: 15, city: 'Indore' },
  { id: 'u4', name: 'Fairview University', students: 2670, avgSkill: 58, improvement: 6, city: 'Nagpur' },
];

export const COMPANIES: Company[] = [
  {
    id: 'c1',
    name: 'Solivant Labs',
    field: 'Product Engineering',
    roles: [
      { id: 'r1', title: 'Frontend Engineering Intern', skills: [{ name: 'React', min: 70 }, { name: 'JavaScript', min: 75 }] },
      { id: 'r2', title: 'Data Analyst — Associate', skills: [{ name: 'SQL', min: 65 }, { name: 'Python', min: 60 }] },
    ],
  },
  {
    id: 'c2',
    name: 'Brightwell Analytics',
    field: 'Data & AI',
    roles: [
      { id: 'r3', title: 'ML Engineering Intern', skills: [{ name: 'Python', min: 75 }, { name: 'Machine Learning', min: 65 }] },
    ],
  },
  {
    id: 'c3',
    name: 'Northlane Systems',
    field: 'Cloud Infrastructure',
    roles: [
      { id: 'r4', title: 'Cloud Support Associate', skills: [{ name: 'AWS', min: 60 }, { name: 'Linux', min: 55 }] },
    ],
  },
  {
    id: 'c4',
    name: 'Harbor & Finch Design Co.',
    field: 'Product Design',
    roles: [
      { id: 'r5', title: 'UI/UX Design Intern', skills: [{ name: 'Figma', min: 70 }, { name: 'UI Design', min: 65 }] },
    ],
  },
];

export const AI_TOOLS: AITool[] = [
  { id: 'a1', name: 'Codeium', category: 'Coding', desc: 'An AI pair-programmer that suggests code as you type.', use: 'Speed up assignments and debug faster while you learn to code.' },
  { id: 'a2', name: 'Notion AI', category: 'Writing', desc: 'Drafts, summarises and restructures notes inside your workspace.', use: 'Turn messy lecture notes into clean study material.' },
  { id: 'a3', name: 'Perplexity', category: 'Research', desc: 'An answer engine that cites sources for every claim.', use: 'Research a topic quickly before writing a paper or report.' },
  { id: 'a4', name: 'Figma AI', category: 'Design', desc: 'Generates layout variants and cleans up design files.', use: 'Prototype an interface for your project without starting from zero.' },
  { id: 'a5', name: 'Otter.ai', category: 'Productivity', desc: 'Transcribes and summarises lectures and meetings in real time.', use: 'Revisit a lecture without re-watching the whole recording.' },
  { id: 'a6', name: 'Hugging Face Spaces', category: 'Machine Learning', desc: 'Hosts and runs ML models directly in the browser.', use: 'Test a model for your ML coursework without local setup.' },
];

export const FIELD_UPDATES: FieldUpdate[] = [
  { id: 'f1', field: 'Web Development', title: 'Server components are becoming the default in modern frameworks', summary: 'Teams are shipping less client-side JavaScript by rendering more on the server.' },
  { id: 'f2', field: 'Data Science', title: 'Small, specialised models are outperforming general ones on narrow tasks', summary: 'Companies are fine-tuning compact models instead of calling large general ones.' },
  { id: 'f3', field: 'Cloud', title: 'Cost-aware architecture is now a core interview topic', summary: 'Recruiters increasingly ask candidates to justify infrastructure choices on cost.' },
  { id: 'f4', field: 'Design', title: 'Design systems are absorbing more accessibility testing', summary: 'Component libraries now ship built-in contrast and screen-reader checks.' },
  { id: 'f5', field: 'Product', title: 'Hiring is shifting toward portfolio depth over resume breadth', summary: 'Reviewers are spending more time on one strong project than a long skill list.' },
];

export function mkStudent(p: Partial<Student> & { id: string; name: string; university: string; field: string; role: string }): Student {
  return {
    verified: true,
    resumeHistory: [4.5, 5, 6, 6.5, 7.5, 8],
    discipline: 70,
    punctuality: 75,
    consistency: 68,
    potential: 74,
    weeklyImprovement: 9,
    resumeScore: 7,
    dailyLog: [
      { date: 'Sep 19', topic: 'React Hooks — useEffect cleanup', hours: 1.5 },
      { date: 'Sep 18', topic: 'SQL window functions', hours: 2 },
      { date: 'Sep 17', topic: 'DSA — binary search variants', hours: 1 },
      { date: 'Sep 15', topic: 'System design basics', hours: 1.5 },
    ],
    projects: [
      {
        id: 'p1',
        name: 'Campus Marketplace App',
        tech: ['React', 'Node.js', 'MongoDB'],
        review: 'Solid data modelling and clean component structure. Add pagination and error boundaries to make it production-ready.',
      },
      {
        id: 'p2',
        name: 'Attendance Predictor',
        tech: ['Python', 'Pandas', 'scikit-learn'],
        review: 'Good feature engineering. Model evaluation would benefit from cross-validation instead of a single train/test split.',
      },
    ],
    skills: [],
    ...p,
  };
}

export const STUDENTS: Student[] = [
  mkStudent({
    id: 's1',
    name: 'Aditi Rao',
    university: 'North Ridge College of Engineering',
    field: 'Frontend Engineering',
    role: 'Frontend Engineer',
    resumeScore: 8,
    potential: 82,
    discipline: 80,
    consistency: 78,
    weeklyImprovement: 11,
    skills: [
      { name: 'JavaScript', score: 78, min: 75 },
      { name: 'React', score: 72, min: 70 },
      { name: 'CSS', score: 65, min: 60 },
      { name: 'TypeScript', score: 48, min: 60 },
    ],
  }),
  mkStudent({
    id: 's2',
    name: 'Kabir Mehta',
    university: 'Ashgrove Institute of Technology',
    field: 'Data Science',
    role: 'Data Analyst',
    resumeScore: 6.5,
    potential: 70,
    weeklyImprovement: 6,
    skills: [
      { name: 'Python', score: 74, min: 60 },
      { name: 'SQL', score: 58, min: 65 },
      { name: 'Statistics', score: 66, min: 55 },
    ],
  }),
  mkStudent({
    id: 's3',
    name: 'Meera Iyer',
    university: 'North Ridge College of Engineering',
    field: 'Machine Learning',
    role: 'ML Engineer',
    resumeScore: 7,
    potential: 88,
    weeklyImprovement: 14,
    skills: [
      { name: 'Python', score: 81, min: 75 },
      { name: 'Machine Learning', score: 63, min: 65 },
      { name: 'Math for ML', score: 70, min: 60 },
    ],
  }),
  mkStudent({
    id: 's4',
    name: 'Rohan Das',
    university: 'Meridian State University',
    field: 'Cloud Infrastructure',
    role: 'Cloud Support Associate',
    resumeScore: 5.5,
    potential: 60,
    weeklyImprovement: 4,
    skills: [
      { name: 'AWS', score: 52, min: 60 },
      { name: 'Linux', score: 61, min: 55 },
      { name: 'Networking', score: 47, min: 50 },
    ],
  }),
  mkStudent({
    id: 's5',
    name: 'Sanya Kapoor',
    university: 'Fairview University',
    field: 'Product Design',
    role: 'UI/UX Designer',
    resumeScore: 8.5,
    potential: 79,
    weeklyImprovement: 10,
    skills: [
      { name: 'Figma', score: 80, min: 70 },
      { name: 'UI Design', score: 71, min: 65 },
      { name: 'User Research', score: 55, min: 50 },
    ],
  }),
  mkStudent({
    id: 's6',
    name: 'Devansh Patil',
    university: 'Ashgrove Institute of Technology',
    field: 'Backend Engineering',
    role: 'Backend Engineer',
    resumeScore: 6,
    potential: 65,
    weeklyImprovement: 5,
    skills: [
      { name: 'Java', score: 69, min: 65 },
      { name: 'Spring Boot', score: 54, min: 60 },
      { name: 'SQL', score: 60, min: 55 },
    ],
  }),
  mkStudent({
    id: 's7',
    name: 'Ira Sharma',
    university: 'Meridian State University',
    field: 'Frontend Engineering',
    role: 'Frontend Engineer',
    resumeScore: 7.5,
    potential: 83,
    weeklyImprovement: 12,
    skills: [
      { name: 'JavaScript', score: 80, min: 75 },
      { name: 'React', score: 76, min: 70 },
      { name: 'CSS', score: 70, min: 60 },
    ],
  }),
  mkStudent({
    id: 's8',
    name: 'Yash Verma',
    university: 'Fairview University',
    field: 'Data Science',
    role: 'Data Analyst',
    resumeScore: 4.5,
    potential: 55,
    weeklyImprovement: 3,
    skills: [
      { name: 'Python', score: 58, min: 60 },
      { name: 'SQL', score: 49, min: 65 },
      { name: 'Statistics', score: 51, min: 55 },
    ],
  }),
];

export const OPPORTUNITIES: Opportunity[] = [
  { id: 'o1', title: 'Frontend Engineering Intern', company: 'Solivant Labs', field: 'Frontend Engineering', skills: ['React', 'JavaScript', 'CSS'], match: 88 },
  { id: 'o2', title: 'ML Engineering Intern', company: 'Brightwell Analytics', field: 'Machine Learning', skills: ['Python', 'Machine Learning'], match: 74 },
  { id: 'o3', title: 'Cloud Support Associate', company: 'Northlane Systems', field: 'Cloud Infrastructure', skills: ['AWS', 'Linux'], match: 61 },
  { id: 'o4', title: 'UI/UX Design Intern', company: 'Harbor & Finch Design Co.', field: 'Product Design', skills: ['Figma', 'UI Design'], match: 91 },
  { id: 'o5', title: 'Data Analyst — Associate', company: 'Solivant Labs', field: 'Data Science', skills: ['SQL', 'Python'], match: 69 },
  { id: 'o6', title: 'Backend Engineering Intern', company: 'Northlane Systems', field: 'Backend Engineering', skills: ['Java', 'SQL'], match: 58 },
];

export const ROADMAP: RoadmapItem[] = [
  { skill: 'TypeScript', from: 48, to: 70, weeks: 4, free: 'TypeScript Handbook (official docs)', paid: 'Frontend Masters — TypeScript Fundamentals' },
  { skill: 'System Design Basics', from: 20, to: 55, weeks: 6, free: 'freeCodeCamp — System Design for Beginners', paid: 'Educative — Grokking the System Design Interview' },
  { skill: 'Testing (Jest)', from: 15, to: 50, weeks: 3, free: 'Jest official docs + Testing Library guides', paid: 'Udemy — React Testing Library & Jest' },
];

export const PAPERS: ResearchPaper[] = [
  {
    id: 'pp1',
    title: 'Attention Sparsity in Long-Context Retrieval',
    field: 'Machine Learning',
    desc: 'Explores sparse attention patterns to reduce compute cost in long-context transformer retrieval tasks.',
    discussions: [{ student: 'Meera Iyer', q: 'Did you compare against sliding-window attention as a baseline?' }],
  },
  {
    id: 'pp2',
    title: 'Accessibility Debt in Component Libraries',
    field: 'Human-Computer Interaction',
    desc: 'A survey of accessibility regressions introduced as design systems scale across teams.',
    discussions: [{ student: 'Sanya Kapoor', q: 'Would this apply to headless component libraries too?' }],
  },
];

export const ACADEMICIANS: Academician[] = [
  { id: 'ac1', name: 'Dr. Naveen Bhatt', field: 'Machine Learning', papers: [PAPERS[0]] },
  { id: 'ac2', name: 'Dr. Leela Krishnan', field: 'Human-Computer Interaction', papers: [PAPERS[1]] },
  { id: 'ac3', name: 'Dr. Farhan Ali', field: 'Distributed Systems', papers: [] },
  { id: 'ac4', name: 'Dr. Priya Nathan', field: 'Computational Linguistics', papers: [] },
];

export const NOTIFICATIONS: NotificationItem[] = [
  { id: 'n1', text: 'North Ridge College sent you a learning roadmap suggestion.' },
  { id: 'n2', text: 'Your JavaScript skill score increased to 78/100.' },
  { id: 'n3', text: 'Solivant Labs viewed your profile.' },
];
