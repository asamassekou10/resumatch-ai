import axios from 'axios';
import config from '../config';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: config.api.baseURL,
  timeout: config.api.timeout,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common error cases
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

// API service class
class ApiService {
  // Auth endpoints
  static async login(email, password) {
    const response = await api.post(config.api.endpoints.auth.login, {
      email,
      password
    });
    return response.data;
  }

  static async register(email, password) {
    const response = await api.post(config.api.endpoints.auth.register, {
      email,
      password
    });
    return response.data;
  }

  static async logout() {
    const response = await api.post(config.api.endpoints.auth.logout);
    return response.data;
  }

  static async getCurrentUser() {
    const response = await api.get(config.api.endpoints.auth.me);
    return response.data;
  }

  static async changePassword(currentPassword, newPassword) {
    const response = await api.post(config.api.endpoints.auth.changePassword, {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  }

  // LinkedIn OAuth endpoints
  static async getLinkedInStatus() {
    const response = await api.get(config.api.endpoints.auth.linkedinStatus);
    return response.data;
  }

  static getLinkedInLoginUrl() {
    return `${config.api.baseURL}${config.api.endpoints.auth.linkedinLogin}`;
  }

  static async getLinkedInProfile() {
    const response = await api.get(config.api.endpoints.auth.linkedinProfile);
    return response.data;
  }

  static async disconnectLinkedIn() {
    const response = await api.post(config.api.endpoints.auth.linkedinDisconnect);
    return response.data;
  }

  // Analysis endpoints
  static async analyzeResume(formData) {
    const response = await api.post(config.api.endpoints.analysis.analyze, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  static async getAnalyses(page = 1, perPage = 20) {
    const response = await api.get(config.api.endpoints.analysis.analyses, {
      params: { page, per_page: perPage }
    });
    return response.data;
  }

  static async getAnalysis(analysisId) {
    const response = await api.get(`${config.api.endpoints.analysis.analyses}/${analysisId}`);
    return response.data;
  }

  static async generateFeedback(analysisId) {
    const response = await api.post(`${config.api.endpoints.analysis.feedback}/${analysisId}/feedback`);
    return response.data;
  }

  static async optimizeResume(analysisId) {
    const response = await api.post(`${config.api.endpoints.analysis.optimize}/${analysisId}/optimize`);
    return response.data;
  }

  static async generateCoverLetter(analysisId) {
    const response = await api.post(`${config.api.endpoints.analysis.coverLetter}/${analysisId}/cover-letter`);
    return response.data;
  }

  static async getSkillSuggestions(analysisId) {
    const response = await api.post(`${config.api.endpoints.analysis.skillSuggestions}/${analysisId}/skill-suggestions`);
    return response.data;
  }

  static async deleteAnalysis(analysisId) {
    const response = await api.delete(`${config.api.endpoints.analysis.analyses}/${analysisId}`);
    return response.data;
  }

  // Dashboard endpoints
  static async getDashboardStats() {
    const response = await api.get(config.api.endpoints.dashboard.stats);
    return response.data;
  }

  static async getInsights() {
    const response = await api.get(config.api.endpoints.dashboard.insights);
    return response.data;
  }

  // Market Intelligence endpoints
  static async getTopDemandedSkills(limit = 10, days = 90) {
    const response = await api.get(config.api.endpoints.market.demandSkills, {
      params: { limit, days }
    });
    return response.data;
  }

  static async getSkillDemand(skillId) {
    const response = await api.get(`${config.api.endpoints.market.skillDemand}/${skillId}`);
    return response.data;
  }

  static async getSalaryTrends(skillId, days = 180) {
    const response = await api.get(`${config.api.endpoints.market.salaryTrends}/${skillId}/salary-trends`, {
      params: { days }
    });
    return response.data;
  }

  static async getSkillGapAnalysis(skills, jobTitle = null) {
    const response = await api.post(config.api.endpoints.market.gapAnalysis, {
      skills,
      job_title: jobTitle
    });
    return response.data;
  }

  static async getIndustrySkills(industry, days = 90) {
    const response = await api.get(`${config.api.endpoints.market.industrySkills}/${industry}/skills`, {
      params: { days }
    });
    return response.data;
  }

  static async getLocationSalaries(location, skillId = null) {
    const endpoint = `${config.api.endpoints.market.locationSalaries}/${location}/salaries`;
    const response = await api.get(endpoint, {
      params: skillId ? { skill_id: skillId } : {}
    });
    return response.data;
  }

  static async getMarketSummary() {
    const response = await api.get(config.api.endpoints.market.summary);
    return response.data;
  }

  // Job Posting endpoints
  static async ingestJobPostings(postings, extractSkills = true) {
    const response = await api.post(config.api.endpoints.jobs.ingest, {
      postings,
      extract_skills: extractSkills
    });
    return response.data;
  }

  static async loadSampleData() {
    const response = await api.post(config.api.endpoints.jobs.loadSample);
    return response.data;
  }

  static async getJobStatistics() {
    const response = await api.get(config.api.endpoints.jobs.statistics);
    return response.data;
  }

  static async getJobSources() {
    const response = await api.get(config.api.endpoints.jobs.sources);
    return response.data;
  }

  static async ingestRealJobs() {
    const response = await api.post(config.api.endpoints.jobs.ingestReal);
    return response.data;
  }

  // Skill endpoints
  static async getExtractedSkills(analysisId) {
    const response = await api.get(`${config.api.endpoints.skills.extract}/${analysisId}`);
    return response.data;
  }

  static async submitSkillFeedback(extractionId, confirmed, rejected = false) {
    const response = await api.post(`${config.api.endpoints.skills.feedback}/${extractionId}/feedback`, {
      confirmed,
      rejected
    });
    return response.data;
  }

  static async getExtractionQuality(analysisId) {
    const response = await api.get(`${config.api.endpoints.skills.quality}/${analysisId}/extraction-quality`);
    return response.data;
  }

  static async getMethodsAccuracy() {
    const response = await api.get(config.api.endpoints.skills.methodsAccuracy);
    return response.data;
  }

  static async getSkillRelationships(skillId, topN = 10) {
    const response = await api.get(`${config.api.endpoints.skills.relationships}/skill/${skillId}`, {
      params: { top_n: topN }
    });
    return response.data;
  }

  static async getRecommendedSkills(skills, topN = 5) {
    const response = await api.post(config.api.endpoints.skills.recommend, {
      skills,
      top_n: topN
    });
    return response.data;
  }

  static async persistSkillRelationships() {
    const response = await api.post(config.api.endpoints.skills.persist);
    return response.data;
  }

  // Health check
  static async healthCheck() {
    const response = await api.get(config.api.endpoints.health);
    return response.data;
  }

  // Job Seeker Insights endpoints
  static async getInsightsDashboard() {
    const response = await api.get('/api/insights/dashboard');
    return response.data;
  }

  static async getInsightsLearningRoadmap() {
    const response = await api.get('/api/insights/learning-roadmap');
    return response.data;
  }

  static async getInsightsCompetitiveness() {
    const response = await api.get('/api/insights/competitiveness-score');
    return response.data;
  }

  static async getInsightsSalaryEstimate() {
    const response = await api.get('/api/insights/salary-estimator');
    return response.data;
  }

  static async getInsightsTrendingSkills() {
    const response = await api.get('/api/insights/trending-skills');
    return response.data;
  }

  static async getInsightsLocation() {
    const response = await api.get('/api/insights/location-intelligence');
    return response.data;
  }
}

// Utility functions for error handling
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.message || config.errors.validation;
      case 401:
        return config.errors.unauthorized;
      case 403:
        return config.errors.forbidden;
      case 404:
        return config.errors.notFound;
      case 413:
        return 'File too large. Maximum file size is 16MB.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return config.errors.serverError;
      default:
        return data.message || config.errors.serverError;
    }
  } else if (error.request) {
    // Request was made but no response received
    return config.errors.network;
  } else {
    // Something else happened
    return error.message || config.errors.serverError;
  }
};

// Utility function to create form data for file uploads
export const createFormData = (file, jobDescription, jobTitle = '', companyName = '') => {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('job_description', jobDescription);
  
  if (jobTitle) formData.append('job_title', jobTitle);
  if (companyName) formData.append('company_name', companyName);
  
  return formData;
};

// Utility function to validate file before upload
export const validateFile = (file) => {
  const errors = [];
  
  // Check file size
  if (file.size > config.app.maxFileSize) {
    errors.push(`File size must be less than ${config.app.maxFileSize / (1024 * 1024)}MB`);
  }
  
  // Check file type
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
  if (!config.app.allowedFileTypes.includes(fileExtension)) {
    errors.push(`File type not supported. Allowed types: ${config.app.allowedFileTypes.join(', ')}`);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export default ApiService;
