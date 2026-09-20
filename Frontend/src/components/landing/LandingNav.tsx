import React, { useState } from 'react';
import { Icon } from '../common/Icon';
import { Button } from '../common/UIComponents';
import { PORTAL_META } from '../common/PortalShell';
import { useAuth } from '../../context/AuthContext';

interface LandingNavProps {
  go: (page: string) => void;
  openAuth: (mode: 'login' | 'register') => void;
}

export const LandingNav: React.FC<LandingNavProps> = ({ go, openAuth }) => {
  const [open, setOpen] = useState(false);
  const { currentUser, logout } = useAuth();
  const items = ['academician', 'student', 'university', 'industry'];

  return (
    <header
      className="sticky top-0 z-40 backdrop-blur bg-deepblue/90 text-cream"
      style={{ paddingTop: 'env(safe-area-inset-top,0px)' }}
    >
      <div className="max-w-7xl mx-auto px-5 sm:px-8 h-16 flex items-center justify-between">
        <button
          onClick={() => go('landing')}
          className="font-display text-xl font-semibold tracking-tight focus-ring rounded"
        >
          Confluence
        </button>
        <nav className="hidden md:flex items-center gap-1">
          {items.map((k) => (
            <button
              key={k}
              onClick={() => go(k)}
              className="px-3.5 py-2 rounded-lg text-sm font-medium text-cream/85 hover:text-cream hover:bg-white/10 transition focus-ring"
            >
              {PORTAL_META[k].label}
            </button>
          ))}
        </nav>
        <div className="hidden md:flex items-center gap-2">
          <button className="p-2 rounded-lg hover:bg-white/10 focus-ring" aria-label="Search">
            <Icon name="search" className="w-[18px] h-[18px]" />
          </button>
          {currentUser ? (
            <div className="flex items-center gap-2">
              <span className="text-xs text-cream/80">
                Hi, <strong className="text-cream">{currentUser.name}</strong>
              </span>
              <Button
                variant="outline"
                className="border-cream/40 text-cream hover:bg-white/10 text-xs px-3 py-1.5"
                onClick={() => go(currentUser.role === 'institute' ? 'university' : currentUser.role)}
              >
                My Portal
              </Button>
              <Button
                variant="ghost"
                className="text-xs text-cream/70 hover:text-cream px-2.5 py-1.5"
                onClick={logout}
              >
                Log out
              </Button>
            </div>
          ) : (
            <>
              <Button
                variant="outline"
                className="border-cream/40 text-cream hover:bg-white/10"
                onClick={() => openAuth('login')}
              >
                Log in
              </Button>
              <Button variant="sagesolid" onClick={() => openAuth('register')}>
                Register
              </Button>
            </>
          )}
        </div>
        <button
          className="md:hidden p-2 rounded-lg hover:bg-white/10 focus-ring"
          onClick={() => setOpen((v) => !v)}
          aria-label="Menu"
        >
          <Icon name={open ? "x" : "menu"} className="w-5 h-5" />
        </button>
      </div>
      {open && (
        <div className="md:hidden border-t border-white/10 px-5 pb-4 pt-2 flex flex-col gap-1">
          {items.map((k) => (
            <button
              key={k}
              onClick={() => {
                go(k);
                setOpen(false);
              }}
              className="text-left px-3 py-2.5 rounded-lg text-sm font-medium hover:bg-white/10"
            >
              {PORTAL_META[k].label}
            </button>
          ))}
          <div className="flex gap-2 mt-2">
            {currentUser ? (
              <Button
                variant="sagesolid"
                className="flex-1"
                onClick={() => {
                  go(currentUser.role === 'institute' ? 'university' : currentUser.role);
                  setOpen(false);
                }}
              >
                Enter {currentUser.role} portal
              </Button>
            ) : (
              <>
                <Button
                  variant="outline"
                  className="border-cream/40 text-cream flex-1"
                  onClick={() => {
                    openAuth('login');
                    setOpen(false);
                  }}
                >
                  Log in
                </Button>
                <Button
                  variant="sagesolid"
                  className="flex-1"
                  onClick={() => {
                    openAuth('register');
                    setOpen(false);
                  }}
                >
                  Register
                </Button>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
