import React from 'react';
import { Icon } from './Icon';

export const VerifiedBadge: React.FC<{ small?: boolean }> = ({ small }) => {
  return (
    <span
      className={
        "inline-flex items-center gap-1 rounded-full bg-sage/20 text-sagedeep border border-sage/50 " +
        (small ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs") +
        " font-semibold"
      }
    >
      <Icon name="checkc" className={small ? "w-3 h-3" : "w-3.5 h-3.5"} />
      Verified
    </span>
  );
};

export const Tag: React.FC<{ children: React.ReactNode; tone?: 'sage' | 'blue' | 'amber' | 'rose' }> = ({
  children,
  tone = "sage",
}) => {
  const tones = {
    sage:  "bg-sage/15 text-sagedeep border-sage/40",
    blue:  "bg-deepblue/10 text-deepblue border-deepblue/25",
    amber: "bg-amber-100 text-amber-800 border-amber-300",
    rose:  "bg-rose-100 text-rose-700 border-rose-300",
  };
  return (
    <span className={"inline-block rounded-full border px-2.5 py-1 text-xs font-medium " + tones[tone]}>
      {children}
    </span>
  );
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'sagesolid' | 'outline' | 'ghost';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  className = "",
  ...rest
}) => {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all duration-150 focus-ring disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary:   "bg-deepblue text-cream hover:bg-deepblue2 active:scale-[.98]",
    sagesolid: "bg-sagedeep text-pcream hover:bg-[#3d492e] active:scale-[.98]",
    outline:   "border border-current bg-transparent hover:bg-black/5 active:scale-[.98]",
    ghost:     "bg-transparent hover:bg-black/5",
  };
  return (
    <button className={base + " " + variants[variant] + " " + className} {...rest}>
      {children}
    </button>
  );
};

export const ProgressBar: React.FC<{
  value: number;
  max?: number;
  colorClass?: string;
  trackClass?: string;
  height?: string;
}> = ({ value, max = 100, colorClass = "bg-sagedeep", trackClass = "bg-black/10", height = "h-2" }) => {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div className={`w-full ${trackClass} rounded-full ${height} overflow-hidden`}>
      <div className={`${colorClass} ${height} rounded-full growbar`} style={{ width: pct + "%" }} />
    </div>
  );
};

export const SkillBar: React.FC<{ name: string; score: number; min: number }> = ({ name, score, min }) => {
  const gap = Math.max(0, min - score);
  const ok = score >= min;
  return (
    <div className="mb-3.5">
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-sm font-semibold">{name}</span>
        <span className="text-xs text-[var(--text-muted)]">
          {score}/100 <span className="opacity-60">· needs {min}</span>
        </span>
      </div>
      <div className="relative w-full bg-black/10 rounded-full h-2.5 overflow-hidden">
        <div className="absolute top-0 bottom-0 w-px bg-deepblue/50 z-10" style={{ left: min + "%" }} />
        <div
          className={`h-2.5 rounded-full growbar ${ok ? "bg-sagedeep" : "bg-amber-500"}`}
          style={{ width: score + "%" }}
        />
      </div>
      {!ok && <div className="text-[11px] text-amber-700 mt-1">{gap} points to the required level</div>}
    </div>
  );
};

export const Card: React.FC<{
  children: React.ReactNode;
  className?: string;
  as?: any;
  [key: string]: any;
}> = ({ children, className = "", as: Comp = 'div', ...rest }) => {
  return (
    <Comp className={"bg-[var(--surface)] border border-[var(--border)] rounded-2xl shadow-sm " + className} {...rest}>
      {children}
    </Comp>
  );
};

export const StatBlock: React.FC<{ label: string; value: string | number; sub?: string }> = ({
  label,
  value,
  sub,
}) => {
  return (
    <Card className="p-4">
      <div className="text-2xl font-display font-semibold">{value}</div>
      <div className="text-xs text-[var(--text-muted)] mt-1">{label}</div>
      {sub && <div className="text-[11px] text-sagedeep mt-1 font-medium">{sub}</div>}
    </Card>
  );
};

export const Modal: React.FC<{
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  wide?: boolean;
}> = ({ open, onClose, title, children, wide }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div
        className={
          "relative bg-[var(--surface)] rounded-t-2xl sm:rounded-2xl w-full " +
          (wide ? "sm:max-w-2xl" : "sm:max-w-md") +
          " max-h-[88vh] overflow-y-auto p-5 sm:p-6 rise"
        }
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display text-lg font-semibold">{title}</h3>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-black/5 focus-ring">
            <Icon name="x" className="w-4 h-4" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

export const SearchInput: React.FC<{
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
}> = ({ value, onChange, placeholder }) => {
  return (
    <div className="relative">
      <Icon name="search" className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] pl-9 pr-3 py-2.5 text-sm focus-ring"
      />
    </div>
  );
};

export const EmptyState: React.FC<{ text: string }> = ({ text }) => {
  return <div className="text-center py-10 text-sm text-[var(--text-muted)]">{text}</div>;
};

export const PageHeader: React.FC<{
  title: string;
  desc?: string;
  action?: React.ReactNode;
}> = ({ title, desc, action }) => {
  return (
    <div className="flex items-start justify-between gap-4 flex-wrap mb-6 rise">
      <div>
        <h1 className="font-display text-2xl sm:text-3xl font-semibold">{title}</h1>
        {desc && <p className="text-sm text-[var(--text-muted)] mt-1.5 max-w-xl">{desc}</p>}
      </div>
      {action}
    </div>
  );
};
