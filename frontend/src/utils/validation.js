import config from '../config';

// Validation utility functions
export const validators = {
  // Email validation
  email: (value) => {
    if (!value) {
      return 'Email is required';
    }
    
    if (!config.validation.email.pattern.test(value)) {
      return config.validation.email.message;
    }
    
    return null;
  },

  // Password validation
  password: (value) => {
    if (!value) {
      return 'Password is required';
    }
    
    if (value.length < config.validation.password.minLength) {
      return `Password must be at least ${config.validation.password.minLength} characters`;
    }
    
    if (value.length > config.validation.password.maxLength) {
      return `Password must be less than ${config.validation.password.maxLength} characters`;
    }
    
    return null;
  },

  // Job description validation
  jobDescription: (value) => {
    if (!value) {
      return 'Job description is required';
    }
    
    if (value.length < config.validation.jobDescription.minLength) {
      return `Job description must be at least ${config.validation.jobDescription.minLength} characters`;
    }
    
    if (value.length > config.validation.jobDescription.maxLength) {
      return `Job description must be less than ${config.validation.jobDescription.maxLength} characters`;
    }
    
    return null;
  },

  // Job title validation
  jobTitle: (value) => {
    if (value && value.length > config.validation.jobTitle.maxLength) {
      return config.validation.jobTitle.message;
    }
    
    return null;
  },

  // Company name validation
  companyName: (value) => {
    if (value && value.length > config.validation.companyName.maxLength) {
      return config.validation.companyName.message;
    }
    
    return null;
  },

  // File validation
  file: (file) => {
    if (!file) {
      return 'Please select a file';
    }
    
    // Check file size
    if (file.size > config.app.maxFileSize) {
      return `File size must be less than ${config.app.maxFileSize / (1024 * 1024)}MB`;
    }
    
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!config.app.allowedFileTypes.includes(fileExtension)) {
      return `File type not supported. Allowed types: ${config.app.allowedFileTypes.join(', ')}`;
    }
    
    return null;
  },

  // Required field validation
  required: (value, fieldName = 'This field') => {
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      return `${fieldName} is required`;
    }
    
    return null;
  },

  // Minimum length validation
  minLength: (value, minLength, fieldName = 'This field') => {
    if (value && value.length < minLength) {
      return `${fieldName} must be at least ${minLength} characters`;
    }
    
    return null;
  },

  // Maximum length validation
  maxLength: (value, maxLength, fieldName = 'This field') => {
    if (value && value.length > maxLength) {
      return `${fieldName} must be less than ${maxLength} characters`;
    }
    
    return null;
  }
};

// Form validation helper
export const validateForm = (data, rules) => {
  const errors = {};
  
  for (const field in rules) {
    const value = data[field];
    const fieldRules = rules[field];
    
    for (const rule of fieldRules) {
      const error = rule(value, field);
      if (error) {
        errors[field] = error;
        break; // Stop at first error for each field
      }
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Common validation rules
export const validationRules = {
  login: {
    email: [validators.required, validators.email],
    password: [validators.required]
  },
  
  register: {
    email: [validators.required, validators.email],
    password: [validators.required, validators.password]
  },
  
  analysis: {
    jobDescription: [validators.required, validators.jobDescription],
    jobTitle: [validators.jobTitle],
    companyName: [validators.companyName],
    resume: [validators.file]
  },
  
  changePassword: {
    currentPassword: [validators.required],
    newPassword: [validators.required, validators.password]
  }
};

// Sanitization functions
export const sanitizeInput = {
  // Remove HTML tags and scripts
  html: (value) => {
    if (typeof value !== 'string') return value;
    
    // Remove HTML tags
    const withoutTags = value.replace(/<[^>]*>/g, '');
    
    // Remove script content
    const withoutScripts = withoutTags.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    
    return withoutScripts.trim();
  },

  // Remove extra whitespace
  whitespace: (value) => {
    if (typeof value !== 'string') return value;
    return value.replace(/\s+/g, ' ').trim();
  },

  // Sanitize all text inputs
  text: (value) => {
    if (typeof value !== 'string') return value;
    return sanitizeInput.whitespace(sanitizeInput.html(value));
  }
};

// Format validation error for display
export const formatValidationError = (error) => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error && error.message) {
    return error.message;
  }
  
  return 'Validation error';
};

// Check if a value is empty
export const isEmpty = (value) => {
  if (value === null || value === undefined) {
    return true;
  }
  
  if (typeof value === 'string') {
    return value.trim() === '';
  }
  
  if (Array.isArray(value)) {
    return value.length === 0;
  }
  
  if (typeof value === 'object') {
    return Object.keys(value).length === 0;
  }
  
  return false;
};

// Debounce function for input validation
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export default {
  validators,
  validateForm,
  validationRules,
  sanitizeInput,
  formatValidationError,
  isEmpty,
  debounce
};
