import React from 'react';

export const ICONP: Record<string, string> = {
  home:      "M4 11.5 12 5l8 6.5M6 10.5V19h12v-8.5", 
  flask:     "M9 3h6M10 3v5.2L5.5 16a2 2 0 0 0 1.8 3h9.4a2 2 0 0 0 1.8-3L14 8.2V3",
  student:   "M3 8.5 12 4l9 4.5-9 4.5-9-4.5Zm4 2.2V16c0 1.4 2.3 3 5 3s5-1.6 5-3v-5.3",
  building:  "M5 21V5a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v16M13 21v-8a1 1 0 0 1 1-1h5a1 1 0 0 1 1 1v8M8 7h.01M8 10h.01M8 13h.01M3 21h18",
  briefcase: "M4 8h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1Zm4 0V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18",
  search:    "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm9 2-4.35-4.35",
  bell:      "M6 9a6 6 0 1 1 12 0c0 4 1.5 5.5 1.5 5.5h-15S6 13 6 9Zm4.5 9a1.7 1.7 0 0 0 3 0",
  user:      "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 9a7 7 0 0 1 14 0",
  chevron:   "m9 6 6 6-6 6",
  check:     "m5 13 4 4L19 7",
  checkc:    "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm-4-9 2.6 2.6L16 10",
  upload:    "M12 16V4m0 0 4 4m-4-4-4 4M5 16v3a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3",
  msg:       "M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9l-5 4V6a1 1 0 0 1 1-1Z",
  award:     "M12 15a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm-3 4.3L8 22l4-2 4 2-1-2.7",
  target:    "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-4a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0-4a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z",
  calendar:  "M7 3v3M17 3v3M4 8h16M5 6h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1Z",
  zap:       "M13 3 5 14h6l-1 7 8-11h-6l1-7Z",
  filter:    "M4 5h16l-6 8v6l-4 2v-8L4 5Z",
  users:     "M9 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-6 8a6 6 0 0 1 12 0M18 8a3 3 0 1 1 0 6M22 20a5 5 0 0 0-4.7-5",
  bars:      "M6 20V10M12 20V4M18 20v-7",
  book:      "M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15ZM20 18H6.5A2.5 2.5 0 0 0 4 20.5",
  arrowr:    "M5 12h14M13 6l6 6-6 6",
  x:         "M6 6l12 12M18 6 6 18",
  menu:      "M4 7h16M4 12h16M4 17h16",
  compass:   "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm3.5-12.5-2 5-5 2 2-5 5-2Z",
  link:      "M9 15 15 9M10 7l1.6-1.6a3.5 3.5 0 0 1 5 5L15 12M14 17l-1.6 1.6a3.5 3.5 0 0 1-5-5L9 12",
  file:      "M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm7 0v5h5",
};

interface IconProps {
  name: string;
  className?: string;
  strokeWidth?: number;
}

export const Icon: React.FC<IconProps> = ({ name, className = "w-5 h-5", strokeWidth = 1.8 }) => {
  const d = ICONP[name] || ICONP.home;
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d={d} />
    </svg>
  );
};
