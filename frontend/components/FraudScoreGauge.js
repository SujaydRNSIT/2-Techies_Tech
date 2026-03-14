export default function FraudScoreGauge({ score }) {
  const getColor = (s) => {
    if (s <= 30) return 'text-success-600';
    if (s <= 70) return 'text-warning-600';
    return 'text-danger-600';
  };

  const getBgColor = (s) => {
    if (s <= 30) return 'bg-success-500';
    if (s <= 70) return 'bg-warning-500';
    return 'bg-danger-500';
  };

  const getLabel = (s) => {
    if (s <= 30) return 'LOW RISK';
    if (s <= 70) return 'MEDIUM RISK';
    return 'HIGH RISK';
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-40 h-40">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="8"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 283} 283`}
            className={`${getBgColor(score)} transition-all duration-1000 ease-out`}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${getColor(score)}`}>
            {score}
          </span>
          <span className="text-xs text-gray-500 mt-1">/ 100</span>
        </div>
      </div>
      <span className={`mt-2 font-bold text-lg ${getColor(score)}`}>
        {getLabel(score)}
      </span>
    </div>
  );
}
