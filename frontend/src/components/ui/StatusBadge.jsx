/**
 * StatusBadge Component
 * Displays a colored badge for job application status
 */

const STATUS_CONFIG = {
  saved: {
    label: 'Saved',
    bgColor: 'bg-gray-500/20',
    textColor: 'text-gray-300',
    borderColor: 'border-gray-500/30',
    dotColor: 'bg-gray-400'
  },
  applied: {
    label: 'Applied',
    bgColor: 'bg-blue-500/20',
    textColor: 'text-blue-300',
    borderColor: 'border-blue-500/30',
    dotColor: 'bg-blue-400'
  },
  phone_screen: {
    label: 'Phone Screen',
    bgColor: 'bg-cyan-500/20',
    textColor: 'text-cyan-300',
    borderColor: 'border-cyan-500/30',
    dotColor: 'bg-cyan-400'
  },
  interview: {
    label: 'Interview',
    bgColor: 'bg-amber-500/20',
    textColor: 'text-amber-300',
    borderColor: 'border-amber-500/30',
    dotColor: 'bg-amber-400'
  },
  offer: {
    label: 'Offer',
    bgColor: 'bg-green-500/20',
    textColor: 'text-green-300',
    borderColor: 'border-green-500/30',
    dotColor: 'bg-green-400'
  },
  rejected: {
    label: 'Rejected',
    bgColor: 'bg-red-500/20',
    textColor: 'text-red-300',
    borderColor: 'border-red-500/30',
    dotColor: 'bg-red-400'
  },
  withdrawn: {
    label: 'Withdrawn',
    bgColor: 'bg-orange-500/20',
    textColor: 'text-orange-300',
    borderColor: 'border-orange-500/30',
    dotColor: 'bg-orange-400'
  },
  accepted: {
    label: 'Accepted',
    bgColor: 'bg-purple-500/20',
    textColor: 'text-purple-300',
    borderColor: 'border-purple-500/30',
    dotColor: 'bg-purple-400'
  }
};

const StatusBadge = ({ status, size = 'md', showDot = true }) => {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.saved;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5'
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 font-medium rounded-full border
        ${config.bgColor} ${config.textColor} ${config.borderColor}
        ${sizeClasses[size]}
      `}
    >
      {showDot && (
        <span className={`w-2 h-2 rounded-full ${config.dotColor}`} />
      )}
      {config.label}
    </span>
  );
};

export { STATUS_CONFIG };
export default StatusBadge;
