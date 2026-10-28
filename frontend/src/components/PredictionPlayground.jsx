import React, { useState, useEffect } from 'react';
import { PlayCircle, Sparkles, CheckCircle2, RotateCcw, Zap, Layers } from 'lucide-react';
import { predict } from '../services/api';

export default function PredictionPlayground({
  experimentId,
  datasetSummary,
  targetColumn,
  winner,
  classes = [],
}) {
  const [inputs, setInputs] = useState({});
  const [predictionResult, setPredictionResult] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [error, setError] = useState(null);

  // Initialize form fields based on dataset columns excluding target
  useEffect(() => {
    if (!datasetSummary?.columns) return;

    const featureCols = datasetSummary.columns.filter((c) => c !== targetColumn);
    const initialValues = {};

    // Use sample preview values as initial default inputs
    const sampleRow = datasetSummary.sample_preview?.[0] || {};
    featureCols.forEach((col) => {
      initialValues[col] = sampleRow[col] !== undefined ? sampleRow[col] : '';
    });

    setInputs(initialValues);
  }, [datasetSummary, targetColumn]);

  const handleInputChange = (col, value) => {
    setInputs((prev) => ({
      ...prev,
      [col]: value,
    }));
  };

  const handlePredict = async (e) => {
    e?.preventDefault();
    if (!experimentId) return;

    try {
      setIsPredicting(true);
      setError(null);

      // Convert inputs to proper types if numeric
      const numericCols = datasetSummary?.numeric_columns || [];
      const parsedInputs = {};
      Object.entries(inputs).forEach(([k, v]) => {
        if (numericCols.includes(k) && v !== '' && !isNaN(Number(v))) {
          parsedInputs[k] = Number(v);
        } else {
          parsedInputs[k] = v;
        }
      });

      const res = await predict(experimentId, [parsedInputs]);
      setPredictionResult(res);
    } catch (err) {
      setError(err.message || 'Inference failed.');
    } finally {
      setIsPredicting(false);
    }
  };

  const loadSampleRow = (rowIndex) => {
    const sample = datasetSummary?.sample_preview?.[rowIndex];
    if (!sample) return;

    const updated = {};
    datasetSummary.columns
      .filter((c) => c !== targetColumn)
      .forEach((col) => {
        updated[col] = sample[col] !== undefined ? sample[col] : '';
      });
    setInputs(updated);
    setPredictionResult(null);
  };

  const featureCols = datasetSummary?.columns?.filter((c) => c !== targetColumn) || [];

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <PlayCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100 flex items-center space-x-2">
              <span>Interactive Model Playground</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-300 border border-teal-500/20 font-mono">
                {winner?.algorithm_name || 'Champion Model'}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Pass custom feature instances into the fitted pipeline to generate live predictions and class probabilities
            </p>
          </div>
        </div>

        {/* Quick Sample Filler Buttons */}
        {datasetSummary?.sample_preview?.length > 0 && (
          <div className="flex items-center space-x-2">
            <span className="text-[11px] text-slate-400">Quick Fill:</span>
            {datasetSummary.sample_preview.slice(0, 3).map((_, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => loadSampleRow(idx)}
                className="px-2.5 py-1 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors font-mono"
              >
                Sample #{idx + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-800/40 text-xs text-rose-300">
          {error}
        </div>
      )}

      {/* Input Features Form Grid */}
      <form onSubmit={handlePredict} className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {featureCols.map((col) => {
            const isNum = datasetSummary?.numeric_columns?.includes(col);
            return (
              <div key={col} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-slate-300 truncate" title={col}>
                    {col}
                  </label>
                  <span className={`text-[9px] px-1 rounded font-mono ${
                    isNum ? 'text-cyan-400 bg-cyan-950/80' : 'text-purple-400 bg-purple-950/80'
                  }`}>
                    {isNum ? 'num' : 'cat'}
                  </span>
                </div>
                <input
                  type={isNum ? 'number' : 'text'}
                  step={isNum ? 'any' : undefined}
                  value={inputs[col] ?? ''}
                  onChange={(e) => handleInputChange(col, e.target.value)}
                  placeholder={`Enter ${col}...`}
                  className="w-full bg-slate-900/90 border border-slate-700/80 text-slate-100 rounded-xl px-3 py-2 text-xs font-mono focus:outline-none focus:border-teal-500 transition-colors"
                />
              </div>
            );
          })}
        </div>

        {/* Action Button */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-slate-800">
          <p className="text-xs text-slate-400">
            Target feature: <span className="text-teal-400 font-mono font-bold">{targetColumn}</span>
          </p>

          <button
            type="submit"
            disabled={isPredicting}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-teal-500/20 disabled:opacity-50"
          >
            {isPredicting ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Running Inference...</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5 fill-slate-950" />
                <span>Predict Class Label</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Prediction Output Showcase */}
      {predictionResult && (
        <div className="mt-6 p-5 rounded-2xl bg-gradient-to-r from-teal-950/40 via-slate-900 to-cyan-950/30 border-2 border-teal-500/40 space-y-4 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-teal-400 font-mono">
                Model Inference Output
              </span>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-slate-300">Predicted Class:</span>
                <span className="px-3.5 py-1 rounded-xl bg-teal-500 text-slate-950 font-mono font-black text-lg shadow-md shadow-teal-500/30">
                  {predictionResult.predictions?.[0]}
                </span>
              </div>
            </div>

            <div className="text-xs text-slate-400 font-mono bg-slate-950/60 px-3 py-1.5 rounded-xl border border-slate-800">
              Evaluated via: {winner?.algorithm_name}
            </div>
          </div>

          {/* Probabilities Breakdown */}
          {predictionResult.probabilities?.[0] && (
            <div className="space-y-2 pt-2 border-t border-slate-800/80">
              <span className="text-xs font-semibold text-slate-300">
                Class Probability Distribution
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {Object.entries(predictionResult.probabilities[0]).map(([cls, prob]) => {
                  const pct = (prob * 100).toFixed(1);
                  const isPredicted = String(predictionResult.predictions?.[0]) === String(cls);

                  return (
                    <div key={cls} className="space-y-1 p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                      <div className="flex justify-between text-xs font-mono">
                        <span className={`font-semibold ${isPredicted ? 'text-teal-300' : 'text-slate-400'}`}>
                          Class: {cls} {isPredicted ? '★ (Predicted)' : ''}
                        </span>
                        <span className="font-bold text-white">{pct}%</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${
                            isPredicted ? 'bg-gradient-to-r from-teal-400 to-emerald-400' : 'bg-slate-600'
                          }`}
                          style={{ width: `${Math.max(Number(pct), 2)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
