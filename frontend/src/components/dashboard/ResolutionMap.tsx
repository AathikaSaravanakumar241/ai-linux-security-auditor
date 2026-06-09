import React, { useState } from 'react';
import { AuditComparison, ComparisonFinding } from '../../types';

interface ResolutionMapProps {
  comparison: AuditComparison;
}

export default function ResolutionMap({ comparison }: ResolutionMapProps) {
  const [activeTab, setActiveTab] = useState<'all' | 'resolved' | 'remaining' | 'new'>('all');

  const { resolved, remaining, new: newIssues, previous_audit_date } = comparison;

  const totalResolved = resolved.length;
  const totalRemaining = remaining.length;
  const totalNew = newIssues.length;

  const formattedDate = previous_audit_date
    ? new Date(previous_audit_date).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : 'unknown date';

  const renderFindingCard = (finding: ComparisonFinding, status: 'resolved' | 'remaining' | 'new') => {
    let statusBg = '';
    let statusText = '';
    let statusBorder = '';
    let icon = '';

    if (status === 'resolved') {
      statusBg = 'bg-green-500/10';
      statusText = 'text-green-400';
      statusBorder = 'border-green-500/20';
      icon = '✓';
    } else if (status === 'remaining') {
      statusBg = 'bg-orange-500/10';
      statusText = 'text-orange-400';
      statusBorder = 'border-orange-500/20';
      icon = '⚠️';
    } else {
      statusBg = 'bg-blue-500/10';
      statusText = 'text-blue-400';
      statusBorder = 'border-blue-500/20';
      icon = '🔍';
    }

    // Map severity to tag colors
    const severityColors: Record<string, string> = {
      critical: 'bg-red-500/20 text-red-400 border-red-500/30',
      high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    };

    const sevKey = finding.severity.toLowerCase();
    const sevClass = severityColors[sevKey] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';

    return (
      <div
        key={finding.issue}
        className={`p-4 bg-[#0d1117]/60 border ${statusBorder} rounded-lg flex flex-col gap-2 transition-all hover:bg-[#21262d]/20`}
      >
        <div className="flex justify-between items-start gap-2">
          <div className="flex items-center gap-2">
            <span className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-xs ${statusBg} ${statusText}`}>
              {icon}
            </span>
            <span className="font-semibold text-white text-sm">{finding.issue}</span>
          </div>
          <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase border ${sevClass}`}>
            {finding.severity}
          </span>
        </div>
        
        {finding.explanation && (
          <p className="text-xs text-gray-400 pl-7 leading-relaxed">{finding.explanation}</p>
        )}

        {status === 'remaining' && finding.fix_command && (
          <div className="mt-2 pl-7">
            <div className="text-[10px] text-gray-500 uppercase font-mono mb-1">Fix Command:</div>
            <pre className="p-2 bg-[#0d1117] border border-[#30363d] rounded text-[10.5px] font-mono text-[#8b949e] overflow-x-auto whitespace-pre-wrap leading-tight">
              {finding.fix_command}
            </pre>
          </div>
        )}
      </div>
    );
  };

  const getFilteredFindings = () => {
    switch (activeTab) {
      case 'resolved':
        return resolved.map(f => ({ ...f, status: 'resolved' as const }));
      case 'remaining':
        return remaining.map(f => ({ ...f, status: 'remaining' as const }));
      case 'new':
        return newIssues.map(f => ({ ...f, status: 'new' as const }));
      default:
        return [
          ...newIssues.map(f => ({ ...f, status: 'new' as const })),
          ...remaining.map(f => ({ ...f, status: 'remaining' as const })),
          ...resolved.map(f => ({ ...f, status: 'resolved' as const })),
        ];
    }
  };

  const filtered = getFilteredFindings();

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6 shadow-lg space-y-6">
      {/* Header info */}
      <div className="border-b border-[#30363d] pb-4 flex flex-col md:flex-row md:items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            🔄 Resolution Checklist Map
          </h2>
          <p className="text-xs text-[#8b949e] mt-1 font-mono">
            Compared against previous server audit from <span className="text-gray-300 font-semibold">{formattedDate}</span>
          </p>
        </div>
        
        {/* Quick statistics */}
        <div className="flex gap-2">
          <div className="px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-lg text-center font-mono">
            <div className="text-xs text-green-400 font-bold">{totalResolved}</div>
            <div className="text-[9px] text-gray-500 uppercase">Resolved</div>
          </div>
          <div className="px-3 py-1 bg-orange-500/10 border border-orange-500/20 rounded-lg text-center font-mono">
            <div className="text-xs text-orange-400 font-bold">{totalRemaining}</div>
            <div className="text-[9px] text-gray-500 uppercase">Remaining</div>
          </div>
          <div className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-lg text-center font-mono">
            <div className="text-xs text-blue-400 font-bold">{totalNew}</div>
            <div className="text-[9px] text-gray-500 uppercase">New</div>
          </div>
        </div>
      </div>

      {/* Tabs selector */}
      <div className="flex border-b border-[#30363d] gap-2">
        <button
          onClick={() => setActiveTab('all')}
          className={`pb-2 px-3 text-xs font-semibold border-b-2 cursor-pointer transition-colors ${
            activeTab === 'all'
              ? 'border-[#58a6ff] text-white'
              : 'border-transparent text-gray-500 hover:text-gray-300'
          }`}
        >
          All Comparison ({totalResolved + totalRemaining + totalNew})
        </button>
        <button
          onClick={() => setActiveTab('resolved')}
          className={`pb-2 px-3 text-xs font-semibold border-b-2 cursor-pointer transition-colors ${
            activeTab === 'resolved'
              ? 'border-green-500 text-green-400'
              : 'border-transparent text-gray-500 hover:text-green-500/70'
          }`}
        >
          Resolved 🎉 ({totalResolved})
        </button>
        <button
          onClick={() => setActiveTab('remaining')}
          className={`pb-2 px-3 text-xs font-semibold border-b-2 cursor-pointer transition-colors ${
            activeTab === 'remaining'
              ? 'border-orange-500 text-orange-400'
              : 'border-transparent text-gray-500 hover:text-orange-500/70'
          }`}
        >
          Remaining ⚠️ ({totalRemaining})
        </button>
        <button
          onClick={() => setActiveTab('new')}
          className={`pb-2 px-3 text-xs font-semibold border-b-2 cursor-pointer transition-colors ${
            activeTab === 'new'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-500 hover:text-blue-500/70'
          }`}
        >
          New Issues 🔍 ({totalNew})
        </button>
      </div>

      {/* Checklist items list */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="py-6 text-center text-gray-500 text-xs font-mono">
            No items in this category.
          </div>
        ) : (
          filtered.map(item => renderFindingCard(item, item.status))
        )}
      </div>
    </div>
  );
}
