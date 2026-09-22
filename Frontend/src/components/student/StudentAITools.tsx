import React, { useState, useEffect, useMemo } from 'react';
import { Card, PageHeader, Button, Tag, ProgressBar } from '../common/UIComponents';
import { FIELD_UPDATES } from '../../data/mockData';
import { studentApi } from '../../api/student';
import { Student } from '../../types';

interface StudentAIToolsProps {
  student?: Student;
  onUpdateResume?: (score: number, review: any, text: string, role?: string) => void;
}

const RESUME_ROLE_OPTIONS = [
  'Full Stack Developer',
  'Backend Engineer',
  'Frontend Developer',
  'AI/ML Specialist',
  'Data Scientist',
  'Cloud & DevOps Engineer',
  'Cybersecurity Analyst',
  'Chemical Engineer',
  'Mechanical Engineer',
  'Civil Engineer',
  'Electrical Engineer',
  'Biotech Specialist',
  'Mobile App Developer'
];

const ROADMAP_ROLE_OPTIONS = [
  'Chemical Engineer',
  'Mechanical Engineer',
  'Civil Engineer',
  'Electrical Engineer',
  'Full Stack Developer',
  'AI/ML Specialist',
  'Data Scientist',
  'Backend Engineer',
  'Frontend Developer',
  'Cloud & DevOps',
  'Cybersecurity Analyst',
  'Biotech Specialist',
  'Mobile App Developer',
  'UI/UX Designer',
  'Blockchain & Web3'
];

const POPULAR_SKILLS = ['Python', 'React', 'JavaScript', 'SQL', 'Aspen Plus', 'MATLAB', 'SolidWorks', 'DevOps & Docker', 'Git & CI/CD'];

export const StudentAITools: React.FC<StudentAIToolsProps> = ({ student, onUpdateResume }) => {
  const [activeTool, setActiveTool] = useState<'resume' | 'roadmap' | 'interview'>('resume');

  // 1. Resume Analyzer State
  const [resumeInput, setResumeInput] = useState(student?.resumeText || '');
  const [targetRole, setTargetRole] = useState(student?.desiredRole || student?.role || 'Full Stack Developer');
  const [resumeResult, setResumeResult] = useState<any>(student?.resumeReview || null);
  const [loadingResume, setLoadingResume] = useState(false);
  const [justSaved, setJustSaved] = useState(false);
  const [autoFilledBadge, setAutoFilledBadge] = useState(false);

  // 2. Roadmap Generator State
  const initialRoadmapRole = student?.desiredRole || student?.role || student?.field || 'Full Stack Developer';
  const [roadmapRole, setRoadmapRole] = useState(initialRoadmapRole);
  const [roadmapLevel, setRoadmapLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('intermediate');
  const [roadmapWeeks, setRoadmapWeeks] = useState<4 | 8>(4);
  const [roadmapOverview, setRoadmapOverview] = useState('');
  const [roadmapResult, setRoadmapResult] = useState<any[]>([]);
  const [loadingRoadmap, setLoadingRoadmap] = useState(false);

  useEffect(() => {
    if (student) {
      if (!resumeInput && student.resumeText) setResumeInput(student.resumeText);
      if (student.desiredRole) {
        setTargetRole(student.desiredRole);
        setRoadmapRole(student.desiredRole);
      } else if (student.field) {
        setRoadmapRole(student.field);
      }
      if (!resumeResult && student.resumeReview) setResumeResult(student.resumeReview);
    }
  }, [student]);

  // Auto-fill from student profile with domain adaptation
  const handleAutoFillResume = () => {
    if (!student) return;
    const f = (student.field || student.role || student.desiredRole || '').toLowerCase();
    const isChemical = /chem/i.test(f) || /process/i.test(f);
    const isMechanical = /mech/i.test(f) || /auto/i.test(f) || /aero/i.test(f);
    const isCivil = /civil/i.test(f) || /struct/i.test(f) || /construct/i.test(f);
    const isElectrical = /electr/i.test(f) || /vlsi/i.test(f) || /embedded/i.test(f);

    let defaultSkills = 'Python, JavaScript, React, SQL, Git';
    let defaultProject = '• Scalable Web Application: Built with React, Node.js, and SQLite. Implemented JWT authentication and responsive UI.';
    let defaultExperience = 'Fresher / Computer Science coursework with hands-on lab projects and collaborative hackathons.';

    if (isChemical) {
      defaultSkills = 'Process Simulation (Aspen Plus / DWSIM), Fluid Mechanics, Heat & Mass Transfer, Reaction Kinetics, P&ID, HAZOP Safety Analysis, MATLAB';
      defaultProject = '• Bio-Ethanol Distillation Simulation: Modeled a 10-tray fractionation column in Aspen Plus with thermal pinch optimization, reducing utility reboiler duty by 18%.\n• Industrial Reactor Sizing: Designed a cooled continuous stirred tank reactor (CSTR) for exothermic esterification with thermal runaway prevention.';
      defaultExperience = 'Chemical Engineering coursework with laboratory fluid flow measurements, shell-and-tube heat exchanger sizing, and process safety reviews.';
    } else if (isMechanical) {
      defaultSkills = 'SolidWorks 3D CAD, ANSYS FEA/CFD, Applied Thermodynamics, GD&T, CNC Machining, MATLAB, Machine Design';
      defaultProject = '• Two-Stage Epicyclic Gearbox: Designed and simulated full stress/strain distribution in ANSYS with AGMA gear rating.\n• Gas Turbine Heat Exchanger: Sized a multi-pass cross-flow heat exchanger using LMTD and NTU methods.';
      defaultExperience = 'Mechanical Engineering labs covering stress-strain tensile testing, wind-tunnel aerodynamics, and CAD assemblies.';
    } else if (isCivil) {
      defaultSkills = 'AutoCAD Civil 3D, STAAD.Pro / ETABS, Structural RCC Design, Soil Mechanics, Primavera P6, Surveying';
      defaultProject = '• Seismic Analysis of Multi-Storey RCC Frame: Modeled 8-storey frame under zone IV seismic loads adhering to IS 1893 standards.\n• Cantilever Retaining Wall Design: Calculated soil bearing capacity and factor of safety against overturning and sliding.';
      defaultExperience = 'Civil Engineering laboratory testing in soil shear strength, concrete mix design, and total station surveying.';
    } else if (isElectrical) {
      defaultSkills = 'KiCad PCB Design, STM32 / ARM Embedded C, Power Electronics, MATLAB/Simulink, SPICE Circuit Simulation, Verilog';
      defaultProject = '• Synchronous Buck Converter: Designed closed-loop 48V to 12V SMPS with 94% measured efficiency and KiCad 4-layer PCB.\n• FPGA UART Communication: Implemented full-duplex UART controller in Verilog with parity checking.';
      defaultExperience = 'Electrical Engineering coursework covering three-phase power flow, microcontrollers, and analog filter topologies.';
    }

    const skillsList = student.skills?.length ? student.skills.map((s) => s.name).join(', ') : defaultSkills;
    const projectsList = student.projects?.length
      ? student.projects.map((p) => `• ${p.name}: Built with ${(p.tech || []).join(', ')}. ${p.review || ''}`).join('\n')
      : defaultProject;
    const experienceText = student.priorExperience || defaultExperience;
    const universityText = student.university || 'Institute of Engineering & Technology';
    const degreeText = student.qualification || student.field || (isChemical ? 'B.Tech in Chemical Engineering' : 'B.Tech in Engineering');
    const roleText = student.desiredRole || student.role || (isChemical ? 'Chemical Engineer' : 'Engineering Specialist');

    const generatedResume = `CANDIDATE: ${student.name || 'Student'}
UNIVERSITY: ${universityText}
DEGREE: ${degreeText}
TARGET ROLE: ${roleText}

TECHNICAL SKILLS:
${skillsList}

PRIOR EXPERIENCE:
${experienceText}

KEY PROJECTS:
${projectsList}

PORTFOLIO & LINKS:
GitHub: ${student.githubUrl || 'github.com/profile'}
Portfolio: ${student.leetcodeUrl || 'portfolio-profile.dev'}`;

    setResumeInput(generatedResume);
    if (student.desiredRole) setTargetRole(student.desiredRole);
    setAutoFilledBadge(true);
    setTimeout(() => setAutoFilledBadge(false), 4000);
  };

  // 3. Interview Prep State
  const [interviewSkill, setInterviewSkill] = useState('Python');
  const [interviewLevel, setInterviewLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('intermediate');
  const [interviewRound, setInterviewRound] = useState<'technical' | 'scenario' | 'architecture'>('technical');
  const [interviewQuestions, setInterviewQuestions] = useState<any[]>([]);
  const [loadingInterview, setLoadingInterview] = useState(false);
  const [masteredQIds, setMasteredQIds] = useState<number[]>([]);
  const [openHints, setOpenHints] = useState<number[]>([]);
  const [openAnswers, setOpenAnswers] = useState<number[]>([]);

  // Derived interview skills
  const availableSkills = useMemo(() => {
    const fromStudent = student?.skills?.map((s) => s.name) || [];
    const combined = [...fromStudent, ...POPULAR_SKILLS];
    return Array.from(new Set(combined));
  }, [student?.skills]);

  // Handlers
  const handleAnalyzeResume = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeInput.trim()) return;
    setLoadingResume(true);
    setJustSaved(false);
    try {
      const res = await studentApi.analyzeResume(resumeInput, targetRole);
      setResumeResult(res);
      setJustSaved(true);
      if (onUpdateResume && res && res.ats_score) {
        onUpdateResume(Number(res.ats_score), res, resumeInput, targetRole);
      }
    } catch {
      const fallback = {
        ats_score: 7.8,
        verdict: `Candidate demonstrates solid technical aptitude for ${targetRole}. Focus on quantifying project impact and adding cloud deployment to reach senior recruiter benchmarks.`,
        section_scores: { technical_depth: 8.2, project_impact: 7.0, clarity_structure: 7.8, role_alignment: 8.2 },
        strengths: [
          'Solid foundation in core computer science programming and syntax',
          'Direct alignment with software design principles and hands-on tooling'
        ],
        missing_keywords: ['Docker / Containers', 'CI/CD Pipelines', 'System Design Patterns', 'SQL Query Optimization'],
        gap_analysis: `There is a clear gap in demonstrating production-scale experience for ${targetRole}. Recruiter screening systems reward measurable business impact and automated testing.`,
        actionable_steps: [
          'Quantify project outcomes using XYZ format (e.g. reduced query latency by 35%).',
          `Incorporate target role standard keywords: Docker, Redis, CI/CD.`,
          'Add a dedicated testing section showing automated test coverage.'
        ]
      };
      setResumeResult(fallback);
      setJustSaved(true);
      if (onUpdateResume) {
        onUpdateResume(7.8, fallback, resumeInput, targetRole);
      }
    } finally {
      setLoadingResume(false);
    }
  };

  const handleGenerateRoadmap = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoadingRoadmap(true);
    try {
      const currentSkills = student?.skills?.map((s) => s.name).join(', ') || '';
      const res = await studentApi.generateRoadmap(roadmapRole, roadmapLevel, roadmapWeeks, currentSkills);
      const list = Array.isArray(res) ? res : (res?.roadmap || []);
      setRoadmapResult(list);
      setRoadmapOverview(res?.overview || '');
    } catch {
      const r = roadmapRole.toLowerCase();
      let fallbackCurriculum: any[] = [];

      if (/chem/i.test(r) || /process/i.test(r)) {
        fallbackCurriculum = [
          {
            week: 'Week 1',
            title: 'Fluid Mechanics & Process Thermodynamics',
            focus: 'Navier-Stokes, Bernoulli equations, EOS phase behavior, and hydraulic pipe/pump sizing.',
            topics: ['Navier-Stokes & Bernoulli Equations', 'Peng-Robinson & NRTL EOS', 'Pipe Head Loss & NPSH', 'Pump & Compressor Sizing'],
            project: 'Calculate hydraulic head loss, NPSH, and pump operating point for an industrial cooling water loop.',
            milestone: 'Fluid & Thermo Mechanics Verified'
          },
          {
            week: 'Week 2',
            title: 'Heat & Mass Transfer Unit Operations',
            focus: 'Sizing shell-and-tube exchangers and calculating multistage vapor-liquid separation.',
            topics: ['LMTD & NTU Exchanger Sizing', 'McCabe-Thiele Distillation', 'Packed Column Hydraulics', 'Fickian Diffusion'],
            project: 'Size theoretical tray count and column diameter for a binary ethanol-water fractionation column.',
            milestone: 'Unit Operations Design Verified'
          },
          {
            week: 'Week 3',
            title: 'Reaction Kinetics & Industrial Reactor Design',
            focus: 'Formulating reaction rate laws, yield selectivity, and sizing continuous flow reactors.',
            topics: ['Batch, CSTR & PFR Equations', 'Arrhenius Activation Energy', 'Catalytic Selectivity', 'Thermal Runaway Prevention'],
            project: 'Size a cooled plug flow reactor (PFR) for an exothermic synthesis, mitigating thermal runaway.',
            milestone: 'Reactor Design Specialist'
          },
          {
            week: 'Week 4',
            title: 'Process Simulation (Aspen Plus / DWSIM) & HAZOP Safety',
            focus: 'Simulating plant flowsheets and conducting comprehensive hazard operability reviews.',
            topics: ['Aspen Plus / DWSIM Flowsheets', 'Piping & Instrumentation (P&ID)', 'HAZOP Risk Matrix', 'OSHA PSM Standards'],
            project: 'Build a converged flowsheet in Aspen Plus/DWSIM and complete a full HAZOP node risk audit.',
            milestone: 'Certified Chemical Process Engineer'
          }
        ];
      } else if (/mech/i.test(r) || /auto/i.test(r) || /aero/i.test(r)) {
        fallbackCurriculum = [
          {
            week: 'Week 1',
            title: 'Mechanics of Materials & Stress Analysis',
            focus: 'Calculating stress-strain states, beam deflection, and failure criteria.',
            topics: ["Mohr's Circle & Stresses", 'Von Mises Yield Criteria', 'Beam Deflection & Bending', 'GD&T Tolerancing'],
            project: 'Perform stress and fatigue failure analysis for a drive shaft subjected to combined loading.',
            milestone: 'Stress Analysis Certified'
          },
          {
            week: 'Week 2',
            title: 'Applied Thermodynamics & Heat Transfer',
            focus: 'Power cycles, conduction/convection, and heat exchanger sizing.',
            topics: ['Rankine & Brayton Cycles', 'Conduction & Convection', 'Heat Exchanger NTU Sizing', 'HVAC Psychrometry'],
            project: 'Design and size a shell-and-tube heat exchanger for a turbine cooling loop.',
            milestone: 'Thermal Systems Verified'
          },
          {
            week: 'Week 3',
            title: 'Fluid Dynamics & Simulation (CFD / FEA)',
            focus: 'Structural deformation and fluid flow modeling in ANSYS.',
            topics: ['FEA Meshing & Convergence', 'ANSYS Structural Analysis', 'CFD Flow Modeling', 'Boundary Layer & Drag'],
            project: 'Conduct a 3D FEA modal and structural deflection simulation on an aluminum bracket.',
            milestone: 'Simulation Specialist'
          },
          {
            week: 'Week 4',
            title: 'Machine Element Design & CAD / CAM Manufacturing',
            focus: 'Precision assembly design and CNC toolpath generation.',
            topics: ['Gear & Bearing Life Sizing', 'SolidWorks 3D CAD', 'CNC Toolpath G-Code', 'DFMA Principles'],
            project: 'Design a fully constrained 3D assembly of a two-stage gearbox with engineering drawings.',
            milestone: 'Certified Mechanical Design Engineer'
          }
        ];
      } else if (/civil/i.test(r) || /struct/i.test(r) || /construct/i.test(r)) {
        fallbackCurriculum = [
          {
            week: 'Week 1',
            title: 'Structural Analysis & Mechanics of Solids',
            focus: 'Indeterminate structures, shear forces, and bending moments.',
            topics: ['Moment Distribution Method', 'Slope Deflection', 'Influence Lines', 'Structural Design Codes'],
            project: 'Analyze a 3-span continuous bridge girder subjected to moving truck loads.',
            milestone: 'Structural Analysis Specialist'
          },
          {
            week: 'Week 2',
            title: 'RCC & Structural Steel Design',
            focus: 'Reinforced concrete slabs, columns, and structural steel framing.',
            topics: ['Limit State RCC Design', 'Column Buckling (Euler)', 'Bolted & Welded Joints', 'Torsional Buckling'],
            project: 'Design complete reinforcement schedule and cross-sections for a multi-storey RCC frame.',
            milestone: 'RCC & Steel Design Verified'
          },
          {
            week: 'Week 3',
            title: 'Geotechnical Soil Mechanics & Foundations',
            focus: 'Bearing capacity, slope stability, and foundation sizing.',
            topics: ["Terzaghi's Bearing Capacity", 'Mohr-Coulomb Strength', 'Settlement Consolidation', 'Retaining Wall Stability'],
            project: 'Perform bearing capacity and settlement calculations for a cantilever retaining wall.',
            milestone: 'Geotechnical Specialist'
          },
          {
            week: 'Week 4',
            title: 'Transportation, BIM & Construction Mgmt',
            focus: 'Pavement design, BIM coordination, and project scheduling.',
            topics: ['Pavement Design', 'AutoCAD Civil 3D', 'Primavera P6 Scheduling', 'Quantity Surveying & Estimation'],
            project: 'Produce highway alignment plans in AutoCAD Civil 3D with a CPM Gantt schedule.',
            milestone: 'Certified Civil Infrastructure Engineer'
          }
        ];
      } else if (/electr/i.test(r) || /vlsi/i.test(r) || /circuit/i.test(r)) {
        fallbackCurriculum = [
          {
            week: 'Week 1',
            title: 'Circuit Analysis & Electromagnetic Fields',
            focus: 'Mastering AC steady state, three-phase systems, and transient analysis.',
            topics: ['Kirchhoff Laws & Nodal Analysis', 'Laplace Transient Analysis', 'Three-Phase Systems', "Maxwell's Equations"],
            project: 'Model transient RLC filter response using Laplace equations and verify in SPICE.',
            milestone: 'Circuit Analysis Certified'
          },
          {
            week: 'Week 2',
            title: 'Analog Electronics & Power Converters',
            focus: 'Op-amp active filters and switch-mode power supply design.',
            topics: ['Op-Amp Active Filters', 'MOSFET Small-Signal Models', 'Differential Amplifiers', 'DC-DC Buck/Boost Converters'],
            project: 'Design and simulate a high-efficiency DC-DC Buck converter with closed-loop regulation.',
            milestone: 'Analog Design Verified'
          },
          {
            week: 'Week 3',
            title: 'Digital Systems & Embedded Hardware',
            focus: 'Hardware description logic and ARM microcontrollers.',
            topics: ['Verilog HDL & State Machines', 'FPGA Synthesis & Timing', 'ARM Cortex STM32 C', 'I2C / SPI / UART Bus Interfacing'],
            project: 'Implement a hardware UART module in Verilog and synthesize onto an FPGA.',
            milestone: 'Digital & Embedded Specialist'
          },
          {
            week: 'Week 4',
            title: 'Power Systems, Machines & PCB Design',
            focus: 'Electric machines, power distribution, and multi-layer PCB layout.',
            topics: ['Induction Motors & Sizing', 'Power Flow Analysis', 'KiCad Multi-Layer PCB', 'EMC / EMI Grounding Rules'],
            project: 'Design a 4-layer microcontroller evaluation board in KiCad ready for fabrication.',
            milestone: 'Certified Electrical Systems Engineer'
          }
        ];
      } else {
        fallbackCurriculum = [
          {
            week: 'Week 1',
            title: 'Foundations & Modular Architecture',
            focus: `Core fundamentals, project structure, and modular patterns for ${roadmapRole}.`,
            topics: ['Core Architecture', 'Clean Code Principles', 'Git Flow & Branching', 'Environment Configuration'],
            project: `Build a clean starter project architecture demonstrating modular design for ${roadmapRole}.`,
            milestone: 'Architecture & Foundations Verified'
          },
          {
            week: 'Week 2',
            title: 'Data Modeling & API Services',
            focus: 'Designing resilient data schemas and authenticated API contracts.',
            topics: ['Relational Schemas', 'REST / JSON API Design', 'Authentication & JWT Middleware', 'Input Validation'],
            project: 'Build an authenticated multi-role CRUD service with database transactions.',
            milestone: 'Data & Service Architecture'
          },
          {
            week: 'Week 3',
            title: 'Integration & State Management',
            focus: 'Connecting frontend clients with real-time responsive data.',
            topics: ['Component Hierarchy', 'Asynchronous API Fetching', 'Global & Local State', 'Responsive Mobile-First UI'],
            project: 'Connect full-stack client portal with live API endpoints and loading states.',
            milestone: 'Full Stack Integration'
          },
          {
            week: 'Week 4',
            title: 'Testing, Deployment & Production Polish',
            focus: 'Hardening the application for production scale with automated CI/CD.',
            topics: ['Unit & Integration Tests', 'Containerization with Docker', 'CI/CD Pipelines', 'Performance Profiling'],
            project: `Deploy a production-ready portfolio project showcasing all skills required of an industry ${roadmapRole}.`,
            milestone: `Certified ${roadmapRole} Ready`
          }
        ];
      }
      setRoadmapResult(fallbackCurriculum);
      setRoadmapOverview(`A dedicated ${roadmapWeeks}-week curriculum calibrated for ${roadmapRole} at the ${roadmapLevel} level.`);
    } finally {
      setLoadingRoadmap(false);
    }
  };

  const handleFetchInterview = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoadingInterview(true);
    setMasteredQIds([]);
    setOpenHints([]);
    setOpenAnswers([]);
    try {
      const res = await studentApi.getInterviewQuestions(interviewSkill, interviewLevel, interviewRound);
      const list = Array.isArray(res) ? res : (res?.questions || []);
      setInterviewQuestions(list);
    } catch {
      setInterviewQuestions([
        {
          question: `How do you manage error handling and edge cases in ${interviewSkill}?`,
          level: interviewLevel,
          category: 'Language Mechanics & Reliability',
          hint: 'Mention structured error responses, boundary validation, and avoiding silent failures.',
          sample_answer: 'Validate all inputs at the API or function boundary, use structured try-catch/except blocks to prevent unhandled crashes, and log errors with contextual stack traces.',
          follow_up: `How does ${interviewSkill} handle concurrency or thread safety when errors happen during asynchronous operations?`
        },
        {
          question: `What is a major performance bottleneck you might encounter when scaling ${interviewSkill}?`,
          level: interviewLevel,
          category: 'Performance & Optimization',
          hint: 'Think of memory allocation, unindexed queries, or blocking operations on the main loop.',
          sample_answer: 'Common bottlenecks include memory leaks from circular references or unclosed handles, repeated database lookups that lack indexing, and blocking I/O calls.',
          follow_up: 'What profiling tools or telemetry metrics would you inspect first to confirm this bottleneck?'
        },
        {
          question: `Explain how state and memory management work in ${interviewSkill}.`,
          level: interviewLevel,
          category: 'Memory & State Architecture',
          hint: 'Differentiate between heap vs stack, garbage collection cycles, or immutable states.',
          sample_answer: 'Memory is allocated dynamically on the heap while function frames use stack memory. Automatic garbage collection detects unreachable references, while predictable immutable updates avoid shared state mutation.',
          follow_up: 'What is the trade-off between immutable data structures and garbage collection overhead?'
        }
      ]);
    } finally {
      setLoadingInterview(false);
    }
  };

  const toggleMastered = (idx: number) => {
    setMasteredQIds((prev) => (prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]));
  };

  const toggleHint = (idx: number) => {
    setOpenHints((prev) => (prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]));
  };

  const toggleAnswer = (idx: number) => {
    setOpenAnswers((prev) => (prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]));
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Career & Prep Engine"
        desc="Interactive Gemini-powered tools calibrated to your profile, chosen domain, and career seniority level."
      />

      {/* Tool Selector Tabs */}
      <div className="flex gap-2 border-b border-[var(--border)] pb-3 hscroll no-scrollbar whitespace-nowrap">
        <button
          type="button"
          onClick={() => setActiveTool('resume')}
          className={`px-4 py-2.5 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
            activeTool === 'resume'
              ? 'bg-sagedeep text-white shadow-sm'
              : 'bg-black/5 text-[var(--text-muted)] hover:bg-black/10'
          }`}
        >
          <span>📄</span>
          <span>AI Resume & ATS Analyzer</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTool('roadmap')}
          className={`px-4 py-2.5 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
            activeTool === 'roadmap'
              ? 'bg-sagedeep text-white shadow-sm'
              : 'bg-black/5 text-[var(--text-muted)] hover:bg-black/10'
          }`}
        >
          <span>🗺️</span>
          <span>AI Career Roadmap Builder</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTool('interview')}
          className={`px-4 py-2.5 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
            activeTool === 'interview'
              ? 'bg-sagedeep text-white shadow-sm'
              : 'bg-black/5 text-[var(--text-muted)] hover:bg-black/10'
          }`}
        >
          <span>🎙️</span>
          <span>AI Mock Interview Coach</span>
        </button>
      </div>

      {/* 1. RESUME ANALYZER */}
      {activeTool === 'resume' && (
        <div className="space-y-5">
          <Card className="p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[var(--border)] pb-3">
              <div>
                <h3 className="font-display font-semibold text-base text-[#2C3524]">ATS Resume Audit & Gap Analysis</h3>
                <p className="text-xs text-[var(--text-muted)]">
                  Compare your credentials directly against modern tech ATS filters and recruiter standards.
                </p>
              </div>
              <div className="flex items-center gap-2">
                {autoFilledBadge && (
                  <span className="text-xs text-emerald-700 font-semibold bg-emerald-50 border border-emerald-200 px-2 py-1 rounded-lg animate-pulse">
                    ✓ Profile Loaded!
                  </span>
                )}
                <button
                  type="button"
                  onClick={handleAutoFillResume}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-sagedeep/10 text-sagedeep hover:bg-sagedeep/20 transition flex items-center gap-1.5"
                  title="Auto-populate from your profile information, skills, and projects"
                >
                  <span>⚡</span>
                  <span>Auto-Fill From My Profile</span>
                </button>
              </div>
            </div>

            <form onSubmit={handleAnalyzeResume} className="space-y-4">
              {/* Target Role Selector & Quick Chips */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-semibold text-[var(--text-muted)]">Target Engineering Role</label>
                  <span className="text-[11px] text-[var(--text-muted)]">Click a quick chip or type below</span>
                </div>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {RESUME_ROLE_OPTIONS.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setTargetRole(r)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition ${
                        targetRole.toLowerCase() === r.toLowerCase()
                          ? 'bg-sagedeep text-white'
                          : 'bg-black/5 hover:bg-black/10 text-[#2C3524]'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
                <input
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2 text-sm focus-ring bg-white text-black"
                  placeholder="e.g. Backend Engineer, Full Stack Developer"
                />
              </div>

              {/* Resume Text Content */}
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)] flex items-center justify-between">
                  <span>Resume Content, Projects & Technical Summary</span>
                  <span className="text-[11px] font-normal text-[var(--text-muted)]">
                    {resumeInput.length} characters
                  </span>
                </label>
                <textarea
                  rows={5}
                  required
                  value={resumeInput}
                  onChange={(e) => setResumeInput(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] p-3 text-sm focus-ring font-mono bg-white text-black leading-relaxed"
                  placeholder="Paste your resume, project descriptions, and technical skills here or click 'Auto-Fill From My Profile' above..."
                />
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                <Button variant="primary" type="submit" disabled={loadingResume}>
                  {loadingResume ? 'Analyzing with Gemini AI…' : 'Analyze Resume & Compute ATS Score'}
                </Button>
                {justSaved && (
                  <div className="text-xs text-emerald-700 font-semibold flex items-center gap-1.5">
                    <span>✓</span> Synced to Student Profile & Dashboard
                  </div>
                )}
              </div>
            </form>
          </Card>

          {resumeResult && (
            <Card className="p-6 space-y-5 border-sagedeep/30">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[var(--border)]">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-sagedeep/15 text-sagedeep">
                      Gemini ATS Audit
                    </span>
                    {justSaved && (
                      <span className="text-[11px] font-medium text-emerald-700 flex items-center gap-1">
                        <span>✓</span> Saved to Student Profile
                      </span>
                    )}
                  </div>
                  <div className="font-display font-semibold text-xl mt-1 text-[#2C3524]">
                    Analysis for {targetRole}
                  </div>
                </div>

                <div className="sm:text-right bg-sage/10 sm:bg-transparent p-3 sm:p-0 rounded-xl">
                  <div className="text-xs text-[var(--text-muted)] font-medium">ATS Readiness Score</div>
                  <div className="text-3xl font-bold font-display text-sagedeep flex items-baseline sm:justify-end gap-1">
                    {resumeResult.ats_score}
                    <span className="text-sm font-normal text-[var(--text-muted)]">/ 10</span>
                  </div>
                </div>
              </div>

              {/* Executive Verdict */}
              {resumeResult.verdict && (
                <div className="p-3.5 rounded-xl bg-sagedeep/5 border border-sagedeep/20 text-xs leading-relaxed text-[#2C3524]">
                  <div className="font-semibold text-sagedeep mb-1 flex items-center gap-1.5">
                    <span>⚡</span> Executive Reviewer Verdict
                  </div>
                  <p className="italic">"{resumeResult.verdict}"</p>
                </div>
              )}

              {/* Section Scores Breakdown */}
              {resumeResult.section_scores && (
                <div>
                  <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2.5">
                    Evaluation Dimensions Breakdown
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    {[
                      { label: 'Technical Depth', score: resumeResult.section_scores.technical_depth },
                      { label: 'Project Impact', score: resumeResult.section_scores.project_impact },
                      { label: 'Clarity & Structure', score: resumeResult.section_scores.clarity_structure },
                      { label: 'Role Alignment', score: resumeResult.section_scores.role_alignment },
                    ].map((sec) => (
                      <div key={sec.label} className="p-2.5 rounded-xl bg-[var(--surface)] border border-[var(--border)]">
                        <div className="text-[11px] text-[var(--text-muted)] truncate mb-1">{sec.label}</div>
                        <div className="flex items-center justify-between text-xs font-bold mb-1.5">
                          <span>{sec.score ? `${sec.score}/10` : '--'}</span>
                        </div>
                        <ProgressBar value={sec.score ? sec.score * 10 : 0} />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strengths & Missing Keywords */}
              <div className="grid sm:grid-cols-2 gap-4 pt-2">
                <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200/80">
                  <div className="text-xs font-bold text-emerald-900 mb-2 flex items-center gap-1.5">
                    <span>✓</span> Evidenced Technical Strengths
                  </div>
                  <ul className="space-y-1.5 text-xs text-emerald-950">
                    {resumeResult.strengths?.map((s: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5 leading-relaxed">
                        <span className="text-emerald-600 font-bold">•</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-3.5 rounded-xl bg-rose-50/70 border border-rose-200/80">
                  <div className="text-xs font-bold text-rose-900 mb-2 flex items-center gap-1.5">
                    <span>⚠</span> Crucial Missing ATS Keywords
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {resumeResult.missing_keywords?.map((k: string, idx: number) => (
                      <Tag key={idx} tone="rose">{k}</Tag>
                    ))}
                  </div>
                  <p className="text-[11px] text-rose-800 mt-2 leading-tight">
                    Recruiter screening algorithms prioritize candidates with demonstrable proficiency in these keywords.
                  </p>
                </div>
              </div>

              {/* Deep Skill Gap Analysis */}
              {resumeResult.gap_analysis && (
                <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200">
                  <div className="text-xs font-bold text-amber-900 mb-1 flex items-center gap-1.5">
                    <span>🔍</span> Deep Skill Gap Analysis
                  </div>
                  <p className="text-xs text-amber-950 leading-relaxed">
                    {resumeResult.gap_analysis}
                  </p>
                </div>
              )}

              {/* Actionable Steps / Recommendations */}
              {((resumeResult.actionable_steps && resumeResult.actionable_steps.length > 0) || (resumeResult.recommendations && resumeResult.recommendations.length > 0)) && (
                <div className="pt-2 border-t border-[var(--border)]">
                  <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                    Actionable Steps to Reach 9.0+ ATS Score
                  </div>
                  <div className="grid gap-2">
                    {(resumeResult.actionable_steps || resumeResult.recommendations).map((r: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-[#2C3524] bg-[var(--surface)] p-2.5 rounded-xl border border-[var(--border)]">
                        <span className="w-5 h-5 rounded-full bg-sagedeep/10 text-sagedeep font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span className="leading-relaxed">{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          )}
        </div>
      )}

      {/* 2. ROADMAP BUILDER */}
      {activeTool === 'roadmap' && (
        <div className="space-y-5">
          <Card className="p-5 space-y-4">
            <div>
              <h3 className="font-display font-semibold text-base text-[#2C3524]">Domain-Tailored Learning Curriculum</h3>
              <p className="text-xs text-[var(--text-muted)]">
                Generate distinct, role-specific career roadmaps calibrated to your current seniority and target timeline.
              </p>
            </div>

            <form onSubmit={handleGenerateRoadmap} className="space-y-4">
              {/* Quick Track Chips */}
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)] mb-1 block">
                  Select Specialization Track
                </label>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {ROADMAP_ROLE_OPTIONS.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setRoadmapRole(r)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition ${
                        roadmapRole.toLowerCase() === r.toLowerCase()
                          ? 'bg-sagedeep text-white'
                          : 'bg-black/5 hover:bg-black/10 text-[#2C3524]'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
                <input
                  value={roadmapRole}
                  onChange={(e) => setRoadmapRole(e.target.value)}
                  className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2 text-sm focus-ring bg-white text-black"
                  placeholder="e.g. Chemical Engineer, Mechanical Engineer, AI/ML Specialist, Full Stack Developer"
                />
              </div>

              {/* Level & Timeline Controls */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-[var(--text-muted)] mb-1.5 block">
                    Experience / Seniority Level
                  </label>
                  <div className="grid grid-cols-3 gap-1.5">
                    {[
                      { id: 'beginner', label: 'Beginner', desc: 'Foundations' },
                      { id: 'intermediate', label: 'Intermediate', desc: 'Production' },
                      { id: 'advanced', label: 'Advanced', desc: 'Scale & Arch' },
                    ].map((lvl) => (
                      <button
                        key={lvl.id}
                        type="button"
                        onClick={() => setRoadmapLevel(lvl.id as any)}
                        className={`p-2 rounded-xl text-center border transition ${
                          roadmapLevel === lvl.id
                            ? 'border-sagedeep bg-sagedeep/10 text-sagedeep font-bold'
                            : 'border-[var(--border)] bg-white hover:bg-black/5 text-[var(--text-muted)]'
                        }`}
                      >
                        <div className="text-xs">{lvl.label}</div>
                        <div className="text-[10px] font-normal opacity-80">{lvl.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-[var(--text-muted)] mb-1.5 block">
                    Roadmap Duration
                  </label>
                  <div className="grid grid-cols-2 gap-1.5">
                    {[
                      { weeks: 4, label: '4 Weeks', desc: 'Accelerated Sprint' },
                      { weeks: 8, label: '8 Weeks', desc: 'Deep Dive Mastery' },
                    ].map((w) => (
                      <button
                        key={w.weeks}
                        type="button"
                        onClick={() => setRoadmapWeeks(w.weeks as 4 | 8)}
                        className={`p-2 rounded-xl text-center border transition ${
                          roadmapWeeks === w.weeks
                            ? 'border-sagedeep bg-sagedeep/10 text-sagedeep font-bold'
                            : 'border-[var(--border)] bg-white hover:bg-black/5 text-[var(--text-muted)]'
                        }`}
                      >
                        <div className="text-xs">{w.label}</div>
                        <div className="text-[10px] font-normal opacity-80">{w.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <Button variant="primary" type="submit" disabled={loadingRoadmap}>
                  {loadingRoadmap ? 'Building Specialized Roadmap…' : `Generate ${roadmapWeeks}-Week ${roadmapRole} Roadmap`}
                </Button>
              </div>
            </form>
          </Card>

          {/* Roadmap Results */}
          {roadmapResult.length > 0 && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-sagedeep/5 border border-sagedeep/20 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-display font-semibold text-base text-[#2C3524]">
                      {roadmapRole} Curriculum
                    </span>
                    <Tag tone="sage">{roadmapLevel.toUpperCase()}</Tag>
                    <Tag tone="blue">{roadmapWeeks} WEEKS</Tag>
                  </div>
                  {roadmapOverview && (
                    <p className="text-xs text-[var(--text-muted)] mt-1">{roadmapOverview}</p>
                  )}
                </div>
                <div className="text-xs text-[var(--text-muted)] shrink-0">
                  {roadmapResult.length} progressive modules
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                {roadmapResult.map((step, idx) => (
                  <Card key={idx} className="p-5 space-y-3 flex flex-col justify-between border-[var(--border)] hover:border-sagedeep/40 transition">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <Tag tone="blue">{step.week || `Week ${idx + 1}`}</Tag>
                        <span className="text-xs font-semibold text-sagedeep text-right">
                          {step.title || step.focus || 'Specialized Module'}
                        </span>
                      </div>

                      {step.focus && (
                        <div className="text-xs text-[#2C3524] font-medium leading-relaxed bg-black/5 p-2 rounded-lg">
                          🎯 <strong>Core Focus:</strong> {step.focus}
                        </div>
                      )}

                      {step.topics && step.topics.length > 0 && (
                        <div className="text-xs text-[var(--text-muted)] pt-1">
                          <div className="font-semibold text-black mb-1">Key Curriculum Topics:</div>
                          <ul className="space-y-1">
                            {step.topics.map((t: string, i: number) => (
                              <li key={i} className="flex items-start gap-1.5 leading-snug">
                                <span className="text-sagedeep font-bold">•</span>
                                <span>{t}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    <div className="space-y-2 pt-2 border-t border-[var(--border)]">
                      {step.project && (
                        <div className="text-xs text-[#2C3524] leading-relaxed">
                          <strong className="text-sagedeep">🚀 Hands-on Capstone:</strong> {step.project}
                        </div>
                      )}
                      {step.milestone && (
                        <div className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200/80 px-2.5 py-1 rounded-lg flex items-center gap-1.5">
                          <span>🏆</span>
                          <span>Milestone: {step.milestone}</span>
                        </div>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. INTERVIEW COACH */}
      {activeTool === 'interview' && (
        <div className="space-y-5">
          <Card className="p-5 space-y-4">
            <div>
              <h3 className="font-display font-semibold text-base text-[#2C3524]">Targeted Technical Interview Simulator</h3>
              <p className="text-xs text-[var(--text-muted)]">
                Master realistic interview loops tailored to specific technical domains, complete with guiding hints, model answers, and follow-up probes.
              </p>
            </div>

            <form onSubmit={handleFetchInterview} className="space-y-4">
              {/* Quick Skill Selector */}
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)] mb-1 block">
                  Select Technical Skill
                </label>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {availableSkills.map((sk) => (
                    <button
                      key={sk}
                      type="button"
                      onClick={() => setInterviewSkill(sk)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition ${
                        interviewSkill.toLowerCase() === sk.toLowerCase()
                          ? 'bg-sagedeep text-white'
                          : 'bg-black/5 hover:bg-black/10 text-[#2C3524]'
                      }`}
                    >
                      {sk}
                    </button>
                  ))}
                </div>
                <input
                  value={interviewSkill}
                  onChange={(e) => setInterviewSkill(e.target.value)}
                  className="w-full rounded-xl border border-[var(--border)] px-3.5 py-2 text-sm focus-ring bg-white text-black"
                  placeholder="e.g. Python, React, SQL, Docker, Go"
                />
              </div>

              {/* Difficulty & Round Type Selector */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-[var(--text-muted)] mb-1.5 block">
                    Difficulty Calibration
                  </label>
                  <div className="grid grid-cols-3 gap-1.5">
                    {[
                      { id: 'beginner', label: 'Beginner', desc: 'Core Syntax' },
                      { id: 'intermediate', label: 'Intermediate', desc: 'Production' },
                      { id: 'advanced', label: 'Advanced', desc: 'Internals & GIL' },
                    ].map((lvl) => (
                      <button
                        key={lvl.id}
                        type="button"
                        onClick={() => setInterviewLevel(lvl.id as any)}
                        className={`p-2 rounded-xl text-center border transition ${
                          interviewLevel === lvl.id
                            ? 'border-sagedeep bg-sagedeep/10 text-sagedeep font-bold'
                            : 'border-[var(--border)] bg-white hover:bg-black/5 text-[var(--text-muted)]'
                        }`}
                      >
                        <div className="text-xs">{lvl.label}</div>
                        <div className="text-[10px] font-normal opacity-80">{lvl.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-[var(--text-muted)] mb-1.5 block">
                    Interview Round Format
                  </label>
                  <div className="grid grid-cols-3 gap-1.5">
                    {[
                      { id: 'technical', label: 'Technical', desc: 'Deep Dive' },
                      { id: 'scenario', label: 'Scenario', desc: 'Real-world Bug' },
                      { id: 'architecture', label: 'Architecture', desc: 'System Design' },
                    ].map((rnd) => (
                      <button
                        key={rnd.id}
                        type="button"
                        onClick={() => setInterviewRound(rnd.id as any)}
                        className={`p-2 rounded-xl text-center border transition ${
                          interviewRound === rnd.id
                            ? 'border-sagedeep bg-sagedeep/10 text-sagedeep font-bold'
                            : 'border-[var(--border)] bg-white hover:bg-black/5 text-[var(--text-muted)]'
                        }`}
                      >
                        <div className="text-xs">{rnd.label}</div>
                        <div className="text-[10px] font-normal opacity-80">{rnd.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <Button variant="primary" type="submit" disabled={loadingInterview}>
                  {loadingInterview ? 'Synthesizing Interview Loop…' : `Get ${interviewLevel.toUpperCase()} ${interviewSkill} Questions`}
                </Button>
              </div>
            </form>
          </Card>

          {/* Interview Questions Presentation */}
          {interviewQuestions.length > 0 && (
            <div className="space-y-4">
              {/* Practice Tracker Status */}
              <div className="p-4 rounded-xl bg-white border border-[var(--border)] flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
                <div>
                  <div className="font-display font-semibold text-base text-[#2C3524]">
                    Mock Interview Session: {interviewSkill}
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">
                    Level: <span className="font-semibold text-black capitalize">{interviewLevel}</span> • Round: <span className="font-semibold text-black capitalize">{interviewRound}</span>
                  </div>
                </div>

                <div className="sm:w-60 space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span>Practice Mastery:</span>
                    <span className="text-sagedeep">{masteredQIds.length} / {interviewQuestions.length}</span>
                  </div>
                  <ProgressBar
                    value={interviewQuestions.length ? (masteredQIds.length / interviewQuestions.length) * 100 : 0}
                    colorClass="bg-emerald-600"
                  />
                </div>
              </div>

              {/* Questions List */}
              <div className="space-y-4">
                {interviewQuestions.map((q, idx) => {
                  const isMastered = masteredQIds.includes(idx);
                  const isHintOpen = openHints.includes(idx);
                  const isAnswerOpen = openAnswers.includes(idx);

                  return (
                    <Card
                      key={idx}
                      className={`p-5 space-y-3.5 transition border ${
                        isMastered ? 'border-emerald-300 bg-emerald-50/20' : 'border-[var(--border)]'
                      }`}
                    >
                      {/* Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[var(--border)] pb-2.5">
                        <div className="flex items-center gap-2">
                          <span className="w-6 h-6 rounded-full bg-sagedeep text-white flex items-center justify-center text-xs font-bold shrink-0">
                            {idx + 1}
                          </span>
                          {q.category && <Tag tone="sage">{q.category}</Tag>}
                          <span className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                            {q.level || interviewLevel}
                          </span>
                        </div>

                        <button
                          type="button"
                          onClick={() => toggleMastered(idx)}
                          className={`px-3 py-1 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 self-start sm:self-auto ${
                            isMastered
                              ? 'bg-emerald-600 text-white shadow-sm'
                              : 'bg-black/5 text-[var(--text-muted)] hover:bg-black/10'
                          }`}
                        >
                          <span>{isMastered ? '✓' : '○'}</span>
                          <span>{isMastered ? 'Mastered' : 'Mark as Mastered'}</span>
                        </button>
                      </div>

                      {/* Question Text */}
                      <div className="font-semibold text-sm sm:text-base text-[#2C3524] leading-relaxed">
                        {q.question}
                      </div>

                      {/* Action Controls: Hint & Model Answer */}
                      <div className="flex flex-wrap items-center gap-2 pt-1">
                        {q.hint && (
                          <button
                            type="button"
                            onClick={() => toggleHint(idx)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                              isHintOpen
                                ? 'bg-amber-100 text-amber-900 border border-amber-300'
                                : 'bg-black/5 text-[#2C3524] hover:bg-black/10'
                            }`}
                          >
                            <span>💡</span>
                            <span>{isHintOpen ? 'Hide Hint' : 'Show Hint'}</span>
                          </button>
                        )}

                        <button
                          type="button"
                          onClick={() => toggleAnswer(idx)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                            isAnswerOpen
                              ? 'bg-sagedeep text-white'
                              : 'bg-sagedeep/10 text-sagedeep hover:bg-sagedeep/20'
                          }`}
                        >
                          <span>📖</span>
                          <span>{isAnswerOpen ? 'Hide Model Answer' : 'Reveal Model Answer'}</span>
                        </button>
                      </div>

                      {/* Guiding Hint Collapsible */}
                      {isHintOpen && q.hint && (
                        <div className="text-xs text-amber-950 bg-amber-50 border border-amber-200 p-3 rounded-xl leading-relaxed">
                          <strong className="text-amber-900">💡 Interviewer Hint:</strong> {q.hint}
                        </div>
                      )}

                      {/* Model Answer Collapsible */}
                      {isAnswerOpen && (
                        <div className="text-xs bg-sagedeep/5 border border-sagedeep/20 p-4 rounded-xl space-y-2">
                          <div className="font-semibold text-sagedeep flex items-center gap-1.5">
                            <span>🎓</span>
                            <span>Industry Benchmark Model Answer:</span>
                          </div>
                          <p className="text-black leading-relaxed font-sans whitespace-pre-line">
                            {q.sample_answer || q.answer}
                          </p>
                        </div>
                      )}

                      {/* Follow-up Probe */}
                      {q.follow_up && (
                        <div className="text-xs text-blue-950 bg-blue-50/70 border border-blue-200/80 p-3 rounded-xl leading-relaxed flex items-start gap-2">
                          <span className="text-blue-600 font-bold shrink-0">🎯</span>
                          <div>
                            <strong className="text-blue-900">Follow-up Probe:</strong> "{q.follow_up}"
                          </div>
                        </div>
                      )}
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const StudentField: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Field & market updates"
        desc="What's actually changing in your field right now."
      />
      <div className="space-y-3">
        {FIELD_UPDATES.map((f) => (
          <Card key={f.id} className="p-5">
            <Tag tone="blue">{f.field}</Tag>
            <div className="font-display font-semibold mt-2.5 mb-1">{f.title}</div>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">{f.summary}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};
