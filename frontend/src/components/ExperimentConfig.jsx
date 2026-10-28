import React from 'react';
import { Sliders, Play, Check, Shield, Zap, Sparkles } from 'lucide-react';

const ALL_ALGORITHMS = [
  {
    id: 'random_forest',
    name: 'Random Forest',
    type: 'Bagging Ensemble',
    scaling: false,
    importance: true,
    desc: 'Robust against overfitting; computes Gini impurity feature importances.',
  },
  {
    id: 'gradient_boosting',
    name: 'Gradient Boosting',
    type: 'Boosting Ensemble',
    scaling: false,
    importance: true,
    desc: 'Sequentially minimizes residual errors; high predictive accuracy.',
  },
  {
    id: 'logistic_regression',
    name: 'Logistic Regression',
    type: 'Linear Model',
    scaling: true,
    importance: true,
    desc: 'L2-regularized probabilistic linear classifier with standard scaling.',
  },
  {
    id: 'svm',
    name: 'Support Vector Machine (RBF)',
    type: 'Kernel Machine',
    scaling: true,
    importance: false,
    desc: 'Maximizes separating margin with RBF non-linear kernel.',
  },
  {
    id: 'knn',
    name: 'K-Nearest Neighbors',
    type: 'Instance-Based',
    scaling: true,
    importance: false,
    desc: 'Classifies via majority vote of k nearest Euclidean neighbors.',
  },
  {
    id: 'decision_tree',
    name: 'Decision Tree',
    type: 'Single Tree',
    scaling: false,
    importance: true,
    desc: 'White-box rule-based tree partitioner with pruning depth.',
  },
];

const METRICS = [
  { id: 'f1_weighted', label: 'F1 Score (Weighted)', desc: 'Harmonic mean of precision & recall; robust against class imbalance.' },
  { id: 'accuracy', label: 'Accuracy', desc: 'Fraction of correctly predicted instances across all classes.' },
  { id: 'precision_weighted', label: 'Precision (Weighted)', desc: 'Focuses on minimizing false positive misclassifications.' },
  { id: 'recall_weighted', label: 'Recall (Weighted)', desc: 'Focuses on minimizing false negative omissions.' },
  { id: 'roc_auc_ovr', label: 'ROC-AUC (OVR)', desc: 'One-vs-Rest area under ROC curve using probability predictions.' },
];

export default function ExperimentConfig({
  config,
  setConfig,
  onRunExperiment,
  isRunning,
  disabled,
}) {
  const toggleAlgorithm = (algoId) => {
    const current = config.selected_algorithms || ALL_ALGORITHMS.map(a => a.id);
    let updated;
    if (current.includes(algoId)) {
      if (current.length === 1) return; // Prevent 0 algorithms
      updated = current.filter(id => id !== algoId);
    } else {
      updated = [...current, algoId];
    }
    setConfig(prev => ({ ...prev, selected_algorithms: updated }));
  };

  const selectAll = () => {
    setConfig(prev => ({ ...prev, selected_algorithms: ALL_ALGORITHMS.map(a => a.id) }));
  };

  const selectedList = config.selected_algorithms || ALL_ALGORITHMS.map(a => a.id);

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">
              Experiment & Model Configuration
            </h3>
            <p className="text-xs text-slate-400">
              Select classifiers, cross-validation parameters, and the primary optimization metric
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={selectAll}
            className="text-xs font-medium text-teal-400 hover:text-teal-300 underline underline-offset-4"
          >
            Select All (6)
          </button>
        </div>
      </div>

      {/* Algorithm Selector Grid */}
      <div className="space-y-3">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Algorithms to Benchmark ({selectedList.length}/6 selected)
        </label>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {ALL_ALGORITHMS.map((algo) => {
            const isSelected = selectedList.includes(algo.id);

            return (
              <div
                key={algo.id}
                onClick={() => !isRunning && toggleAlgorithm(algo.id)}
                className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-slate-900/90 border-teal-500/50 shadow-sm shadow-teal-500/10'
                    : 'bg-slate-950/40 border-slate-800/80 opacity-60 hover:opacity-85'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-slate-100 flex items-center space-x-1.5">
                      <span>{algo.name}</span>
                    </span>
                    <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${
                      isSelected ? 'bg-teal-500 border-teal-400 text-slate-950' : 'border-slate-700 bg-slate-900'
                    }`}>
                      {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 line-clamp-2">
                    {algo.desc}
                  </p>
                </div>

                <div className="flex items-center space-x-1.5 pt-3 text-[10px]">
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/80 font-mono">
                    {algo.type}
                  </span>
                  {algo.scaling && (
                    <span className="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/80 font-mono">
                      Scale Pipeline
                    </span>
                  )}
                  {algo.importance && (
                    <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/80 font-mono">
                      Features
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Hyperparameters & Validation Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
        {/* Primary Metric */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <label className="text-xs font-semibold text-slate-300 block">
            Primary Ranking Metric
          </label>
          <select
            value={config.primary_metric}
            onChange={(e) => setConfig(prev => ({ ...prev, primary_metric: e.target.value }))}
            disabled={isRunning}
            className="w-full bg-slate-950 border border-slate-700 text-slate-100 rounded-lg px-3 py-2 text-xs font-medium focus:outline-none focus:border-teal-500"
          >
            {METRICS.map(m => (
              <option key={m.id} value={m.id}>
                {m.label}
              </option>
            ))}
          </select>
          <p className="text-[11px] text-slate-500">
            {METRICS.find(m => m.id === config.primary_metric)?.desc}
          </p>
        </div>

        {/* Cross Validation Folds */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300">
              Stratified CV Folds
            </label>
            <span className="text-xs font-mono font-bold text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20">
              {config.cv_folds} Folds
            </span>
          </div>
          <input
            type="range"
            min="2"
            max="10"
            step="1"
            value={config.cv_folds}
            onChange={(e) => setConfig(prev => ({ ...prev, cv_folds: parseInt(e.target.value, 10) }))}
            disabled={isRunning}
            className="w-full accent-teal-400 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>2 folds (Fastest)</span>
            <span>5 (Balanced)</span>
            <span>10 (Exhaustive)</span>
          </div>
        </div>

        {/* Held-out Test Split */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300">
              Held-out Test Split
            </label>
            <span className="text-xs font-mono font-bold text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20">
              {Math.round(config.test_size * 100)}% Test
            </span>
          </div>
          <input
            type="range"
            min="0.1"
            max="0.4"
            step="0.05"
            value={config.test_size}
            onChange={(e) => setConfig(prev => ({ ...prev, test_size: parseFloat(e.target.value) }))}
            disabled={isRunning}
            className="w-full accent-teal-400 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>10% (More Train)</span>
            <span>20% (Default)</span>
            <span>40% (Strict Holdout)</span>
          </div>
        </div>
      </div>

      {/* Launch Agent Action Banner */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-800/80">
        <div className="flex items-center space-x-2 text-xs text-slate-400">
          <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Strict anti-leakage isolation active (Random seed: {config.random_state})</span>
        </div>

        <button
          type="button"
          onClick={onRunExperiment}
          disabled={isRunning || disabled || selectedList.length === 0}
          className="w-full sm:w-auto inline-flex items-center justify-center space-x-2.5 px-6 py-3 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-400 hover:from-teal-400 hover:to-emerald-300 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-teal-500/25 disabled:opacity-50 disabled:pointer-events-none hover:scale-[1.02]"
        >
          {isRunning ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>Agent Executing Pipeline...</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4 fill-slate-950" />
              <span>Run ClassifyAI Orchestration Agent</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
