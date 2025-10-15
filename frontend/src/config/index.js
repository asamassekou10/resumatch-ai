// Application configuration
const config = {
  // API Configuration
  api: {
    baseURL: process.env.REACT_APP_API_URL || 'https://resumatch-backend-7qdb.onrender.com/api/v1',
    timeout: parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000,
    endpoints: {
      auth: {
        login: '/auth/login',
        register: '/auth/register',
        logout: '/auth/logout',
        me: '/auth/me',
        changePassword: '/auth/change-password'
      },
      analysis: {
        analyze: '/analysis/analyze',
        analyses: '/analysis/analyses',
        feedback: '/analysis/analyses',
        optimize: '/analysis/analyses',
        coverLetter: '/analysis/analyses',
        skillSuggestions: '/analysis/analyses'
      },
      dashboard: {
        stats: '/dashboard/stats',
        insights: '/dashboard/insights'
      },
      health: '/health'
    }
  },

  // Environment
  env: process.env.REACT_APP_ENV || 'development',
  isDevelopment: process.env.REACT_APP_ENV === 'development',
  isProduction: process.env.REACT_APP_ENV === 'production',

  // Feature Flags
  features: {
    analytics: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
    debug: process.env.REACT_APP_ENABLE_DEBUG === 'true'
  },

  // External Services
  services: {
    sentry: {
      dsn: process.env.REACT_APP_SENTRY_DSN
    },
    analytics: {
      googleAnalyticsId: process.env.REACT_APP_GOOGLE_ANALYTICS_ID
    }
  },

  // Application Settings
  app: {
    name: 'ResumeAnalyzer AI',
    version: '2.0.0',
    maxFileSize: 16 * 1024 * 1024, // 16MB
    allowedFileTypes: ['.pdf', '.docx', '.txt'],
    supportedMimeTypes: [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain'
    ]
  },

  // UI Configuration
  ui: {
    theme: {
      primary: '#06B6D4', // cyan-500
      secondary: '#3B82F6', // blue-500
      success: '#10B981', // emerald-500
      warning: '#F59E0B', // amber-500
      error: '#EF4444', // red-500
      info: '#8B5CF6' // violet-500
    },
    breakpoints: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px'
    }
  },

  // Storage Keys
  storage: {
    token: 'resume_analyzer_token',
    user: 'resume_analyzer_user',
    theme: 'resume_analyzer_theme',
    settings: 'resume_analyzer_settings'
  },

  // Validation Rules
  validation: {
    email: {
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      message: 'Please enter a valid email address'
    },
    password: {
      minLength: 6,
      maxLength: 128,
      message: 'Password must be between 6 and 128 characters'
    },
    jobDescription: {
      minLength: 50,
      maxLength: 10000,
      message: 'Job description must be between 50 and 10,000 characters'
    },
    jobTitle: {
      maxLength: 200,
      message: 'Job title must be less than 200 characters'
    },
    companyName: {
      maxLength: 200,
      message: 'Company name must be less than 200 characters'
    }
  },

  // Error Messages
  errors: {
    network: 'Network error. Please check your connection and try again.',
    unauthorized: 'You are not authorized to perform this action.',
    forbidden: 'Access denied.',
    notFound: 'The requested resource was not found.',
    serverError: 'An unexpected error occurred. Please try again later.',
    validation: 'Please check your input and try again.',
    fileUpload: 'File upload failed. Please try again.',
    analysisFailed: 'Analysis failed. Please try again with a different file or job description.'
  },

  // Success Messages
  messages: {
    loginSuccess: 'Welcome back!',
    registerSuccess: 'Account created successfully!',
    logoutSuccess: 'You have been logged out successfully.',
    analysisSuccess: 'Analysis completed successfully!',
    feedbackGenerated: 'AI feedback generated successfully!',
    resumeOptimized: 'Resume optimized successfully!',
    coverLetterGenerated: 'Cover letter generated successfully!',
    passwordChanged: 'Password changed successfully!'
  }
};

export default config;
