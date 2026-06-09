import React from 'react';
import { Link } from 'react-router-dom';
import { AuditSummary } from '../../types';

interface HistoryTableProps {
  audits: AuditSummary[];
  sortColumn: 'server_ip' | 'audit_date';
  sortDirection: 'asc' | 'desc';
  onSort: (column: 'server_ip' | 'audit_date') => void;
}

export default function HistoryTable({
  audits,
  sortColumn,
  sortDirection,
  onSort,
}: HistoryTableProps) {
  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  };

  const renderSortIndicator = (column: 'server_ip' | 'audit_date') => {
    if (sortColumn !== column) return null;
    return sortDirection === 'asc' ? ' ▴' : ' ▾';
  };

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden shadow-md">
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left border-collapse">
          <thead>
            <tr className="bg-[#0d1117]/80 border-b border-[#30363d] text-[#8b949e]">
              <th
                onClick={() => onSort('server_ip')}
                className="py-3.5 px-5 font-semibold uppercase tracking-wider text-xs cursor-pointer select-none hover:text-white transition-colors"
              >
                Server IP {renderSortIndicator('server_ip')}
              </th>
              <th
                onClick={() => onSort('audit_date')}
                className="py-3.5 px-5 font-semibold uppercase tracking-wider text-xs cursor-pointer select-none hover:text-white transition-colors"
              >
                Audit Date {renderSortIndicator('audit_date')}
              </th>
              <th className="py-3.5 px-5 font-semibold uppercase tracking-wider text-xs text-center">
                Critical
              </th>
              <th className="py-3.5 px-5 font-semibold uppercase tracking-wider text-xs text-center">
                High
              </th>
              <th className="py-3.5 px-5 font-semibold uppercase tracking-wider text-xs text-center">
                Medium
              </th>
              <th className="py-3.5 px-5 font-semibold uppercase tracking-wider text-xs text-center">
                Low
              </th>
              <th className="py-3.5 px-5 font-semibold uppercase tracking-wider text-xs text-right">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#30363d]">
            {audits.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-[#8b949e] font-mono text-xs">
                  No audits found matching the criteria. Run a new audit to generate scanner records.
                </td>
              </tr>
            ) : (
              audits.map((audit) => (
                <tr
                  key={audit.id}
                  className="hover:bg-[#21262d]/40 transition-colors"
                >
                  {/* IP Address */}
                  <td className="py-4 px-5 font-mono text-white font-semibold">
                    {audit.server_ip}
                  </td>
                  {/* Date */}
                  <td className="py-4 px-5 text-gray-400 font-mono text-xs">
                    {formatTime(audit.audit_date)}
                  </td>
                  {/* Critical count badge */}
                  <td className="py-4 px-5 text-center">
                    <span className={`inline-block w-8 py-0.5 rounded font-mono text-xs font-bold ${
                      audit.severity_breakdown.critical > 0
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'bg-transparent text-gray-600 border border-transparent'
                    }`}>
                      {audit.severity_breakdown.critical}
                    </span>
                  </td>
                  {/* High count badge */}
                  <td className="py-4 px-5 text-center">
                    <span className={`inline-block w-8 py-0.5 rounded font-mono text-xs font-bold ${
                      audit.severity_breakdown.high > 0
                        ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                        : 'bg-transparent text-gray-600 border border-transparent'
                    }`}>
                      {audit.severity_breakdown.high}
                    </span>
                  </td>
                  {/* Medium count badge */}
                  <td className="py-4 px-5 text-center">
                    <span className={`inline-block w-8 py-0.5 rounded font-mono text-xs font-bold ${
                      audit.severity_breakdown.medium > 0
                        ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                        : 'bg-transparent text-gray-600 border border-transparent'
                    }`}>
                      {audit.severity_breakdown.medium}
                    </span>
                  </td>
                  {/* Low count badge */}
                  <td className="py-4 px-5 text-center">
                    <span className={`inline-block w-8 py-0.5 rounded font-mono text-xs font-bold ${
                      audit.severity_breakdown.low > 0
                        ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                        : 'bg-transparent text-gray-600 border border-transparent'
                    }`}>
                      {audit.severity_breakdown.low}
                    </span>
                  </td>
                  {/* Action link */}
                  <td className="py-4 px-5 text-right">
                    <Link
                      to={`/audit/${audit.id}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-[#58a6ff] hover:text-[#79c0ff] hover:underline"
                    >
                      View Report
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
