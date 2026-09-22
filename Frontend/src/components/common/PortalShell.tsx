import React, { useState, useEffect } from 'react';
import { Icon } from './Icon';
import { useAuth } from '../../context/AuthContext';
import { authApi } from '../../api/auth';
import { NotificationItem } from '../../types';

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
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loadingNotifs, setLoadingNotifs] = useState(false);
  const { currentUser, logout } = useAuth();

  useEffect(() => {
    let isMounted = true;
    const fetchNotifs = async () => {
      setLoadingNotifs(true);
      try {
        const res = await authApi.getNotifications();
        if (isMounted && res && res.notifications) {
          setNotifications(res.notifications);
        }
      } catch {
        // fallback gracefully
      } finally {
        if (isMounted) setLoadingNotifs(false);
      }
    };
    fetchNotifs();
    return () => {
      isMounted = false;
    };
  }, [currentUser]);

  const meta = PORTAL_META[portalKey] || PORTAL_META.student;
  const userPortalKey = currentUser
    ? (currentUser.role === 'institute' ? 'university' : currentUser.role)
    : null;
  const items = userPortalKey ? [userPortalKey] : ['academician', 'student', 'university', 'industry'];

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
          <button
            onClick={() => go(userPortalKey || 'landing')}
            className="font-display text-lg font-semibold shrink-0 focus-ring rounded"
          >
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
            {currentUser && (
              <button
                onClick={async () => {
                  await logout();
                  window.location.hash = '';
                  go('landing');
                }}
                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/10 text-pcream hover:bg-rose-700/80 transition"
              >
                Sign out
              </button>
            )}
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
                {notifications.length > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-amber-400 ring-2 ring-sagedeep" />
                )}
              </button>
              {notifOpen && (
                <div className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] bg-white text-[#2C3524] rounded-2xl shadow-xl border border-[#E1D6AE] p-2.5 rise z-50 max-h-96 overflow-y-auto">
                  <div className="flex items-center justify-between px-2 py-1.5 border-b border-[#E1D6AE]/60 mb-1.5">
                    <div className="text-xs font-bold text-[#2C3524] flex items-center gap-1.5">
                      <span>Notifications</span>
                      <span className="px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-sage/20 text-sagedeep">
                        {notifications.length}
                      </span>
                    </div>
                    {loadingNotifs && (
                      <span className="text-[10px] text-[#6B7660] animate-pulse">Syncing…</span>
                    )}
                  </div>

                  {notifications.length === 0 ? (
                    <div className="py-6 text-center text-xs text-[#6B7660]">
                      No new notifications right now.
                    </div>
                  ) : (
                    <div className="space-y-1.5">
                      {notifications.map((n) => (
                        <div
                          key={n.id}
                          className="p-2.5 text-xs rounded-xl hover:bg-pcream/60 transition border border-transparent hover:border-[#E1D6AE]/40"
                        >
                          <div className="flex items-center justify-between gap-1.5 mb-1">
                            {n.tag && (
                              <span
                                className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                                  n.type === 'success'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : n.type === 'warning'
                                    ? 'bg-amber-100 text-amber-900'
                                    : 'bg-sagedeep/10 text-sagedeep'
                                }`}
                              >
                                {n.tag}
                              </span>
                            )}
                            {n.time && (
                              <span className="text-[10px] text-[#8B9480] ml-auto font-medium">
                                {n.time}
                              </span>
                            )}
                          </div>
                          <p className="text-xs leading-relaxed text-[#2C3524]">{n.text}</p>
                        </div>
                      ))}
                    </div>
                  )}
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
                          window.location.hash = '';
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
