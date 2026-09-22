import React from 'react';
import { LandingNav } from './LandingNav';
import { FlowDiagram, EcosystemFlow } from './FlowDiagram';
import { Icon } from '../common/Icon';
import { Button } from '../common/UIComponents';
import { PORTAL_META } from '../common/PortalShell';

interface LandingPageProps {
  go: (page: string) => void;
  openAuth: (mode: 'login' | 'register') => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ go, openAuth }) => {
  return (
    <div className="bg-cream text-deepblue w-full max-w-full overflow-x-hidden min-h-screen">
      <LandingNav go={go} openAuth={openAuth} />

      {/* HERO — on deep blue, fully responsive across every screen */}
      <section className="bg-deepblue text-cream w-full max-w-full overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20 lg:py-24 grid lg:grid-cols-[1.15fr_0.85fr] gap-8 lg:gap-12 items-center w-full min-w-0">
          <div className="rise w-full min-w-0">
            <p className="text-mutedsage text-xs sm:text-sm font-semibold tracking-wide mb-3 sm:mb-4">
              One ecosystem, four roles
            </p>
            <h1 className="font-display text-3xl sm:text-5xl lg:text-6xl leading-[1.1] font-semibold max-w-xl break-words">
              Where research becomes learning, and learning becomes opportunity.
            </h1>
            <p className="mt-4 sm:mt-6 text-cream/75 text-sm sm:text-base lg:text-lg max-w-lg leading-relaxed break-words">
              VidyaSarthi connects academicians, students, universities and industries in a
              single, continuous loop — instead of four separate systems that don't talk to each other.
            </p>
            <div className="mt-6 sm:mt-8 flex flex-wrap gap-2.5 sm:gap-3">
              <Button variant="sagesolid" onClick={() => go('student')} className="text-xs sm:text-sm px-4 py-2.5">
                Enter as a student
              </Button>
              <Button
                variant="outline"
                className="border-cream/40 text-cream hover:bg-white/10 text-xs sm:text-sm px-4 py-2.5"
                onClick={() => go('industry')}
              >
                I'm hiring talent
              </Button>
            </div>
          </div>
          <div className="rise w-full min-w-0 max-w-full" style={{ animationDelay: '.1s' }}>
            <div className="rounded-2xl bg-white/5 border border-white/10 p-4 sm:p-6 w-full min-w-0 max-w-full overflow-hidden shadow-2xl">
              <FlowDiagram inverted={true} />
              <div className="mt-5 sm:mt-6 grid grid-cols-2 gap-2.5 sm:gap-3">
                <div className="rounded-xl bg-white/5 p-3 sm:p-3.5 border border-white/5">
                  <div className="text-xl sm:text-2xl font-display text-cream font-bold">9,700+</div>
                  <div className="text-[11px] sm:text-xs text-cream/60 mt-0.5">verified students</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3 sm:p-3.5 border border-white/5">
                  <div className="text-xl sm:text-2xl font-display text-cream font-bold">120+</div>
                  <div className="text-[11px] sm:text-xs text-cream/60 mt-0.5">published papers</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3 sm:p-3.5 border border-white/5">
                  <div className="text-xl sm:text-2xl font-display text-cream font-bold">4</div>
                  <div className="text-[11px] sm:text-xs text-cream/60 mt-0.5">universities onboard</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3 sm:p-3.5 border border-white/5">
                  <div className="text-xl sm:text-2xl font-display text-cream font-bold">4</div>
                  <div className="text-[11px] sm:text-xs text-cream/60 mt-0.5">hiring companies</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FOUR DOMAINS — equal weight */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20 w-full overflow-hidden">
        <div className="flex items-end justify-between flex-wrap gap-3 mb-8">
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-semibold">Four roles. One platform.</h2>
            <p className="text-xs sm:text-sm text-deepblue/60 mt-1 max-w-sm">
              Each portal is built for its own audience, but every one of them speaks to the others.
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
          {Object.entries(PORTAL_META).map(([k, m]) => (
            <button
              key={k}
              onClick={() => go(k)}
              className="text-left rounded-2xl border border-deepblue/12 bg-white p-5 sm:p-6 hover:border-deepblue/30 hover:shadow-md transition group focus-ring w-full"
            >
              <div className="w-11 h-11 rounded-xl bg-mutedsage/50 flex items-center justify-center mb-4 group-hover:bg-mutedsage transition">
                <Icon name={m.icon} className="w-5 h-5" />
              </div>
              <div className="font-display text-lg font-semibold mb-1.5">{m.label}</div>
              <p className="text-xs sm:text-sm text-deepblue/65 leading-relaxed mb-4">{m.blurb}</p>
              <span className="text-xs sm:text-sm font-semibold inline-flex items-center gap-1 text-deepblue">
                Enter portal <Icon name="arrowr" className="w-3.5 h-3.5" />
              </span>
            </button>
          ))}
        </div>
      </section>

      {/* ECOSYSTEM FLOW */}
      <section className="bg-mutedsage/25 border-y border-deepblue/10 w-full overflow-hidden">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20 w-full min-w-0">
          <h2 className="font-display text-2xl sm:text-3xl font-semibold mb-2">How information moves between roles</h2>
          <p className="text-xs sm:text-sm text-deepblue/65 mb-6 sm:mb-8 max-w-xl">
            Nothing here lives in isolation — a research paper, a daily learning log and a hiring filter all feed the same loop.
          </p>
          <EcosystemFlow />
        </div>
      </section>

      {/* JOURNEY */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20 text-center w-full overflow-hidden">
        <h2 className="font-display text-2xl sm:text-3xl font-semibold mb-6 sm:mb-8">The platform journey</h2>
        <div className="max-w-xl mx-auto w-full px-2">
          <FlowDiagram inverted={false} />
        </div>
      </section>

      {/* ENTRY POINTS */}
      <section className="bg-deepblue text-cream w-full overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20 w-full">
          <h2 className="font-display text-2xl sm:text-3xl font-semibold mb-6 sm:mb-8 text-center">Choose where you start</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
            {Object.entries(PORTAL_META).map(([k, m]) => (
              <button
                key={k}
                onClick={() => go(k)}
                className="rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 p-5 sm:p-6 text-left transition focus-ring w-full"
              >
                <Icon name={m.icon} className="w-6 h-6 mb-4 text-mutedsage" />
                <div className="font-display font-semibold text-base sm:text-lg">{m.label} Portal</div>
                <div className="text-xs text-cream/55 mt-1">Get started →</div>
              </button>
            ))}
          </div>
        </div>
      </section>

      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 text-xs text-deepblue/50 flex flex-wrap items-center justify-between gap-3 w-full">
        <span>© 2026 VidyaSarthi — a demonstration prototype.</span>
        <span>Research + Learning + Universities + Industry</span>
      </footer>
    </div>
  );
};
