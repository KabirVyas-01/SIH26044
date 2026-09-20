import React, { useState } from 'react';
import { Icon } from './Icon';
import { NOTIFICATIONS } from '../../data/mockData';
import { useAuth } from '../../context/AuthContext';

export const PORTAL_META: Record<string, { label: string; icon: string; blurb: string }> = {
  student:     { label: 'Students',      icon: 'student',  blurb: 'Learn, test your skills and track real progress.' },
  academician: { label: 'Academicians',  icon: 'flask',    blurb: 'Publish research and hear from readers who engage with it.' },
  university:  { label: 'Universities',  icon: 'building', blurb: 'See how your students are actually growing, skill by skill.' },
  industry:    { label: 'Industries',    icon: 'briefcase',blurb: 'Find candidates by proven skill, not just a resume.' },
};

interface PortalTab {
  key: string;
  label: string;
  icon: string;
}

interface PortalShellProps {
  portalKey: string;
  tabs: PortalTab[];
  active: string;
  setActive: (tab: string) => void;
  go: (page: string) => void;
  children: React.ReactNode;
  subtitle?: string;
}

export const PortalShell: React.FC<PortalShellProps> = ({
  portalKey,
  tabs,
  active,
  setActive,
  go,
  children,
  subtitle,
}) => {
  const [mobileNav, setMobileNav] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { currentUser, logout } = useAuth();
  const meta = PORTAL_META[portalKey] || PORTAL_META.student;
  const items = ['academician', 'student', 'university', 'industry'];

  return (
    <div
      className="min-h-screen bg-pcream text-[#2C3524] portal-shell"
      style={
        {
          '--bg': '#F2E8CF',
          '--surface': '#FFFFFF',
          '--text': '#2C3524',
          '--text-muted': '#6B7660',
          '--border': '#E1D6AE',
        } as React.CSSProperties
      }
    >
      {/* topbar */}
      <header className="sticky top-0 z-40 bg-sagedeep text-pcream" style={{ paddingTop: 'env(safe-area-inset-top,0px)' }}>
        <div className="px-4 sm:px-6 h-16 flex items-center gap-3">
          <button
            className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-white/10"
            onClick={() => setMobileNav((v) => !v)}
            aria-label="Open sidebar"
          >
            <Icon name="menu" className="w-5 h-5" />
          </button>
          <button onClick={() => go('landing')} className="font-display text-lg font-semibold shrink-0 focus-ring rounded">
            Confluence
          </button>
          <span className="hidden sm:inline text-pcream/50">/</span>
          <span className="hidden sm:inline text-sm font-medium text-pcream/85">{meta.label} Portal</span>

          <div className="ml-auto flex items-center gap-1 sm:gap-2">
            <div className="hidden md:flex items-center gap-1 mr-2">
              {items.map((k) => (
                <button
                  key={k}
                  onClick={() => go(k)}
                  className={
                    "px-3 py-1.5 rounded-lg text-xs font-semibold transition " +
                    (k === portalKey
                      ? "bg-white/15 text-pcream"
                      : "text-pcream/70 hover:bg-white/10 hover:text-pcream")
                  }
                >
                  {PORTAL_META[k].label}
                </button>
              ))}
            </div>
            <div className="relative hidden sm:block w-48">
              <Icon name="search" className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-pcream/60" />
              <input
                placeholder="Search…"
                className="w-full bg-white/10 focus:bg-white/15 placeholder-pcream/50 rounded-lg pl-8 pr-2 py-1.5 text-xs text-pcream outline-none"
              />
            </div>
            <div className="relative">
              <button
                onClick={() => setNotifOpen((v) => !v)}
                className="p-2 rounded-lg hover:bg-white/10 relative focus-ring"
                aria-label="Notifications"
              >
                <Icon name="bell" className="w-[18px] h-[18px]" />
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-amber-400" />
              </button>
              {notifOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white text-[#2C3524] rounded-xl shadow-lg border border-[#E1D6AE] p-2 rise z-50">
                  <div className="text-xs font-semibold px-2 py-1.5 text-[#6B7660]">Notifications</div>
                  {NOTIFICATIONS.map((n) => (
                    <div key={n.id} className="px-2.5 py-2 text-xs rounded-lg hover:bg-pcream/60">
                      {n.text}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* User Profile & Session Dropdown */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen((v) => !v)}
                className="w-8 h-8 rounded-full bg-mutedsage/70 text-deepblue flex items-center justify-center text-xs font-bold shrink-0 hover:ring-2 hover:ring-white/40 focus-ring"
                title={currentUser ? `${currentUser.name} (${currentUser.role})` : 'User Profile'}
              >
                {currentUser ? currentUser.name[0].toUpperCase() : <Icon name="user" className="w-4 h-4" />}
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white text-[#2C3524] rounded-xl shadow-lg border border-[#E1D6AE] p-2 rise z-50">
                  {currentUser ? (
                    <>
                      <div className="px-3 py-2 border-b border-[#E1D6AE]">
                        <div className="text-xs font-semibold">{currentUser.name}</div>
                        <div className="text-[11px] text-[#6B7660] truncate">{currentUser.email}</div>
                        <span className="inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold bg-sage/20 text-sagedeep">
                          {currentUser.role}
                        </span>
                      </div>
                      <button
                        onClick={async () => {
                          await logout();
                          setUserMenuOpen(false);
                          go('landing');
                        }}
                        className="w-full text-left px-3 py-2 text-xs text-rose-700 hover:bg-rose-50 rounded-lg mt-1 font-medium transition"
                      >
                        Sign out
                      </button>
                    </>
                  ) : (
                    <div className="px-3 py-2 text-xs text-[#6B7660]">
                      <p className="mb-2">Browsing as demo visitor.</p>
                      <button
                        onClick={() => {
                          setUserMenuOpen(false);
                          go('landing');
                        }}
                        className="text-sagedeep font-semibold underline underline-offset-2"
                      >
                        Log in or register
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* sidebar */}
        <aside
          className={
            (mobileNav ? "translate-x-0" : "-translate-x-full") +
            " lg:translate-x-0 fixed lg:sticky top-16 lg:top-16 left-0 z-30 w-64 h-[calc(100vh-4rem)] bg-white border-r border-[#E1D6AE] p-3 transition-transform duration-200 overflow-y-auto"
          }
        >
          <div className="px-2 py-3 mb-1">
            <div className="text-xs font-semibold text-[#6B7660] uppercase tracking-wide">{meta.label}</div>
            {subtitle && <div className="text-[11px] text-[#8B9480] mt-0.5">{subtitle}</div>}
          </div>
          <nav className="space-y-1">
            {tabs.map((t) => (
              <button
                key={t.key}
                onClick={() => {
                  setActive(t.key);
                  setMobileNav(false);
                }}
                className={
                  "w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition focus-ring " +
                  (active === t.key ? "bg-sage/25 text-[#2C3524]" : "text-[#556248] hover:bg-pcream")
                }
              >
                <Icon name={t.icon} className="w-4 h-4 shrink-0" />
                {t.label}
              </button>
            ))}
          </nav>
        </aside>
        {mobileNav && <div className="fixed inset-0 bg-black/30 z-20 lg:hidden" onClick={() => setMobileNav(false)} />}

        {/* main */}
        <main className="flex-1 min-w-0 px-4 sm:px-6 lg:px-8 py-6 sm:py-8 max-w-6xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  );
};
