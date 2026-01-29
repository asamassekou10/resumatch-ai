import React from 'react';
import { Lock, Shield, CheckCircle, CreditCard } from 'lucide-react';

/**
 * TrustSignals Component
 * Displays trust badges for security, guarantees, and payment options
 */
const TrustSignals = ({ variant = 'horizontal', className = '' }) => {
  const signals = [
    { icon: Lock, text: '256-bit SSL Secured', color: 'text-green-400' },
    { icon: Shield, text: 'No Credit Card Required', color: 'text-blue-400' },
    { icon: CheckCircle, text: 'Money-back Guarantee', color: 'text-cyan-400' },
  ];

  if (variant === 'compact') {
    return (
      <div className={`flex flex-wrap justify-center gap-4 ${className}`}>
        {signals.map((signal, index) => {
          const Icon = signal.icon;
          return (
            <div key={index} className="flex items-center gap-2 text-gray-400 text-xs">
              <Icon className={`w-3.5 h-3.5 ${signal.color}`} />
              <span>{signal.text}</span>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className={`flex flex-wrap justify-center gap-4 md:gap-6 ${className}`}>
      {signals.map((signal, index) => {
        const Icon = signal.icon;
        return (
          <div key={index} className="flex items-center gap-2 text-gray-400 text-sm">
            <Icon className={`w-4 h-4 ${signal.color}`} />
            <span>{signal.text}</span>
          </div>
        );
      })}
    </div>
  );
};

export default TrustSignals;
