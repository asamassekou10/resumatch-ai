import { RefreshCw } from 'lucide-react';

/**
 * LoadingSpinner Component
 *
 * Used as a Suspense fallback during lazy-loaded route transitions.
 * Provides visual feedback while code chunks are being loaded.
 *
 * Features:
 * - Centered full-screen display
 * - Animated spinner icon
 * - Consistent branding with app theme
 * - Accessible loading state
 *
 * @param {Object} props
 * @param {string} props.message - Optional loading message (default: "Loading...")
 * @param {boolean} props.fullScreen - Whether to show fullscreen (default: true)
 */
const LoadingSpinner = ({
  message = 'Loading...',
  fullScreen = true
}) => {
  const containerClasses = fullScreen
    ? 'min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900'
    : 'flex items-center justify-center p-8';

  return (
    <div className={containerClasses}>
      <div className="text-center">
        {/* Animated Spinner Icon */}
        <div className="flex justify-center mb-4">
          <RefreshCw
            className="w-12 h-12 text-cyan-400 animate-spin"
            aria-hidden="true"
          />
        </div>

        {/* Loading Message */}
        <p
          className="text-slate-300 text-lg font-medium"
          role="status"
          aria-live="polite"
        >
          {message}
        </p>

        {/* Optional: Loading dots animation */}
        <div className="flex justify-center gap-1 mt-4">
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
