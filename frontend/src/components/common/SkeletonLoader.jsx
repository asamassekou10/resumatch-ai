import React from 'react';

/**
 * Reusable skeleton loading components for better UX during data loading
 */

// Base skeleton with animation
const SkeletonBase = ({ className = '' }) => (
  <div className={`animate-pulse bg-slate-700/50 rounded ${className}`}></div>
);

// Text skeleton
export const SkeletonText = ({ width = 'w-full', height = 'h-4' }) => (
  <SkeletonBase className={`${width} ${height}`} />
);

// Paragraph skeleton (multiple lines)
export const SkeletonParagraph = ({ lines = 3 }) => (
  <div className="space-y-2">
    {Array.from({ length: lines }).map((_, i) => (
      <SkeletonText
        key={i}
        width={i === lines - 1 ? 'w-3/4' : 'w-full'}
      />
    ))}
  </div>
);

// Avatar/circle skeleton
export const SkeletonAvatar = ({ size = 'w-10 h-10' }) => (
  <SkeletonBase className={`${size} rounded-full`} />
);

// Card skeleton
export const SkeletonCard = ({ className = '' }) => (
  <div className={`bg-slate-800/50 border border-slate-700 rounded-xl p-6 ${className}`}>
    <div className="flex items-center space-x-4 mb-4">
      <SkeletonAvatar />
      <div className="flex-1 space-y-2">
        <SkeletonText width="w-1/3" />
        <SkeletonText width="w-1/2" height="h-3" />
      </div>
    </div>
    <SkeletonParagraph lines={2} />
  </div>
);

// Job match card skeleton
export const SkeletonJobCard = () => (
  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
    <div className="flex justify-between items-start mb-4">
      <div className="flex-1">
        <SkeletonText width="w-2/3" height="h-6" />
        <div className="mt-2">
          <SkeletonText width="w-1/2" height="h-4" />
        </div>
      </div>
      <SkeletonBase className="w-16 h-16 rounded-xl" />
    </div>
    <div className="flex flex-wrap gap-2 mb-4">
      <SkeletonBase className="w-20 h-6 rounded-full" />
      <SkeletonBase className="w-24 h-6 rounded-full" />
      <SkeletonBase className="w-16 h-6 rounded-full" />
    </div>
    <SkeletonParagraph lines={2} />
    <div className="flex gap-2 mt-4">
      <SkeletonBase className="flex-1 h-10 rounded-lg" />
      <SkeletonBase className="w-10 h-10 rounded-lg" />
    </div>
  </div>
);

// Analysis card skeleton
export const SkeletonAnalysisCard = () => (
  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
    <div className="flex justify-between items-start mb-4">
      <div className="flex-1">
        <SkeletonText width="w-3/4" height="h-6" />
        <div className="mt-2">
          <SkeletonText width="w-1/2" height="h-4" />
        </div>
      </div>
      <SkeletonBase className="w-20 h-20 rounded-full" />
    </div>
    <div className="space-y-3">
      <div className="flex justify-between">
        <SkeletonText width="w-24" height="h-4" />
        <SkeletonText width="w-16" height="h-4" />
      </div>
      <SkeletonBase className="w-full h-2 rounded-full" />
    </div>
  </div>
);

// Stats card skeleton
export const SkeletonStatsCard = () => (
  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
    <div className="flex items-center justify-between mb-4">
      <SkeletonBase className="w-10 h-10 rounded-lg" />
      <SkeletonText width="w-20" height="h-3" />
    </div>
    <SkeletonText width="w-1/2" height="h-8" />
    <div className="mt-2">
      <SkeletonText width="w-3/4" height="h-3" />
    </div>
  </div>
);

// Table row skeleton
export const SkeletonTableRow = ({ columns = 4 }) => (
  <tr className="border-b border-slate-700">
    {Array.from({ length: columns }).map((_, i) => (
      <td key={i} className="p-4">
        <SkeletonText width={i === 0 ? 'w-3/4' : 'w-1/2'} />
      </td>
    ))}
  </tr>
);

// Full page loading skeleton
export const SkeletonPage = ({ title = true }) => (
  <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
    <div className="max-w-7xl mx-auto">
      {title && (
        <div className="mb-8">
          <SkeletonText width="w-1/4" height="h-8" />
          <div className="mt-2">
            <SkeletonText width="w-1/2" height="h-4" />
          </div>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <SkeletonStatsCard />
        <SkeletonStatsCard />
        <SkeletonStatsCard />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  </div>
);

// Job matches loading skeleton
export const SkeletonJobMatches = () => (
  <div className="space-y-4">
    <div className="flex justify-between items-center mb-6">
      <SkeletonText width="w-32" height="h-6" />
      <SkeletonBase className="w-24 h-8 rounded-lg" />
    </div>
    <SkeletonJobCard />
    <SkeletonJobCard />
    <SkeletonJobCard />
  </div>
);

// Interview prep loading skeleton
export const SkeletonInterviewPrep = () => (
  <div className="space-y-6">
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      <SkeletonText width="w-1/3" height="h-6" />
      <div className="mt-4 space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="border border-slate-600 rounded-lg p-4">
            <SkeletonText width="w-3/4" height="h-5" />
            <div className="mt-3">
              <SkeletonParagraph lines={2} />
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Company intel loading skeleton
export const SkeletonCompanyIntel = () => (
  <div className="space-y-6">
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      <div className="flex items-center gap-4 mb-6">
        <SkeletonBase className="w-16 h-16 rounded-xl" />
        <div className="flex-1">
          <SkeletonText width="w-1/3" height="h-7" />
          <div className="mt-2 flex gap-2">
            <SkeletonBase className="w-20 h-5 rounded-full" />
            <SkeletonBase className="w-24 h-5 rounded-full" />
          </div>
        </div>
      </div>
      <SkeletonParagraph lines={4} />
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <SkeletonCard />
      <SkeletonCard />
    </div>
  </div>
);

// Default export for simple usage
export default SkeletonBase;
