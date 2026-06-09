import React, { useState } from 'react';
import { Finding } from '../../types';
import SeverityBadge from '../common/SeverityBadge';

interface FindingsTableProps {
  findings: Finding[];
}

export default function FindingsTable({ findings }: FindingsTableProps) {
  // Automatically expand the first finding by default so suggestions are visible immediately
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>(() => {
    if (findings.length > 0) {
      return { [findings[0].id]: true };
    }
    return {};
  });
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const expandAll = () => {
    const nextState: Record<string, boolean> = {};
    findings.forEach((f) => {
      nextState[f.id] = true;
    });
    setExpandedIds(nextState);
  };

  const collapseAll = () => {
    setExpandedIds({});
  };

  const handleCopy = (e: React.MouseEvent, id: string, text: string) => {
    e.stopPropagation(); // Avoid collapsing/expanding card
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (findings.length === 0) {
    return (
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-10 text-center space-y-3">
        <div className="text-3xl">🎉</div>
        <h3 className="text-lg font-semibold text-white">No security vulnerabilities detected</h3>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          The Gemini Security Auditor did not identify any deviations from Linux configuration best practices.
        </p>
      </div>
    );
  }

  const allExpanded = findings.length > 0 && findings.every((f) => expandedIds[f.id]);

  return (
    <div className="space-y-4">
      {/* Controls to expand/collapse all */}
      <div className="flex justify-end pb-1">
        <button
          onClick={allExpanded ? collapseAll : expandAll}
          className="px-3 py-1.5 text-xs font-semibold rounded-md border border-[#30363d] hover:border-[#8b949e]/30 bg-[#21262d] text-[#c9d1d9] transition-colors cursor-pointer"
        >
          {allExpanded ? 'Collapse All ▲' : 'Expand All & Show Suggestions ▼'}
        </button>
      </div>

      {findings.map((finding) => {
        const isExpanded = !!expandedIds[finding.id];
        const isCopied = copiedId === finding.id;

        return (
          <div
            key={finding.id}
            onClick={() => toggleExpand(finding.id)}
            className={`bg-[#161b22] border rounded-lg overflow-hidden transition-all duration-200 cursor-pointer ${
              isExpanded
                ? 'border-[#8b949e]/40 shadow-lg'
                : 'border-[#30363d] hover:border-[#8b949e]/20'
            }`}
          >
            {/* Finding Header */}
            <div className="p-5 flex items-center justify-between gap-4">
              <div className="flex items-center gap-4 min-w-0 flex-wrap sm:flex-nowrap">
                <SeverityBadge severity={finding.severity} />
                <h3 className="text-sm font-semibold text-white truncate min-w-0">
                  {finding.issue}
                </h3>
                {finding.fix_command && (
                  <span className="inline-flex px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    💡 Fix Suggestion Available
                  </span>
                )}
              </div>
              <div className="shrink-0 flex items-center gap-3">
                <span className="text-xs text-gray-500 font-mono">
                  {isExpanded ? 'Collapse ▲' : 'Expand ▼'}
                </span>
              </div>
            </div>

            {/* Finding Expanded Details */}
            {isExpanded && (
              <div className="px-5 pb-5 border-t border-[#30363d] pt-5 bg-[#0d1117]/50 space-y-5">
                {/* Explanation */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
                    Detailed Explanation
                  </h4>
                  <p className="text-sm text-[#8b949e] leading-relaxed">
                    {finding.explanation || 'No detailed explanation provided.'}
                  </p>
                </div>

                {/* Impact */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
                    Business / Security Impact
                  </h4>
                  <p className="text-sm text-[#8b949e] leading-relaxed">
                    {finding.impact || 'No impact analysis provided.'}
                  </p>
                </div>

                {/* Remediation Fix Command */}
                {finding.fix_command && (
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
                        Remediation Suggestion (Fix Command)
                      </h4>
                      <button
                        onClick={(e) => handleCopy(e, finding.id, finding.fix_command)}
                        className={`text-xs font-mono font-semibold px-2.5 py-1 rounded transition-colors cursor-pointer ${
                          isCopied
                            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                            : 'bg-[#21262d] text-gray-400 hover:text-white border border-[#30363d]'
                        }`}
                      >
                        {isCopied ? '✓ Copied' : '📋 Copy Command'}
                      </button>
                    </div>
                    <div className="relative">
                      <pre className="p-4 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#c9d1d9] text-xs font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed">
                        {finding.fix_command}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
