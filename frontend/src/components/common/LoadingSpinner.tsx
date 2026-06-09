import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  subMessage?: string;
}

export default function LoadingSpinner({ message = 'Loading...', subMessage }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 animate-pulse">
      {/* Outer spinning ring */}
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-4 border-t-[#1f6feb] border-r-transparent border-b-[#1f6feb]/20 border-l-transparent animate-spin"></div>
        <div className="absolute inset-2 rounded-full border-4 border-t-red-500 border-r-transparent border-b-red-500/20 border-l-transparent animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
      </div>
      <p className="mt-6 text-sm font-semibold text-white tracking-wide uppercase font-mono">{message}</p>
      {subMessage && (
        <p className="mt-2 text-xs text-gray-500 font-mono text-center max-w-sm px-4">
          {subMessage}
        </p>
      )}
    </div>
  );
}
