import { motion } from 'framer-motion';
import { GraduationCap, BookOpen, FileText, CheckCircle, ArrowRight, Users, Award, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import SEO from '../common/SEO';
import ShimmerButton from '../ui/ShimmerButton';
import SpotlightCard from '../ui/SpotlightCard';
import Footer from '../ui/Footer';
import { ROUTES } from '../../config/routes';

const StudentResources = () => {
  const navigate = useNavigate();

  const resources = [
    {
      icon: <FileText className="w-6 h-6" />,
      title: 'Free Resume Analysis',
      description: 'Get instant AI-powered feedback on your resume. Perfect for students creating their first professional resume.',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: 'Resume Templates',
      description: 'Download professional resume templates designed specifically for students and recent graduates.',
      color: 'from-blue-500 to-pink-500',
    },
    {
      icon: <CheckCircle className="w-6 h-6" />,
      title: 'ATS Optimization Guide',
      description: 'Learn how to optimize your resume for Applicant Tracking Systems used by most employers.',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: <Award className="w-6 h-6" />,
      title: 'Career Advice Blog',
      description: 'Read expert tips on job searching, networking, and building your career as a student.',
      color: 'from-yellow-500 to-orange-500',
    },
  ];

  const benefits = [
    'Free tier with 5 resume analysis credits',
    'No credit card required',
    'Student-friendly pricing for Pro and Elite plans',
    'Industry-specific resume tips',
    'ATS optimization for better job applications',
    'Access to job matching and career insights',
  ];

  return (
    <>
      <SEO
        title="Student Resources - Free Resume Tools for Students"
        description="Free resume analysis tools and resources for students and recent graduates. Get AI-powered resume feedback, templates, and career advice to land your first job."
        keywords="student resume, free resume analysis, student resources, college resume, graduate resume, entry level resume"
        url="https://resumeanalyzerai.com/resources/for-students"
      />
      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background atmosphere */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
        <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 py-12">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 border border-blue-500/30 rounded-full mb-6">
              <GraduationCap className="w-5 h-5 text-blue-400" />
              <span className="text-sm text-blue-300 font-medium">For Students & Recent Graduates</span>
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6 font-display">
              Free Resume Resources for{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-blue-500 to-pink-500">
                Students
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto mb-8">
              Get professional resume help without breaking the bank. Our free tools and resources are designed specifically for students and recent graduates entering the job market.
            </p>
            <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
              Analyze Your Resume Free <ArrowRight size={16} />
            </ShimmerButton>
          </motion.div>

          {/* Resources Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {resources.map((resource, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <SpotlightCard className="rounded-xl p-6 h-full">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${resource.color} flex items-center justify-center text-white mb-4`}>
                    {resource.icon}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2 font-display">
                    {resource.title}
                  </h3>
                  <p className="text-gray-400">
                    {resource.description}
                  </p>
                </SpotlightCard>
              </motion.div>
            ))}
          </div>

          {/* Benefits Section */}
          <SpotlightCard className="rounded-xl p-8 mb-12 bg-gradient-to-r from-blue-500/10 to-blue-600/10 border border-blue-500/20">
            <div className="flex items-center gap-3 mb-6">
              <Users className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-bold text-white font-display">Why Students Love ResumeAnalyzer AI</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-300">{benefit}</span>
                </div>
              ))}
            </div>
          </SpotlightCard>

          {/* CTA Section */}
          <SpotlightCard className="rounded-xl p-8 bg-gradient-to-r from-blue-500/10 to-blue-600/10 border border-blue-500/20 text-center">
            <Zap className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-4 font-display">
              Ready to Create Your Professional Resume?
            </h2>
            <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
              Join thousands of students who have used our free tools to create resumes that get interviews. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
                Start Free Analysis <ArrowRight size={16} />
              </ShimmerButton>
              <button
                onClick={() => navigate(ROUTES.PRICING)}
                className="px-8 py-3 rounded-full font-bold text-sm text-gray-300 border border-white/10 hover:bg-white/5 hover:text-white transition-all"
              >
                View Student Pricing
              </button>
            </div>
          </SpotlightCard>
        </div>
        <Footer />
      </div>
    </>
  );
};

export default StudentResources;


