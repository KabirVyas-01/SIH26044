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
    <div className="bg-cream text-deepblue">
      <LandingNav go={go} openAuth={openAuth} />

      {/* HERO — on deep blue, reversed from the cliché cream+serif hero */}
      <section className="bg-deepblue text-cream">
        <div className="max-w-7xl mx-auto px-5 sm:px-8 py-16 sm:py-24 grid lg:grid-cols-[1.15fr_0.85fr] gap-12 items-center">
          <div className="rise">
            <p className="text-mutedsage text-sm font-semibold tracking-wide mb-4">One ecosystem, four roles</p>
            <h1 className="font-display text-[2.5rem] sm:text-6xl leading-[1.05] font-semibold max-w-xl">
              Where research becomes learning, and learning becomes opportunity.
            </h1>
            <p className="mt-6 text-cream/75 text-base sm:text-lg max-w-lg leading-relaxed">
              Confluence connects academicians, students, universities and industries in a
              single, continuous loop — instead of four separate systems that don't talk to each other.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button variant="sagesolid" onClick={() => go('student')}>
                Enter as a student
              </Button>
              <Button
                variant="outline"
                className="border-cream/40 text-cream hover:bg-white/10"
                onClick={() => go('industry')}
              >
                I'm hiring talent
              </Button>
            </div>
          </div>
          <div className="rise" style={{ animationDelay: '.1s' }}>
            <div className="rounded-2xl bg-white/5 border border-white/10 p-6">
              <FlowDiagram />
              <div className="mt-6 grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-white/5 p-3.5">
                  <div className="text-2xl font-display">9,700+</div>
                  <div className="text-xs text-cream/60 mt-0.5">verified students</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3.5">
                  <div className="text-2xl font-display">120+</div>
                  <div className="text-xs text-cream/60 mt-0.5">published papers</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3.5">
                  <div className="text-2xl font-display">4</div>
                  <div className="text-xs text-cream/60 mt-0.5">universities onboard</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3.5">
                  <div className="text-2xl font-display">4</div>
                  <div className="text-xs text-cream/60 mt-0.5">hiring companies</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FOUR DOMAINS — equal weight */}
      <section className="max-w-7xl mx-auto px-5 sm:px-8 py-16 sm:py-20">
        <div className="flex items-end justify-between flex-wrap gap-3 mb-8">
          <h2 className="font-display text-2xl sm:text-3xl font-semibold">Four roles. One platform.</h2>
          <p className="text-sm text-deepblue/60 max-w-sm">
            Each portal is built for its own audience, but every one of them speaks to the others.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(PORTAL_META).map(([k, m]) => (
            <button
              key={k}
              onClick={() => go(k)}
              className="text-left rounded-2xl border border-deepblue/12 bg-white p-6 hover:border-deepblue/30 hover:shadow-md transition group focus-ring"
            >
              <div className="w-11 h-11 rounded-xl bg-mutedsage/50 flex items-center justify-center mb-4 group-hover:bg-mutedsage transition">
                <Icon name={m.icon} className="w-5 h-5" />
              </div>
              <div className="font-display text-lg font-semibold mb-1.5">{m.label}</div>
              <p className="text-sm text-deepblue/65 leading-relaxed mb-4">{m.blurb}</p>
              <span className="text-sm font-semibold inline-flex items-center gap-1 text-deepblue">
                Enter portal <Icon name="arrowr" className="w-3.5 h-3.5" />
              </span>
            </button>
          ))}
        </div>
      </section>

      {/* ECOSYSTEM FLOW */}
      <section className="bg-mutedsage/25 border-y border-deepblue/10">
        <div className="max-w-5xl mx-auto px-5 sm:px-8 py-16 sm:py-20">
          <h2 className="font-display text-2xl sm:text-3xl font-semibold mb-2">How information moves between roles</h2>
          <p className="text-sm text-deepblue/65 mb-8 max-w-xl">
            Nothing here lives in isolation — a research paper, a daily learning log and a hiring filter all feed the same loop.
          </p>
          <EcosystemFlow />
        </div>
      </section>

      {/* JOURNEY */}
      <section className="max-w-5xl mx-auto px-5 sm:px-8 py-16 sm:py-20 text-center">
        <h2 className="font-display text-2xl sm:text-3xl font-semibold mb-8">The platform journey</h2>
        <FlowDiagram />
      </section>

      {/* ENTRY POINTS */}
      <section className="bg-deepblue text-cream">
        <div className="max-w-7xl mx-auto px-5 sm:px-8 py-16 sm:py-20">
          <h2 className="font-display text-2xl sm:text-3xl font-semibold mb-8 text-center">Choose where you start</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(PORTAL_META).map(([k, m]) => (
              <button
                key={k}
                onClick={() => go(k)}
                className="rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 p-6 text-left transition focus-ring"
              >
                <Icon name={m.icon} className="w-6 h-6 mb-4 text-mutedsage" />
                <div className="font-display font-semibold">{m.label} Portal</div>
                <div className="text-xs text-cream/55 mt-1">Get started →</div>
              </button>
            ))}
          </div>
        </div>
      </section>

      <footer className="max-w-7xl mx-auto px-5 sm:px-8 py-10 text-xs text-deepblue/50 flex flex-wrap items-center justify-between gap-3">
        <span>© 2026 Confluence — a demonstration prototype.</span>
        <span>Research + Learning + Universities + Industry</span>
      </footer>
    </div>
  );
};
