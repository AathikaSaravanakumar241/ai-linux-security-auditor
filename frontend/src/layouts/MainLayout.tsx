import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { 
    to: '/dashboard', 
    label: 'Dashboard', 
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    )
  },
  { 
    to: '/audit/new', 
    label: 'New Audit', 
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m4-2H6" />
      </svg>
    )
  },
  { 
    to: '/history', 
    label: 'Audit History', 
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  },
];

export default function MainLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Simulated logout redirect
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-[#0d1117] text-[#c9d1d9] font-sans overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#161b22] border-r border-[#30363d] flex flex-col shrink-0">
        {/* Brand/Header */}
        <div className="p-6 border-b border-[#30363d] flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#1f6feb] flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
            🛡️
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white tracking-wider uppercase">
              Security Auditor
            </h1>
            <p className="text-[10px] text-gray-400 font-mono tracking-tight">
              PRO EDITION v1.0
            </p>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navItems.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-[#1f6feb]/10 text-[#58a6ff] border-l-4 border-[#1f6feb]'
                    : 'text-[#8b949e] hover:text-white hover:bg-[#21262d]'
                }`
              }
            >
              <span className="shrink-0">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer info & Logout */}
        <div className="p-4 border-t border-[#30363d] bg-[#0d1117]/50 space-y-3">
          <div className="flex items-center justify-between text-xs text-gray-500 font-mono">
            <span>STATUS: ACTIVE</span>
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 border border-[#30363d] hover:border-red-500 hover:text-red-500 text-xs font-semibold rounded-md transition-colors bg-transparent cursor-pointer"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Pane */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto bg-[#0d1117]">
        <div className="flex-1 p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
