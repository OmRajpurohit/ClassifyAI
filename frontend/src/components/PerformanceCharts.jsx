import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts';
import { BarChart3, TrendingUp, Zap } from 'lucide-react';

export default function PerformanceCharts({ results }) {
  const [selectedMetric, setSelectedMetric] = useState('f1_weighted');

  if (!results?.ranked_models?.length) return null;

  // Prepare chart data
  const chartData = results.ranked_models.map((m) => {
    const f1 = m.all_metrics?.f1_weighted?.mean != null ? m.all_metrics.f1_weighted.mean * 100 : 0;
    const acc = m.all_metrics?.accuracy?.mean != null ? m.all_metrics.accuracy.mean * 100 : 0;
    const prec = m.all_metrics?.precision_weighted?.mean != null ? m.all_metrics.precision_weighted.mean * 100 : 0;
    const rec = m.all_metrics?.recall_weighted?.mean != null ? m.all_metrics.recall_weighted.mean * 100 : 0;

    return {
      name: m.algorithm_name,
      shortName: m.algorithm_name.replace('Support Vector Machine', 'SVM').replace('Logistic Regression', 'LogReg'),
      F1: Number(f1.toFixed(2)),
      Accuracy: Number(acc.toFixed(2)),
      Precision: Number(prec.toFixed(2)),
      Recall: Number(rec.toFixed(2)),
      trainTimeMs: Number((m.training_duration_seconds * 1000).toFixed(1)),
      isWinner: m.is_winner,
    };
  });

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">
              Cross-Validation Performance Comparison
            </h3>
            <p className="text-xs text-slate-400">
              Side-by-side benchmark of classifiers across primary evaluation metrics
            </p>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex items-center space-x-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800">
          {['All Metrics', 'Training Latency'].map((mode) => (
            <button
              key={mode}
              onClick={() => setSelectedMetric(mode)}
              className={`px-3 py-1 text-xs rounded-lg font-medium transition-all ${
                selectedMetric === mode
                  ? 'bg-teal-500 text-slate-950 font-bold shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {selectedMetric === 'Training Latency' ? (
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="shortName" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} unit="ms" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#090d16',
                  borderColor: '#334155',
                  borderRadius: '12px',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="trainTimeMs" name="Train Time (ms)" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.isWinner ? '#2dd4bf' : '#6366f1'}
                  />
                ))}
              </Bar>
            </BarChart>
          ) : (
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="shortName" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} domain={[0, 100]} unit="%" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#090d16',
                  borderColor: '#334155',
                  borderRadius: '12px',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="F1" fill="#2dd4bf" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Accuracy" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Precision" fill="#a855f7" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Recall" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
