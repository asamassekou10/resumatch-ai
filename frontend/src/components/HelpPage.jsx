import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import { Search, ChevronDown, Mail, MessageSquare, BookOpen, FileText, Shield, Send, CheckCircle } from 'lucide-react';
import SpotlightCard from './ui/SpotlightCard';
import Footer from './ui/Footer';
import SEO from './common/SEO';
import { generateFAQSchema } from '../utils/structuredData';
import axios from 'axios';
import config from '../config';

const API_URL = config.api.baseURL;

// FAQs data - defined at module level before use
  const faqs = [
    {
      question: 'How do I analyze my resume?',
      answer: 'To analyze your resume, go to the Dashboard and click "Analyze Resume". Upload your resume file (PDF, DOCX, or TXT), optionally add a job description, and click "Analyze". You\'ll receive detailed feedback within seconds.'
    },
    {
      question: 'What file formats are supported?',
      answer: 'We support PDF (.pdf), Microsoft Word (.docx), and plain text (.txt) files. For best results, we recommend using PDF format as it preserves formatting and structure.'
    },
    {
      question: 'How do I get more credits?',
      answer: 'Credits are included with your subscription plan. Free users get 5 credits, Pro users get 100 credits per month, and Elite users get 1000 credits. You can also purchase additional credits from the Billing page or upgrade your plan for more monthly credits.'
    },
    {
      question: 'What is the job matching feature?',
      answer: 'Our AI-powered job matching analyzes your resume and finds relevant job opportunities from our database of real-time job listings. It scores each match based on your skills, experience, and the job requirements, helping you find the best opportunities.'
    },
    {
      question: 'How accurate is the AI analysis?',
      answer: 'Our AI is trained on thousands of successful resumes and hiring patterns across multiple industries. It provides industry-standard feedback with 95%+ accuracy. However, we recommend using it as a guide alongside professional resume services for best results.'
    },
    {
      question: 'Can I cancel my subscription anytime?',
      answer: 'Yes! You can cancel your subscription at any time from the Billing page. You\'ll retain access to your plan features until the end of your current billing period. No questions asked, no cancellation fees.'
    },
    {
      question: 'What makes your resume analysis different?',
      answer: 'Our AI analyzes multiple factors including ATS compatibility, keyword optimization, formatting, content quality, and industry-specific requirements. We provide actionable feedback with specific suggestions for improvement, not just generic advice.'
    },
    {
      question: 'How does the ATS score work?',
      answer: 'The ATS (Applicant Tracking System) score measures how well your resume will perform when scanned by automated systems that companies use. We check for proper formatting, keyword usage, section organization, and readability. A score above 80% means your resume is well-optimized for ATS systems.'
    },
    {
      question: 'Can I analyze the same resume multiple times?',
      answer: 'Yes! Each analysis uses one credit, but you can analyze the same resume as many times as you want. This is useful for tracking improvements as you update your resume based on our feedback.'
    },
    {
      question: 'Is my resume data kept private?',
      answer: 'Absolutely. We take privacy seriously. Your resume data is encrypted, never shared with third parties, and you can delete it anytime from your profile. We only use anonymized data to improve our AI models, and you can opt out of this in your privacy settings.'
  },
];

const HelpPage = ({ defaultTab = 'help' }) => {
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState(null);
  const [activeView, setActiveView] = useState(defaultTab); // 'help', 'terms', 'privacy', 'feedback'
  const [feedbackData, setFeedbackData] = useState({
    name: '',
    email: '',
    rating: 0,
    message: '',
    category: 'general'
  });
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Check for feedback query parameter
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('feedback') === 'true') {
      setActiveView('feedback');
    }
  }, [location]);
  
  // Get SEO metadata based on active view
  const getSEOMetadata = () => {
    switch (activeView) {
      case 'feedback':
        return {
          title: 'Share Your Feedback',
          description: 'Tell us about your experience with ResumeAnalyzer AI. Your feedback helps us improve and serve you better.',
          keywords: 'feedback, user feedback, testimonial, review, suggestions',
          url: 'https://resumeanalyzerai.com/help?feedback=true'
        };
      case 'terms':
        return {
          title: 'Terms of Service',
          description: 'Read our Terms of Service to understand the terms and conditions for using ResumeAnalyzer AI. Learn about user rights, subscription terms, and acceptable use policies.',
          keywords: 'terms of service, user agreement, legal terms, resume analyzer terms',
          url: 'https://resumeanalyzerai.com/help/terms'
        };
      case 'privacy':
        return {
          title: 'Privacy Policy',
          description: 'Learn how ResumeAnalyzer AI protects your privacy. Our Privacy Policy explains how we collect, use, and safeguard your personal information and resume data.',
          keywords: 'privacy policy, data protection, GDPR, user privacy, resume data security',
          url: 'https://resumeanalyzerai.com/help/privacy'
        };
      default:
        return {
          title: 'Help & Support',
          description: 'Get help with ResumeAnalyzer AI. Find answers to frequently asked questions, learn how to use our features, and contact our support team for assistance.',
          keywords: 'help, support, FAQ, resume analyzer help, how to use, customer support',
          url: 'https://resumeanalyzerai.com/help'
        };
    }
  };
  
  const seoMetadata = getSEOMetadata();
  
  // Generate FAQ schema for help page
  const faqSchema = activeView === 'help' ? generateFAQSchema(faqs) : null;

  const categories = [
    {
      icon: '📄',
      title: 'Getting Started',
      articles: 5,
      color: 'from-cyan-500 to-blue-500'
    },
    {
      icon: '💳',
      title: 'Billing & Plans',
      articles: 8,
      color: 'from-blue-500 to-pink-500'
    },
    {
      icon: '🎯',
      title: 'Resume Tips',
      articles: 12,
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: '🤖',
      title: 'AI Features',
      articles: 6,
      color: 'from-yellow-500 to-orange-500'
    },
  ];

  const filteredFaqs = searchQuery
    ? faqs.filter(faq =>
        faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : faqs;

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFeedbackError('');

    try {
      await axios.post(`${API_URL}/api/feedback`, feedbackData);
      setFeedbackSubmitted(true);
      setFeedbackData({
        name: '',
        email: '',
        rating: 0,
        message: '',
        category: 'general'
      });
    } catch (error) {
      setFeedbackError(error.response?.data?.error || 'Failed to submit feedback. Please try again or email us at support@resumeanalyzerai.com');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <SEO
        title={seoMetadata.title}
        description={seoMetadata.description}
        keywords={seoMetadata.keywords}
        url={seoMetadata.url}
        structuredData={faqSchema ? [faqSchema] : null}
      />
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="max-w-5xl mx-auto px-4 py-8 relative z-10">
        {/* View Tabs */}
        <div className="flex justify-center gap-2 mb-8 border-b border-white/10 pb-4 relative z-10 flex-wrap">
          <button
            onClick={() => setActiveView('help')}
            className={`px-6 py-3 rounded-t-lg transition font-medium relative z-10 ${
              activeView === 'help'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            Help & FAQs
          </button>
          <button
            onClick={() => setActiveView('feedback')}
            className={`px-6 py-3 rounded-t-lg transition font-medium flex items-center gap-2 relative z-10 ${
              activeView === 'feedback'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Feedback
          </button>
          <button
            onClick={() => setActiveView('terms')}
            className={`px-6 py-3 rounded-t-lg transition font-medium flex items-center gap-2 relative z-10 ${
              activeView === 'terms'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <FileText className="w-4 h-4" />
            Terms of Service
          </button>
          <button
            onClick={() => setActiveView('privacy')}
            className={`px-6 py-3 rounded-t-lg transition font-medium flex items-center gap-2 relative z-10 ${
              activeView === 'privacy'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <Shield className="w-4 h-4" />
            Privacy Policy
          </button>
        </div>

        {/* Help & FAQs View */}
        {activeView === 'help' && (
          <>
            {/* Header */}
            <div className="text-center mb-12 relative z-10">
              <h1 className="text-4xl font-bold text-white mb-4 font-display relative z-10">How can we help you?</h1>
              <p className="text-gray-400 mb-8 relative z-10">Search our knowledge base or browse categories below</p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto relative z-10">
            <input
              type="text"
              placeholder="Search for help..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition pr-12 relative z-10"
            />
            <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {/* Categories */}
        <div className="mb-12 relative z-10">
          <h2 className="text-2xl font-bold text-white mb-6 font-display relative z-10">Browse by Category</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {categories.map((category, index) => (
              <SpotlightCard key={index} className="rounded-xl p-6 cursor-pointer group">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative z-10"
                >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${category.color} flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition`}>
                  {category.icon}
                </div>
                <h3 className="text-white font-semibold mb-2 relative z-10 font-display">{category.title}</h3>
                <p className="text-gray-400 text-sm relative z-10">{category.articles} articles</p>
                </motion.div>
              </SpotlightCard>
            ))}
          </div>
        </div>

        {/* FAQs */}
        <div className="mb-12 relative z-10">
          <h2 className="text-2xl font-bold text-white mb-6 font-display relative z-10">
            {searchQuery ? `Search Results (${filteredFaqs.length})` : 'Frequently Asked Questions'}
          </h2>

          {filteredFaqs.length > 0 ? (
            <div className="space-y-3">
              {filteredFaqs.map((faq, index) => (
                <SpotlightCard key={index} className="rounded-xl overflow-hidden">
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="relative z-10"
                  >
                  <button
                    onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                    className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-slate-700/30 transition"
                  >
                    <span className="text-white font-medium pr-4 relative z-10">{faq.question}</span>
                    <ChevronDown
                      className={`w-5 h-5 text-blue-400 transition-transform flex-shrink-0 relative z-10 ${
                        expandedFaq === index ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                  {expandedFaq === index && (
                    <div className="px-6 pb-4 relative z-10">
                      <p className="text-gray-300 leading-relaxed relative z-10">{faq.answer}</p>
                    </div>
                  )}
                  </motion.div>
                </SpotlightCard>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 relative z-10">
              <p className="text-gray-400 relative z-10">No results found for "{searchQuery}"</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 px-6 py-2 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg transition relative z-10"
              >
                Clear Search
              </button>
            </div>
          )}
        </div>

        {/* Contact Support */}
        <SpotlightCard className="bg-gradient-to-r from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-2xl p-8 relative z-10">
          <h2 className="text-2xl font-bold text-white mb-6 text-center font-display relative z-10">Still need help?</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
            <div className="text-center relative z-10">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4 relative z-10">
                <Mail className="w-8 h-8 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold mb-2 relative z-10 font-display">Email Support</h3>
              <p className="text-gray-400 text-sm mb-3 relative z-10">We'll respond within 24 hours</p>
              <a
                href="mailto:support@resumeanalyzerai.com"
                className="text-blue-400 hover:text-blue-300 text-sm relative z-10"
              >
                support@resumeanalyzerai.com
              </a>
            </div>

            <div className="text-center relative z-10">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4 relative z-10">
                <MessageSquare className="w-8 h-8 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold mb-2 relative z-10 font-display">Live Chat</h3>
              <p className="text-gray-400 text-sm relative z-10">Coming soon for Pro & Elite users</p>
            </div>

            <div className="text-center relative z-10">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4 relative z-10">
                <BookOpen className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-white font-semibold mb-2 relative z-10 font-display">Documentation</h3>
              <p className="text-gray-400 text-sm relative z-10">Comprehensive guides coming soon</p>
            </div>
          </div>
        </SpotlightCard>
          </>
        )}

        {/* Feedback View */}
        {activeView === 'feedback' && (
          <SpotlightCard className="rounded-2xl p-8 max-w-2xl mx-auto relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative z-10"
            >
              {!feedbackSubmitted ? (
                <>
                  <h1 className="text-3xl font-bold text-white mb-4 font-display relative z-10">Share Your Feedback</h1>
                  <p className="text-gray-400 mb-8 relative z-10">
                    We'd love to hear about your experience with ResumeAnalyzer AI. Your feedback helps us improve!
                  </p>

                  <form onSubmit={handleFeedbackSubmit} className="space-y-6 relative z-10">
                    {/* Name Field */}
                    <div>
                      <label className="block text-white font-medium mb-2">Name</label>
                      <input
                        type="text"
                        required
                        value={feedbackData.name}
                        onChange={(e) => setFeedbackData({ ...feedbackData, name: e.target.value })}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
                        placeholder="Your name"
                      />
                    </div>

                    {/* Email Field */}
                    <div>
                      <label className="block text-white font-medium mb-2">Email</label>
                      <input
                        type="email"
                        required
                        value={feedbackData.email}
                        onChange={(e) => setFeedbackData({ ...feedbackData, email: e.target.value })}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
                        placeholder="your@email.com"
                      />
                    </div>

                    {/* Rating */}
                    <div>
                      <label className="block text-white font-medium mb-3">How would you rate your experience?</label>
                      <div className="flex gap-2">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            type="button"
                            onClick={() => setFeedbackData({ ...feedbackData, rating: star })}
                            className="group"
                          >
                            <svg
                              className={`w-10 h-10 transition ${
                                star <= feedbackData.rating
                                  ? 'text-yellow-400 fill-yellow-400'
                                  : 'text-gray-600 group-hover:text-gray-400'
                              }`}
                              fill={star <= feedbackData.rating ? 'currentColor' : 'none'}
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                              />
                            </svg>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Category */}
                    <div>
                      <label className="block text-white font-medium mb-2">Category</label>
                      <select
                        value={feedbackData.category}
                        onChange={(e) => setFeedbackData({ ...feedbackData, category: e.target.value })}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
                      >
                        <option value="general">General Feedback</option>
                        <option value="bug">Report a Bug</option>
                        <option value="feature">Feature Request</option>
                        <option value="support">Support Issue</option>
                        <option value="praise">Praise/Testimonial</option>
                      </select>
                    </div>

                    {/* Message */}
                    <div>
                      <label className="block text-white font-medium mb-2">Message</label>
                      <textarea
                        required
                        value={feedbackData.message}
                        onChange={(e) => setFeedbackData({ ...feedbackData, message: e.target.value })}
                        rows={6}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition resize-none"
                        placeholder="Tell us about your experience, suggestions, or any issues you've encountered..."
                      />
                    </div>

                    {feedbackError && (
                      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <p className="text-red-400 text-sm">{feedbackError}</p>
                      </div>
                    )}

                    {/* Submit Button */}
                    <button
                      type="submit"
                      disabled={isSubmitting || feedbackData.rating === 0}
                      className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                          Submitting...
                        </>
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          Submit Feedback
                        </>
                      )}
                    </button>
                  </form>
                </>
              ) : (
                <div className="text-center py-12">
                  <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <CheckCircle className="w-12 h-12 text-green-400" />
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-3 font-display">Thank You!</h2>
                  <p className="text-gray-400 mb-6">
                    Your feedback has been submitted successfully. We'll review it carefully and use it to improve ResumeAnalyzer AI.
                  </p>
                  <button
                    onClick={() => {
                      setFeedbackSubmitted(false);
                      setActiveView('help');
                    }}
                    className="px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg transition"
                  >
                    Back to Help
                  </button>
                </div>
              )}
            </motion.div>
          </SpotlightCard>
        )}

        {/* Terms of Service View */}
        {activeView === 'terms' && (
          <SpotlightCard className="rounded-2xl p-8 max-w-4xl mx-auto relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative z-10"
            >
            <h1 className="text-3xl font-bold text-white mb-6 font-display relative z-10">Terms of Service</h1>
            <p className="text-gray-400 mb-8 relative z-10">Last updated: December 9, 2024</p>

            <div className="space-y-6 text-gray-300 relative z-10">
              <section>
                <h2 className="text-xl font-semibold text-white mb-3">1. Acceptance of Terms</h2>
                <p className="leading-relaxed">
                  By accessing and using ResumeAnalyzer AI ("Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to these Terms of Service, please do not use our Service.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">2. Description of Service</h2>
                <p className="leading-relaxed mb-3">
                  ResumeAnalyzer AI provides an AI-powered platform for resume analysis, optimization, and job matching. Our services include but are not limited to:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Resume analysis and scoring</li>
                  <li>ATS (Applicant Tracking System) optimization</li>
                  <li>Keyword optimization recommendations</li>
                  <li>Job matching and recommendations</li>
                  <li>Career path analysis</li>
                  <li>Interview preparation tools</li>
                  <li>Skill extraction and verification</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">3. User Accounts</h2>
                <p className="leading-relaxed mb-3">
                  To access certain features of the Service, you must register for an account. You agree to:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Provide accurate, current, and complete information during registration</li>
                  <li>Maintain and promptly update your account information</li>
                  <li>Maintain the security of your password and account</li>
                  <li>Accept responsibility for all activities that occur under your account</li>
                  <li>Notify us immediately of any unauthorized use of your account</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">4. Subscription Plans and Billing</h2>
                <p className="leading-relaxed mb-3">
                  We offer multiple subscription tiers (Free, Pro, Elite) with varying features and credit allocations:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Subscription fees are billed in advance on a monthly basis</li>
                  <li>Credits are allocated monthly and do not roll over to the next billing period</li>
                  <li>All fees are non-refundable except as required by law</li>
                  <li>You may cancel your subscription at any time, effective at the end of the current billing period</li>
                  <li>We reserve the right to change subscription prices with 30 days notice</li>
                  <li>Payment processing is handled securely through Stripe</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">5. Acceptable Use</h2>
                <p className="leading-relaxed mb-3">
                  You agree not to:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Use the Service for any illegal or unauthorized purpose</li>
                  <li>Attempt to gain unauthorized access to any portion of the Service</li>
                  <li>Interfere with or disrupt the Service or servers</li>
                  <li>Upload malicious code, viruses, or any harmful content</li>
                  <li>Scrape, crawl, or use automated means to access the Service without permission</li>
                  <li>Impersonate another person or entity</li>
                  <li>Share your account credentials with others</li>
                  <li>Use the Service to spam or send unsolicited communications</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">6. Intellectual Property Rights</h2>
                <p className="leading-relaxed mb-3">
                  The Service and its original content, features, and functionality are owned by ResumeAnalyzer AI and are protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.
                </p>
                <p className="leading-relaxed">
                  You retain all rights to your resume content. By using our Service, you grant us a limited license to process and analyze your content solely for the purpose of providing our services to you.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">7. AI-Generated Content</h2>
                <p className="leading-relaxed mb-3">
                  Our Service uses artificial intelligence to analyze resumes and provide recommendations. You acknowledge that:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>AI-generated recommendations are suggestions and not guarantees</li>
                  <li>You are responsible for reviewing and verifying all AI-generated content</li>
                  <li>Results may vary based on your specific circumstances</li>
                  <li>We do not guarantee job placement or interview success</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">8. Data Privacy and Security</h2>
                <p className="leading-relaxed">
                  Your privacy is important to us. Please review our Privacy Policy to understand how we collect, use, and protect your personal information. By using the Service, you consent to our data practices as described in the Privacy Policy.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">9. Disclaimer of Warranties</h2>
                <p className="leading-relaxed">
                  THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, OR COMPLETELY SECURE.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">10. Limitation of Liability</h2>
                <p className="leading-relaxed">
                  TO THE MAXIMUM EXTENT PERMITTED BY LAW, RESUMEANALYZER AI SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES RESULTING FROM YOUR USE OF THE SERVICE.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">11. Termination</h2>
                <p className="leading-relaxed">
                  We may terminate or suspend your account and access to the Service immediately, without prior notice or liability, for any reason, including breach of these Terms. Upon termination, your right to use the Service will immediately cease.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">12. Changes to Terms</h2>
                <p className="leading-relaxed">
                  We reserve the right to modify these Terms at any time. We will notify users of any material changes via email or through the Service. Your continued use of the Service after such modifications constitutes acceptance of the updated Terms.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">13. Governing Law</h2>
                <p className="leading-relaxed">
                  These Terms shall be governed by and construed in accordance with the laws of the United States, without regard to its conflict of law provisions.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">14. Contact Information</h2>
                <p className="leading-relaxed">
                  If you have any questions about these Terms, please contact us at:
                  <br />
                  Email: support@resumeanalyzerai.com
                </p>
              </section>
            </div>
            </motion.div>
          </SpotlightCard>
        )}

        {/* Privacy Policy View */}
        {activeView === 'privacy' && (
          <SpotlightCard className="rounded-2xl p-8 max-w-4xl mx-auto relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative z-10"
            >
            <h1 className="text-3xl font-bold text-white mb-6 font-display relative z-10">Privacy Policy</h1>
            <p className="text-gray-400 mb-8 relative z-10">Last updated: December 9, 2024</p>

            <div className="space-y-6 text-gray-300 relative z-10">
              <section>
                <h2 className="text-xl font-semibold text-white mb-3">1. Introduction</h2>
                <p className="leading-relaxed">
                  ResumeAnalyzer AI ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Service. Please read this policy carefully.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">2. Information We Collect</h2>

                <h3 className="text-lg font-semibold text-white mb-2 mt-4">2.1 Personal Information</h3>
                <p className="leading-relaxed mb-3">
                  We collect information that you provide directly to us:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Name and email address</li>
                  <li>Account credentials (username and password)</li>
                  <li>Payment information (processed securely through Stripe)</li>
                  <li>Resume content and job descriptions you upload</li>
                  <li>Profile information and preferences</li>
                  <li>Communications with our support team</li>
                </ul>

                <h3 className="text-lg font-semibold text-white mb-2 mt-4">2.2 Automatically Collected Information</h3>
                <p className="leading-relaxed mb-3">
                  When you use our Service, we automatically collect:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>IP address and device information</li>
                  <li>Browser type and version</li>
                  <li>Usage data (pages visited, features used, time spent)</li>
                  <li>Cookies and similar tracking technologies</li>
                  <li>Error logs and performance data</li>
                </ul>

                <h3 className="text-lg font-semibold text-white mb-2 mt-4">2.3 AI Analysis Data</h3>
                <p className="leading-relaxed">
                  We process your resume content using AI technology to provide analysis and recommendations. This includes extracting skills, education, experience, and other relevant information from your resume.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">3. How We Use Your Information</h2>
                <p className="leading-relaxed mb-3">
                  We use the collected information for the following purposes:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>To provide, maintain, and improve our Service</li>
                  <li>To process your resume and generate analysis reports</li>
                  <li>To match you with relevant job opportunities</li>
                  <li>To process payments and manage subscriptions</li>
                  <li>To send you service-related notifications and updates</li>
                  <li>To respond to your inquiries and provide customer support</li>
                  <li>To detect, prevent, and address technical issues and security threats</li>
                  <li>To analyze usage patterns and improve our AI algorithms</li>
                  <li>To comply with legal obligations</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">4. Data Sharing and Disclosure</h2>
                <p className="leading-relaxed mb-3">
                  We do not sell your personal information. We may share your information in the following circumstances:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Service Providers:</strong> Third-party vendors who perform services on our behalf (e.g., Stripe for payments, cloud hosting providers)</li>
                  <li><strong>AI Processing:</strong> OpenAI and other AI service providers for resume analysis (data is processed securely and not used for training)</li>
                  <li><strong>Legal Requirements:</strong> When required by law or to protect our rights and safety</li>
                  <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
                  <li><strong>With Your Consent:</strong> When you explicitly authorize us to share your information</li>
                </ul>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">5. Data Security</h2>
                <p className="leading-relaxed mb-3">
                  We implement appropriate technical and organizational measures to protect your information:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Encryption of data in transit using HTTPS/TLS</li>
                  <li>Encryption of sensitive data at rest</li>
                  <li>Secure password hashing using industry-standard algorithms</li>
                  <li>Regular security audits and updates</li>
                  <li>Access controls and authentication requirements</li>
                  <li>Secure payment processing through PCI-compliant providers</li>
                </ul>
                <p className="leading-relaxed mt-3">
                  However, no method of transmission over the Internet or electronic storage is 100% secure. While we strive to protect your information, we cannot guarantee absolute security.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">6. Data Retention</h2>
                <p className="leading-relaxed">
                  We retain your personal information for as long as necessary to provide our Service and fulfill the purposes outlined in this Privacy Policy. You may delete your account at any time, which will result in the deletion of your personal data within 30 days, except where we are required to retain it for legal purposes.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">7. Your Rights and Choices</h2>
                <p className="leading-relaxed mb-3">
                  You have the following rights regarding your personal information:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Access:</strong> Request a copy of your personal data</li>
                  <li><strong>Correction:</strong> Update or correct inaccurate information</li>
                  <li><strong>Deletion:</strong> Request deletion of your personal data</li>
                  <li><strong>Export:</strong> Download your data in a portable format</li>
                  <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
                  <li><strong>Data Portability:</strong> Receive your data in a structured, machine-readable format</li>
                </ul>
                <p className="leading-relaxed mt-3">
                  To exercise these rights, please contact us at support@resumeanalyzerai.com or use the settings in your account dashboard.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">8. Cookies and Tracking Technologies</h2>
                <p className="leading-relaxed mb-3">
                  We use cookies and similar technologies to:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Maintain your session and keep you logged in</li>
                  <li>Remember your preferences and settings</li>
                  <li>Analyze usage patterns and improve our Service</li>
                  <li>Provide personalized content and recommendations</li>
                </ul>
                <p className="leading-relaxed mt-3">
                  You can control cookies through your browser settings. However, disabling cookies may limit your ability to use certain features of our Service.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">9. Third-Party Links</h2>
                <p className="leading-relaxed">
                  Our Service may contain links to third-party websites or services. We are not responsible for the privacy practices of these external sites. We encourage you to review their privacy policies before providing any personal information.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">10. Children's Privacy</h2>
                <p className="leading-relaxed">
                  Our Service is not intended for children under 13 years of age. We do not knowingly collect personal information from children. If you become aware that a child has provided us with personal information, please contact us immediately.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">11. International Data Transfers</h2>
                <p className="leading-relaxed">
                  Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place to protect your information in accordance with this Privacy Policy.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">12. California Privacy Rights</h2>
                <p className="leading-relaxed">
                  If you are a California resident, you have additional rights under the California Consumer Privacy Act (CCPA), including the right to know what personal information we collect, the right to delete your information, and the right to opt-out of the sale of your information (we do not sell personal information).
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">13. Changes to This Privacy Policy</h2>
                <p className="leading-relaxed">
                  We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new Privacy Policy on this page and updating the "Last updated" date. We encourage you to review this Privacy Policy periodically.
                </p>
              </section>

              <section>
                <h2 className="text-xl font-semibold text-white mb-3">14. Contact Us</h2>
                <p className="leading-relaxed">
                  If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us at:
                </p>
                <div className="mt-3 p-4 bg-slate-900/50 rounded-lg">
                  <p className="font-semibold text-white">ResumeAnalyzer AI</p>
                  <p>Email: support@resumeanalyzerai.com</p>
                  <p>Email (Privacy): privacy@resumeanalyzerai.com</p>
                </div>
              </section>
            </div>
            </motion.div>
          </SpotlightCard>
        )}
      </div>
      <Footer />
    </div>
    </>
  );
};

export default HelpPage;
