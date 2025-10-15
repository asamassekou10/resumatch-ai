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
    const token = localStorage.getItem('resume_analyzer_token');
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
      localStorage.removeItem('resume_analyzer_token');
      localStorage.removeItem('resume_analyzer_user');
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

  // Health check
  static async healthCheck() {
    const response = await api.get(config.api.endpoints.health);
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
