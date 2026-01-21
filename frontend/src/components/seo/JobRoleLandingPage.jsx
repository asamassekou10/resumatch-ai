/**
 * Job Role Landing Page
 *
 * Programmatic SEO page for job role-specific resume guides.
 * Features:
 * - Unique, intent-matched content per role
 * - Full structured data (FAQ, HowTo, Breadcrumb, WebPage)
 * - Hub-and-spoke internal linking
 * - Breadcrumb navigation
 * - Dynamic FAQ section
 * - Optimized for Core Web Vitals
 */

import { useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  CheckCircle,
  ArrowRight,
  FileText,
  TrendingUp,
  AlertCircle,
  Target,
  Sparkles
} from 'lucide-react';
import SEO from '../common/SEO';
import ShimmerButton from '../ui/ShimmerButton';
import SpotlightCard from '../ui/SpotlightCard';
import PromotionBanner from '../ui/PromotionBanner';
import Breadcrumbs from './Breadcrumbs';
import FAQSection from './FAQSection';
import InternalLinks from './InternalLinks';
import { getJobRoleBySlug, JOB_ROLES } from '../../utils/jobRoles';
import { ROUTES } from '../../config/routes';
import {
  generateFAQSchema,
  generateHowToSchema,
  generateBreadcrumbSchema,
  generateWebPageSchema
} from '../../utils/structuredData';
import {
  generateRoleFAQs,
  generateMetaTitle,
  generateMetaDescription,
  generateBreadcrumbs,
  generateInternalLinks,
  generateIntroParagraph,
  generateHowToSteps,
  getIndustryHub
} from '../../utils/seoContentGenerator';

const JobRoleLandingPage = () => {
  const { roleSlug } = useParams();
  const navigate = useNavigate();
  const jobRole = getJobRoleBySlug(roleSlug);

  // Redirect if role not found
  useEffect(() => {
    if (!jobRole) {
      navigate(ROUTES.LANDING, { replace: true });
    }
  }, [jobRole, navigate]);

  // Memoize all SEO content generation to prevent recalculation
  const seoContent = useMemo(() => {
    if (!jobRole) return null;

    const faqs = generateRoleFAQs(jobRole);
    const breadcrumbs = generateBreadcrumbs(jobRole);
    const howToSteps = generateHowToSteps(jobRole);
    const internalLinks = generateInternalLinks(jobRole, JOB_ROLES, []);
    const industryHub = getIndustryHub(jobRole.slug);

    return {
      faqs,
      breadcrumbs,
      howToSteps,
      internalLinks,
      industryHub,
      introParagraph: generateIntroParagraph(jobRole)
    };
  }, [jobRole]);

  // Generate all structured data schemas
  const structuredData = useMemo(() => {
    if (!jobRole || !seoContent) return [];

    const pageUrl = `https://www.resumeanalyzerai.com/resume-for/${jobRole.slug}`;

    return [
      // FAQ Schema - Critical for rich snippets
      generateFAQSchema(seoContent.faqs),

      // HowTo Schema - Better than JobPosting for guides
      generateHowToSchema({
        name: `How to Write a ${jobRole.name} Resume`,
        description: `Complete guide to creating an ATS-optimized ${jobRole.name} resume with keywords, skills, and expert tips.`,
        role: jobRole.name,
        slug: jobRole.slug,
        steps: seoContent.howToSteps
      }),

      // Breadcrumb Schema
      generateBreadcrumbSchema(seoContent.breadcrumbs),

      // WebPage Schema
      generateWebPageSchema({
        name: `${jobRole.name} Resume Guide`,
        description: generateMetaDescription(jobRole),
        url: pageUrl,
        about: `${jobRole.name} Resume Writing`,
        datePublished: '2026-01-01',
        dateModified: new Date().toISOString().split('T')[0]
      })
    ];
  }, [jobRole, seoContent]);

  if (!jobRole || !seoContent) {
    return null;
  }

  const seoMetadata = {
    title: generateMetaTitle(jobRole, 'primary'),
    description: generateMetaDescription(jobRole),
    keywords: `${jobRole.name.toLowerCase()} resume, ${jobRole.industry.toLowerCase()} resume, ${jobRole.keywords.join(', ').toLowerCase()}, resume tips, ATS optimization`,
    url: `https://www.resumeanalyzerai.com/resume-for/${jobRole.slug}`
  };

  return (
    <>
      <SEO
        title={seoMetadata.title}
        description={seoMetadata.description}
        keywords={seoMetadata.keywords}
        url={seoMetadata.url}
        structuredData={structuredData}
      />

      <div className="min-h-screen bg-black relative overflow-hidden">
        {/* Background atmosphere */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
        <div
          className="absolute inset-0 z-0 pointer-events-none"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)',
            backgroundSize: '50px 50px'
          }}
        />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          {/* Breadcrumbs */}
          <Breadcrumbs items={seoContent.breadcrumbs} />

          {/* Hero Section */}
          <motion.header
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            {/* Industry Badge */}
            {seoContent.industryHub && (
              <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-full text-sm text-blue-300 mb-6">
                <Target className="w-4 h-4" />
                {seoContent.industryHub.name} Industry
              </span>
            )}

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6 font-display">
              How to Write a{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-blue-500 to-pink-500">
                {jobRole.name}
              </span>{' '}
              Resume
            </h1>

            <p className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto mb-8">
              {jobRole.description}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <ShimmerButton onClick={() => navigate(ROUTES.GUEST_ANALYZE)}>
                <Sparkles className="w-4 h-4 mr-2" />
                Analyze Your {jobRole.name} Resume Free
              </ShimmerButton>
              <button
                onClick={() => {
                  const faqSection = document.getElementById('faq-section');
                  faqSection?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="px-6 py-3 rounded-full font-bold text-sm text-gray-300 border border-white/10 hover:bg-white/5 hover:text-white transition-all"
              >
                Read the Guide
              </button>
            </div>
          </motion.header>

          {/* Intro Content - Unique per role */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-12"
          >
            <SpotlightCard className="rounded-xl p-8">
              <div className="article-prose prose prose-invert prose-lg max-w-none text-gray-300 leading-relaxed">
                {seoContent.introParagraph.split('\n\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </SpotlightCard>
          </motion.section>

          {/* Key Information Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {/* ATS Keywords */}
            <SpotlightCard className="rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-blue-400" />
                <h2 className="text-xl font-bold text-white font-display">
                  ATS Keywords to Include
                </h2>
              </div>
              <p className="text-sm text-gray-400 mb-4">
                These keywords appear frequently in {jobRole.name} job descriptions:
              </p>
              <div className="flex flex-wrap gap-2">
                {jobRole.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full text-sm text-blue-300"
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
                <h2 className="text-xl font-bold text-white font-display">
                  Essential Skills
                </h2>
              </div>
              <p className="text-sm text-gray-400 mb-4">
                Must-have skills for {jobRole.name} positions:
              </p>
              <ul className="space-y-2">
                {jobRole.skills.map((skill, index) => (
                  <li
                    key={index}
                    className="flex items-center gap-2 text-gray-300"
                  >
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>{skill}</span>
                  </li>
                ))}
              </ul>
            </SpotlightCard>
          </div>

          {/* Step-by-Step Guide */}
          <section className="mb-12" id="how-to-guide">
            <SpotlightCard className="rounded-xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <FileText className="w-6 h-6 text-blue-400" />
                <h2 className="text-2xl font-bold text-white font-display">
                  How to Write Your {jobRole.name} Resume
                </h2>
              </div>

              <ol className="space-y-6">
                {seoContent.howToSteps.map((step, index) => (
                  <motion.li
                    key={index}
                    id={`step-${index + 1}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-4"
                  >
                    <span className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-sm">
                      {index + 1}
                    </span>
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-2">
                        {step.name}
                      </h3>
                      <p className="text-gray-300">{step.text}</p>
                    </div>
                  </motion.li>
                ))}
              </ol>
            </SpotlightCard>
          </section>

          {/* Resume Tips */}
          <SpotlightCard className="rounded-xl p-8 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <FileText className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-bold text-white font-display">
                Expert Tips for {jobRole.name} Resumes
              </h2>
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
              <h2 className="text-2xl font-bold text-white font-display">
                Common {jobRole.name} Resume Mistakes
              </h2>
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

          {/* FAQ Section */}
          <div id="faq-section">
            <FAQSection
              faqs={seoContent.faqs}
              title={`${jobRole.name} Resume FAQ`}
            />
          </div>

          {/* Promotion Banners */}
          <div className="mt-12">
            <PromotionBanner variant="trial" />
            <PromotionBanner variant="student" className="mt-8" />
          </div>

          {/* CTA Section */}
          <SpotlightCard className="rounded-xl p-8 mt-12 bg-gradient-to-r from-blue-500/10 to-blue-600/10 border border-blue-500/20">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white mb-4 font-display">
                Ready to Optimize Your {jobRole.name} Resume?
              </h2>
              <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
                Get instant AI-powered feedback on your resume. Our advanced
                analysis will help you highlight the right keywords, skills, and
                achievements for {jobRole.name} positions.
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

          {/* Internal Links Section - Hub and Spoke */}
          <InternalLinks
            hub={seoContent.internalLinks.hub}
            relatedRoles={seoContent.internalLinks.relatedRoles}
            relatedPosts={seoContent.internalLinks.relatedPosts}
            currentRole={jobRole.slug}
          />
        </div>
      </div>
    </>
  );
};

export default JobRoleLandingPage;
