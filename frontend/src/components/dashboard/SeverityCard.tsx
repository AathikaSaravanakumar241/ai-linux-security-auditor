import React from 'react';

interface SeverityCardProps {
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  count: number;
  active: boolean;
  onClick: () => void;
}

const colorMap = {
  Critical: {
    bg: 'bg-red-500/10 hover:bg-red-500/15',
    border: 'border-red-500/30',
    activeBorder: 'border-red-500 ring-2 ring-red-500/20',
    text: 'text-red-400',
    title: 'Critical Severity',
    icon: '🚨',
  },
  High: {
    bg: 'bg-orange-500/10 hover:bg-orange-500/15',
    border: 'border-orange-500/30',
    activeBorder: 'border-orange-500 ring-2 ring-orange-500/20',
    text: 'text-orange-400',
    title: 'High Severity',
    icon: '⚠️',
  },
  Medium: {
    bg: 'bg-yellow-500/10 hover:bg-yellow-500/15',
    border: 'border-yellow-500/30',
    activeBorder: 'border-yellow-500 ring-2 ring-yellow-500/20',
    text: 'text-yellow-400',
    title: 'Medium Severity',
    icon: '⚡',
  },
  Low: {
    bg: 'bg-blue-500/10 hover:bg-blue-500/15',
    border: 'border-blue-500/30',
    activeBorder: 'border-blue-500 ring-2 ring-blue-500/20',
    text: 'text-blue-400',
    title: 'Low Severity',
    icon: 'ℹ️',
  },
};

export default function SeverityCard({ severity, count, active, onClick }: SeverityCardProps) {
  const styles = colorMap[severity];

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left p-5 rounded-lg border transition-all duration-200 cursor-pointer ${styles.bg} ${
        active ? styles.activeBorder : `${styles.border} hover:border-[#8b949e]/30`
      }`}
    >
      <div className="flex justify-between items-start">
        <div className="text-xl">{styles.icon}</div>
        <span className="text-xs font-mono font-semibold text-[#8b949e] uppercase tracking-wider">
          Filter
        </span>
      </div>
      <div className="mt-4">
        <p className="text-xs font-semibold text-[#8b949e] uppercase tracking-wider">{styles.title}</p>
        <p className={`text-3xl font-bold mt-1 ${styles.text}`}>{count}</p>
      </div>
    </button>
  );
}
