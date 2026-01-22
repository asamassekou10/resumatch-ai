/**
 * ResumeEditor Component
 * Edit parsed resume data with section-based organization
 */

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  User, Mail, Phone, MapPin, Linkedin, Globe,
  Briefcase, GraduationCap, Code, Award, Plus, Trash2, Save,
  ChevronDown, ChevronUp
} from 'lucide-react';

const ResumeEditor = ({ data, onSave, onDataChange, saving }) => {
  const [formData, setFormData] = useState(data);
  const [expandedSections, setExpandedSections] = useState({
    contact: true,
    summary: true,
    experience: true,
    education: true,
    skills: true,
    certifications: false,
    projects: false
  });
  const [hasChanges, setHasChanges] = useState(false);
  const debounceTimerRef = useRef(null);

  useEffect(() => {
    setFormData(data);
    setHasChanges(false);
  }, [data]);

  // Debounced callback to notify parent of changes
  useEffect(() => {
    if (onDataChange && formData && formData !== data) {
      // Clear existing timer
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      
      // Set new timer
      debounceTimerRef.current = setTimeout(() => {
        onDataChange(formData);
      }, 500); // 500ms debounce
    }

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [formData, onDataChange, data]);

  const updateField = (path, value) => {
    setFormData(prev => {
      const newData = JSON.parse(JSON.stringify(prev));
      const keys = path.split('.');
      let current = newData;

      for (let i = 0; i < keys.length - 1; i++) {
        const key = isNaN(keys[i]) ? keys[i] : parseInt(keys[i]);
        current = current[key];
      }

      const lastKey = isNaN(keys[keys.length - 1])
        ? keys[keys.length - 1]
        : parseInt(keys[keys.length - 1]);
      current[lastKey] = value;

      return newData;
    });
    setHasChanges(true);
  };

  const addListItem = (path, defaultItem) => {
    setFormData(prev => {
      const newData = JSON.parse(JSON.stringify(prev));
      const keys = path.split('.');
      let current = newData;

      for (const key of keys) {
        current = current[isNaN(key) ? key : parseInt(key)];
      }

      current.push(defaultItem);
      return newData;
    });
    setHasChanges(true);
  };

  const removeListItem = (path, index) => {
    setFormData(prev => {
      const newData = JSON.parse(JSON.stringify(prev));
      const keys = path.split('.');
      let current = newData;

      for (const key of keys) {
        current = current[isNaN(key) ? key : parseInt(key)];
      }

      current.splice(index, 1);
      return newData;
    });
    setHasChanges(true);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleSave = () => {
    onSave(formData);
    setHasChanges(false);
  };

  const SectionHeader = ({ title, icon: Icon, section, count }) => (
    <button
      onClick={() => toggleSection(section)}
      className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition rounded-t-xl"
    >
      <div className="flex items-center gap-3">
        <Icon className="w-5 h-5 text-blue-400" />
        <span className="font-semibold text-white">{title}</span>
        {count !== undefined && (
          <span className="text-xs text-gray-500 bg-white/10 px-2 py-0.5 rounded">
            {count}
          </span>
        )}
      </div>
      {expandedSections[section] ? (
        <ChevronUp className="w-5 h-5 text-gray-400" />
      ) : (
        <ChevronDown className="w-5 h-5 text-gray-400" />
      )}
    </button>
  );

  const InputField = ({ label, value, onChange, placeholder, type = 'text', icon: Icon, fieldKey }) => {
    // Use useMemo to prevent unnecessary re-renders
    const handleChange = (e) => {
      onChange(e.target.value);
    };
    
    return (
      <div>
        <label className="block text-sm text-gray-400 mb-1 flex items-center gap-2">
          {Icon && <Icon className="w-4 h-4" />}
          {label}
        </label>
        <input
          key={fieldKey || label}
          type={type}
          value={value || ''}
          onChange={handleChange}
          placeholder={placeholder}
          className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition text-sm"
        />
      </div>
    );
  };

  const TextAreaField = ({ label, value, onChange, placeholder, rows = 3, fieldKey }) => {
    const handleChange = (e) => {
      onChange(e.target.value);
    };
    
    return (
      <div>
        <label className="block text-sm text-gray-400 mb-1">{label}</label>
        <textarea
          key={fieldKey || label}
          value={value || ''}
          onChange={handleChange}
          placeholder={placeholder}
          rows={rows}
          className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition text-sm resize-none"
        />
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
            hasChanges
              ? 'bg-green-500 text-white hover:bg-green-600'
              : 'bg-gray-700 text-gray-400 cursor-not-allowed'
          }`}
        >
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : hasChanges ? 'Save Changes' : 'No Changes'}
        </button>
      </div>

      {/* Contact Section */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
        initial={false}
      >
        <SectionHeader title="Contact Information" icon={User} section="contact" />
        {expandedSections.contact && (
          <div className="p-4 pt-0 grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField
              fieldKey="contact-name"
              label="Full Name"
              icon={User}
              value={formData.contact?.name}
              onChange={(v) => updateField('contact.name', v)}
              placeholder="John Doe"
            />
            <InputField
              fieldKey="contact-email"
              label="Email"
              icon={Mail}
              type="email"
              value={formData.contact?.email}
              onChange={(v) => updateField('contact.email', v)}
              placeholder="john@example.com"
            />
            <InputField
              fieldKey="contact-phone"
              label="Phone"
              icon={Phone}
              value={formData.contact?.phone}
              onChange={(v) => updateField('contact.phone', v)}
              placeholder="+1 (555) 123-4567"
            />
            <InputField
              fieldKey="contact-location"
              label="Location"
              icon={MapPin}
              value={formData.contact?.location}
              onChange={(v) => updateField('contact.location', v)}
              placeholder="San Francisco, CA"
            />
            <InputField
              fieldKey="contact-linkedin"
              label="LinkedIn"
              icon={Linkedin}
              value={formData.contact?.linkedin}
              onChange={(v) => updateField('contact.linkedin', v)}
              placeholder="linkedin.com/in/johndoe"
            />
            <InputField
              fieldKey="contact-website"
              label="Website"
              icon={Globe}
              value={formData.contact?.website}
              onChange={(v) => updateField('contact.website', v)}
              placeholder="johndoe.com"
            />
          </div>
        )}
      </motion.div>

      {/* Summary Section */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
        initial={false}
      >
        <SectionHeader title="Professional Summary" icon={User} section="summary" />
        {expandedSections.summary && (
          <div className="p-4 pt-0">
            <TextAreaField
              fieldKey="summary"
              label="Summary"
              value={formData.summary}
              onChange={(v) => updateField('summary', v)}
              placeholder="Experienced professional with..."
              rows={4}
            />
          </div>
        )}
      </motion.div>

      {/* Experience Section */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
        initial={false}
      >
        <SectionHeader
          title="Work Experience"
          icon={Briefcase}
          section="experience"
          count={formData.experience?.length || 0}
        />
        {expandedSections.experience && (
          <div className="p-4 pt-0 space-y-4">
            {formData.experience?.map((exp, idx) => (
              <div key={idx} className="p-4 bg-white/5 rounded-lg border border-white/5">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs text-gray-500">Experience {idx + 1}</span>
                  <button
                    onClick={() => removeListItem('experience', idx)}
                    className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <InputField
                    fieldKey={`exp-${idx}-title`}
                    label="Job Title"
                    value={exp.title}
                    onChange={(v) => updateField(`experience.${idx}.title`, v)}
                    placeholder="Software Engineer"
                  />
                  <InputField
                    fieldKey={`exp-${idx}-company`}
                    label="Company"
                    value={exp.company}
                    onChange={(v) => updateField(`experience.${idx}.company`, v)}
                    placeholder="Tech Corp"
                  />
                  <InputField
                    fieldKey={`exp-${idx}-location`}
                    label="Location"
                    value={exp.location}
                    onChange={(v) => updateField(`experience.${idx}.location`, v)}
                    placeholder="San Francisco, CA"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <InputField
                      fieldKey={`exp-${idx}-start`}
                      label="Start Date"
                      value={exp.start_date}
                      onChange={(v) => updateField(`experience.${idx}.start_date`, v)}
                      placeholder="Jan 2020"
                    />
                    <InputField
                      fieldKey={`exp-${idx}-end`}
                      label="End Date"
                      value={exp.end_date}
                      onChange={(v) => updateField(`experience.${idx}.end_date`, v)}
                      placeholder="Present"
                    />
                  </div>
                </div>
                <div className="mt-3">
                  <label className="block text-sm text-gray-400 mb-1">Achievements (one per line)</label>
                  <textarea
                    key={`exp-${idx}-achievements`}
                    value={exp.achievements?.join('\n') || ''}
                    onChange={(e) => updateField(`experience.${idx}.achievements`, e.target.value.split('\n'))}
                    placeholder="Led team of 5 engineers...&#10;Increased performance by 40%..."
                    rows={4}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition text-sm resize-none"
                  />
                </div>
              </div>
            ))}
            <button
              onClick={() => addListItem('experience', {
                title: '',
                company: '',
                location: '',
                start_date: '',
                end_date: '',
                achievements: []
              })}
              className="w-full p-3 border border-dashed border-white/20 rounded-lg text-gray-400 hover:text-white hover:border-white/40 transition flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Experience
            </button>
          </div>
        )}
      </motion.div>

      {/* Education Section */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
        initial={false}
      >
        <SectionHeader
          title="Education"
          icon={GraduationCap}
          section="education"
          count={formData.education?.length || 0}
        />
        {expandedSections.education && (
          <div className="p-4 pt-0 space-y-4">
            {formData.education?.map((edu, idx) => (
              <div key={idx} className="p-4 bg-white/5 rounded-lg border border-white/5">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs text-gray-500">Education {idx + 1}</span>
                  <button
                    onClick={() => removeListItem('education', idx)}
                    className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <InputField
                    fieldKey={`edu-${idx}-degree`}
                    label="Degree"
                    value={edu.degree}
                    onChange={(v) => updateField(`education.${idx}.degree`, v)}
                    placeholder="Bachelor of Science"
                  />
                  <InputField
                    fieldKey={`edu-${idx}-field`}
                    label="Field of Study"
                    value={edu.field}
                    onChange={(v) => updateField(`education.${idx}.field`, v)}
                    placeholder="Computer Science"
                  />
                  <InputField
                    fieldKey={`edu-${idx}-institution`}
                    label="Institution"
                    value={edu.institution}
                    onChange={(v) => updateField(`education.${idx}.institution`, v)}
                    placeholder="MIT"
                  />
                  <InputField
                    fieldKey={`edu-${idx}-graduation`}
                    label="Graduation Date"
                    value={edu.graduation_date}
                    onChange={(v) => updateField(`education.${idx}.graduation_date`, v)}
                    placeholder="2020"
                  />
                  <InputField
                    fieldKey={`edu-${idx}-gpa`}
                    label="GPA (optional)"
                    value={edu.gpa}
                    onChange={(v) => updateField(`education.${idx}.gpa`, v)}
                    placeholder="3.8"
                  />
                  <InputField
                    fieldKey={`edu-${idx}-honors`}
                    label="Honors (optional)"
                    value={edu.honors}
                    onChange={(v) => updateField(`education.${idx}.honors`, v)}
                    placeholder="Magna Cum Laude"
                  />
                </div>
              </div>
            ))}
            <button
              onClick={() => addListItem('education', {
                degree: '',
                field: '',
                institution: '',
                graduation_date: '',
                gpa: '',
                honors: ''
              })}
              className="w-full p-3 border border-dashed border-white/20 rounded-lg text-gray-400 hover:text-white hover:border-white/40 transition flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Education
            </button>
          </div>
        )}
      </motion.div>

      {/* Skills Section */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
        initial={false}
      >
        <SectionHeader title="Skills" icon={Code} section="skills" />
        {expandedSections.skills && (
          <div className="p-4 pt-0 space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Technical Skills (comma separated)</label>
              <textarea
                key="skills-technical"
                value={formData.skills?.technical?.join(', ') || ''}
                onChange={(e) => updateField('skills.technical', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                placeholder="Python, React, AWS, Docker..."
                rows={2}
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition text-sm resize-none"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Soft Skills (comma separated)</label>
              <textarea
                key="skills-soft"
                value={formData.skills?.soft?.join(', ') || ''}
                onChange={(e) => updateField('skills.soft', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                placeholder="Leadership, Communication, Problem Solving..."
                rows={2}
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition text-sm resize-none"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Languages (comma separated)</label>
              <textarea
                key="skills-languages"
                value={formData.skills?.languages?.join(', ') || ''}
                onChange={(e) => updateField('skills.languages', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                placeholder="English, Spanish, Mandarin..."
                rows={1}
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition text-sm resize-none"
              />
            </div>
          </div>
        )}
      </motion.div>

      {/* Certifications Section */}
      <motion.div
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
        initial={false}
      >
        <SectionHeader
          title="Certifications"
          icon={Award}
          section="certifications"
          count={formData.certifications?.length || 0}
        />
        {expandedSections.certifications && (
          <div className="p-4 pt-0 space-y-4">
            {formData.certifications?.map((cert, idx) => (
              <div key={idx} className="p-4 bg-white/5 rounded-lg border border-white/5">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs text-gray-500">Certification {idx + 1}</span>
                  <button
                    onClick={() => removeListItem('certifications', idx)}
                    className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <InputField
                    fieldKey={`cert-${idx}-name`}
                    label="Certification Name"
                    value={cert.name}
                    onChange={(v) => updateField(`certifications.${idx}.name`, v)}
                    placeholder="AWS Solutions Architect"
                  />
                  <InputField
                    fieldKey={`cert-${idx}-issuer`}
                    label="Issuer"
                    value={cert.issuer}
                    onChange={(v) => updateField(`certifications.${idx}.issuer`, v)}
                    placeholder="Amazon"
                  />
                  <InputField
                    fieldKey={`cert-${idx}-date`}
                    label="Date"
                    value={cert.date}
                    onChange={(v) => updateField(`certifications.${idx}.date`, v)}
                    placeholder="2023"
                  />
                </div>
              </div>
            ))}
            <button
              onClick={() => addListItem('certifications', {
                name: '',
                issuer: '',
                date: ''
              })}
              className="w-full p-3 border border-dashed border-white/20 rounded-lg text-gray-400 hover:text-white hover:border-white/40 transition flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Certification
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default ResumeEditor;
