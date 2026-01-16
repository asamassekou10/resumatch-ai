/**
 * JobApplicationModal Component
 * Modal for adding/editing job applications
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Building2, Briefcase, Link2, MapPin, DollarSign, Calendar, FileText, Save } from 'lucide-react';

const WORK_TYPES = [
  { value: '', label: 'Select work type' },
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'onsite', label: 'On-site' }
];

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

const JobApplicationModal = ({ isOpen, onClose, onSave, application = null, isLoading = false }) => {
  const isEditing = !!application;

  const [formData, setFormData] = useState({
    company_name: '',
    job_title: '',
    job_url: '',
    location: '',
    work_type: '',
    salary_min: '',
    salary_max: '',
    status: 'saved',
    date_applied: '',
    date_interview: '',
    follow_up_date: '',
    notes: '',
    referral_contact: '',
    cover_letter_used: false
  });

  const [errors, setErrors] = useState({});

  // Reset form when modal opens/closes or application changes
  useEffect(() => {
    if (isOpen) {
      if (application) {
        setFormData({
          company_name: application.company_name || '',
          job_title: application.job_title || '',
          job_url: application.job_url || '',
          location: application.location || '',
          work_type: application.work_type || '',
          salary_min: application.salary_min || '',
          salary_max: application.salary_max || '',
          status: application.status || 'saved',
          date_applied: application.date_applied ? application.date_applied.split('T')[0] : '',
          date_interview: application.date_interview ? application.date_interview.split('T')[0] : '',
          follow_up_date: application.follow_up_date ? application.follow_up_date.split('T')[0] : '',
          notes: application.notes || '',
          referral_contact: application.referral_contact || '',
          cover_letter_used: application.cover_letter_used || false
        });
      } else {
        setFormData({
          company_name: '',
          job_title: '',
          job_url: '',
          location: '',
          work_type: '',
          salary_min: '',
          salary_max: '',
          status: 'saved',
          date_applied: '',
          date_interview: '',
          follow_up_date: '',
          notes: '',
          referral_contact: '',
          cover_letter_used: false
        });
      }
      setErrors({});
    }
  }, [isOpen, application]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error when field is modified
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.company_name.trim()) {
      newErrors.company_name = 'Company name is required';
    }
    if (!formData.job_title.trim()) {
      newErrors.job_title = 'Job title is required';
    }
    if (formData.job_url && !formData.job_url.match(/^https?:\/\/.+/)) {
      newErrors.job_url = 'Please enter a valid URL starting with http:// or https://';
    }
    if (formData.salary_min && formData.salary_max) {
      if (parseInt(formData.salary_min) > parseInt(formData.salary_max)) {
        newErrors.salary_max = 'Max salary must be greater than min salary';
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    // Clean up data before sending
    const cleanData = {
      ...formData,
      salary_min: formData.salary_min ? parseInt(formData.salary_min) : null,
      salary_max: formData.salary_max ? parseInt(formData.salary_max) : null,
      date_applied: formData.date_applied || null,
      date_interview: formData.date_interview || null,
      follow_up_date: formData.follow_up_date || null,
      job_url: formData.job_url || null,
      location: formData.location || null,
      work_type: formData.work_type || null,
      notes: formData.notes || null,
      referral_contact: formData.referral_contact || null
    };

    onSave(cleanData);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 overflow-y-auto">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="flex min-h-full items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-2xl bg-gray-900 rounded-2xl shadow-2xl border border-white/10 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
              <h2 className="text-xl font-bold text-white font-display">
                {isEditing ? 'Edit Application' : 'Add New Application'}
              </h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
              {/* Company & Job Title Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <Building2 className="w-4 h-4 inline mr-2" />
                    Company Name *
                  </label>
                  <input
                    type="text"
                    name="company_name"
                    value={formData.company_name}
                    onChange={handleChange}
                    className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition ${
                      errors.company_name ? 'border-red-500' : 'border-white/10'
                    }`}
                    placeholder="e.g., Google"
                  />
                  {errors.company_name && (
                    <p className="text-red-400 text-xs mt-1">{errors.company_name}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <Briefcase className="w-4 h-4 inline mr-2" />
                    Job Title *
                  </label>
                  <input
                    type="text"
                    name="job_title"
                    value={formData.job_title}
                    onChange={handleChange}
                    className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition ${
                      errors.job_title ? 'border-red-500' : 'border-white/10'
                    }`}
                    placeholder="e.g., Software Engineer"
                  />
                  {errors.job_title && (
                    <p className="text-red-400 text-xs mt-1">{errors.job_title}</p>
                  )}
                </div>
              </div>

              {/* Job URL */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Link2 className="w-4 h-4 inline mr-2" />
                  Job URL
                </label>
                <input
                  type="text"
                  name="job_url"
                  value={formData.job_url}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition ${
                    errors.job_url ? 'border-red-500' : 'border-white/10'
                  }`}
                  placeholder="https://linkedin.com/jobs/..."
                />
                {errors.job_url && (
                  <p className="text-red-400 text-xs mt-1">{errors.job_url}</p>
                )}
              </div>

              {/* Location & Work Type Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <MapPin className="w-4 h-4 inline mr-2" />
                    Location
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                    placeholder="e.g., San Francisco, CA"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Work Type
                  </label>
                  <select
                    name="work_type"
                    value={formData.work_type}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  >
                    {WORK_TYPES.map(type => (
                      <option key={type.value} value={type.value} className="bg-gray-900">
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Salary Range */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <DollarSign className="w-4 h-4 inline mr-2" />
                    Min Salary
                  </label>
                  <input
                    type="number"
                    name="salary_min"
                    value={formData.salary_min}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                    placeholder="e.g., 80000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Max Salary
                  </label>
                  <input
                    type="number"
                    name="salary_max"
                    value={formData.salary_max}
                    onChange={handleChange}
                    className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition ${
                      errors.salary_max ? 'border-red-500' : 'border-white/10'
                    }`}
                    placeholder="e.g., 120000"
                  />
                  {errors.salary_max && (
                    <p className="text-red-400 text-xs mt-1">{errors.salary_max}</p>
                  )}
                </div>
              </div>

              {/* Status & Dates Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Status
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  >
                    {STATUSES.map(s => (
                      <option key={s.value} value={s.value} className="bg-gray-900">
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <Calendar className="w-4 h-4 inline mr-2" />
                    Date Applied
                  </label>
                  <input
                    type="date"
                    name="date_applied"
                    value={formData.date_applied}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  />
                </div>
              </div>

              {/* Interview & Follow-up Dates */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Interview Date
                  </label>
                  <input
                    type="date"
                    name="date_interview"
                    value={formData.date_interview}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Follow-up Date
                  </label>
                  <input
                    type="date"
                    name="follow_up_date"
                    value={formData.follow_up_date}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  />
                </div>
              </div>

              {/* Referral */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Referral Contact
                </label>
                <input
                  type="text"
                  name="referral_contact"
                  value={formData.referral_contact}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  placeholder="e.g., John Smith (friend@company.com)"
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <FileText className="w-4 h-4 inline mr-2" />
                  Notes
                </label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition resize-none"
                  placeholder="Add any notes about this application..."
                />
              </div>

              {/* Cover Letter Checkbox */}
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="cover_letter_used"
                  name="cover_letter_used"
                  checked={formData.cover_letter_used}
                  onChange={handleChange}
                  className="w-5 h-5 rounded border-white/20 bg-white/5 text-blue-500 focus:ring-blue-500/50"
                />
                <label htmlFor="cover_letter_used" className="text-gray-300">
                  Cover letter included with application
                </label>
              </div>
            </form>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-white/10 bg-white/5">
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2.5 text-gray-300 hover:text-white transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    {isEditing ? 'Update' : 'Add Application'}
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </AnimatePresence>
  );
};

export default JobApplicationModal;
