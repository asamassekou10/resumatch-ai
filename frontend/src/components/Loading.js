import React from 'react';

// Loading spinner component
export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  return (
    <div className={`animate-spin rounded-full border-b-2 border-cyan-500 ${sizeClasses[size]} ${className}`}></div>
  );
};

// Full page loading component
export const FullPageLoading = ({ message = 'Loading...' }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="text-center">
        <LoadingSpinner size="xl" className="mx-auto mb-4" />
        <p className="text-slate-300 text-lg">{message}</p>
      </div>
    </div>
  );
};

// Button loading component
export const LoadingButton = ({ 
  isLoading, 
  children, 
  loadingText = 'Loading...', 
  className = '',
  ...props 
}) => {
  return (
    <button
      className={`relative ${className}`}
      disabled={isLoading}
      {...props}
    >
      {isLoading && (
        <LoadingSpinner size="sm" className="absolute left-3 top-1/2 transform -translate-y-1/2" />
      )}
      <span className={isLoading ? 'ml-6' : ''}>
        {isLoading ? loadingText : children}
      </span>
    </button>
  );
};

// Card loading skeleton
export const LoadingSkeleton = ({ className = '' }) => {
  return (
    <div className={`animate-pulse bg-slate-800/50 rounded-lg ${className}`}>
      <div className="p-6">
        <div className="h-4 bg-slate-700 rounded mb-4"></div>
        <div className="h-4 bg-slate-700 rounded mb-2"></div>
        <div className="h-4 bg-slate-700 rounded w-3/4"></div>
      </div>
    </div>
  );
};

// Table loading skeleton
export const TableLoadingSkeleton = ({ rows = 5, columns = 4 }) => {
  return (
    <div className="animate-pulse">
      <div className="bg-slate-800/50 rounded-lg overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-600">
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: columns }).map((_, index) => (
              <div key={index} className="h-4 bg-slate-700 rounded"></div>
            ))}
          </div>
        </div>
        
        {/* Rows */}
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="px-6 py-4 border-b border-slate-600 last:border-b-0">
            <div className="grid grid-cols-4 gap-4">
              {Array.from({ length: columns }).map((_, colIndex) => (
                <div key={colIndex} className="h-4 bg-slate-700 rounded"></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Chart loading skeleton
export const ChartLoadingSkeleton = ({ height = '300px' }) => {
  return (
    <div className="animate-pulse bg-slate-800/50 rounded-lg p-6" style={{ height }}>
      <div className="h-6 bg-slate-700 rounded mb-4 w-1/3"></div>
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="flex items-center space-x-3">
            <div className="h-4 bg-slate-700 rounded w-1/4"></div>
            <div className="flex-1 h-4 bg-slate-700 rounded"></div>
            <div className="h-4 bg-slate-700 rounded w-16"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Inline loading component
export const InlineLoading = ({ message = 'Loading...' }) => {
  return (
    <div className="flex items-center justify-center py-8">
      <div className="flex items-center space-x-3">
        <LoadingSpinner size="sm" />
        <span className="text-slate-300">{message}</span>
      </div>
    </div>
  );
};

// Progress bar component
export const ProgressBar = ({ progress, className = '' }) => {
  return (
    <div className={`w-full bg-slate-700 rounded-full h-2 ${className}`}>
      <div
        className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      ></div>
    </div>
  );
};

// Loading overlay component
export const LoadingOverlay = ({ isLoading, children, message = 'Loading...' }) => {
  return (
    <div className="relative">
      {children}
      {isLoading && (
        <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center rounded-lg">
          <div className="text-center">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-slate-300">{message}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default {
  LoadingSpinner,
  FullPageLoading,
  LoadingButton,
  LoadingSkeleton,
  TableLoadingSkeleton,
  ChartLoadingSkeleton,
  InlineLoading,
  ProgressBar,
  LoadingOverlay
};
