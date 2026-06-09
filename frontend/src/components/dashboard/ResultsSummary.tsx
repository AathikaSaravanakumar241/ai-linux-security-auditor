import React from 'react';
import { SeverityBreakdown } from '../../types';

interface ResultsSummaryProps {
  serverIp: string;
  auditDate: string;
  totalFindings: number;
  severityBreakdown: SeverityBreakdown;
}

export default function ResultsSummary({
  serverIp,
  auditDate,
  totalFindings,
  severityBreakdown,
}: ResultsSummaryProps) {
  const formattedDate = new Date(auditDate).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  // Calculate a basic security health index score:
  // Starts at 100. Subtract 25 for Critical, 15 for High, 5 for Medium, 1 for Low.
  // Clamp score between 0 and 100.
  const score = Math.max(
    0,
    100 -
      (severityBreakdown.critical * 25 +
        severityBreakdown.high * 15 +
        severityBreakdown.medium * 5 +
        severityBreakdown.low * 1)
  );

  let healthLabel = 'Excellent';
  let healthColor = 'text-green-400';
  let progressBg = 'bg-green-500';
  if (score < 50) {
    healthLabel = 'Poor / Critical';
    healthColor = 'text-red-400';
    progressBg = 'bg-red-500';
  } else if (score < 75) {
    healthLabel = 'Fair / Warning';
    healthColor = 'text-orange-400';
    progressBg = 'bg-orange-500';
  } else if (score < 95) {
    healthLabel = 'Good';
    healthColor = 'text-yellow-400';
    progressBg = 'bg-yellow-500';
  }

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6 flex flex-col md:flex-row gap-8 justify-between items-start md:items-center shadow-lg">
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🖥️</span>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">{serverIp}</h2>
            <p className="text-xs font-mono text-[#8b949e]">AUDITED: {formattedDate}</p>
          </div>
        </div>
        <div className="flex gap-4 mt-2">
          <div className="text-xs text-[#8b949e]">
            Total Vulnerability Vectors: <span className="text-white font-semibold">{totalFindings}</span>
          </div>
        </div>
      </div>

      {/* Security Score Panel */}
      <div className="w-full md:w-64 bg-[#0d1117] border border-[#30363d] rounded-lg p-4 flex flex-col justify-center">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#8b949e]">
            Security Rating
          </span>
          <span className={`text-xs font-mono font-bold ${healthColor}`}>
            {healthLabel}
          </span>
        </div>
        
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-extrabold text-white">{score}</span>
          <span className="text-xs text-gray-500">/ 100</span>
        </div>

        {/* Score slider bar */}
        <div className="w-full bg-[#30363d] h-2 rounded-full mt-3 overflow-hidden">
          <div
            className={`${progressBg} h-full transition-all duration-500`}
            style={{ width: `${score}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
