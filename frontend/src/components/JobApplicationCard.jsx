/**
 * JobApplicationCard Component
 * Card display for a single job application in the tracker
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Star, MapPin, ExternalLink, Calendar, Clock, Edit2, Trash2,
  ChevronDown, ChevronUp, MoreVertical, Archive
} from 'lucide-react';
import StatusBadge, { STATUS_CONFIG } from './ui/StatusBadge';
import SpotlightCard from './ui/SpotlightCard';

const STATUSES = [
  { value: 'saved', label: 'Saved' },
  { value: 'applied', label: 'Applied' },
  { value: 'phone_screen', label: 'Phone Screen' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'withdrawn', label: 'Withdrawn' }
];

const JobApplicationCard = ({
  application,
  onEdit,
  onDelete,
  onStatusChange,
  onToggleStar,
  onToggleArchive
}) => {
  const [expanded, setExpanded] = useState(false);
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const [showActionsMenu, setShowActionsMenu] = useState(false);

  const formatDate = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatSalary = (min, max) => {
    if (!min && !max) return null;
    const format = (num) => {
      if (num >= 1000) return `$${(num / 1000).toFixed(0)}k`;
      return `$${num}`;
    };
    if (min && max) return `${format(min)} - ${format(max)}`;
    if (min) return `${format(min)}+`;
    return `Up to ${format(max)}`;
  };

  const isFollowUpDue = () => {
    if (!application.follow_up_date) return false;
    const followUp = new Date(application.follow_up_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return followUp <= today;
  };

  const salary = formatSalary(application.salary_min, application.salary_max);

  return (
    <SpotlightCard className="rounded-xl overflow-hidden">
      <div className="p-4 sm:p-5">
        {/* Header Row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            {/* Star Button */}
            <button
              onClick={() => onToggleStar(application.id)}
              className={`mt-1 p-1 rounded transition flex-shrink-0 ${
                application.is_starred
                  ? 'text-yellow-400 hover:text-yellow-300'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              <Star className={`w-5 h-5 ${application.is_starred ? 'fill-current' : ''}`} />
            </button>

            {/* Company & Title */}
            <div className="min-w-0 flex-1">
              <h3 className="text-lg font-semibold text-white truncate font-display">
                {application.company_name}
              </h3>
              <p className="text-gray-300 truncate">{application.job_title}</p>

              {/* Meta Info */}
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-gray-400">
                {application.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5" />
                    {application.location}
                  </span>
                )}
                {application.work_type && (
                  <span className="capitalize">{application.work_type}</span>
                )}
                {salary && (
                  <span className="text-green-400">{salary}</span>
                )}
              </div>
            </div>
          </div>

          {/* Right Side - Status & Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Status Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowStatusMenu(!showStatusMenu)}
                className="flex items-center gap-1"
              >
                <StatusBadge status={application.status} size="md" />
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>

              {showStatusMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowStatusMenu(false)}
                  />
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 top-full mt-1 w-40 bg-gray-800 border border-white/10 rounded-lg shadow-xl z-20 py-1"
                  >
                    {STATUSES.map(s => (
                      <button
                        key={s.value}
                        onClick={() => {
                          onStatusChange(application.id, s.value);
                          setShowStatusMenu(false);
                        }}
                        className={`w-full px-3 py-2 text-left text-sm hover:bg-white/10 transition flex items-center gap-2 ${
                          application.status === s.value ? 'text-blue-400' : 'text-gray-300'
                        }`}
                      >
                        <span className={`w-2 h-2 rounded-full ${STATUS_CONFIG[s.value]?.dotColor || 'bg-gray-400'}`} />
                        {s.label}
                      </button>
                    ))}
                  </motion.div>
                </>
              )}
            </div>

            {/* Actions Menu */}
            <div className="relative">
              <button
                onClick={() => setShowActionsMenu(!showActionsMenu)}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition"
              >
                <MoreVertical className="w-5 h-5" />
              </button>

              {showActionsMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowActionsMenu(false)}
                  />
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 top-full mt-1 w-40 bg-gray-800 border border-white/10 rounded-lg shadow-xl z-20 py-1"
                  >
                    <button
                      onClick={() => {
                        onEdit(application);
                        setShowActionsMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-white/10 transition flex items-center gap-2"
                    >
                      <Edit2 className="w-4 h-4" />
                      Edit
                    </button>
                    {application.job_url && (
                      <a
                        href={application.job_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={() => setShowActionsMenu(false)}
                        className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-white/10 transition flex items-center gap-2"
                      >
                        <ExternalLink className="w-4 h-4" />
                        View Job
                      </a>
                    )}
                    <button
                      onClick={() => {
                        onToggleArchive(application.id);
                        setShowActionsMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-white/10 transition flex items-center gap-2"
                    >
                      <Archive className="w-4 h-4" />
                      {application.is_archived ? 'Unarchive' : 'Archive'}
                    </button>
                    <button
                      onClick={() => {
                        onDelete(application.id);
                        setShowActionsMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-sm text-red-400 hover:bg-red-500/10 transition flex items-center gap-2"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </button>
                  </motion.div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Dates Row */}
        <div className="flex flex-wrap items-center gap-4 mt-4 text-sm">
          {application.date_applied && (
            <span className="flex items-center gap-1.5 text-gray-400">
              <Calendar className="w-4 h-4" />
              Applied: {formatDate(application.date_applied)}
            </span>
          )}
          {application.date_interview && (
            <span className="flex items-center gap-1.5 text-amber-400">
              <Calendar className="w-4 h-4" />
              Interview: {formatDate(application.date_interview)}
            </span>
          )}
          {application.follow_up_date && (
            <span className={`flex items-center gap-1.5 ${isFollowUpDue() ? 'text-red-400' : 'text-gray-400'}`}>
              <Clock className="w-4 h-4" />
              Follow-up: {formatDate(application.follow_up_date)}
              {isFollowUpDue() && <span className="text-xs bg-red-500/20 px-1.5 py-0.5 rounded">Due!</span>}
            </span>
          )}
        </div>

        {/* Expandable Notes Section */}
        {(application.notes || application.referral_contact) && (
          <>
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 mt-4 text-sm text-gray-400 hover:text-white transition"
            >
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              {expanded ? 'Hide details' : 'Show details'}
            </button>

            {expanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 pt-3 border-t border-white/10"
              >
                {application.referral_contact && (
                  <p className="text-sm text-gray-400 mb-2">
                    <span className="text-gray-500">Referral:</span> {application.referral_contact}
                  </p>
                )}
                {application.notes && (
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">{application.notes}</p>
                )}
                {application.cover_letter_used && (
                  <span className="inline-flex items-center gap-1 mt-2 text-xs text-blue-400 bg-blue-500/10 px-2 py-1 rounded">
                    Cover letter included
                  </span>
                )}
              </motion.div>
            )}
          </>
        )}
      </div>
    </SpotlightCard>
  );
};

export default JobApplicationCard;
