import React from 'react';
import { Sparkles, Activity, RefreshCw, Cpu, BookOpen } from 'lucide-react';

export default function Header({ health, onReset, isRunning }) {
  return (
    <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-xl sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-teal-500/20">
            <Sparkles className="h-5 w-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white font-['JetBrains_Mono']">
                Classify<span className="text-teal-400">AI</span>
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-300 border border-teal-500/20 font-medium">
                v1.0 Agent
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Autonomous Machine Learning Classifier Selection & Preprocessing
            </p>
          </div>
        </div>

        {/* Status & Quick Actions */}
        <div className="flex items-center space-x-3">
          {/* Health status badge */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
            {health?.status === 'ok' ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-slate-300 font-medium hidden md:inline">API Online</span>
                <span className="text-slate-500 hidden lg:inline">({health.algorithms_count || 6} models)</span>
              </>
            ) : (
              <>
                <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse"></span>
                <span className="text-amber-300 font-medium">Connecting...</span>
              </>
            )}
          </div>

          {/* API Docs Button */}
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 text-xs text-slate-300 hover:text-white transition-colors"
            title="Open Interactive FastAPI Docs"
          >
            <BookOpen className="h-3.5 w-3.5 text-teal-400" />
            <span>API Docs</span>
          </a>

          {/* Reset / New Experiment Button */}
          {onReset && (
            <button
              onClick={onReset}
              disabled={isRunning}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 text-teal-300 text-xs font-medium transition-all disabled:opacity-50"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>New Run</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
