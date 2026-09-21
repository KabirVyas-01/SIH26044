import React, { useState, useEffect, Fragment } from 'react';
import { LandingPage } from './components/landing/LandingPage';
import { AuthModal } from './components/landing/AuthModal';
import { StudentPortal } from './components/student/StudentPortal';
import { AcademicianPortal } from './components/academician/AcademicianPortal';
import { UniversityPortal } from './components/university/UniversityPortal';
import { IndustryPortal } from './components/industry/IndustryPortal';
import { AuthProvider, useAuth } from './context/AuthContext';
import { UserRole } from './types';
import './App.css';

function MainContent() {
  const [page, setPage] = useState('landing');
  const [authMode, setAuthMode] = useState<'login' | 'register' | null>(null);
  const { currentUser } = useAuth();

  const userPortal = currentUser
    ? (currentUser.role === 'institute' ? 'university' : currentUser.role)
    : null;

  const go = (p: string) => {
    if (userPortal) {
      // Logged in: stay in own portal only
      setPage(userPortal);
    } else {
      // Logged out / visitor: free navigation across all 4 portals
      setPage(p);
    }
    window.scrollTo(0, 0);
  };

  // Sync state whenever login or logout occurs
  useEffect(() => {
    if (currentUser) {
      const allowed = currentUser.role === 'institute' ? 'university' : currentUser.role;
      setPage(allowed);
    } else {
      setPage('landing');
    }
  }, [currentUser]);

  useEffect(() => {
    const map: Record<string, string> = {
      landing: '',
      student: 'student',
      academician: 'academician',
      university: 'university',
      industry: 'industry',
    };
    const h = '#' + (map[page] || '');
    if (window.location.hash !== h) {
      window.history.replaceState(null, '', h || '#');
    }
  }, [page]);

  useEffect(() => {
    const applyHash = () => {
      if (currentUser) {
        const allowed = currentUser.role === 'institute' ? 'university' : currentUser.role;
        setPage(allowed);
      } else {
        const h = window.location.hash.replace('#', '');
        if (['student', 'academician', 'university', 'industry'].includes(h)) {
          setPage(h);
        } else {
          setPage('landing');
        }
      }
    };
    applyHash();
    window.addEventListener('hashchange', applyHash);
    return () => window.removeEventListener('hashchange', applyHash);
  }, [currentUser]);

  const openAuth = (mode: 'login' | 'register') => setAuthMode(mode);

  const handleAuthSuccess = (userRole: UserRole) => {
    if (userRole === 'institute') {
      setPage('university');
    } else {
      setPage(userRole);
    }
  };

  let body;
  if (page === 'landing') {
    body = <LandingPage go={go} openAuth={openAuth} />;
  } else if (page === 'student') {
    body = <StudentPortal go={go} />;
  } else if (page === 'academician') {
    body = <AcademicianPortal go={go} />;
  } else if (page === 'university') {
    body = <UniversityPortal go={go} />;
  } else if (page === 'industry') {
    body = <IndustryPortal go={go} />;
  }

  return (
    <Fragment>
      {body}
      <AuthModal
        mode={authMode}
        onClose={() => setAuthMode(null)}
        setMode={setAuthMode}
        onSuccess={handleAuthSuccess}
      />
    </Fragment>
  );
}

export function App() {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
}

export default App;
