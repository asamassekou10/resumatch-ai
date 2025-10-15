import React from 'react';

const Breadcrumb = ({ view, setView, token, currentAnalysis = null }) => {
  const getBreadcrumbItems = () => {
    const items = [];
    
    // Always start with Home
    items.push({
      label: 'Home',
      onClick: () => setView(token ? 'dashboard' : 'landing'),
      active: false
    });

    if (token) {
      // User is authenticated
      switch (view) {
        case 'dashboard':
          items.push({ label: 'Dashboard', active: true });
          break;
        case 'analyze':
          items.push(
            { label: 'Dashboard', onClick: () => setView('dashboard'), active: false },
            { label: 'New Analysis', active: true }
          );
          break;
        case 'result':
          items.push(
            { label: 'Dashboard', onClick: () => setView('dashboard'), active: false },
            { 
              label: currentAnalysis?.job_title || 'Analysis Results', 
              active: true 
            }
          );
          break;
        default:
          break;
      }
    } else {
      // User is not authenticated
      switch (view) {
        case 'login':
          items.push({ label: 'Login', active: true });
          break;
        case 'register':
          items.push({ label: 'Register', active: true });
          break;
        default:
          items.push({ label: 'Landing', active: true });
          break;
      }
    }

    return items;
  };

  const items = getBreadcrumbItems();

  if (items.length <= 1) return null;

  return (
    <nav className="flex items-center space-x-2 text-sm text-slate-400 mb-6">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          {item.active ? (
            <span className="text-slate-300 font-medium">{item.label}</span>
          ) : (
            <button
              onClick={item.onClick}
              className="text-slate-400 hover:text-cyan-400 transition-colors"
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
