import React, { useState } from 'react';
import { Database, Hash, Type, AlertTriangle, CheckCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';

export default function DatasetOverview({ dataset, target, droppedColumns = [], setDroppedColumns, processedPreview }) {
  const [showAllColumns, setShowAllColumns] = useState(false);

  if (!dataset) return null;

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* Header with filename */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100 flex items-center space-x-2">
              <span>{dataset.filename}</span>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-teal-300 border border-slate-700">
                Dataset ID: {dataset.dataset_id?.slice(0, 8)}...
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Exploratory Data Analysis and Feature Profiling Complete
            </p>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <span className="text-[11px] font-medium text-slate-400">Total Rows</span>
          <p className="text-xl font-bold text-white font-mono">{dataset.row_count?.toLocaleString()}</p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <span className="text-[11px] font-medium text-slate-400">Total Columns</span>
          <p className="text-xl font-bold text-white font-mono">{dataset.column_count}</p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <span className="text-[11px] font-medium text-slate-400 flex items-center space-x-1">
            <Hash className="w-3 h-3 text-cyan-400" />
            <span>Numeric Features</span>
          </span>
          <p className="text-xl font-bold text-cyan-400 font-mono">{dataset.numeric_columns?.length || 0}</p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <span className="text-[11px] font-medium text-slate-400 flex items-center space-x-1">
            <Type className="w-3 h-3 text-purple-400" />
            <span>Categorical Features</span>
          </span>
          <p className="text-xl font-bold text-purple-400 font-mono">{dataset.categorical_columns?.length || 0}</p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <span className="text-[11px] font-medium text-slate-400">Missing Values</span>
          <div className="flex items-center space-x-1.5">
            <p className={`text-xl font-bold font-mono ${dataset.total_missing_values > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {dataset.total_missing_values}
            </p>
            {dataset.total_missing_values === 0 && (
              <CheckCircle className="w-4 h-4 text-emerald-400 inline" />
            )}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
          <span className="text-[11px] font-medium text-slate-400">Duplicate Rows</span>
          <p className="text-xl font-bold text-slate-200 font-mono">{dataset.duplicate_row_count}</p>
        </div>
      </div>

      {/* Target Candidates & Summary Notes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Recommended Target Columns */}
        <div className="p-4 rounded-xl bg-teal-950/20 border border-teal-800/30 space-y-2">
          <div className="flex items-center space-x-2 text-teal-300 text-xs font-semibold uppercase tracking-wider">
            <Info className="w-3.5 h-3.5" />
            <span>Recommended Target Columns</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {dataset.target_candidates?.length > 0 ? (
              dataset.target_candidates.map((col) => (
                <span
                  key={col}
                  className="px-2.5 py-1 rounded-md bg-teal-500/20 text-teal-200 border border-teal-500/30 text-xs font-mono font-medium"
                >
                  {col} ({dataset.unique_values_per_column?.[col]} classes)
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-400">Any low-cardinality discrete column can be selected.</span>
            )}
          </div>
        </div>

        {/* Quality Notes */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center space-x-2 text-slate-300 text-xs font-semibold uppercase tracking-wider">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span>Agent Profiling Insights</span>
          </div>
          <ul className="text-xs text-slate-400 space-y-1">
            {dataset.summary_notes?.slice(0, 3).map((note, idx) => (
              <li key={idx} className="flex items-start space-x-1.5">
                <span className="text-teal-400">•</span>
                <span>{note}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Interactive Sample Table Preview */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Processed Feature Preview (First {processedPreview?.sample_preview?.length || 5} Rows)
          </h4>
          <span className="text-xs text-slate-500">
            {processedPreview?.columns?.length ?? dataset.columns?.length} features after selected drops
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/40">
          <table className="w-full text-left text-xs text-slate-300 border-collapse">
            <thead className="bg-slate-900/90 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3 font-semibold text-slate-500">#</th>
                {(processedPreview?.columns || dataset.columns || []).map((col) => {
                  const isNum = dataset.numeric_columns?.includes(col);
                  return (
                    <th key={col} className="py-2.5 px-3 font-semibold whitespace-nowrap">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-slate-200">{col}</span>
                        <span className={`text-[9px] px-1 py-0.2 rounded font-mono ${
                          isNum ? 'bg-cyan-950 text-cyan-300 border border-cyan-800' : 'bg-purple-950 text-purple-300 border border-purple-800'
                        }`}>
                          {isNum ? 'num' : 'cat'}
                        </span>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {(processedPreview?.sample_preview || dataset.sample_preview || []).map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2 px-3 text-slate-500">{idx + 1}</td>
                  {(processedPreview?.columns || dataset.columns || []).map((col) => (
                    <td key={col} className="py-2 px-3 whitespace-nowrap text-slate-300">
                      {row[col] !== null && row[col] !== undefined ? String(row[col]) : (
                        <span className="text-amber-500/70 italic">null</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {processedPreview && <div className="space-y-3">
          <p className="text-xs text-slate-400">{processedPreview.note} {processedPreview.removed_target_rows > 0 && `${processedPreview.removed_target_rows} row(s) with missing target “${target}” are omitted.`}</p>
          <div className="rounded-xl border border-slate-800 p-4 space-y-1"><h4 className="text-xs uppercase tracking-wider text-slate-300 font-semibold">Row-by-row changes</h4>
            {(processedPreview.row_reasons || []).map(item => <p key={item.row} className="text-xs text-slate-400">Row {item.row}: {item.reasons.join('; ')}</p>)}
          </div>
          <div className="rounded-xl border border-slate-800 p-4 space-y-2"><h4 className="text-xs uppercase tracking-wider text-slate-300 font-semibold">Preprocessing reasons by feature</h4>
            {Object.entries(processedPreview.explanations || {}).map(([col, reason]) => <label key={col} className="flex gap-2 text-xs text-slate-400"><input type="checkbox" checked={!droppedColumns.includes(col)} onChange={e => setDroppedColumns?.(prev => e.target.checked ? prev.filter(c => c !== col) : [...prev, col])} /><span><b className="text-slate-200">{col}</b>: {reason}</span></label>)}
            <p className="text-[11px] text-teal-300">Uncheck a feature to exclude it from model training.</p>
          </div>
        </div>}
      </div>
    </div>
  );
}
