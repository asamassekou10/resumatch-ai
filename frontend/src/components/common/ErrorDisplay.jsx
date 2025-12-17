import React from 'react';
import { AlertTriangle, RefreshCw, WifiOff, Lock, Server, Clock, HelpCircle } from 'lucide-react';

/**
 * User-friendly error display component with helpful messages and actions
 */

// Map error codes/types to user-friendly messages
const getErrorInfo = (error, errorType) => {
  // Network errors
  if (error?.message?.includes('Network') || error?.code === 'ERR_NETWORK' || errorType === 'NETWORK_ERROR') {
    return {
      icon: WifiOff,
      title: 'Connection Problem',
      message: "We couldn't connect to our servers. Please check your internet connection and try again.",
      color: 'amber',
      action: 'retry'
    };
  }

  // Timeout errors
  if (error?.code === 'ECONNABORTED' || errorType === 'TIMEOUT') {
    return {
      icon: Clock,
      title: 'Request Timed Out',
      message: "The request took too long to complete. This might be due to a slow connection. Please try again.",
      color: 'amber',
      action: 'retry'
    };
  }

  // Authentication errors
  if (error?.response?.status === 401 || errorType === 'UNAUTHORIZED') {
    return {
      icon: Lock,
      title: 'Session Expired',
      message: "Your session has expired. Please log in again to continue.",
      color: 'amber',
      action: 'login'
    };
  }

  // Forbidden errors
  if (error?.response?.status === 403 || errorType === 'FORBIDDEN') {
    return {
      icon: Lock,
      title: 'Access Denied',
      message: "You don't have permission to access this feature. Please upgrade your plan or contact support.",
      color: 'red',
      action: 'upgrade'
    };
  }

  // Not found errors
  if (error?.response?.status === 404 || errorType === 'NOT_FOUND') {
    return {
      icon: HelpCircle,
      title: 'Not Found',
      message: "We couldn't find what you're looking for. It may have been moved or deleted.",
      color: 'slate',
      action: 'back'
    };
  }

  // Rate limit errors
  if (error?.response?.status === 429 || errorType === 'RATE_LIMITED') {
    return {
      icon: Clock,
      title: 'Too Many Requests',
      message: "You've made too many requests. Please wait a moment before trying again.",
      color: 'amber',
      action: 'wait'
    };
  }

  // Payment required
  if (error?.response?.status === 402 || errorType === 'PAYMENT_REQUIRED') {
    return {
      icon: Lock,
      title: 'Credits Required',
      message: "You've run out of credits. Upgrade your plan to continue using this feature.",
      color: 'purple',
      action: 'upgrade'
    };
  }

  // Server errors
  if (error?.response?.status >= 500 || errorType === 'INTERNAL_SERVER_ERROR') {
    return {
      icon: Server,
      title: 'Server Error',
      message: "Something went wrong on our end. Our team has been notified. Please try again later.",
      color: 'red',
      action: 'retry'
    };
  }

  // Validation errors
  if (error?.response?.status === 400 || errorType === 'VALIDATION_ERROR') {
    return {
      icon: AlertTriangle,
      title: 'Invalid Request',
      message: error?.response?.data?.error || "Please check your input and try again.",
      color: 'amber',
      action: 'fix'
    };
  }

  // Default error
  return {
    icon: AlertTriangle,
    title: 'Something Went Wrong',
    message: error?.message || "An unexpected error occurred. Please try again.",
    color: 'red',
    action: 'retry'
  };
};

// Color variants
const colorClasses = {
  red: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    icon: 'text-red-400',
    title: 'text-red-300',
    button: 'bg-red-500 hover:bg-red-600'
  },
  amber: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    icon: 'text-amber-400',
    title: 'text-amber-300',
    button: 'bg-amber-500 hover:bg-amber-600'
  },
  purple: {
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
    icon: 'text-purple-400',
    title: 'text-purple-300',
    button: 'bg-purple-500 hover:bg-purple-600'
  },
  slate: {
    bg: 'bg-slate-500/10',
    border: 'border-slate-500/30',
    icon: 'text-slate-400',
    title: 'text-slate-300',
    button: 'bg-slate-600 hover:bg-slate-500'
  }
};

const ErrorDisplay = ({
  error,
  errorType,
  onRetry,
  onLogin,
  onUpgrade,
  onBack,
  compact = false,
  className = ''
}) => {
  const errorInfo = getErrorInfo(error, errorType);
  const Icon = errorInfo.icon;
  const colors = colorClasses[errorInfo.color] || colorClasses.red;

  // Determine which action button to show
  const renderAction = () => {
    switch (errorInfo.action) {
      case 'retry':
        return onRetry && (
          <button
            onClick={onRetry}
            className={`flex items-center gap-2 px-4 py-2 ${colors.button} text-white font-medium rounded-lg transition-colors`}
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        );
      case 'login':
        return onLogin && (
          <button
            onClick={onLogin}
            className={`flex items-center gap-2 px-4 py-2 ${colors.button} text-white font-medium rounded-lg transition-colors`}
          >
            <Lock className="w-4 h-4" />
            Log In Again
          </button>
        );
      case 'upgrade':
        return onUpgrade && (
          <button
            onClick={onUpgrade}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-medium rounded-lg transition-opacity hover:opacity-90"
          >
            Upgrade Plan
          </button>
        );
      case 'back':
        return onBack && (
          <button
            onClick={onBack}
            className={`flex items-center gap-2 px-4 py-2 ${colors.button} text-white font-medium rounded-lg transition-colors`}
          >
            Go Back
          </button>
        );
      case 'wait':
        return (
          <p className="text-sm text-slate-400">
            Please wait a few minutes before trying again.
          </p>
        );
      default:
        return onRetry && (
          <button
            onClick={onRetry}
            className={`flex items-center gap-2 px-4 py-2 ${colors.button} text-white font-medium rounded-lg transition-colors`}
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        );
    }
  };

  if (compact) {
    return (
      <div className={`flex items-center gap-3 p-3 ${colors.bg} border ${colors.border} rounded-lg ${className}`}>
        <Icon className={`w-5 h-5 ${colors.icon} flex-shrink-0`} />
        <p className="text-sm text-slate-300 flex-1">{errorInfo.message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
            title="Retry"
          >
            <RefreshCw className="w-4 h-4 text-slate-400" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`${colors.bg} border ${colors.border} rounded-xl p-6 ${className}`}>
      <div className="flex flex-col items-center text-center">
        {/* Icon */}
        <div className={`w-12 h-12 rounded-full ${colors.bg} flex items-center justify-center mb-4`}>
          <Icon className={`w-6 h-6 ${colors.icon}`} />
        </div>

        {/* Title */}
        <h3 className={`text-lg font-semibold ${colors.title} mb-2`}>
          {errorInfo.title}
        </h3>

        {/* Message */}
        <p className="text-slate-400 mb-6 max-w-md">
          {errorInfo.message}
        </p>

        {/* Action */}
        {renderAction()}
      </div>
    </div>
  );
};

// Inline error for form fields
export const InlineError = ({ message }) => {
  if (!message) return null;

  return (
    <div className="flex items-center gap-2 mt-1 text-red-400 text-sm">
      <AlertTriangle className="w-3.5 h-3.5" />
      <span>{message}</span>
    </div>
  );
};

// Toast-style error notification
export const ErrorToast = ({ message, onClose }) => (
  <div className="fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 bg-red-500/90 backdrop-blur-sm text-white rounded-lg shadow-lg animate-slide-up">
    <AlertTriangle className="w-5 h-5 flex-shrink-0" />
    <p className="text-sm font-medium">{message}</p>
    {onClose && (
      <button
        onClick={onClose}
        className="ml-2 p-1 hover:bg-white/20 rounded transition-colors"
      >
        <span className="sr-only">Close</span>
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    )}
  </div>
);

export default ErrorDisplay;
