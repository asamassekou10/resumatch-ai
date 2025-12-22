/**
 * Credits utility functions
 * Provides consistent credit limit calculations across the application
 */

/**
 * Get maximum credits for a subscription tier
 * @param {string} tier - Subscription tier ('free', 'pro', 'elite')
 * @returns {number} Maximum credits for the tier
 */
export const getMaxCredits = (tier) => {
  switch (tier) {
    case 'free':
      return 5;
    case 'pro':
      return 100;
    case 'elite':
      return 1000;
    default:
      return 5; // Default to free tier
  }
};

/**
 * Get formatted credits display string
 * @param {number} credits - Current credits
 * @param {string} tier - Subscription tier
 * @returns {string} Formatted string "X/Y Credits"
 */
export const getCreditsDisplay = (credits, tier) => {
  const maxCredits = getMaxCredits(tier);
  return `${credits || 0}/${maxCredits}`;
};

