import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight, FileText, TrendingUp, AlertCircle } from 'lucide-react';
import SEO from '../common/SEO';
import ShimmerButton from '../ui/ShimmerButton';
import SpotlightCard from '../ui/SpotlightCard';
import { getJobRoleBySlug } from '../../utils/jobRoles';
import { ROUTES } from '../../config/routes';
import { generateJobPostingSchema } from '../../utils/structuredData';

const JobRoleLandingPage = () => {
  const { roleSlug } = useParams();
  const navigate = useNavigate();
  const jobRole = getJobRoleBySlug(roleSlug);

  // Redirect to 404 or homepage if role not found
  useEffect(() => {
    if (!jobRole) {
      navigate(ROUTES.LANDING, { replace: true });
    }
  }, [jobRole, navigate]);

  if (!jobRole) {
    return null;
  }

  // Generate structured data for this role
  const jobPostingSchema = generateJobPostingSchema({
    title: jobRole.name,
    description: jobRole.description,
    skills: jobRole.skills,
    industry: jobRole.industry,
  });

  const seoMetadata = {
    title: `Resume for ${jobRole.name}`,
    description: `${jobRole.description} Get expert tips, common mistakes to avoid, and optimize your ${jobRole.name.toLowerCase()} resume with AI-powered analysis.`,
    keywords: `${jobRole.name.toLowerCase()} resume, ${jobRole.industry.toLowerCase()} resume, ${jobRole.keywords.join(', ')}`,
    url: `https://resumeanalyzerai.com/resume-for/${jobRole.slug}`,
  };

  return (
    <>
      <SEO
        title={seoMetadata.title}
        description={seoMetadata.description}
        keywords={seoMetadata.keywords}
        url={seoMetadata.url}
        structuredData={[jobPostingSchema]}
      />
      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background atmosphere */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4 font-display">
              Create a Winning Resume for{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500">
                {jobRole.name}
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto mb-8">
              {jobRole.description}
            </p>
            <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
              Analyze Your {jobRole.name} Resume <ArrowRight size={16} />
            </ShimmerButton>
          </motion.div>

          {/* Key Information Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {/* Industry Keywords */}
            <SpotlightCard className="rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-bold text-white font-display">Key Keywords to Include</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {jobRole.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-sm text-purple-300"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </SpotlightCard>

            {/* Essential Skills */}
            <SpotlightCard className="rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle className="w-6 h-6 text-green-400" />
                <h2 className="text-xl font-bold text-white font-display">Essential Skills</h2>
              </div>
              <ul className="space-y-2">
                {jobRole.skills.map((skill, index) => (
                  <li key={index} className="flex items-center gap-2 text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>{skill}</span>
                  </li>
                ))}
              </ul>
            </SpotlightCard>
          </div>

          {/* Resume Tips */}
          <SpotlightCard className="rounded-xl p-8 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <FileText className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-bold text-white font-display">Resume Tips for {jobRole.name}</h2>
            </div>
            <ul className="space-y-4">
              {jobRole.tips.map((tip, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3 text-gray-300"
                >
                  <CheckCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                  <span>{tip}</span>
                </motion.li>
              ))}
            </ul>
          </SpotlightCard>

          {/* Common Mistakes */}
          <SpotlightCard className="rounded-xl p-8 mb-8 bg-red-900/10 border border-red-500/20">
            <div className="flex items-center gap-3 mb-6">
              <AlertCircle className="w-6 h-6 text-red-400" />
              <h2 className="text-2xl font-bold text-white font-display">Common Mistakes to Avoid</h2>
            </div>
            <ul className="space-y-4">
              {jobRole.commonMistakes.map((mistake, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3 text-gray-300"
                >
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <span>{mistake}</span>
                </motion.li>
              ))}
            </ul>
          </SpotlightCard>

          {/* CTA Section */}
          <SpotlightCard className="rounded-xl p-8 bg-gradient-to-r from-purple-500/10 to-blue-600/10 border border-purple-500/20">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white mb-4 font-display">
                Ready to Optimize Your {jobRole.name} Resume?
              </h2>
              <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
                Get instant AI-powered feedback on your resume. Our advanced analysis will help you highlight the right keywords, skills, and achievements for {jobRole.name} positions.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
                  Analyze Your Resume Free <ArrowRight size={16} />
                </ShimmerButton>
                <button
                  onClick={() => navigate(ROUTES.PRICING)}
                  className="px-8 py-3 rounded-full font-bold text-sm text-gray-300 border border-white/10 hover:bg-white/5 hover:text-white transition-all"
                >
                  View Pricing
                </button>
              </div>
            </div>
          </SpotlightCard>
        </div>
      </div>
    </>
  );
};

export default JobRoleLandingPage;

