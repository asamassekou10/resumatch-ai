import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, ChevronDown, Mail, MessageSquare, BookOpen } from 'lucide-react';

const HelpPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState(null);

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
      color: 'from-purple-500 to-pink-500'
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

  const filteredFaqs = searchQuery
    ? faqs.filter(faq =>
        faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : faqs;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">How can we help you?</h1>
          <p className="text-slate-400 mb-8">Search our knowledge base or browse categories below</p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <input
              type="text"
              placeholder="Search for help..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-6 py-4 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition pr-12"
            />
            <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          </div>
        </div>

        {/* Categories */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Browse by Category</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {categories.map((category, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-cyan-500/50 transition cursor-pointer group"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${category.color} flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition`}>
                  {category.icon}
                </div>
                <h3 className="text-white font-semibold mb-2">{category.title}</h3>
                <p className="text-slate-400 text-sm">{category.articles} articles</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* FAQs */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">
            {searchQuery ? `Search Results (${filteredFaqs.length})` : 'Frequently Asked Questions'}
          </h2>

          {filteredFaqs.length > 0 ? (
            <div className="space-y-3">
              {filteredFaqs.map((faq, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                    className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-slate-700/30 transition"
                  >
                    <span className="text-white font-medium pr-4">{faq.question}</span>
                    <ChevronDown
                      className={`w-5 h-5 text-cyan-400 transition-transform flex-shrink-0 ${
                        expandedFaq === index ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                  {expandedFaq === index && (
                    <div className="px-6 pb-4">
                      <p className="text-slate-300 leading-relaxed">{faq.answer}</p>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-slate-400">No results found for "{searchQuery}"</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-4 px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition"
              >
                Clear Search
              </button>
            </div>
          )}
        </div>

        {/* Contact Support */}
        <div className="bg-gradient-to-r from-cyan-500/10 to-purple-600/10 border border-cyan-500/20 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Still need help?</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-cyan-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Email Support</h3>
              <p className="text-slate-400 text-sm mb-3">We'll respond within 24 hours</p>
              <a
                href="mailto:support@resumeanalyzerai.com"
                className="text-cyan-400 hover:text-cyan-300 text-sm"
              >
                support@resumeanalyzerai.com
              </a>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-8 h-8 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Live Chat</h3>
              <p className="text-slate-400 text-sm mb-3">Pro & Elite users only</p>
              <button className="text-purple-400 hover:text-purple-300 text-sm">
                Start Chat →
              </button>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Documentation</h3>
              <p className="text-slate-400 text-sm mb-3">Comprehensive guides</p>
              <button className="text-green-400 hover:text-green-300 text-sm">
                Browse Docs →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpPage;
