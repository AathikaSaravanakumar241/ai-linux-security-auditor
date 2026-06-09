import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import StatCard from '../components/common/StatCard';
import { useAudit } from '../hooks/useAudit';
import { AuditSummary } from '../types';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function DashboardPage() {
  const { fetchAudits, loading } = useAudit();
  const [audits, setAudits] = useState<AuditSummary[]>([]);

  useEffect(() => {
    fetchAudits(100, 0)
      .then((data) => setAudits(data))
      .catch((err) => console.error('Failed to load dashboard data:', err));
  }, [fetchAudits]);

  // Aggregate stats across all audits
  const stats = React.useMemo(() => {
    let critical = 0;
    let high = 0;
    let medium = 0;
    let low = 0;

    audits.forEach((a) => {
      critical += a.severity_breakdown.critical;
      high += a.severity_breakdown.high;
      medium += a.severity_breakdown.medium;
      low += a.severity_breakdown.low;
    });

    return { critical, high, medium, low };
  }, [audits]);

  const recentAudits = React.useMemo(() => {
    return audits.slice(0, 5);
  }, [audits]);

  if (loading && audits.length === 0) {
    return <LoadingSpinner message="Calculating dashboard statistics..." />;
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6 border-b border-[#30363d] pb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            🛡️ Security Dashboard
          </h1>
          <p className="text-[#8b949e] mt-2 text-sm">
            Operational status and vulnerabilities metrics aggregated from target audits.
          </p>
        </div>
        <Link
          to="/audit/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#238636] hover:bg-[#2ea043] text-white font-semibold rounded-lg text-sm transition-colors shadow-md shadow-green-500/10 cursor-pointer"
        >
          🔍 Run Security Scan
        </Link>
      </div>

      {/* Aggregate metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Critical issues"
          value={stats.critical}
          icon={<span className="text-red-500">🚨</span>}
          colorClass="text-red-400"
        />
        <StatCard
          title="Total High issues"
          value={stats.high}
          icon={<span className="text-orange-500">⚠️</span>}
          colorClass="text-orange-400"
        />
        <StatCard
          title="Total Medium issues"
          value={stats.medium}
          icon={<span className="text-yellow-500">⚡</span>}
          colorClass="text-yellow-400"
        />
        <StatCard
          title="Total Low issues"
          value={stats.low}
          icon={<span className="text-blue-500">ℹ️</span>}
          colorClass="text-blue-400"
        />
      </div>

      {/* Recent scanner runs feed */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6 shadow-lg">
        <div className="flex justify-between items-center mb-6 border-b border-[#30363d] pb-3">
          <h2 className="text-lg font-semibold text-white">Recent Audits</h2>
          {audits.length > 5 && (
            <Link to="/history" className="text-xs text-[#58a6ff] hover:underline">
              View History →
            </Link>
          )}
        </div>

        {recentAudits.length === 0 ? (
          <div className="py-12 text-center text-[#8b949e] space-y-3 font-mono text-xs">
            <p>No scans found in database logs.</p>
            <p className="text-gray-600">Click the button above to execute your first security check.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentAudits.map((audit) => {
              const formattedDate = new Date(audit.audit_date).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              });

              return (
                <div
                  key={audit.id}
                  className="p-4 bg-[#0d1117]/60 border border-[#30363d] hover:border-[#8b949e]/30 rounded-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 transition-all"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-white font-semibold">{audit.server_ip}</span>
                      <span className="text-[10px] text-gray-500 font-mono">
                        (AUDIT-{audit.id.slice(0, 8).toUpperCase()})
                      </span>
                    </div>
                    <p className="text-xs text-[#8b949e] font-mono">Date: {formattedDate}</p>
                  </div>

                  {/* Findings breakdown indicators */}
                  <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
                    <div className="flex gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-500/10 text-red-400 border border-red-500/20">
                        C: {audit.severity_breakdown.critical}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">
                        H: {audit.severity_breakdown.high}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                        M: {audit.severity_breakdown.medium}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        L: {audit.severity_breakdown.low}
                      </span>
                    </div>
                    
                    <Link
                      to={`/audit/${audit.id}`}
                      className="px-3 py-1 bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] rounded text-xs text-[#c9d1d9] font-medium transition-colors"
                    >
                      Report
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
