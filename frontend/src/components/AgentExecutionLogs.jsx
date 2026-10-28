import React, { useState, useEffect, useRef } from 'react';
import { Terminal, CheckCircle2, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';

export default function AgentExecutionLogs({ logs = [], isRunning }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);
  const terminalEndRef = useRef(null);

  // Auto-scroll to bottom of logs when updated
  useEffect(() => {
    if (isExpanded && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isRunning, isExpanded]);

  const copyLogs = () => {
    navigator.clipboard.writeText(logs.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-card rounded-2xl overflow-hidden border border-slate-800">
      {/* Terminal Title Bar */}
      <div className="bg-slate-900/90 px-4 py-3 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>

          <div className="flex items-center space-x-2 text-xs font-mono text-slate-300">
            <Terminal className="w-3.5 h-3.5 text-teal-400" />
            <span>ClassifyAI Orchestration Agent Audit Trail</span>
            {isRunning && (
              <span className="flex items-center space-x-1 text-teal-400 animate-pulse text-[11px]">
                <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                <span>Running...</span>
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {logs.length > 0 && (
            <button
              onClick={copyLogs}
              className="p-1 rounded text-slate-400 hover:text-slate-200 transition-colors"
              title="Copy audit logs"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          )}

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded text-slate-400 hover:text-slate-200 transition-colors"
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Terminal Content Body */}
      {isExpanded && (
        <div className="bg-slate-950 p-4 max-h-64 overflow-y-auto font-mono text-xs text-slate-300 space-y-1.5 selection:bg-teal-500/30">
          {logs.length === 0 && isRunning && (
            <div className="flex items-center space-x-2 text-slate-500 italic">
              <div className="w-3 h-3 border border-teal-400 border-t-transparent rounded-full animate-spin" />
              <span>Initializing agent environment and validating schema isolation...</span>
            </div>
          )}

          {logs.map((log, index) => {
            const isSuccess = log.includes('Winner') || log.includes('Finished') || log.includes('passed');
            const isWarn = log.includes('Imbalance') || log.includes('warning') || log.includes('ambiguity');
            const isFold = log.includes('Fold') || log.includes('Evaluating');

            return (
              <div key={index} className="flex items-start space-x-2 leading-relaxed">
                <span className="text-slate-600 select-none text-[10px] pt-0.5">
                  [{String(index + 1).padStart(2, '0')}]
                </span>
                <span
                  className={
                    isSuccess
                      ? 'text-emerald-400 font-semibold'
                      : isWarn
                      ? 'text-amber-400'
                      : isFold
                      ? 'text-cyan-300'
                      : 'text-slate-300'
                  }
                >
                  {log}
                </span>
              </div>
            );
          })}

          <div ref={terminalEndRef} />
        </div>
      )}
    </div>
  );
}
