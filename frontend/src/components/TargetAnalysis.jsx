import React, { useEffect, useState } from 'react';
import { Target, AlertCircle, CheckCircle, PieChart, Layers, ShieldCheck } from 'lucide-react';
import { analyzeTarget } from '../services/api';

export default function TargetAnalysis({
  dataset,
  selectedTarget,
  setSelectedTarget,
  targetAnalysis,
  setTargetAnalysis,
  setError,
}) {
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // Automatically analyze the selected target
  useEffect(() => {
    if (!dataset?.dataset_id || !selectedTarget) return;

    let isMounted = true;
    async function fetchTargetDetails() {
      try {
        setLoadingAnalysis(true);
        const data = await analyzeTarget(dataset.dataset_id, selectedTarget);
        if (isMounted) {
          setTargetAnalysis(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(`Target column analysis failed: ${err.message}`);
        }
      } finally {
        if (isMounted) setLoadingAnalysis(false);
      }
    }

    fetchTargetDetails();
    return () => {
      isMounted = false;
    };
  }, [dataset?.dataset_id, selectedTarget]);

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* Header and Target Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">
              Classification Target Column
            </h3>
            <p className="text-xs text-slate-400">
              Select the feature label column to predict
            </p>
          </div>
        </div>

        {/* Target Select Dropdown */}
        <div className="flex items-center space-x-2">
          <label className="text-xs font-medium text-slate-400 whitespace-nowrap">
            Target:
          </label>
          <select
            value={selectedTarget}
            onChange={(e) => setSelectedTarget(e.target.value)}
            disabled={loadingAnalysis}
            className="bg-slate-900 border border-slate-700 text-slate-100 rounded-lg px-3 py-1.5 text-xs font-mono font-medium focus:outline-none focus:border-teal-500 transition-colors cursor-pointer"
          >
            {dataset?.columns?.map((col) => (
              <option key={col} value={col}>
                {col} {dataset.target_candidates?.includes(col) ? '★ (Candidate)' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loadingAnalysis && (
        <div className="py-8 flex flex-col items-center justify-center space-y-2 text-slate-400">
          <div className="w-6 h-6 border-2 border-teal-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs">Analyzing class frequencies and imbalance...</span>
        </div>
      )}

      {!loadingAnalysis && targetAnalysis && (
        <div className="space-y-6">
          {/* Status Badges Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Number of Classes */}
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 font-medium">Task Type</span>
                <p className="text-sm font-bold text-white">
                  {targetAnalysis.is_multiclass ? 'Multi-Class' : 'Binary'} ({targetAnalysis.num_classes} Classes)
                </p>
              </div>
            </div>

            {/* Imbalance Status */}
            <div className={`p-3.5 rounded-xl border flex items-center space-x-3 ${
              targetAnalysis.is_imbalanced
                ? 'bg-amber-950/20 border-amber-800/40 text-amber-300'
                : 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300'
            }`}>
              <div className={`p-2 rounded-lg border ${
                targetAnalysis.is_imbalanced
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              }`}>
                {targetAnalysis.is_imbalanced ? (
                  <AlertCircle className="w-4 h-4" />
                ) : (
                  <CheckCircle className="w-4 h-4" />
                )}
              </div>
              <div>
                <span className="text-[11px] font-medium opacity-80">Distribution State</span>
                <p className="text-sm font-bold">
                  {targetAnalysis.is_imbalanced
                    ? `Imbalanced (${targetAnalysis.imbalance_ratio?.toFixed(2)}:1)`
                    : 'Balanced Classes'}
                </p>
              </div>
            </div>

            {/* Stratified CV Safeguard */}
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 font-medium">Validation Strategy</span>
                <p className="text-sm font-bold text-teal-300">
                  Stratified K-Fold
                </p>
              </div>
            </div>
          </div>

          {/* Class Frequency Breakdown Bars */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
              <PieChart className="w-3.5 h-3.5 text-cyan-400" />
              <span>Class Frequencies & Ratios</span>
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {Object.entries(targetAnalysis.class_distribution || {}).map(([cls, count]) => {
                const pct = targetAnalysis.class_percentages?.[cls] || 0;
                const isMajority = targetAnalysis.majority_class === cls;
                const isMinority = targetAnalysis.minority_class === cls;

                return (
                  <div key={cls} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-mono font-bold text-white px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                          Class: {cls}
                        </span>
                        {isMajority && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                            Majority
                          </span>
                        )}
                        {isMinority && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                            Minority
                          </span>
                        )}
                      </div>
                      <span className="text-xs font-mono text-slate-300 font-semibold">
                        {count} rows ({pct.toFixed(1)}%)
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-teal-500 to-cyan-400 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${Math.max(pct, 5)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Smart Agent Recommendations */}
          {targetAnalysis.recommendations?.length > 0 && (
            <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Agent Optimization Tactics
              </span>
              <ul className="text-xs text-slate-300 space-y-1">
                {targetAnalysis.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-center space-x-2">
                    <span className="text-teal-400 font-bold">✓</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
