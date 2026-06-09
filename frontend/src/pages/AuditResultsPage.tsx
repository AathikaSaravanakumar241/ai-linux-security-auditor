import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAudit } from '../hooks/useAudit';
import { AuditDetail, Finding, AuditComparison } from '../types';
import ResultsSummary from '../components/dashboard/ResultsSummary';
import SeverityCard from '../components/dashboard/SeverityCard';
import FindingsTable from '../components/dashboard/FindingsTable';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ResolutionMap from '../components/dashboard/ResolutionMap';

export default function AuditResultsPage() {
  const { id } = useParams<{ id: string }>();
  const { fetchAudit, fetchComparison, loading, error } = useAudit();
  const [auditData, setAuditData] = useState<AuditDetail | null>(null);
  const [comparisonData, setComparisonData] = useState<AuditComparison | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string | null>(null);
  const [showRawReport, setShowRawReport] = useState<boolean>(false);

  useEffect(() => {
    if (id) {
      setAuditData(null);
      setComparisonData(null);
      fetchAudit(id)
        .then((data) => {
          setAuditData(data);
          fetchComparison(id)
            .then((comp) => setComparisonData(comp))
            .catch((err) => console.error('Failed to load comparison:', err));
        })
        .catch((err) => console.error('Failed to load audit:', err));
    }
  }, [id, fetchAudit, fetchComparison]);

  const toggleSeverityFilter = (severity: string) => {
    if (severityFilter === severity) {
      setSeverityFilter(null); // Reset filter
    } else {
      setSeverityFilter(severity);
    }
  };

  if (loading) {
    return (
      <LoadingSpinner
        message="Analyzing security configurations"
        subMessage="Decrypting audit results and formatting intelligence telemetry reports..."
      />
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto py-10 space-y-6">
        <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-lg text-center space-y-4">
          <div className="text-4xl">🚨</div>
          <h2 className="text-xl font-bold text-white">Execution Failure</h2>
          <p className="text-sm text-gray-400 font-mono">
            {error}
          </p>
          <div className="pt-4">
            <Link
              to="/audit/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#21262d] border border-[#30363d] hover:border-[#8b949e]/30 text-white font-medium rounded-lg text-sm transition-colors cursor-pointer"
            >
              ← Back to New Audit
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!auditData) {
    return (
      <div className="text-center py-20 text-[#8b949e]">
        No audit record found for ID: {id}
      </div>
    );
  }

  // Filter findings based on selected severity card
  const filteredFindings = severityFilter
    ? auditData.findings.filter((f) => f.severity.toLowerCase() === severityFilter.toLowerCase())
    : auditData.findings;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header breadcrumbs */}
      <div className="flex justify-between items-center border-b border-[#30363d] pb-6">
        <div>
          <div className="text-xs font-mono text-gray-500 mb-1 flex items-center gap-1.5">
            <Link to="/history" className="hover:text-white transition-colors">HISTORY</Link>
            <span>/</span>
            <span>AUDIT-{auditData.id.slice(0, 8).toUpperCase()}</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Vulnerability Scanner Report
          </h1>
        </div>
        <Link
          to="/audit/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-[#21262d] border border-[#30363d] hover:border-[#8b949e]/30 text-white font-medium rounded-lg text-sm transition-colors cursor-pointer"
        >
          ➕ Run Another Scan
        </Link>
      </div>

      {/* Server summary card */}
      <ResultsSummary
        serverIp={auditData.server_ip}
        auditDate={auditData.audit_date}
        totalFindings={auditData.findings.length}
        severityBreakdown={auditData.severity_breakdown}
      />

      {/* Resolution Checklist Map */}
      {comparisonData && (comparisonData.resolved.length > 0 || comparisonData.remaining.length > 0 || comparisonData.new.length > 0) && (
        <ResolutionMap comparison={comparisonData} />
      )}

      {/* Severity breakdown filter cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <SeverityCard
          severity="Critical"
          count={auditData.severity_breakdown.critical}
          active={severityFilter === 'Critical'}
          onClick={() => toggleSeverityFilter('Critical')}
        />
        <SeverityCard
          severity="High"
          count={auditData.severity_breakdown.high}
          active={severityFilter === 'High'}
          onClick={() => toggleSeverityFilter('High')}
        />
        <SeverityCard
          severity="Medium"
          count={auditData.severity_breakdown.medium}
          active={severityFilter === 'Medium'}
          onClick={() => toggleSeverityFilter('Medium')}
        />
        <SeverityCard
          severity="Low"
          count={auditData.severity_breakdown.low}
          active={severityFilter === 'Low'}
          onClick={() => toggleSeverityFilter('Low')}
        />
      </div>

      {/* Findings details section */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-white">
            {severityFilter ? `${severityFilter} Severity ` : 'All '} Discovered Findings ({filteredFindings.length})
          </h2>
          {severityFilter && (
            <button
              onClick={() => setSeverityFilter(null)}
              className="text-xs text-[#58a6ff] hover:underline cursor-pointer bg-transparent border-none"
            >
              Clear Filter
            </button>
          )}
        </div>

        <FindingsTable findings={filteredFindings} />
      </div>

      {/* Raw Command Output log collector */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
        <button
          type="button"
          onClick={() => setShowRawReport(!showRawReport)}
          className="w-full p-5 flex items-center justify-between text-left font-semibold text-white bg-[#161b22] border-none cursor-pointer hover:bg-[#21262d] transition-colors"
        >
          <span className="flex items-center gap-2">
            🗒️ View Raw System Configuration Logs
          </span>
          <span className="text-xs text-gray-500 font-mono">
            {showRawReport ? 'Hide Logs ▲' : 'Show Logs ▼'}
          </span>
        </button>

        {showRawReport && (
          <div className="p-5 border-t border-[#30363d] bg-[#0d1117]/50">
            <pre className="p-4 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#8b949e] text-xs font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-[500px]">
              {auditData.raw_report || 'No raw configuration log available.'}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
