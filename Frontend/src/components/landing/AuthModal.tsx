import React, { useState, useEffect } from 'react';
import { Modal, Button } from '../common/UIComponents';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';

interface AuthModalProps {
  mode: 'login' | 'register' | null;
  onClose: () => void;
  setMode: (mode: 'login' | 'register') => void;
  onSuccess?: (role: UserRole) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ mode, onClose, setMode, onSuccess }) => {
  const { login, signup } = useAuth();
  const [role, setRole] = useState<UserRole>('student');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [college, setCollege] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setError(null);
  }, [mode, role]);

  if (!mode) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'login') {
        const user = await login(role, email, password);
        onClose();
        if (onSuccess) onSuccess(user.role);
      } else {
        const payload: Record<string, any> = {
          email,
          password,
        };
        if (role === 'student') {
          payload.name = name;
          payload.college = college;
        } else if (role === 'industry') {
          payload.company_name = name;
        } else if (role === 'institute') {
          payload.name = name;
        } else if (role === 'academician') {
          payload.name = name;
        }

        const user = await signup(role, payload);
        onClose();
        if (onSuccess) onSuccess(user.role);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (roleChoice: UserRole, demoEmail: string) => {
    setRole(roleChoice);
    setEmail(demoEmail);
    setPassword('Password123!');
  };

  return (
    <Modal
      open={!!mode}
      onClose={onClose}
      title={mode === 'login' ? 'Log in to Confluence' : 'Create your account'}
    >
      <form onSubmit={handleSubmit} className="space-y-3">
        {error && (
          <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
            {error}
          </div>
        )}

        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">I am logging in as…</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm focus-ring bg-white text-black font-medium"
          >
            <option value="student" className="text-black bg-white">Student</option>
            <option value="academician" className="text-black bg-white">Academician</option>
            <option value="institute" className="text-black bg-white">University representative</option>
            <option value="industry" className="text-black bg-white">Industry representative</option>
          </select>
        </div>

        {mode === 'register' && (
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">
              {role === 'industry' ? 'Company Name' : role === 'institute' ? 'Institute Name' : 'Full Name'}
            </label>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm focus-ring bg-white text-black placeholder-gray-400"
              placeholder={role === 'industry' ? 'e.g. Acme Tech' : 'e.g. Kareena Patel'}
            />
          </div>
        )}

        {mode === 'register' && role === 'student' && (
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">College / University</label>
            <input
              value={college}
              onChange={(e) => setCollege(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm focus-ring bg-white text-black placeholder-gray-400"
              placeholder="e.g. MSU Baroda"
            />
          </div>
        )}

        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm focus-ring bg-white text-black placeholder-gray-400"
            placeholder="you@university.edu"
          />
        </div>

        <div>
          <label className="text-xs font-semibold text-[var(--text-muted)]">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm focus-ring bg-white text-black placeholder-gray-400"
            placeholder="••••••••"
          />
        </div>

        <Button variant="primary" type="submit" className="w-full mt-2" disabled={loading}>
          {loading ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
        </Button>

        {/* Quick Demo Fill Helper */}
        {mode === 'login' && (
          <div className="pt-2 border-t border-[var(--border)] mt-3">
            <div className="text-[11px] text-[var(--text-muted)] mb-1.5 font-medium">Quick Demo Accounts:</div>
            <div className="flex flex-wrap gap-1">
              <button
                type="button"
                onClick={() => fillDemo('student', 'kareena@college.edu')}
                className="px-2 py-1 rounded bg-black/5 hover:bg-black/10 text-[11px]"
              >
                Student Demo
              </button>
              <button
                type="button"
                onClick={() => fillDemo('industry', 'recruitment@adoratech.io')}
                className="px-2 py-1 rounded bg-black/5 hover:bg-black/10 text-[11px]"
              >
                Industry Demo
              </button>
              <button
                type="button"
                onClick={() => fillDemo('academician', 'xyz@msu.edu')}
                className="px-2 py-1 rounded bg-black/5 hover:bg-black/10 text-[11px]"
              >
                Faculty Demo
              </button>
              <button
                type="button"
                onClick={() => fillDemo('institute', 'tnp@msu.edu')}
                className="px-2 py-1 rounded bg-black/5 hover:bg-black/10 text-[11px]"
              >
                Institute Demo
              </button>
            </div>
          </div>
        )}

        <p className="text-xs text-center text-[var(--text-muted)] pt-1">
          {mode === 'login' ? "New here? " : "Already registered? "}
          <button
            type="button"
            className="font-semibold underline underline-offset-2"
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          >
            {mode === 'login' ? 'Register' : 'Log in'}
          </button>
        </p>
      </form>
    </Modal>
  );
};
