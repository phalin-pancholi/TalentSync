import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Users, Briefcase, Home, ChevronRight } from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();

  const getBreadcrumbs = () => {
    const path = location.pathname;
    const segments = path.split('/').filter(Boolean);
    
    if (path === '/') return [{ label: 'Home', path: '/' }];
    
    const breadcrumbs = [{ label: 'Home', path: '/' }];
    
    if (segments[0] === 'jobs' && segments[1]) {
      breadcrumbs.push({ label: 'Job Details', path: `/jobs/${segments[1]}` });
      
      if (segments[2] === 'candidates') {
        breadcrumbs.push({ label: 'Candidates', path: `/jobs/${segments[1]}/candidates` });
      }
    }
    
    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-teal-500 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-slate-800">TalentSync</h1>
              </div>
            </div>
            
            <nav className="flex items-center space-x-6">
              <Link 
                to="/" 
                className="flex items-center space-x-2 text-slate-600 hover:text-blue-600 transition-colors duration-200"
              >
                <Home className="w-4 h-4" />
                <span className="font-medium">Jobs</span>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Breadcrumbs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <nav className="flex items-center space-x-2 text-sm">
          {breadcrumbs.map((breadcrumb, index) => (
            <div key={breadcrumb.path} className="flex items-center space-x-2">
              {index > 0 && <ChevronRight className="w-4 h-4 text-slate-400" />}
              {index === breadcrumbs.length - 1 ? (
                <span className="text-slate-500 font-medium">{breadcrumb.label}</span>
              ) : (
                <Link 
                  to={breadcrumb.path}
                  className="text-blue-600 hover:text-blue-800 transition-colors duration-200 font-medium"
                >
                  {breadcrumb.label}
                </Link>
              )}
            </div>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {children}
      </main>
    </div>
  );
};

export default Layout;