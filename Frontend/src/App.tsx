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

  const go = (p: string) => {
    setPage(p);
    window.scrollTo(0, 0);
  };

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
      const h = window.location.hash.replace('#', '');
      if (['student', 'academician', 'university', 'industry'].includes(h)) {
        setPage(h);
      } else {
        setPage('landing');
      }
    };
    applyHash();
    window.addEventListener('hashchange', applyHash);
    return () => window.removeEventListener('hashchange', applyHash);
  }, []);

  const openAuth = (mode: 'login' | 'register') => setAuthMode(mode);

  const handleAuthSuccess = (userRole: UserRole) => {
    if (userRole === 'institute') {
      go('university');
    } else {
      go(userRole);
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
