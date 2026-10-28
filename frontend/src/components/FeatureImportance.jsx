import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Sparkles, HelpCircle, Layers } from 'lucide-react';

export default function FeatureImportance({ winningDetails, algorithmName }) {
  const importances = winningDetails?.feature_importances || [];

  if (!importances || importances.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <div className="flex items-center space-x-3 pb-3 border-b border-slate-800">
          <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">
              Feature Importance & Interpretability
            </h3>
            <p className="text-xs text-slate-400">
              Global feature attribution for {algorithmName}
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 space-y-2">
          <div className="flex items-center space-x-2 text-amber-300 font-semibold">
            <HelpCircle className="w-4 h-4" />
            <span>Non-Linear / Non-Parametric Model Note</span>
          </div>
          <p>
            The winning classifier ({algorithmName}) uses non-linear decision boundaries or distance metrics where direct linear or Gini feature weights are not intrinsically computed.
          </p>
          <p className="text-slate-500">
            Tree ensemble models (Random Forest, Gradient Boosting, Decision Tree) and Logistic Regression provide explicit Gini impurity or coefficient weights.
          </p>
        </div>
      </div>
    );
  }

  // Sort and take top 10 features
  const sorted = [...importances]
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 10);

  const chartData = sorted.map((item) => ({
    feature: item.feature,
    importance: Number((item.importance * 100).toFixed(2)),
  })).reverse(); // Reverse for clean top-down rendering in horizontal layout

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">
              Top Predictive Feature Importances
            </h3>
            <p className="text-xs text-slate-400">
              Gini impurity / coefficient attribution for the winning model ({algorithmName})
            </p>
          </div>
        </div>

        <span className="text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
          Top {sorted.length} Features
        </span>
      </div>

      {/* Horizontal Bar Chart */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={chartData}
            margin={{ top: 10, right: 30, left: 50, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
            <XAxis type="number" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} unit="%" />
            <YAxis
              type="category"
              dataKey="feature"
              stroke="#64748b"
              tick={{ fill: '#e2e8f0', fontSize: 11 }}
              width={100}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090d16',
                borderColor: '#334155',
                borderRadius: '12px',
                fontSize: '12px',
              }}
              formatter={(val) => [`${val}%`, 'Relative Weight']}
            />
            <Bar dataKey="importance" fill="#14b8a6" radius={[0, 6, 6, 0]}>
              {chartData.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={`rgba(20, 184, 166, ${0.4 + (index / chartData.length) * 0.6})`}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
