import React from 'react';

// Input field component
export const InputField = ({
  label,
  type = 'text',
  name,
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  hasError,
  required = false,
  disabled = false,
  className = '',
  ...props
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-slate-300">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full px-4 py-3 bg-slate-700/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition ${
          hasError 
            ? 'border-red-500 focus:ring-red-500' 
            : 'border-slate-600 hover:border-slate-500'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        {...props}
      />
      
      {hasError && (
        <p className="text-red-400 text-sm">{error}</p>
      )}
    </div>
  );
};

// Textarea field component
export const TextareaField = ({
  label,
  name,
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  hasError,
  required = false,
  disabled = false,
  rows = 4,
  className = '',
  ...props
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-slate-300">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        rows={rows}
        className={`w-full px-4 py-3 bg-slate-700/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition resize-none ${
          hasError 
            ? 'border-red-500 focus:ring-red-500' 
            : 'border-slate-600 hover:border-slate-500'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        {...props}
      />
      
      {hasError && (
        <p className="text-red-400 text-sm">{error}</p>
      )}
    </div>
  );
};

// File upload field component
export const FileUploadField = ({
  label,
  name,
  onChange,
  error,
  hasError,
  required = false,
  disabled = false,
  accept,
  className = '',
  ...props
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-slate-300">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <input
          type="file"
          id={name}
          name={name}
          onChange={onChange}
          disabled={disabled}
          accept={accept}
          className="hidden"
          {...props}
        />
        
        <label
          htmlFor={name}
          className={`block w-full px-4 py-3 bg-slate-700/50 border rounded-lg cursor-pointer transition ${
            hasError 
              ? 'border-red-500' 
              : 'border-slate-600 hover:border-slate-500'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <span className="text-white">Choose file</span>
        </label>
      </div>
      
      {hasError && (
        <p className="text-red-400 text-sm">{error}</p>
      )}
    </div>
  );
};

// Drag and drop file upload component
export const DragDropUpload = ({
  label,
  onFileSelect,
  error,
  hasError,
  required = false,
  disabled = false,
  accept,
  maxSize = 16 * 1024 * 1024,
  className = '',
  children
}) => {
  const [isDragOver, setIsDragOver] = React.useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (disabled) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <div className="block text-sm font-medium text-slate-300">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </div>
      )}
      
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition ${
          isDragOver 
            ? 'border-cyan-400 bg-slate-800/70' 
            : hasError 
              ? 'border-red-500' 
              : 'border-slate-600 hover:border-slate-500'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <input
          type="file"
          onChange={handleFileInput}
          disabled={disabled}
          accept={accept}
          className="hidden"
        />
        
        {children || (
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Drag & Drop Your File Here
              </h3>
              <p className="text-slate-400 mb-2">or click to browse files</p>
              <p className="text-sm text-slate-500">
                Supports PDF, DOCX, TXT files (Max {maxSize / (1024 * 1024)}MB)
              </p>
            </div>
          </div>
        )}
      </div>
      
      {hasError && (
        <p className="text-red-400 text-sm">{error}</p>
      )}
    </div>
  );
};

// Select field component
export const SelectField = ({
  label,
  name,
  value,
  onChange,
  onBlur,
  error,
  hasError,
  required = false,
  disabled = false,
  options = [],
  placeholder = 'Select an option',
  className = '',
  ...props
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-slate-300">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      
      <select
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        disabled={disabled}
        className={`w-full px-4 py-3 bg-slate-700/50 border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition ${
          hasError 
            ? 'border-red-500 focus:ring-red-500' 
            : 'border-slate-600 hover:border-slate-500'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        {...props}
      >
        <option value="" disabled>
          {placeholder}
        </option>
        {options.map((option) => (
          <option key={option.value} value={option.value} className="bg-slate-700">
            {option.label}
          </option>
        ))}
      </select>
      
      {hasError && (
        <p className="text-red-400 text-sm">{error}</p>
      )}
    </div>
  );
};

// Checkbox field component
export const CheckboxField = ({
  label,
  name,
  checked,
  onChange,
  onBlur,
  error,
  hasError,
  required = false,
  disabled = false,
  className = '',
  ...props
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          id={name}
          name={name}
          checked={checked}
          onChange={onChange}
          onBlur={onBlur}
          disabled={disabled}
          className={`w-4 h-4 text-cyan-600 bg-slate-700 border-slate-600 rounded focus:ring-cyan-500 focus:ring-2 ${
            hasError ? 'border-red-500' : ''
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          {...props}
        />
        
        {label && (
          <label htmlFor={name} className="text-sm font-medium text-slate-300">
            {label}
            {required && <span className="text-red-400 ml-1">*</span>}
          </label>
        )}
      </div>
      
      {hasError && (
        <p className="text-red-400 text-sm">{error}</p>
      )}
    </div>
  );
};

const formComponents = {
  InputField,
  TextareaField,
  FileUploadField,
  DragDropUpload,
  SelectField,
  CheckboxField
};

export default formComponents;
