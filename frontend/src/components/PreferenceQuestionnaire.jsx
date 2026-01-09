import { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const PreferenceQuestionnaire = ({ token, onComplete, onSkip, isUpdate = false }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [industries, setIndustries] = useState([]);
  const [experienceLevels, setExperienceLevels] = useState([]);

  // Form state
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [jobTitles, setJobTitles] = useState('');
  const [location, setLocation] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');

  useEffect(() => {
    fetchIndustries();
  }, []);

  const fetchIndustries = async () => {
    try {
      const response = await fetch(`${API_URL}/preferences/industries`);
      const data = await response.json();
      setIndustries(data.industries || []);
      setExperienceLevels(data.experience_levels || []);
    } catch (err) {
      console.error('Failed to fetch industries:', err);
      setIndustries([
        'Technology', 'Healthcare', 'Finance', 'Security', 'Marketing',
        'Sales', 'Human Resources', 'Education', 'Manufacturing', 'Other'
      ]);
      setExperienceLevels([
        'Entry Level (0-2 years)', 'Mid Level (3-5 years)',
        'Senior Level (6-10 years)', 'Executive (10+ years)'
      ]);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/user/preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          preferred_industry: selectedIndustry,
          preferred_job_titles: jobTitles.split(',').map(t => t.trim()).filter(t => t),
          preferred_location: location,
          experience_level: experienceLevel
        })
      });

      if (response.ok) {
        onComplete();
      } else {
        console.error('Failed to save preferences');
        onComplete();
      }
    } catch (err) {
      console.error('Error saving preferences:', err);
      onComplete();
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/user/preferences/skip`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (err) {
      console.error('Error skipping preferences:', err);
    } finally {
      setLoading(false);
      onSkip();
    }
  };

  const nextStep = () => setStep(prev => Math.min(prev + 1, 4));
  const prevStep = () => setStep(prev => Math.max(prev - 1, 1));

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl max-w-xl w-full p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
        {/* Compact Header */}
        <div className="text-center mb-4">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full mb-2">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-white">
            {isUpdate ? 'Update Your Market Insights' : 'Personalize Your Market Insights'}
          </h2>
          <p className="text-slate-400 text-sm">Step {step} of 4</p>
        </div>

        {/* Progress bar */}
        <div className="flex gap-1 mb-5">
          {[1, 2, 3, 4].map(s => (
            <div
              key={s}
              className={`h-1.5 flex-1 rounded-full transition-colors ${
                s <= step ? 'bg-gradient-to-r from-cyan-500 to-blue-600' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>

        {/* Step 1: Industry */}
        {step === 1 && (
          <div>
            <h3 className="text-base font-semibold text-white mb-3">What industry are you in or targeting?</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-[40vh] overflow-y-auto pr-1">
              {industries.map(industry => (
                <button
                  key={industry}
                  onClick={() => setSelectedIndustry(industry)}
                  className={`p-2.5 rounded-lg border text-left text-sm transition-all ${
                    selectedIndustry === industry
                      ? 'border-cyan-500 bg-cyan-500/20 text-cyan-400'
                      : 'border-slate-600 hover:border-slate-500 text-slate-300'
                  }`}
                >
                  {industry}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Job Titles */}
        {step === 2 && (
          <div>
            <h3 className="text-base font-semibold text-white mb-2">What job titles are you targeting?</h3>
            <p className="text-slate-400 text-xs mb-3">Enter one or more job titles, separated by commas</p>
            <input
              type="text"
              value={jobTitles}
              onChange={(e) => setJobTitles(e.target.value)}
              placeholder="e.g., Software Engineer, Data Scientist"
              className="w-full px-3 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition text-sm"
            />
            <div className="mt-3 flex flex-wrap gap-1.5">
              {['Software Engineer', 'Data Analyst', 'Project Manager', 'Product Manager', 'UX Designer'].map(title => (
                <button
                  key={title}
                  onClick={() => setJobTitles(prev => prev ? `${prev}, ${title}` : title)}
                  className="px-2 py-1 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-full text-xs text-slate-300 transition"
                >
                  + {title}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Location */}
        {step === 3 && (
          <div>
            <h3 className="text-base font-semibold text-white mb-3">Where are you looking for jobs?</h3>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., New York, Remote, San Francisco"
              className="w-full px-3 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition text-sm"
            />
            <div className="mt-3 flex flex-wrap gap-1.5">
              {['Remote', 'New York', 'San Francisco', 'Los Angeles', 'Chicago', 'Austin'].map(loc => (
                <button
                  key={loc}
                  onClick={() => setLocation(loc)}
                  className={`px-2.5 py-1 border rounded-full text-xs transition ${
                    location === loc
                      ? 'border-cyan-500 bg-cyan-500/20 text-cyan-400'
                      : 'bg-slate-700 hover:bg-slate-600 border-slate-600 text-slate-300'
                  }`}
                >
                  {loc}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Experience Level */}
        {step === 4 && (
          <div>
            <h3 className="text-base font-semibold text-white mb-3">What's your experience level?</h3>
            <div className="space-y-2">
              {experienceLevels.map(level => (
                <button
                  key={level}
                  onClick={() => setExperienceLevel(level)}
                  className={`w-full p-3 rounded-lg border text-left text-sm transition-all ${
                    experienceLevel === level
                      ? 'border-cyan-500 bg-cyan-500/20 text-cyan-400'
                      : 'border-slate-600 hover:border-slate-500 text-slate-300'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>

            {/* Summary */}
            {(selectedIndustry || jobTitles || location) && (
              <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
                <p className="text-xs text-slate-400 mb-2">Your preferences:</p>
                <div className="flex flex-wrap gap-1.5">
                  {selectedIndustry && (
                    <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 rounded-full text-xs">
                      {selectedIndustry}
                    </span>
                  )}
                  {location && (
                    <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full text-xs">
                      {location}
                    </span>
                  )}
                  {jobTitles && (
                    <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full text-xs">
                      {jobTitles.split(',').length} job title(s)
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Navigation buttons */}
        <div className="flex justify-between mt-5 pt-4 border-t border-slate-700">
          <div>
            {step > 1 ? (
              <button
                onClick={prevStep}
                className="px-4 py-2 text-slate-400 hover:text-white transition text-sm"
              >
                Back
              </button>
            ) : (
              <button
                onClick={handleSkip}
                disabled={loading}
                className="px-4 py-2 text-slate-400 hover:text-white transition text-sm"
              >
                Skip for now
              </button>
            )}
          </div>
          <div>
            {step < 4 ? (
              <button
                onClick={nextStep}
                className="px-5 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg font-medium transition text-sm"
              >
                Continue
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-5 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg font-medium transition flex items-center gap-2 text-sm"
              >
                {loading ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </>
                ) : (
                  'Get Started'
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreferenceQuestionnaire;
