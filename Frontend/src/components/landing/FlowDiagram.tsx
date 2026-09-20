import React, { Fragment } from 'react';

export const FlowDiagram: React.FC = () => {
  const steps = ['Learn', 'Research', 'Improve', 'Connect', 'Discover'];
  return (
    <div className="hscroll no-scrollbar">
      <div className="flex items-center gap-2 min-w-max px-1 py-2">
        {steps.map((s, i) => (
          <Fragment key={s}>
            <div className="flex flex-col items-center gap-2">
              <div className="w-14 h-14 rounded-full bg-mutedsage/40 border border-deepblue/15 flex items-center justify-center font-display text-lg text-deepblue">
                {i + 1}
              </div>
              <span className="text-sm font-semibold">{s}</span>
            </div>
            {i < steps.length - 1 && (
              <svg width="52" height="12" className="text-deepblue/40 shrink-0 mt-[-22px]">
                <line x1="0" y1="6" x2="52" y2="6" stroke="currentColor" strokeWidth="2" className="flowline" />
              </svg>
            )}
          </Fragment>
        ))}
      </div>
    </div>
  );
};

export const EcosystemFlow: React.FC = () => {
  const rows = [
    { who: 'Student',      flow: 'Learns → Tests → Improves → Updates daily → Builds profile → Uploads projects' },
    { who: 'University',   flow: 'Monitors → Understands skill gaps → Tracks improvement → Guides students' },
    { who: 'Industry',     flow: 'Sets requirements → Filters students → Finds candidates → Connects' },
    { who: 'Academician',  flow: 'Publishes research → Students discover it → Discuss → Academician responds' },
  ];
  return (
    <div className="space-y-3">
      {rows.map((r) => (
        <div
          key={r.who}
          className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-4 rounded-xl border border-deepblue/12 bg-white/60 px-4 py-3.5"
        >
          <div className="sm:w-36 shrink-0 font-display font-semibold text-deepblue">{r.who}</div>
          <div className="text-sm text-deepblue/75">{r.flow}</div>
        </div>
      ))}
    </div>
  );
};
