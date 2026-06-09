import React, { useEffect, useState, useMemo } from 'react';
import { useAudit } from '../hooks/useAudit';
import { AuditSummary } from '../types';
import HistoryFilters from '../components/audit/HistoryFilters';
import HistoryTable from '../components/audit/HistoryTable';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function AuditHistoryPage() {
  const { fetchAudits, loading, error } = useAudit();
  const [audits, setAudits] = useState<AuditSummary[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortColumn, setSortColumn] = useState<'server_ip' | 'audit_date'>('audit_date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    // Fetch a generous page size from the backend so we can filter/sort client-side smoothly
    fetchAudits(200, 0)
      .then((data) => setAudits(data))
      .catch((err) => console.error('Failed to load audit logs:', err));
  }, [fetchAudits]);

  const handleSort = (column: 'server_ip' | 'audit_date') => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  // Filter and sort findings
  const processedAudits = useMemo(() => {
    let result = [...audits];

    // 1. Search Query Filter (Server IP)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter((a) => a.server_ip.toLowerCase().includes(q));
    }

    // 2. Severity Count Filter
    if (selectedSeverity !== 'All') {
      const severityKey = selectedSeverity.toLowerCase() as keyof typeof AuditSummary.prototype.severity_breakdown;
      result = result.filter((a) => {
        const counts = a.severity_breakdown;
        if (severityKey === 'critical') return counts.critical > 0;
        if (severityKey === 'high') return counts.high > 0;
        if (severityKey === 'medium') return counts.medium > 0;
        if (severityKey === 'low') return counts.low > 0;
        return true;
      });
    }

    // 3. Sorting
    result.sort((a, b) => {
      let valA = a[sortColumn];
      let valB = b[sortColumn];

      if (sortColumn === 'audit_date') {
        const timeA = new Date(valA).getTime();
        const timeB = new Date(valB).getTime();
        return sortDirection === 'asc' ? timeA - timeB : timeB - timeA;
      } else {
        // String sorting for server_ip
        valA = String(valA).toLowerCase();
        valB = String(valB).toLowerCase();
        if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
        if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      }
    });

    return result;
  }, [audits, searchQuery, selectedSeverity, sortColumn, sortDirection]);

  // Pagination calculations
  const totalItems = processedAudits.length;
  const totalPages = Math.ceil(totalItems / pageSize) || 1;
  
  // Reset page if filters change the item counts
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedSeverity, pageSize]);

  const paginatedAudits = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return processedAudits.slice(startIndex, startIndex + pageSize);
  }, [processedAudits, currentPage, pageSize]);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header section */}
      <div className="mb-6 border-b border-[#30363d] pb-6">
        <h1 className="text-3xl font-bold text-white tracking-tight">
          📜 Audit Execution Logs
        </h1>
        <p className="text-[#8b949e] mt-2 text-sm">
          Browse, search, and filter previous scanner runs executed against your Linux target server profiles.
        </p>
      </div>

      {/* Filter panel */}
      <HistoryFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedSeverity={selectedSeverity}
        onSeverityChange={setSelectedSeverity}
      />

      {loading ? (
        <LoadingSpinner message="Retrieving execution history..." />
      ) : error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400 font-mono">
          <strong>Database Query Failure:</strong> {error}
        </div>
      ) : (
        <div className="space-y-4">
          {/* Main Table */}
          <HistoryTable
            audits={paginatedAudits}
            sortColumn={sortColumn}
            sortDirection={sortDirection}
            onSort={handleSort}
          />

          {/* Pagination controls footer */}
          {totalItems > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-2 text-xs font-mono text-[#8b949e]">
              <div className="flex items-center gap-2">
                <span>Show</span>
                <select
                  value={pageSize}
                  onChange={(e) => setPageSize(parseInt(e.target.value, 10))}
                  className="bg-[#161b22] border border-[#30363d] rounded text-[#c9d1d9] px-2 py-1 focus:outline-none cursor-pointer"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                </select>
                <span>items per page (Total results: {totalItems})</span>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1.5 bg-[#161b22] hover:bg-[#21262d] border border-[#30363d] rounded text-[#c9d1d9] disabled:opacity-30 disabled:hover:bg-[#161b22] disabled:cursor-not-allowed cursor-pointer"
                >
                  ◀ Prev
                </button>
                <span>
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1.5 bg-[#161b22] hover:bg-[#21262d] border border-[#30363d] rounded text-[#c9d1d9] disabled:opacity-30 disabled:hover:bg-[#161b22] disabled:cursor-not-allowed cursor-pointer"
                >
                  Next ▶
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
