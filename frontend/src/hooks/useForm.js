import { useState, useCallback, useRef } from 'react';
import { validateForm, sanitizeInput } from '../utils/validation';

// Custom hook for form management
export const useForm = (initialValues = {}, validationRules = {}, options = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isValid, setIsValid] = useState(false);
  
  const formRef = useRef(null);
  const { 
    validateOnChange = true, 
    validateOnBlur = true,
    sanitizeOnChange = true 
  } = options;

  // Update field value
  const setValue = useCallback((name, value, shouldValidate = true) => {
    let sanitizedValue = value;
    
    // Sanitize input if enabled
    if (sanitizeOnChange && typeof value === 'string') {
      sanitizedValue = sanitizeInput.text(value);
    }
    
    setValues(prev => ({
      ...prev,
      [name]: sanitizedValue
    }));
    
    // Mark field as touched
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    
    // Validate field if enabled
    if (shouldValidate && validateOnChange) {
      validateField(name, sanitizedValue);
    }
  }, [validateOnChange, sanitizeOnChange]);

  // Validate single field
  const validateField = useCallback((name, value = values[name]) => {
    if (!validationRules[name]) return;
    
    const fieldRules = validationRules[name];
    const fieldErrors = [];
    
    for (const rule of fieldRules) {
      const error = rule(value, name);
      if (error) {
        fieldErrors.push(error);
        break; // Stop at first error
      }
    }
    
    setErrors(prev => ({
      ...prev,
      [name]: fieldErrors[0] || null
    }));
    
    // Update overall form validity
    updateFormValidity();
  }, [values, validationRules]);

  // Update overall form validity
  const updateFormValidity = useCallback(() => {
    const hasErrors = Object.values(errors).some(error => error !== null);
    const hasRequiredFields = Object.keys(validationRules).length > 0;
    
    setIsValid(!hasErrors && hasRequiredFields);
  }, [errors, validationRules]);

  // Handle input change
  const handleChange = useCallback((event) => {
    const { name, value, type, checked, files } = event.target;
    
    let inputValue;
    
    if (type === 'checkbox') {
      inputValue = checked;
    } else if (type === 'file') {
      inputValue = files ? files[0] : null;
    } else {
      inputValue = value;
    }
    
    setValue(name, inputValue);
  }, [setValue]);

  // Handle input blur
  const handleBlur = useCallback((event) => {
    const { name } = event.target;
    
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    
    if (validateOnBlur) {
      validateField(name);
    }
  }, [validateOnBlur, validateField]);

  // Validate entire form
  const validate = useCallback(() => {
    const validation = validateForm(values, validationRules);
    
    setErrors(validation.errors);
    setTouched(
      Object.keys(validationRules).reduce((acc, key) => {
        acc[key] = true;
        return acc;
      }, {})
    );
    
    setIsValid(validation.isValid);
    return validation.isValid;
  }, [values, validationRules]);

  // Reset form
  const reset = useCallback((newValues = initialValues) => {
    setValues(newValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
    setIsValid(false);
  }, [initialValues]);

  // Set field error manually
  const setError = useCallback((name, error) => {
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
    updateFormValidity();
  }, [updateFormValidity]);

  // Clear field error
  const clearError = useCallback((name) => {
    setErrors(prev => ({
      ...prev,
      [name]: null
    }));
    updateFormValidity();
  }, [updateFormValidity]);

  // Clear all errors
  const clearErrors = useCallback(() => {
    setErrors({});
    setIsValid(true);
  }, []);

  // Set multiple values
  const setValues = useCallback((newValues) => {
    setValues(prev => ({
      ...prev,
      ...newValues
    }));
    
    // Mark fields as touched
    const touchedFields = Object.keys(newValues).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    
    setTouched(prev => ({
      ...prev,
      ...touchedFields
    }));
  }, []);

  // Get field props for input components
  const getFieldProps = useCallback((name) => ({
    name,
    value: values[name] || '',
    onChange: handleChange,
    onBlur: handleBlur,
    error: touched[name] ? errors[name] : null,
    hasError: touched[name] && errors[name] !== null
  }), [values, handleChange, handleBlur, errors, touched]);

  // Handle form submission
  const handleSubmit = useCallback((onSubmit) => {
    return async (event) => {
      event.preventDefault();
      
      setIsSubmitting(true);
      
      // Validate form before submission
      const isValid = validate();
      
      if (isValid) {
        try {
          await onSubmit(values);
        } catch (error) {
          console.error('Form submission error:', error);
        }
      }
      
      setIsSubmitting(false);
    };
  }, [values, validate]);

  // Check if field has been touched and has error
  const hasFieldError = useCallback((name) => {
    return touched[name] && errors[name] !== null;
  }, [touched, errors]);

  // Check if field is required
  const isFieldRequired = useCallback((name) => {
    return validationRules[name] && validationRules[name].some(rule => 
      rule.name === 'required' || rule.toString().includes('required')
    );
  }, [validationRules]);

  return {
    // Values and state
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    
    // Actions
    setValue,
    setValues,
    setError,
    clearError,
    clearErrors,
    reset,
    validate,
    
    // Event handlers
    handleChange,
    handleBlur,
    handleSubmit,
    
    // Utilities
    getFieldProps,
    hasFieldError,
    isFieldRequired,
    
    // Form ref
    formRef
  };
};

// Hook for file upload forms
export const useFileUpload = (options = {}) => {
  const {
    maxSize = 16 * 1024 * 1024, // 16MB
    allowedTypes = ['.pdf', '.docx', '.txt'],
    onFileSelect = null,
    onError = null
  } = options;

  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const validateFile = useCallback((file) => {
    const errors = [];
    
    if (!file) {
      errors.push('Please select a file');
      return { isValid: false, errors };
    }
    
    // Check file size
    if (file.size > maxSize) {
      errors.push(`File size must be less than ${maxSize / (1024 * 1024)}MB`);
    }
    
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      errors.push(`File type not supported. Allowed types: ${allowedTypes.join(', ')}`);
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }, [maxSize, allowedTypes]);

  const handleFileSelect = useCallback((selectedFile) => {
    const validation = validateFile(selectedFile);
    
    if (validation.isValid) {
      setFile(selectedFile);
      setError(null);
      onFileSelect?.(selectedFile);
    } else {
      setError(validation.errors[0]);
      setFile(null);
      onError?.(validation.errors[0]);
    }
  }, [validateFile, onFileSelect, onError]);

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const clearFile = useCallback(() => {
    setFile(null);
    setError(null);
  }, []);

  return {
    file,
    error,
    isDragOver,
    handleFileSelect,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    clearFile,
    validateFile
  };
};

export default useForm;
