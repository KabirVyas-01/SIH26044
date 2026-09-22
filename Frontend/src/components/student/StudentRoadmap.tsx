import React, { useState, useMemo } from 'react';
import { Card, Button, StatBlock, PageHeader, Tag, ProgressBar } from '../common/UIComponents';
import { Icon } from '../common/Icon';
import { SkillTestModal } from './SkillTestModal';
import { ROADMAP } from '../../data/mockData';
import { Student, RoadmapItem } from '../../types';

interface StudentRoadmapProps {
  student?: Student;
  onNavigate?: (tab: string) => void;
}

const DOMAIN_ROADMAPS: Record<string, { name: string; tag: string; items: RoadmapItem[] }> = {
  chemical: {
    name: 'Chemical & Process Engineering',
    tag: 'Process & Chemical',
    items: [
      {
        skill: 'Process Simulation (Aspen Plus / DWSIM)',
        from: 25,
        to: 75,
        weeks: 4,
        free: 'DWSIM Open Source Process Simulator Tutorials & Flowsheet Guides',
        paid: 'Aspen Plus: Chemical Engineering Flowsheet Simulation (AIChE / Udemy)'
      },
      {
        skill: 'Unit Operations & Distillation (McCabe-Thiele)',
        from: 35,
        to: 80,
        weeks: 5,
        free: 'NPTEL Mass Transfer Operations (IIT Guwahati — Prof. B. Mandal)',
        paid: 'Coursera — Separation Process Principles & Multistage Distillation'
      },
      {
        skill: 'Chemical Reaction Kinetics & Reactor Sizing (CSTR/PFR)',
        from: 30,
        to: 75,
        weeks: 4,
        free: 'Elements of Chemical Reaction Engineering (H.S. Fogler Open Courseware)',
        paid: 'AIChE Academy — Industrial Reactor Sizing & Thermal Runaway Mitigation'
      },
      {
        skill: 'Process Safety Management & HAZOP Analysis',
        from: 20,
        to: 70,
        weeks: 3,
        free: 'US Chemical Safety Board (CSB) Case Studies & OSHA PSM Standards',
        paid: 'SAChE Certificate in Chemical Process Safety (AIChE)'
      }
    ]
  },
  mechanical: {
    name: 'Mechanical & Thermal Engineering',
    tag: 'Mechanical & CAD',
    items: [
      {
        skill: 'Finite Element Analysis (FEA / ANSYS)',
        from: 30,
        to: 75,
        weeks: 4,
        free: 'Cornell SimCafe ANSYS FEA Structural & Thermal Simulation Modules',
        paid: 'ANSYS Mechanical Professional Certification'
      },
      {
        skill: 'Applied Thermodynamics & Heat Exchangers',
        from: 35,
        to: 70,
        weeks: 4,
        free: 'MIT OpenCourseWare Thermodynamics & Heat Transfer',
        paid: 'ASME Shell & Tube Heat Exchanger Thermal Rating & Sizing'
      },
      {
        skill: 'SolidWorks 3D CAD & GD&T Standards',
        from: 40,
        to: 85,
        weeks: 3,
        free: 'SolidWorks Official Guides & ASME Y14.5 GD&T Tolerancing',
        paid: 'CSWA / CSWP Certified SolidWorks Associate Prep'
      },
      {
        skill: 'Machine Element Design & Dynamics',
        from: 25,
        to: 65,
        weeks: 5,
        free: 'NPTEL Design of Machine Elements (IIT Madras)',
        paid: "Shigley's Mechanical Engineering Design Masterclass"
      }
    ]
  },
  civil: {
    name: 'Civil & Structural Engineering',
    tag: 'Infrastructure & RCC',
    items: [
      {
        skill: 'Structural RCC Design & Limit State Method',
        from: 35,
        to: 75,
        weeks: 5,
        free: 'NPTEL Design of Reinforced Concrete Structures (IIT Kharagpur)',
        paid: 'STAAD.Pro / ETABS Structural Modeling Certificate'
      },
      {
        skill: 'Geotechnical Soil Mechanics & Foundations',
        from: 30,
        to: 70,
        weeks: 4,
        free: 'MIT OpenCourseWare Soil Mechanics & Bearing Capacity',
        paid: 'ASCE Shallow & Deep Foundation Engineering'
      },
      {
        skill: 'AutoCAD Civil 3D & Highway Alignment',
        from: 25,
        to: 75,
        weeks: 3,
        free: 'Autodesk Civil 3D Official Learning Pathway',
        paid: 'Coursera — Infrastructure & Transportation Design'
      },
      {
        skill: 'Construction Project Planning (Primavera P6)',
        from: 20,
        to: 65,
        weeks: 3,
        free: 'CMU Project Management for Construction Open Textbook',
        paid: 'Primavera P6 Professional Scheduling Certification'
      }
    ]
  },
  electrical: {
    name: 'Electrical & Embedded Systems',
    tag: 'Hardware & Power',
    items: [
      {
        skill: 'Embedded Hardware & ARM Cortex (STM32)',
        from: 30,
        to: 75,
        weeks: 4,
        free: 'FastBit Embedded Brain Academy (GitHub & Docs)',
        paid: 'Udemy — Mastering Microcontrollers with Embedded C'
      },
      {
        skill: 'KiCad Multi-Layer PCB Layout & EMC',
        from: 25,
        to: 70,
        weeks: 3,
        free: 'KiCad Official Video Guides & IPC-2221 Standards',
        paid: 'Robert Feranec Hardware Academy PCB Design Masterclass'
      },
      {
        skill: 'Power Systems Analysis & Electrical Machines',
        from: 35,
        to: 75,
        weeks: 5,
        free: 'NPTEL Power System Analysis (IIT Kharagpur)',
        paid: 'IEEE Power & Energy Society Grid Integration Course'
      },
      {
        skill: 'Analog Circuit Design & SPICE Simulation',
        from: 25,
        to: 65,
        weeks: 4,
        free: 'Analog Devices Educational SPICE Circuits & Wiki',
        paid: 'Texas Instruments Precision Labs: Op-Amp Design'
      }
    ]
  },
  datascience: {
    name: 'Data Science & Machine Learning',
    tag: 'AI & Analytics',
    items: [
      {
        skill: 'Exploratory Data Analysis & Statistical Inference',
        from: 40,
        to: 80,
        weeks: 4,
        free: 'Kaggle Learn & Python Data Science Handbook',
        paid: 'DataCamp — Data Scientist with Python Career Track'
      },
      {
        skill: 'Machine Learning Modeling & Scikit-Learn',
        from: 35,
        to: 75,
        weeks: 5,
        free: 'Coursera — Machine Learning Specialization (Andrew Ng)',
        paid: 'DeepLearning.AI Deep Learning Specialization'
      },
      {
        skill: 'Advanced Relational SQL & Warehousing',
        from: 45,
        to: 80,
        weeks: 3,
        free: 'Mode Analytics SQL Tutorial & LeetCode 50 SQL',
        paid: 'Udacity — Data Engineering Nanodegree'
      },
      {
        skill: 'Production ML Pipelines & Serving',
        from: 20,
        to: 65,
        weeks: 4,
        free: 'Full Stack Deep Learning Course & FastAPI Docs',
        paid: 'Coursera — MLOps by Andrew Ng'
      }
    ]
  },
  software: {
    name: 'Software Engineering & Web',
    tag: 'Full Stack',
    items: ROADMAP
  }
};

const detectDomainKey = (student?: Student): string => {
  const f = (student?.field || student?.role || student?.desiredRole || '').toLowerCase();
  if (/chem/i.test(f) || /process/i.test(f)) return 'chemical';
  if (/mech/i.test(f) || /auto/i.test(f) || /aero/i.test(f)) return 'mechanical';
  if (/civil/i.test(f) || /struct/i.test(f) || /construct/i.test(f)) return 'civil';
  if (/electr/i.test(f) || /vlsi/i.test(f) || /circuit/i.test(f)) return 'electrical';
  if (/data/i.test(f) || /ai/i.test(f) || /ml/i.test(f) || /analytics/i.test(f)) return 'datascience';
  return 'software';
};

export const StudentRoadmap: React.FC<StudentRoadmapProps> = ({ student, onNavigate }) => {
  const defaultDomain = useMemo(() => detectDomainKey(student), [student]);
  const [selectedTrack, setSelectedTrack] = useState<string>(defaultDomain);

  // Sync default domain if student data changes
  React.useEffect(() => {
    setSelectedTrack(defaultDomain);
  }, [defaultDomain]);

  const activeTrackData = DOMAIN_ROADMAPS[selectedTrack] || DOMAIN_ROADMAPS.software;
  const isChemical = selectedTrack === 'chemical';

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <PageHeader
          title="Learning roadmap"
          desc="A structured, domain-accurate progression tailored to your engineering discipline."
        />
        {onNavigate && (
          <Button
            variant="primary"
            onClick={() => onNavigate('aitools')}
            className="shrink-0 flex items-center gap-2 self-start sm:self-auto"
          >
            <Icon name="sparkles" className="w-4 h-4 text-amber-300" />
            <span>AI Roadmap Generator</span>
          </Button>
        )}
      </div>

      {/* Discipline Track Selector */}
      <Card className="p-4 bg-gradient-to-r from-sage/10 via-sage/5 to-transparent border border-sage/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-xs font-semibold text-sagedeep uppercase tracking-wider mb-1">
              Active Discipline Track
            </div>
            <div className="text-base font-display font-semibold text-[#2C3524] flex items-center gap-2">
              <span>{activeTrackData.name}</span>
              <Tag>{activeTrackData.tag}</Tag>
            </div>
            {isChemical && (
              <p className="text-xs text-sagedeep mt-1">
                Zero software web clutter — specialized in fluid mechanics, heat/mass transfer, reactor design, Aspen Plus & HAZOP safety.
              </p>
            )}
          </div>

          <div className="flex flex-wrap gap-1.5 self-start sm:self-auto">
            {Object.entries(DOMAIN_ROADMAPS).map(([k, v]) => (
              <button
                key={k}
                type="button"
                onClick={() => setSelectedTrack(k)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition ${
                  selectedTrack === k
                    ? 'bg-sagedeep text-white shadow-sm'
                    : 'bg-black/5 hover:bg-black/10 text-[#2C3524]'
                }`}
              >
                {v.tag}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Milestones Cards */}
      <div className="space-y-4">
        {activeTrackData.items.map((r) => (
          <Card key={r.skill} className="p-5">
            <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
              <div className="font-display font-semibold text-[#2C3524]">{r.skill}</div>
              <Tag>{r.weeks} weeks</Tag>
            </div>
            <div className="flex items-center gap-3 mb-4">
              <span className="text-xs text-[var(--text-muted)] w-10">{r.from}%</span>
              <ProgressBar value={r.from} colorClass="bg-amber-500" />
              <Icon name="arrowr" className="w-3.5 h-3.5 text-[var(--text-muted)] shrink-0" />
              <ProgressBar value={r.to} />
              <span className="text-xs text-[var(--text-muted)] w-10">{r.to}%</span>
            </div>
            <div className="grid sm:grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-sage/10 border border-sage/30 p-3">
                <div className="text-xs font-semibold text-sagedeep mb-1">Free resource</div>
                <div className="text-xs text-[#2C3524]">{r.free}</div>
              </div>
              <div className="rounded-xl bg-black/5 p-3">
                <div className="text-xs font-semibold text-[var(--text-muted)] mb-1">Paid / Professional resource</div>
                <div className="text-xs text-[#2C3524]">{r.paid}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const StudentDaily: React.FC<{ student: Student }> = ({ student }) => {
  const [log, setLog] = useState(student.dailyLog);
  const [topic, setTopic] = useState('');
  const [hours, setHours] = useState('');
  const [testOpen, setTestOpen] = useState(false);

  const submit = () => {
    if (!topic) return;
    setLog([{ date: 'Today', topic, hours: hours || 1 }, ...log]);
    setTopic('');
    setHours('');
    setTestOpen(true);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Daily learning update"
        desc="Log what you worked on today — a short AI-generated check confirms you actually understood it."
      />

      <Card className="p-5">
        <div className="font-display font-semibold mb-3">Today's learning</div>
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. JavaScript Arrays"
            className="flex-1 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
          />
          <input
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            placeholder="Hours"
            type="number"
            min="0"
            step="0.5"
            className="sm:w-28 rounded-xl border border-[var(--border)] px-3.5 py-2.5 text-sm focus-ring"
          />
          <Button variant="primary" onClick={submit}>
            Submit
          </Button>
        </div>
      </Card>

      <div className="grid sm:grid-cols-4 gap-3">
        <StatBlock label="Discipline" value={student.discipline} />
        <StatBlock label="Punctuality" value={student.punctuality} />
        <StatBlock label="Consistency" value={student.consistency} />
        <StatBlock label="Potential" value={student.potential} />
      </div>

      <Card className="p-5">
        <div className="font-display font-semibold mb-4">Recent activity</div>
        <div className="space-y-3">
          {log.map((l, i) => (
            <div
              key={i}
              className="flex items-center justify-between gap-3 text-sm border-b border-[var(--border)] pb-3 last:border-0 last:pb-0"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="text-xs text-[var(--text-muted)] w-14 shrink-0">{l.date}</span>
                <span className="truncate">{l.topic}</span>
              </div>
              <span className="text-xs text-[var(--text-muted)] shrink-0">{l.hours}h</span>
            </div>
          ))}
        </div>
      </Card>
      <SkillTestModal open={testOpen} onClose={() => setTestOpen(false)} skill={topic || 'today’s topic'} />
    </div>
  );
};
