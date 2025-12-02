import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Target, ChevronDown, Check } from 'lucide-react';
import axios from 'axios';
import '../styles/IndustrySelector.css';

const IndustrySelector = ({ currentIndustry, onChange, showDescription = false }) => {
  const [industries, setIndustries] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIndustries();
  }, []);

  const fetchIndustries = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        'http://localhost:5000/api/market/industries',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setIndustries(response.data.industries || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching industries:', error);
      // Fallback to basic industry list
      setIndustries([
        { name: 'Technology', description: 'Software development and technology solutions' },
        { name: 'Data Science', description: 'Machine learning and data analysis' },
        { name: 'Cybersecurity', description: 'Information security and threat protection' },
        { name: 'Healthcare', description: 'Medical technology and healthcare IT' },
        { name: 'Finance', description: 'Financial services and fintech' },
        { name: 'Marketing', description: 'Digital marketing and customer acquisition' },
        { name: 'Design', description: 'UI/UX and product design' },
        { name: 'General', description: 'Cross-industry roles and skills' }
      ]);
      setLoading(false);
    }
  };

  const handleSelect = (industry) => {
    onChange(industry.name);
    setIsOpen(false);
  };

  const selectedIndustry = industries.find(ind => ind.name === currentIndustry);

  return (
    <div className="industry-selector-container">
      <div className="industry-selector-label">
        <Target className="w-4 h-4" />
        <span>Industry:</span>
      </div>

      <div className="industry-selector-wrapper">
        <button
          className="industry-selector-button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={loading}
        >
          <div className="industry-selector-value">
            {loading ? (
              <span className="loading-text">Loading...</span>
            ) : (
              <>
                <span className="industry-name">{currentIndustry || 'Select Industry'}</span>
                {showDescription && selectedIndustry?.description && (
                  <span className="industry-description">{selectedIndustry.description}</span>
                )}
              </>
            )}
          </div>
          <ChevronDown className={`chevron-icon ${isOpen ? 'open' : ''}`} />
        </button>

        {isOpen && !loading && (
          <motion.div
            className="industry-dropdown"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {industries.map((industry) => (
              <button
                key={industry.name}
                className={`industry-option ${industry.name === currentIndustry ? 'selected' : ''}`}
                onClick={() => handleSelect(industry)}
              >
                <div className="industry-option-content">
                  <div className="industry-option-header">
                    <span className="industry-option-name">{industry.name}</span>
                    {industry.name === currentIndustry && (
                      <Check className="check-icon" />
                    )}
                  </div>
                  {industry.description && (
                    <span className="industry-option-description">{industry.description}</span>
                  )}
                </div>
              </button>
            ))}
          </motion.div>
        )}
      </div>

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="industry-selector-overlay"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default IndustrySelector;
