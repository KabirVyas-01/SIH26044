import React, { Fragment } from 'react';

interface FlowDiagramProps {
  inverted?: boolean;
}

export const FlowDiagram: React.FC<FlowDiagramProps> = ({ inverted = false }) => {
  const steps = ['Learn', 'Research', 'Improve', 'Connect', 'Discover'];
  return (
    <div className="w-full max-w-full overflow-hidden py-1">
      <div className="flex items-center justify-between w-full max-w-full">
        {steps.map((s, i) => (
          <Fragment key={s}>
            <div className="flex flex-col items-center shrink-0">
              <div
                className={`w-9 h-9 xs:w-10 xs:h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 rounded-full border flex items-center justify-center font-display text-xs xs:text-sm sm:text-base md:text-lg transition-transform ${
                  inverted
                    ? 'bg-white/10 border-white/25 text-cream shadow-inner'
                    : 'bg-mutedsage/40 border-deepblue/15 text-deepblue'
                }`}
              >
                {i + 1}
              </div>
              <span
                className={`text-[9px] xs:text-[10px] sm:text-xs md:text-sm font-semibold mt-1 sm:mt-1.5 text-center leading-tight ${
                  inverted ? 'text-cream/80' : 'text-deepblue/80'
                }`}
              >
                {s}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div
                className={`flex-1 min-w-[6px] xs:min-w-[10px] sm:min-w-[16px] max-w-[48px] h-[2px] -mt-3 xs:-mt-3.5 sm:-mt-4 md:-mt-5 shrink transition-opacity ${
                  inverted
                    ? 'bg-gradient-to-r from-white/30 via-white/40 to-white/30'
                    : 'bg-gradient-to-r from-deepblue/25 via-deepblue/40 to-deepblue/25'
                }`}
              />
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
    <div className="space-y-3 w-full max-w-full">
      {rows.map((r) => (
        <div
          key={r.who}
          className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 rounded-xl border border-deepblue/12 bg-white/60 px-3.5 py-3 sm:px-4 sm:py-3.5 break-words w-full"
        >
          <div className="sm:w-36 shrink-0 font-display font-semibold text-deepblue text-sm sm:text-base">{r.who}</div>
          <div className="text-xs sm:text-sm text-deepblue/75 leading-relaxed">{r.flow}</div>
        </div>
      ))}
    </div>
  );
};
