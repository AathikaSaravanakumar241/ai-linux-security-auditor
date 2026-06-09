import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuditForm from '../components/audit/AuditForm';
import { useAudit } from '../hooks/useAudit';
import { AuditRequest } from '../types';

export default function NewAuditPage() {
  const navigate = useNavigate();
  const { runAudit, loading, error } = useAudit();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (credentials: AuditRequest) => {
    setErrorMessage(null);
    try {
      const result = await runAudit(credentials);
      if (result && result.audit_id) {
        navigate(`/audit/${result.audit_id}`);
      } else {
        setErrorMessage('Audit completed, but no audit ID was returned.');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to complete remote server security audit.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-4">
      {/* Header section */}
      <div className="mb-8 border-b border-[#30363d] pb-6">
        <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          🔍 Initiate Server Security Audit
        </h1>
        <p className="text-[#8b949e] mt-2 text-sm leading-relaxed">
          Provide connection credentials to run automated security configuration checks on a target Linux server.
          The auditor will scan settings, count vulnerability vectors, and use Google Gemini AI for remediation recommendations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
        {/* Form Container */}
        <div className="md:col-span-2 bg-[#161b22] border border-[#30363d] rounded-lg p-6 shadow-xl">
          <h2 className="text-lg font-semibold text-white mb-6 border-b border-[#30363d] pb-3">
            Target Connection Details
          </h2>
          
          {error && (
            <div className="p-4 mb-6 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400 font-mono">
              <strong>Error:</strong> {errorMessage || error}
            </div>
          )}

          {errorMessage && !error && (
            <div className="p-4 mb-6 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400 font-mono">
              <strong>Audit Error:</strong> {errorMessage}
            </div>
          )}

          <AuditForm onSubmit={handleSubmit} isLoading={loading} />
        </div>

        {/* Audit Progress/Info panel */}
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6 space-y-6">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider border-b border-[#30363d] pb-3">
            Security Scan Scope
          </h3>
          
          <div className="space-y-4 text-xs font-mono text-[#8b949e]">
            <div className="flex items-start gap-2">
              <span className="text-green-500">✔</span>
              <span>SSH Port Configuration (Root login, password authentication)</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-500">✔</span>
              <span>Authentication Controls (Max attempts, expiration policies)</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-500">✔</span>
              <span>Network Firewall (UFW firewall rules audit)</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-500">✔</span>
              <span>System Telemetry (Kernel version, active user checks)</span>
            </div>
          </div>

          <div className="p-4 bg-[#0d1117] border border-[#30363d] rounded-lg space-y-2">
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
              ℹ️ Pipeline Notes
            </h4>
            <p className="text-[11px] text-[#8b949e] leading-relaxed">
              Audits typically take between 10 to 45 seconds to finish, depending on SSH connection speed and Google Gemini API analysis queues.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
