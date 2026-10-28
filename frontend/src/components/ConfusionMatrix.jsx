import React from 'react';
import { Grid, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ConfusionMatrix({ winningDetails, classes = [] }) {
  if (!winningDetails?.confusion_matrix?.matrix) return null;

  const { matrix, labels } = winningDetails.confusion_matrix;
  const testMetrics = winningDetails.test_metrics || {};

  // Calculate total samples and max value for color scaling
  const flatVals = matrix.flat();
  const maxVal = Math.max(...flatVals, 1);
  const totalSamples = flatVals.reduce((a, b) => a + b, 0);

  // Correct diagonal count
  const correctCount = matrix.reduce((acc, row, i) => acc + (row[i] || 0), 0);
  const testAccuracy = totalSamples > 0 ? (correctCount / totalSamples) * 100 : 0;

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Grid className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">
              Held-Out Test Confusion Matrix
            </h3>
            <p className="text-xs text-slate-400">
              Actual vs Predicted class breakdown on the isolated test split ({totalSamples} samples)
            </p>
          </div>
        </div>

        {/* Test Accuracy Badge */}
        <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800 text-xs font-mono">
          <span className="text-slate-400">Held-Out Test Acc:</span>
          <span className="text-teal-400 font-bold">{testAccuracy.toFixed(1)}%</span>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="flex flex-col items-center justify-center p-4">
        {/* Top Label: Predicted */}
        <div className="text-center pb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-400 font-mono">
            Predicted Class →
          </span>
        </div>

        <div className="flex items-center">
          {/* Left Label: Actual */}
          <div className="pr-4 flex items-center justify-center -rotate-90">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono whitespace-nowrap">
              ← Actual Class
            </span>
          </div>

          {/* Matrix Table */}
          <div className="overflow-x-auto">
            <table className="border-collapse font-mono">
              <thead>
                <tr>
                  <th className="p-2 text-[11px] text-slate-500 text-right pr-3"></th>
                  {labels.map((lbl) => (
                    <th key={lbl} className="p-2 text-xs font-bold text-slate-300 text-center min-w-[70px]">
                      {lbl}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.map((row, rowIdx) => (
                  <tr key={rowIdx}>
                    {/* Actual Label Header */}
                    <td className="p-2 text-xs font-bold text-slate-300 text-right pr-3 whitespace-nowrap">
                      {labels[rowIdx]}
                    </td>

                    {/* Matrix Cells */}
                    {row.map((val, colIdx) => {
                      const isCorrect = rowIdx === colIdx;
                      const intensity = val / maxVal;

                      let cellBg = 'bg-slate-900/60 border-slate-800 text-slate-400';
                      if (isCorrect && val > 0) {
                        cellBg = 'bg-teal-500/25 border-teal-500/40 text-teal-200 font-bold';
                      } else if (!isCorrect && val > 0) {
                        cellBg = 'bg-rose-500/25 border-rose-500/40 text-rose-200 font-bold';
                      }

                      return (
                        <td
                          key={colIdx}
                          className="p-1 text-center"
                        >
                          <div
                            className={`min-w-[70px] h-12 flex flex-col items-center justify-center rounded-xl border transition-all ${cellBg}`}
                            title={`Actual: ${labels[rowIdx]}, Predicted: ${labels[colIdx]} (${val} cases)`}
                          >
                            <span className="text-sm font-extrabold">{val}</span>
                            <span className="text-[10px] opacity-75">
                              {totalSamples > 0 ? `${((val / totalSamples) * 100).toFixed(0)}%` : ''}
                            </span>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-6 pt-4 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded bg-teal-500/30 border border-teal-500/60" />
            <span>Diagonal: Correct Predictions ({correctCount})</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded bg-rose-500/30 border border-rose-500/60" />
            <span>Off-Diagonal: Errors ({totalSamples - correctCount})</span>
          </div>
        </div>
      </div>

      {/* Held-out Test Metrics Bar */}
      {Object.keys(testMetrics).length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          {Object.entries(testMetrics).map(([k, val]) => (
            <div key={k} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">
                Test {k.replace('_', ' ')}
              </span>
              <p className="text-base font-bold text-white font-mono">
                {val !== null ? `${(val * 100).toFixed(1)}%` : '—'}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
