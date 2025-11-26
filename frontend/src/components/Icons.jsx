/**
 * Professional Icon Components
 * Consistent SVG icons for the ResuMatch AI application
 */

// Common icon props
const iconProps = {
  className: "icon",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  viewBox: "0 0 24 24"
};

// Analytics & Charts
export const ChartIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M3 3v18h18" />
    <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" />
  </svg>
);

export const ChartBarIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <rect x="3" y="12" width="4" height="8" rx="1" />
    <rect x="10" y="8" width="4" height="12" rx="1" />
    <rect x="17" y="4" width="4" height="16" rx="1" />
  </svg>
);

export const PieChartIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <circle cx="12" cy="12" r="10" />
    <path d="M12 2v10l8.5 5" />
  </svg>
);

export const TrendingUpIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
    <polyline points="17 6 23 6 23 12" />
  </svg>
);

// Status & Actions
export const CheckIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

export const CheckCircleIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} fill="currentColor" {...props}>
    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
  </svg>
);

export const XIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

export const XCircleIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} fill="currentColor" {...props}>
    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
  </svg>
);

export const AlertCircleIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

// Business & Work
export const BriefcaseIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
  </svg>
);

export const BuildingIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M3 21h18" />
    <path d="M5 21V7l8-4v18" />
    <path d="M19 21V11l-6-4" />
    <path d="M9 9v.01" />
    <path d="M9 12v.01" />
    <path d="M9 15v.01" />
    <path d="M9 18v.01" />
  </svg>
);

export const DollarIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <line x1="12" y1="1" x2="12" y2="23" />
    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
  </svg>
);

export const MapPinIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

export const TargetIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
);

// UI & Navigation
export const RefreshIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <polyline points="23 4 23 10 17 10" />
    <polyline points="1 20 1 14 7 14" />
    <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
  </svg>
);

export const LoadingIcon = ({ className = "w-5 h-5 animate-spin", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <line x1="12" y1="2" x2="12" y2="6" />
    <line x1="12" y1="18" x2="12" y2="22" />
    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" />
    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07" />
    <line x1="2" y1="12" x2="6" y2="12" />
    <line x1="18" y1="12" x2="22" y2="12" />
    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" />
    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93" />
  </svg>
);

export const FileTextIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <polyline points="10 9 9 9 8 9" />
  </svg>
);

export const ClipboardIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
  </svg>
);

export const ListIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <line x1="8" y1="6" x2="21" y2="6" />
    <line x1="8" y1="12" x2="21" y2="12" />
    <line x1="8" y1="18" x2="21" y2="18" />
    <line x1="3" y1="6" x2="3.01" y2="6" />
    <line x1="3" y1="12" x2="3.01" y2="12" />
    <line x1="3" y1="18" x2="3.01" y2="18" />
  </svg>
);

// Special Icons
export const SparklesIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
    <path d="M5 19l.5 1.5L7 21l-1.5.5L5 23l-.5-1.5L3 21l1.5-.5L5 19z" />
    <path d="M19 11l.5 1.5L21 13l-1.5.5L19 15l-.5-1.5L17 13l1.5-.5L19 11z" />
  </svg>
);

export const FireIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 11-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 002.5 2.5z" />
  </svg>
);

export const ZapIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);

export const AwardIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <circle cx="12" cy="8" r="7" />
    <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
  </svg>
);

export const UsersIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

export const LightbulbIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M9 18h6" />
    <path d="M10 22h4" />
    <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0018 8 6 6 0 006 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 018.91 14" />
  </svg>
);

export const DatabaseIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
  </svg>
);

export const GlobeIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <circle cx="12" cy="12" r="10" />
    <line x1="2" y1="12" x2="22" y2="12" />
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
  </svg>
);

export const LayersIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <polygon points="12 2 2 7 12 12 22 7 12 2" />
    <polyline points="2 17 12 22 22 17" />
    <polyline points="2 12 12 17 22 12" />
  </svg>
);

// Empty state icon
export const EmptyChartIcon = ({ className = "w-12 h-12", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <rect x="3" y="3" width="18" height="18" rx="2" />
    <path d="M3 15l5-5 4 4 5-5 4 4" />
    <circle cx="7" cy="7" r="1" fill="currentColor" />
  </svg>
);

// Additional icons
export const BookOpenIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
  </svg>
);

export const ArrowUpIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <polyline points="18 15 12 9 6 15" />
  </svg>
);

export const ArrowDownIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <polyline points="6 9 12 15 18 9" />
  </svg>
);

export const AlertIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

export const ClockIcon = ({ className = "w-5 h-5", ...props }) => (
  <svg {...iconProps} className={className} {...props}>
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

export default {
  ChartIcon,
  ChartBarIcon,
  PieChartIcon,
  TrendingUpIcon,
  CheckIcon,
  CheckCircleIcon,
  XIcon,
  XCircleIcon,
  AlertCircleIcon,
  BriefcaseIcon,
  BuildingIcon,
  DollarIcon,
  MapPinIcon,
  TargetIcon,
  RefreshIcon,
  LoadingIcon,
  FileTextIcon,
  ClipboardIcon,
  ListIcon,
  SparklesIcon,
  FireIcon,
  ZapIcon,
  AwardIcon,
  UsersIcon,
  LightbulbIcon,
  DatabaseIcon,
  GlobeIcon,
  LayersIcon,
  EmptyChartIcon,
  BookOpenIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  AlertIcon,
  ClockIcon
};
