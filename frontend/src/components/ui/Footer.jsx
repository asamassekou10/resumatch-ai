import React from 'react';
import { FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../../config/routes';

/**
 * Footer Component
 * 
 * Premium footer with navigation links and copyright
 * Matches the dark theme design system
 */
const Footer = () => {
  return (
    <footer className="bg-black border-t border-white/10 pt-20 pb-10 relative z-10">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center mb-12">
          <div className="flex items-center gap-2 mb-6 md:mb-0">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <FileText size={18} className="text-white" />
            </div>
            <span className="text-xl font-bold text-white font-display">ResumeAnalyzer AI</span>
          </div>
          <div className="flex gap-8 text-sm text-gray-400">
            <Link to={ROUTES.HELP_PRIVACY} className="hover:text-white transition-colors">
              Privacy Policy
            </Link>
            <Link to={ROUTES.HELP_TERMS} className="hover:text-white transition-colors">
              Terms of Service
            </Link>
            <Link to={ROUTES.HELP} className="hover:text-white transition-colors">
              Support
            </Link>
          </div>
        </div>
        <div className="text-center text-gray-600 text-sm">
          &copy; {new Date().getFullYear()} ResumeAnalyzer AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;

