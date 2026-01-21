/**
 * Resume Guides Index Page (Hub Page)
 *
 * Central hub for all job role resume guides.
 * Features:
 * - Industry-organized role listings
 * - Search/filter functionality
 * - SEO-optimized with ItemList schema
 * - Internal linking to all spokes
 */

import { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Search,
  Briefcase,
  ArrowRight,
  Sparkles,
  Code,
  Heart,
  DollarSign,
  Users,
  Palette,
  BookOpen,
  Wrench,
  TrendingUp
} from 'lucide-react';
import SEO from '../common/SEO';
import ShimmerButton from '../ui/ShimmerButton';
import SpotlightCard from '../ui/SpotlightCard';
import { JOB_ROLES } from '../../utils/jobRoles';
import { ROUTES } from '../../config/routes';
import {
  generateBreadcrumbSchema,
  generateItemListSchema
} from '../../utils/structuredData';
import { INDUSTRY_HUBS } from '../../utils/seoContentGenerator';

// Icon mapping for industries
const industryIcons = {
  technology: Code,
  healthcare: Heart,
  finance: DollarSign,
  business: Briefcase,
  'sales-marketing': TrendingUp,
  creative: Palette,
  education: BookOpen,
  'skilled-trades': Wrench,
  services: Users
};

const ResumeGuidesIndex = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('all');

  // Filter roles based on search and industry
  const filteredRoles = useMemo(() => {
    return JOB_ROLES.filter(role => {
      const matchesSearch = searchQuery === '' ||
        role.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        role.industry.toLowerCase().includes(searchQuery.toLowerCase()) ||
        role.keywords.some(k => k.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesIndustry = selectedIndustry === 'all' ||
        Object.entries(INDUSTRY_HUBS).some(([key, hub]) =>
          key === selectedIndustry && hub.roles.includes(role.slug)
        );

      return matchesSearch && matchesIndustry;
    });
  }, [searchQuery, selectedIndustry]);

  // Group roles by industry for display
  const rolesByIndustry = useMemo(() => {
    const groups = {};

    Object.entries(INDUSTRY_HUBS).forEach(([key, hub]) => {
      groups[key] = {
        ...hub,
        roles: filteredRoles.filter(role => hub.roles.includes(role.slug))
      };
    });

    return groups;
  }, [filteredRoles]);

  // Generate structured data
  const structuredData = useMemo(() => {
    const breadcrumbs = [
      { name: 'Home', url: 'https://www.resumeanalyzerai.com' },
      { name: 'Resume Guides', url: 'https://www.resumeanalyzerai.com/resume-for' }
    ];

    const items = JOB_ROLES.map(role => ({
      name: `${role.name} Resume Guide`,
      url: `https://www.resumeanalyzerai.com/resume-for/${role.slug}`
    }));

    return [
      generateBreadcrumbSchema(breadcrumbs),
      generateItemListSchema(items, 'Resume Writing Guides by Job Role')
    ];
  }, []);

  return (
    <>
      <SEO
        title="Resume Guides by Job Role | Expert Tips for Every Career"
        description="Browse our comprehensive collection of resume guides for every job role. Get industry-specific keywords, skills, and expert tips to land your dream job."
        keywords="resume guides, resume tips, job-specific resume, career resume, ATS optimization, resume templates"
        url="https://www.resumeanalyzerai.com/resume-for"
        structuredData={structuredData}
      />

      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <motion.header
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6 font-display">
              Resume Guides for{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-blue-500 to-pink-500">
                Every Career
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto mb-8">
              Industry-specific resume guides with keywords, skills, and expert tips
              to help you land your dream job. Each guide includes ATS optimization strategies.
            </p>

            <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
              <Sparkles className="w-4 h-4 mr-2" />
              Analyze Your Resume Free
            </ShimmerButton>
          </motion.header>

          {/* Search and Filter */}
          <div className="mb-12">
            <div className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto">
              {/* Search Input */}
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search job roles, industries, or keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 transition-colors"
                />
              </div>

              {/* Industry Filter */}
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-blue-500/50 transition-colors cursor-pointer"
              >
                <option value="all">All Industries</option>
                {Object.entries(INDUSTRY_HUBS).map(([key, hub]) => (
                  <option key={key} value={key}>
                    {hub.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-8 text-center">
            <p className="text-gray-400">
              Showing <span className="text-white font-semibold">{filteredRoles.length}</span> resume guides
              {selectedIndustry !== 'all' && (
                <> in <span className="text-blue-400">{INDUSTRY_HUBS[selectedIndustry]?.name}</span></>
              )}
            </p>
          </div>

          {/* Role Listings by Industry */}
          {selectedIndustry === 'all' ? (
            // Show all industries grouped
            <div className="space-y-12">
              {Object.entries(rolesByIndustry).map(([key, industry]) => {
                if (industry.roles.length === 0) return null;

                const IconComponent = industryIcons[key] || Briefcase;

                return (
                  <section key={key}>
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-blue-500/10 rounded-lg">
                        <IconComponent className="w-6 h-6 text-blue-400" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-white font-display">
                          {industry.name}
                        </h2>
                        <p className="text-sm text-gray-400">
                          {industry.roles.length} resume guides
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {industry.roles.map((role) => (
                        <RoleCard key={role.slug} role={role} />
                      ))}
                    </div>
                  </section>
                );
              })}
            </div>
          ) : (
            // Show filtered results in a grid
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredRoles.map((role) => (
                <RoleCard key={role.slug} role={role} />
              ))}
            </div>
          )}

          {/* No Results */}
          {filteredRoles.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-400 mb-4">
                No resume guides found matching your search.
              </p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedIndustry('all');
                }}
                className="text-blue-400 hover:text-blue-300 transition-colors"
              >
                Clear filters
              </button>
            </div>
          )}

          {/* Bottom CTA */}
          <SpotlightCard className="rounded-xl p-8 mt-16 bg-gradient-to-r from-blue-500/10 to-blue-600/10 border border-blue-500/20">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white mb-4 font-display">
                Don't See Your Role?
              </h2>
              <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
                Our AI resume analyzer works for any job role. Upload your resume
                and get personalized feedback based on your target position.
              </p>
              <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
                Try Free Resume Analysis <ArrowRight size={16} />
              </ShimmerButton>
            </div>
          </SpotlightCard>
        </div>
      </div>
    </>
  );
};

/**
 * Individual Role Card Component
 */
const RoleCard = ({ role }) => {
  return (
    <Link to={`/resume-for/${role.slug}`} className="group">
      <SpotlightCard className="rounded-xl p-5 h-full hover:border-blue-500/50 transition-all">
        <div className="flex flex-col h-full">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors font-display">
              {role.name}
            </h3>
            <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all flex-shrink-0" />
          </div>

          <p className="text-sm text-gray-400 mb-3 line-clamp-2 flex-1">
            {role.description}
          </p>

          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className="px-2 py-1 bg-white/5 rounded-full">
              {role.industry}
            </span>
            <span>{role.keywords.length} keywords</span>
          </div>
        </div>
      </SpotlightCard>
    </Link>
  );
};

export default ResumeGuidesIndex;
