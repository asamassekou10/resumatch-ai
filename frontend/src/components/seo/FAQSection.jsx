/**
 * FAQ Section Component
 *
 * Renders FAQ content with proper semantic markup for SEO.
 * Integrated with schema.org FAQPage structured data.
 */

import { useState } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Individual FAQ item with expand/collapse
 */
const FAQItem = ({ question, answer, isOpen, onToggle, index }) => {
  return (
    <div
      className="border-b border-white/10 last:border-b-0"
      itemScope
      itemProp="mainEntity"
      itemType="https://schema.org/Question"
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between py-5 text-left hover:text-blue-400 transition-colors group"
        aria-expanded={isOpen}
        aria-controls={`faq-answer-${index}`}
      >
        <span
          className="text-white font-semibold pr-4 group-hover:text-blue-400"
          itemProp="name"
        >
          {question}
        </span>
        <ChevronDown
          className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            id={`faq-answer-${index}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className="overflow-hidden"
            itemScope
            itemProp="acceptedAnswer"
            itemType="https://schema.org/Answer"
          >
            <div
              className="pb-5 text-gray-300 leading-relaxed"
              itemProp="text"
            >
              {answer}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

/**
 * FAQ Section with multiple items
 * @param {Object} props
 * @param {Array} props.faqs - Array of {question, answer} objects
 * @param {string} props.title - Section title
 * @param {string} props.className - Additional CSS classes
 */
const FAQSection = ({
  faqs = [],
  title = 'Frequently Asked Questions',
  className = ''
}) => {
  const [openIndex, setOpenIndex] = useState(0); // First one open by default

  if (!faqs || faqs.length === 0) return null;

  const handleToggle = (index) => {
    setOpenIndex(openIndex === index ? -1 : index);
  };

  return (
    <section
      className={`mt-12 ${className}`}
      itemScope
      itemType="https://schema.org/FAQPage"
    >
      <div className="flex items-center gap-3 mb-6">
        <HelpCircle className="w-6 h-6 text-blue-400" />
        <h2 className="text-2xl font-bold text-white font-display">{title}</h2>
      </div>

      <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
        <div className="divide-y divide-white/10">
          {faqs.map((faq, index) => (
            <div key={index} className="px-6">
              <FAQItem
                question={faq.question}
                answer={faq.answer}
                isOpen={openIndex === index}
                onToggle={() => handleToggle(index)}
                index={index}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FAQSection;
