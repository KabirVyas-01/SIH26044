import React, { useState, useEffect } from 'react';
import { Modal, Button } from '../common/UIComponents';
import { useAuth } from '../../context/AuthContext';
import { authApi } from '../../api/auth';
import { instituteApi } from '../../api/institute';
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
  
  // Student onboarding details
  const [skills, setSkills] = useState('');
  const [universityRollNo, setUniversityRollNo] = useState('');
  const [desiredRole, setDesiredRole] = useState('Full Stack Developer');

  // Role-specific fields
  const [department, setDepartment] = useState('');
  const [expertiseDomain, setExpertiseDomain] = useState('');
  const [adminTpoContact, setAdminTpoContact] = useState('');

  // College Dropdown State
  const [institutes, setInstitutes] = useState<{ id: number; name: string }[]>([]);
  const [selectedInstituteId, setSelectedInstituteId] = useState<string>('1');
  const [customCollege, setCustomCollege] = useState('');

  // OTP Verification State
  const [otpStep, setOtpStep] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [demoOtp, setDemoOtp] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch registered universities when modal opens
  useEffect(() => {
    const loadInstitutes = async () => {
      try {
        const res = await instituteApi.getInstitutesList();
        if (res && res.institutes && res.institutes.length > 0) {
          setInstitutes(res.institutes);
          setSelectedInstituteId(String(res.institutes[0].id));
        } else {
          setInstitutes([{ id: 1, name: 'The Maharaja Sayajirao University of Baroda' }]);
          setSelectedInstituteId('1');
        }
      } catch {
        setInstitutes([{ id: 1, name: 'The Maharaja Sayajirao University of Baroda' }]);
        setSelectedInstituteId('1');
      }
    };

    if (mode === 'register') {
      loadInstitutes();
    }
  }, [mode]);

  useEffect(() => {
    setError(null);
    setOtpStep(false);
    setOtpCode('');
    setDemoOtp(null);
  }, [mode, role]);

  if (!mode) return null;

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await authApi.sendOtp(email);
      setDemoOtp(res.demo_otp || null);
      setOtpStep(true);
    } catch (err: any) {
      setError(err.message || 'Failed to send verification code. Please check your email.');
    } finally {
      setLoading(false);
    }
  };

  const handleFinalSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // 1. Verify OTP
      await authApi.verifyOtp(email, otpCode);

      // 2. Prepare payload
      const chosenCollege =
        selectedInstituteId === 'other'
          ? customCollege
          : institutes.find((i) => String(i.id) === selectedInstituteId)?.name || customCollege;

      const payload: Record<string, any> = {
        email,
        password,
      };

      if (role === 'student') {
        payload.name = name;
        payload.college = chosenCollege;
        payload.skills = skills;
        payload.university_roll_no = universityRollNo;
        payload.desired_role = desiredRole;
        if (selectedInstituteId !== 'other' && selectedInstituteId) {
          payload.institute_id = parseInt(selectedInstituteId, 10);
        }
      } else if (role === 'industry') {
        payload.company_name = name;
      } else if (role === 'institute') {
        payload.name = name;
        payload.admin_tpo_contact = adminTpoContact;
      } else if (role === 'academician') {
        payload.name = name;
        payload.department = department;
        payload.expertise_domain = expertiseDomain;
        if (selectedInstituteId !== 'other' && selectedInstituteId) {
          payload.institute_id = parseInt(selectedInstituteId, 10);
        }
      }

      // 3. Register user
      const user = await signup(role, payload);
      onClose();
      if (onSuccess) onSuccess(user.role);
    } catch (err: any) {
      setError(err.message || 'Verification or registration failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const user = await login(role, email, password);
      onClose();
      if (onSuccess) onSuccess(user.role);
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
      title={
        mode === 'login'
          ? 'Log in to Confluence'
          : otpStep
          ? 'Verify your email'
          : 'Create your account'
      }
    >
      {error && (
        <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium mb-3">
          {error}
        </div>
      )}

      {/* 1. LOGIN FORM */}
      {mode === 'login' && (
        <form onSubmit={handleLoginSubmit} className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">I am logging in as…</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm focus-ring bg-white text-black font-medium"
            >
              <option value="student">Student</option>
              <option value="academician">Academician / Faculty</option>
              <option value="institute">University representative</option>
              <option value="industry">Industry representative</option>
            </select>
          </div>

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
            {loading ? 'Please wait…' : 'Log in'}
          </Button>

          {/* Quick Demo Fill Helper */}
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

          <p className="text-xs text-center text-[var(--text-muted)] pt-1">
            New here?{' '}
            <button
              type="button"
              className="font-semibold underline underline-offset-2"
              onClick={() => setMode('register')}
            >
              Register
            </button>
          </p>
        </form>
      )}

      {/* 2. REGISTRATION STEP 1: FILL DETAILS & SEND OTP */}
      {mode === 'register' && !otpStep && (
        <form onSubmit={handleSendOtp} className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">I am registering as…</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm focus-ring bg-white text-black font-medium"
            >
              <option value="student">Student</option>
              <option value="academician">Academician / Faculty</option>
              <option value="institute">University representative</option>
              <option value="industry">Industry representative</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">
              {role === 'industry' ? 'Company Name' : role === 'institute' ? 'Institute Name' : 'Full Name'}
            </label>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              placeholder={role === 'industry' ? 'e.g. Acme Tech' : 'e.g. Aditi Sharma'}
            />
          </div>

          {/* College Dropdown for Students & Academicians */}
          {(role === 'student' || role === 'academician') && (
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">College / University</label>
              <select
                value={selectedInstituteId}
                onChange={(e) => setSelectedInstituteId(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black font-medium"
              >
                {institutes.map((inst) => (
                  <option key={inst.id} value={String(inst.id)}>
                    {inst.name}
                  </option>
                ))}
                <option value="other">Other / Not Listed</option>
              </select>

              {selectedInstituteId === 'other' && (
                <input
                  required
                  value={customCollege}
                  onChange={(e) => setCustomCollege(e.target.value)}
                  className="w-full mt-2 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
                  placeholder="Enter your college name manually"
                />
              )}
            </div>
          )}

          {/* Student Specific Fields */}
          {role === 'student' && (
            <>
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">University Roll No. / Student ID</label>
                <input
                  value={universityRollNo}
                  onChange={(e) => setUniversityRollNo(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
                  placeholder="e.g. 2026-CS-042"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">Target Role / Career Goal</label>
                <input
                  value={desiredRole}
                  onChange={(e) => setDesiredRole(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
                  placeholder="e.g. Full Stack Developer, AI Specialist"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">Known Skills & Tech Interests</label>
                <input
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
                  placeholder="e.g. Python, SQL, React, Data Structures"
                />
              </div>
            </>
          )}

          {/* Academician Specific Fields */}
          {role === 'academician' && (
            <>
              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">Department</label>
                <input
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
                  placeholder="e.g. Dept. of Computer Science & Engineering"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[var(--text-muted)]">Research Domain / Expertise</label>
                <input
                  value={expertiseDomain}
                  onChange={(e) => setExpertiseDomain(e.target.value)}
                  className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
                  placeholder="e.g. Distributed Systems, Machine Learning"
                />
              </div>
            </>
          )}

          {/* Institute Specific Fields */}
          {role === 'institute' && (
            <div>
              <label className="text-xs font-semibold text-[var(--text-muted)]">Placement Cell / TPO Contact Details</label>
              <input
                value={adminTpoContact}
                onChange={(e) => setAdminTpoContact(e.target.value)}
                className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
                placeholder="e.g. Dr. K. Sharma (TPO Head), tpo@univ.edu"
              />
            </div>
          )}

          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
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
              className="w-full mt-1 rounded-xl border border-[var(--border)] px-3 py-2 text-sm focus-ring bg-white text-black placeholder-gray-400"
              placeholder="••••••••"
            />
          </div>

          <Button variant="primary" type="submit" className="w-full mt-2" disabled={loading}>
            {loading ? 'Sending code…' : 'Continue (Send OTP)'}
          </Button>

          <p className="text-xs text-center text-[var(--text-muted)] pt-1">
            Already registered?{' '}
            <button
              type="button"
              className="font-semibold underline underline-offset-2"
              onClick={() => setMode('login')}
            >
              Log in
            </button>
          </p>
        </form>
      )}

      {/* 3. REGISTRATION STEP 2: ENTER OTP & COMPLETE ACCOUNT */}
      {mode === 'register' && otpStep && (
        <form onSubmit={handleFinalSignup} className="space-y-4">
          <div className="text-center py-2">
            <div className="text-sm font-semibold">Check your email</div>
            <p className="text-xs text-[var(--text-muted)] mt-1">
              We sent a 6-digit verification code to <span className="font-semibold text-black">{email}</span>.
            </p>
            {!demoOtp && (
              <p className="text-[11px] text-[var(--text-muted)] mt-1.5 bg-black/5 p-2 rounded-lg">
                📬 An actual email was dispatched to your inbox. Please check your spam/junk folder if it takes a moment to arrive.
              </p>
            )}
          </div>

          {demoOtp && (
            <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between">
              <span>Demo OTP: <strong className="text-sm font-mono tracking-wider">{demoOtp}</strong></span>
              <button
                type="button"
                onClick={() => setOtpCode(demoOtp)}
                className="px-2 py-1 rounded bg-emerald-600 text-white font-medium hover:bg-emerald-700"
              >
                Auto-fill
              </button>
            </div>
          )}

          <div>
            <label className="text-xs font-semibold text-[var(--text-muted)]">6-Digit OTP Code</label>
            <input
              type="text"
              required
              maxLength={6}
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value.trim())}
              className="w-full mt-1 text-center text-xl font-mono tracking-widest rounded-xl border border-[var(--border)] px-3 py-2.5 focus-ring bg-white text-black"
              placeholder="000000"
            />
          </div>

          <Button variant="primary" type="submit" className="w-full" disabled={loading || otpCode.length < 6}>
            {loading ? 'Verifying…' : 'Verify & Create Account'}
          </Button>

          <div className="text-center pt-1">
            <button
              type="button"
              className="text-xs text-[var(--text-muted)] hover:underline"
              onClick={() => setOtpStep(false)}
            >
              ← Back to change details
            </button>
          </div>
        </form>
      )}
    </Modal>
  );
};
