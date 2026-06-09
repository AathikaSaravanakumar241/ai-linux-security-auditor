import React, { useState } from 'react';
import { AuditRequest } from '../../types';

interface AuditFormProps {
  onSubmit: (data: AuditRequest) => void;
  isLoading: boolean;
}

export default function AuditForm({ onSubmit, isLoading }: AuditFormProps) {
  const [formData, setFormData] = useState<AuditRequest>({
    server_ip: '',
    port: 22,
    username: '',
    password: '',
  });

  const [validationError, setValidationError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'port' ? (value ? parseInt(value, 10) : '') : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Basic Validation
    const ipPattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
    const hostPattern = /^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])$/;
    const isIp = ipPattern.test(formData.server_ip);
    const isHostname = hostPattern.test(formData.server_ip) || formData.server_ip === 'localhost';

    if (!formData.server_ip) {
      setValidationError('Server IP or Hostname is required.');
      return;
    }

    if (!isIp && !isHostname) {
      setValidationError('Please enter a valid IP address or Hostname.');
      return;
    }

    if (!formData.port || formData.port < 1 || formData.port > 65535) {
      setValidationError('Port must be a number between 1 and 65535.');
      return;
    }

    if (!formData.username.trim()) {
      setValidationError('SSH Username is required.');
      return;
    }

    if (!formData.password) {
      setValidationError('SSH Password is required.');
      return;
    }

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {validationError && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400 font-mono">
          ⚠️ {validationError}
        </div>
      )}

      {/* Host / Server IP Input */}
      <div>
        <label htmlFor="server_ip" className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
          Server IP Address / Hostname
        </label>
        <div className="relative">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-500">
            🖥️
          </span>
          <input
            id="server_ip"
            name="server_ip"
            type="text"
            required
            disabled={isLoading}
            placeholder="e.g. 192.168.1.15 or localhost"
            value={formData.server_ip}
            onChange={handleChange}
            className="w-full pl-10 pr-4 py-2.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#1f6feb] focus:ring-1 focus:ring-[#1f6feb] transition-colors disabled:opacity-50"
          />
        </div>
      </div>

      {/* Port Input */}
      <div>
        <label htmlFor="port" className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
          SSH Port
        </label>
        <div className="relative">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-500">
            🔌
          </span>
          <input
            id="port"
            name="port"
            type="number"
            min={1}
            max={65535}
            required
            disabled={isLoading}
            value={formData.port}
            onChange={handleChange}
            className="w-full pl-10 pr-4 py-2.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#1f6feb] focus:ring-1 focus:ring-[#1f6feb] transition-colors disabled:opacity-50"
          />
        </div>
      </div>

      {/* Username Input */}
      <div>
        <label htmlFor="username" className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
          SSH Username
        </label>
        <div className="relative">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-500">
            👤
          </span>
          <input
            id="username"
            name="username"
            type="text"
            required
            disabled={isLoading}
            placeholder="e.g. root or ubuntu"
            value={formData.username}
            onChange={handleChange}
            className="w-full pl-10 pr-4 py-2.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#1f6feb] focus:ring-1 focus:ring-[#1f6feb] transition-colors disabled:opacity-50"
          />
        </div>
      </div>

      {/* Password Input */}
      <div>
        <label htmlFor="password" className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
          SSH Password
        </label>
        <div className="relative">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-gray-500">
            🔑
          </span>
          <input
            id="password"
            name="password"
            type="password"
            required
            disabled={isLoading}
            placeholder="••••••••••••"
            value={formData.password}
            onChange={handleChange}
            className="w-full pl-10 pr-4 py-2.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#1f6feb] focus:ring-1 focus:ring-[#1f6feb] transition-colors disabled:opacity-50"
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex items-center justify-center gap-2 py-3 bg-[#238636] hover:bg-[#2ea043] disabled:bg-[#238636]/50 text-white font-semibold rounded-lg transition-all shadow-md shadow-green-500/10 cursor-pointer disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Running Audit Pipeline...
          </>
        ) : (
          <>
            🛡️ Start Security Audit
          </>
        )}
      </button>
    </form>
  );
}
