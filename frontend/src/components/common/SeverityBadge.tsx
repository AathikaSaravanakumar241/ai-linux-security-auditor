import React from 'react';

interface SeverityBadgeProps {
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | string;
}

const colorMap: Record<string, string> = {
  Critical: 'bg-red-500/10 text-red-400 border-red-500/30 shadow-sm shadow-red-500/5',
  High: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  Medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  Low: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
};

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  const normalized = severity.trim().charAt(0).toUpperCase() + severity.trim().slice(1).toLowerCase();
  const classes = colorMap[normalized] || 'bg-gray-500/10 text-gray-400 border-gray-500/30';

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${classes}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
        normalized === 'Critical' ? 'bg-red-400' :
        normalized === 'High' ? 'bg-orange-400' :
        normalized === 'Medium' ? 'bg-yellow-400' :
        normalized === 'Low' ? 'bg-blue-400' : 'bg-gray-400'
      }`}></span>
      {normalized}
    </span>
  );
}
