/**
 * StatBox Component
 * 
 * Displays a large, bold statistic with a label below it.
 * Great for breaking up text with hard data (SEO-friendly).
 * 
 * @param {Object} props
 * @param {string} props.number - The statistic number (e.g., "75%", "250", "$2.4M")
 * @param {string} props.label - The label describing the statistic
 * @param {string} props.color - Optional color variant (defaults to primary blue)
 */
const StatBox = ({ number, label, color = 'blue' }) => {
  const colorClasses = {
    blue: 'text-blue-400',
    cyan: 'text-cyan-400',
    purple: 'text-purple-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400',
  };
  
  const numberColor = colorClasses[color] || colorClasses.blue;
  
  return (
    <div className="my-8 py-6 px-4 text-center border border-white/10 rounded-lg bg-white/5 backdrop-blur-sm">
      <div className={`text-6xl sm:text-7xl font-bold ${numberColor} mb-2 leading-none`}>
        {number}
      </div>
      <div className="text-gray-300 text-sm sm:text-base font-medium uppercase tracking-wide mt-2">
        {label}
      </div>
    </div>
  );
};

export default StatBox;









