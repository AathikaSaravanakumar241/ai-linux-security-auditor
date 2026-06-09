import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('password');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate login persistence and navigation
    setTimeout(() => {
      setIsLoading(false);
      localStorage.setItem('auth_token', 'simulated_jwt_token_key');
      navigate('/dashboard');
    }, 600);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d1117] p-4 text-[#c9d1d9]">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex w-12 h-12 rounded bg-[#1f6feb] items-center justify-center font-bold text-2xl text-white shadow-xl shadow-blue-500/20 mb-4 animate-bounce">
            🛡️
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-wider">
            SECURITY AUDITOR
          </h1>
          <p className="text-[#8b949e] mt-2 text-sm uppercase tracking-widest font-mono">
            AI-Powered Operations
          </p>
        </div>

        {/* Form panel */}
        <form
          onSubmit={handleSubmit}
          className="bg-[#161b22] border border-[#30363d] rounded-lg p-8 space-y-6 shadow-2xl"
        >
          <div>
            <label htmlFor="login-email" className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
              Operator Email Address
            </label>
            <input
              id="login-email"
              type="email"
              required
              disabled={isLoading}
              placeholder="admin@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#1f6feb] focus:ring-1 focus:ring-[#1f6feb] transition-colors disabled:opacity-50"
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
              Security Key Password
            </label>
            <input
              id="login-password"
              type="password"
              required
              disabled={isLoading}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 bg-[#0d1117] border border-[#30363d] rounded-lg text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-[#1f6feb] focus:ring-1 focus:ring-[#1f6feb] transition-colors disabled:opacity-50"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-[#1f6feb] hover:bg-[#388bfd] disabled:bg-[#1f6feb]/50 text-white font-semibold rounded-lg transition-all shadow-md shadow-blue-500/10 cursor-pointer disabled:cursor-not-allowed"
          >
            {isLoading ? 'Decrypting credentials...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
