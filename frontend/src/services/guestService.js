const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const guestService = {
  /**
   * Create a new guest session
   * @returns {Promise<{guest_token, credits, expires_at, session_id}>}
   */
  createSession: async () => {
    try {
      const response = await fetch(`${API_URL}/guest/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create guest session');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating guest session:', error);
      throw error;
    }
  },

  /**
   * Analyze resume as guest
   * @param {string} guestToken - Guest session token
   * @param {File} resumeFile - Resume file object
   * @param {string} jobDescription - Job description
   * @param {string} jobTitle - Target job title (optional)
   * @param {string} companyName - Target company (optional)
   * @returns {Promise<{analysis_id, results, credits_remaining}>}
   */
  analyzeResume: async (guestToken, resumeFile, jobDescription, jobTitle = '', companyName = '') => {
    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('job_description', jobDescription);
      formData.append('job_title', jobTitle);
      formData.append('company_name', companyName);

      const response = await fetch(`${API_URL}/guest/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${guestToken}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Analysis failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error analyzing resume:', error);
      throw error;
    }
  },

  /**
   * Get guest analysis results
   * @param {string} guestToken - Guest session token
   * @param {string} analysisId - Analysis ID to retrieve
   * @returns {Promise<{analysis}>}
   */
  getAnalysis: async (guestToken, analysisId) => {
    try {
      const response = await fetch(`${API_URL}/guest/analysis/${analysisId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${guestToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to retrieve analysis');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error retrieving analysis:', error);
      throw error;
    }
  },

  /**
   * Get current guest session info
   * @param {string} guestToken - Guest session token
   * @returns {Promise<{session, analyses_count, time_remaining_minutes}>}
   */
  getSessionInfo: async (guestToken) => {
    try {
      const response = await fetch(`${API_URL}/guest/session/info`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${guestToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to retrieve session info');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error retrieving session info:', error);
      throw error;
    }
  },

  /**
   * Store guest token in localStorage
   * @param {string} token - Guest token
   * @param {Date} expiresAt - When token expires
   */
  storeGuestToken: (token, expiresAt) => {
    localStorage.setItem('guest_token', token);
    localStorage.setItem('guest_expires_at', expiresAt);
  },

  /**
   * Get stored guest token
   * @returns {string|null}
   */
  getGuestToken: () => {
    return localStorage.getItem('guest_token');
  },

  /**
   * Check if guest session is still valid
   * @returns {boolean}
   */
  isGuestSessionValid: () => {
    const token = localStorage.getItem('guest_token');
    const expiresAt = localStorage.getItem('guest_expires_at');

    if (!token || !expiresAt) return false;

    const expiryTime = new Date(expiresAt).getTime();
    const currentTime = new Date().getTime();

    return currentTime < expiryTime;
  },

  /**
   * Clear guest session from localStorage
   */
  clearGuestSession: () => {
    localStorage.removeItem('guest_token');
    localStorage.removeItem('guest_expires_at');
    localStorage.removeItem('guest_session_id');
  },

  /**
   * Get time remaining in guest session (in minutes)
   * @returns {number}
   */
  getTimeRemaining: () => {
    const expiresAt = localStorage.getItem('guest_expires_at');
    if (!expiresAt) return 0;

    const expiryTime = new Date(expiresAt).getTime();
    const currentTime = new Date().getTime();
    const remainingMs = expiryTime - currentTime;

    return Math.max(0, Math.floor(remainingMs / (1000 * 60))); // Convert to minutes
  },
};

export default guestService;
