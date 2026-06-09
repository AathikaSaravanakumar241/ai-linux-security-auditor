import React from 'react';

interface HistoryFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedSeverity: string;
  onSeverityChange: (severity: string) => void;
}

export default function HistoryFilters({
  searchQuery,
  onSearchChange,
  selectedSeverity,
  onSeverityChange,
}: HistoryFiltersProps) {
  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-5 flex flex-col md:flex-row gap-4 items-center justify-between shadow-md">
      {/* Search Input */}
      <div className="w-full md:w-96 relative">
        <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-500">
          🔍
        </span>
        <input
          type="text"
          placeholder="Search by Server IP / Hostname..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-[#0d1117] border border-[#30363d] rounded-md text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#1f6feb] text-sm font-mono"
        />
      </div>

      {/* Severity Filter Dropdown */}
      <div className="w-full md:w-auto flex items-center gap-3 shrink-0">
        <span className="text-xs font-semibold text-[#8b949e] uppercase tracking-wider whitespace-nowrap">
          Filter Severity:
        </span>
        <select
          value={selectedSeverity}
          onChange={(e) => onSeverityChange(e.target.value)}
          className="bg-[#0d1117] border border-[#30363d] rounded-md text-[#c9d1d9] px-3 py-2 text-sm focus:outline-none focus:border-[#1f6feb] cursor-pointer"
        >
          <option value="All">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>

        {(searchQuery || selectedSeverity !== 'All') && (
          <button
            onClick={() => {
              onSearchChange('');
              onSeverityChange('All');
            }}
            className="text-xs text-[#58a6ff] hover:underline cursor-pointer bg-transparent border-none"
          >
            Reset
          </button>
        )}
      </div>
    </div>
  );
}
