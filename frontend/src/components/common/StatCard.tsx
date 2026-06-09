import React from 'react';

interface StatCardProps {
  title: string;
  value: number | string;
  icon?: React.ReactNode;
  colorClass?: string;
  onClick?: () => void;
  active?: boolean;
}

export default function StatCard({
  title,
  value,
  icon,
  colorClass = 'text-[#58a6ff]',
  onClick,
  active = false,
}: StatCardProps) {
  return (
    <div
      onClick={onClick}
      className={`bg-[#161b22] border rounded-lg p-5 flex items-center gap-4 transition-all duration-200 select-none ${
        onClick ? 'cursor-pointer hover:bg-[#21262d]' : ''
      } ${
        active 
          ? 'border-[#1f6feb] shadow-md shadow-[#1f6feb]/15' 
          : 'border-[#30363d] hover:border-[#8b949e]/30'
      }`}
    >
      {icon && <div className="text-2xl shrink-0">{icon}</div>}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-[#8b949e]">{title}</p>
        <p className={`text-2xl font-bold mt-1 ${colorClass}`}>{value}</p>
      </div>
    </div>
  );
}
