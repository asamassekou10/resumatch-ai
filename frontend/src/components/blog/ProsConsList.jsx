import { CheckCircle2, XCircle } from 'lucide-react';

/**
 * ProsConsList Component
 * 
 * A list component that displays items with green checkmarks (pros) or red X icons (cons)
 */
const ProsConsList = ({ items, type = 'pros' }) => {
  const Icon = type === 'pros' ? CheckCircle2 : XCircle;
  const iconColor = type === 'pros' ? 'text-green-400' : 'text-red-400';
  const textColor = type === 'pros' ? 'text-gray-200' : 'text-gray-300';

  return (
    <ul className="space-y-3 my-6">
      {items.map((item, index) => (
        <li key={index} className="flex items-start gap-3">
          <Icon className={`w-5 h-5 ${iconColor} flex-shrink-0 mt-0.5`} />
          <span className={textColor}>{item}</span>
        </li>
      ))}
    </ul>
  );
};

export default ProsConsList;





