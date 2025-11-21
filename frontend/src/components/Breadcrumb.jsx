import React from 'react';

const Breadcrumb = ({ view, setView, token, currentAnalysis }) => {
  const getBreadcrumbItems = () => {
    const items = [];
    
    if (token) {
      items.push({
        label: 'Dashboard',
        onClick: () => setView('dashboard'),
        active: view === 'dashboard'
      });
    }
    
    if (view === 'analyze') {
      items.push({
        label: 'Analyze Resume',
        active: true
      });
    }
    
    if (view === 'result' && currentAnalysis) {
      items.push({
        label: 'Analysis Results',
        active: true
      });
    }
    
    if (view === 'pricing') {
      items.push({
        label: 'Pricing',
        active: true
      });
    }
    
    return items;
  };

  const items = getBreadcrumbItems();
  
  if (items.length <= 1) return null;

  return (
    <nav className="flex items-center space-x-2 text-sm">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          {item.active ? (
            <span className="text-slate-300 font-medium">{item.label}</span>
          ) : (
            <button
              onClick={item.onClick}
              className="text-cyan-400 hover:text-cyan-300 transition font-medium"
            >
              {item.label}
            </button>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumb;
