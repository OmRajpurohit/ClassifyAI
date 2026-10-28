import React, { useState } from 'react';
import { Trophy, Award, AlertTriangle, Clock, Zap, CheckCircle2, ChevronRight, HelpCircle } from 'lucide-react';

export default function Leaderboard({ results }) {
  const [activeMetricTab, setActiveMetricTab] = useState('all');

  if (!results) return null;

  const {
    winner,
    runner_up,
    score_difference,
    is_statistically_ambiguous,
    poor_performance_warning,
    summary_explanation,
    ranked_models = [],
    failed_models = [],
    config = {},
  } = results;

  const primaryMetricName = config.primary_metric || 'f1_weighted';

  return (
    <div className="space-y-6">
      {/* Champion Model Showcase Card */}
      {winner && (
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-teal-950/40 via-slate-900/90 to-emerald-950/30 border-2 border-teal-500/50 p-6 sm:p-8 shadow-xl shadow-teal-500/10">
          {/* Subtle background glow */}
          <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-400 to-yellow-500 flex items-center justify-center text-slate-950 shadow-lg shadow-amber-500/20">
                  <Trophy className="w-6 h-6 stroke-[2.5]" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs uppercase tracking-wider font-bold text-amber-400 font-mono">
                      Rank #1 — Recommended Champion
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
                      Production Ready
                    </span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                    {winner.algorithm_name}
                  </h2>
                </div>
              </div>

              {/* Primary Score Pill */}
              <div className="text-left sm:text-right bg-slate-900/80 px-4 py-2.5 rounded-xl border border-slate-700/80">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                  CV {primaryMetricName.replace('_', ' ')}
                </span>
                <p className="text-2xl font-extrabold text-teal-400 font-mono">
                  {(winner.primary_score * 100).toFixed(2)}%
                  <span className="text-xs text-slate-400 ml-1 font-normal">
                    ± {(winner.primary_score_std * 100).toFixed(2)}%
                  </span>
                </p>
              </div>
            </div>

            {/* Natural Language Agent Explanation */}
            <p className="text-sm text-slate-300 leading-relaxed max-w-4xl bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
              {summary_explanation}
            </p>

            {/* Runner-Up & Statistical Ambiguity Badges */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
              {runner_up && (
                <span className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex items-center space-x-1.5 font-mono">
                  <Award className="w-3.5 h-3.5 text-slate-400" />
                  <span>Runner-up: {runner_up.algorithm_name} ({(runner_up.primary_score * 100).toFixed(2)}%)</span>
                  {score_difference !== null && (
                    <span className="text-teal-400 font-semibold ml-1">
                      [+{(score_difference * 100).toFixed(2)}% delta]
                    </span>
                  )}
                </span>
              )}

              {is_statistically_ambiguous && (
                <span className="px-3 py-1 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/30 flex items-center space-x-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  <span>Statistical Ambiguity: Runner-up performance is virtually identical (&lt;1% margin).</span>
                </span>
              )}

              {poor_performance_warning && (
                <span className="px-3 py-1 rounded-lg bg-rose-500/10 text-rose-300 border border-rose-500/30 flex items-center space-x-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                  <span>{poor_performance_warning}</span>
                </span>
              )}

              <span className="px-3 py-1 rounded-lg bg-slate-800/80 text-slate-400 border border-slate-700/80 flex items-center space-x-1 font-mono">
                <Clock className="w-3 h-3 text-cyan-400" />
                <span>Fit: {(winner.training_duration_seconds * 1000).toFixed(1)}ms</span>
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Table Container */}
      <div className="glass-card rounded-2xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
          <div>
            <h3 className="text-base font-semibold text-white flex items-center space-x-2">
              <span>Classifier Leaderboard</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                {ranked_models.length} Evaluated
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Deterministic ranking sorted strictly by cross-validation {primaryMetricName}
            </p>
          </div>
        </div>

        {/* Responsive Table */}
        <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/40">
          <table className="w-full text-left text-xs text-slate-300 border-collapse">
            <thead className="bg-slate-900/90 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-3 px-4 font-semibold text-slate-500">Rank</th>
                <th className="py-3 px-4 font-semibold">Algorithm</th>
                <th className="py-3 px-4 font-semibold text-right">Primary Score</th>
                <th className="py-3 px-4 font-semibold text-right">Accuracy</th>
                <th className="py-3 px-4 font-semibold text-right">Precision (W)</th>
                <th className="py-3 px-4 font-semibold text-right">Recall (W)</th>
                <th className="py-3 px-4 font-semibold text-right">Train Time</th>
                <th className="py-3 px-4 font-semibold text-right">Infer Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {ranked_models.map((model) => {
                const isChampion = model.is_winner;
                const isSecond = model.rank === 2;
                const isThird = model.rank === 3;

                const acc = model.all_metrics?.accuracy?.mean;
                const prec = model.all_metrics?.precision_weighted?.mean;
                const rec = model.all_metrics?.recall_weighted?.mean;

                return (
                  <tr
                    key={model.algorithm_id}
                    className={`transition-colors ${
                      isChampion
                        ? 'bg-teal-950/20 hover:bg-teal-950/30 font-semibold'
                        : 'hover:bg-slate-800/30'
                    }`}
                  >
                    {/* Rank Badge */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      {isChampion ? (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30 text-[11px] font-bold">
                          <Trophy className="w-3 h-3 text-amber-400" />
                          <span>#1</span>
                        </span>
                      ) : isSecond ? (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-slate-400/20 text-slate-200 border border-slate-400/30 text-[11px]">
                          <span>#2</span>
                        </span>
                      ) : isThird ? (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-700/20 text-amber-600 border border-amber-700/30 text-[11px]">
                          <span>#3</span>
                        </span>
                      ) : (
                        <span className="text-slate-500 pl-2">#{model.rank}</span>
                      )}
                    </td>

                    {/* Algorithm Name */}
                    <td className="py-3 px-4 whitespace-nowrap font-sans">
                      <div className="flex items-center space-x-2">
                        <span className={`font-semibold ${isChampion ? 'text-teal-300' : 'text-slate-200'}`}>
                          {model.algorithm_name}
                        </span>
                        {isChampion && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30 font-mono">
                            Winner
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Primary Score */}
                    <td className="py-3 px-4 whitespace-nowrap text-right">
                      <span className={`text-sm font-bold ${isChampion ? 'text-teal-400' : 'text-slate-200'}`}>
                        {(model.primary_score * 100).toFixed(2)}%
                      </span>
                      <span className="text-[11px] text-slate-500 block font-normal">
                        ±{(model.primary_score_std * 100).toFixed(2)}%
                      </span>
                    </td>

                    {/* Accuracy */}
                    <td className="py-3 px-4 whitespace-nowrap text-right text-slate-300">
                      {acc !== undefined && acc !== null ? `${(acc * 100).toFixed(1)}%` : '—'}
                    </td>

                    {/* Precision */}
                    <td className="py-3 px-4 whitespace-nowrap text-right text-slate-300">
                      {prec !== undefined && prec !== null ? `${(prec * 100).toFixed(1)}%` : '—'}
                    </td>

                    {/* Recall */}
                    <td className="py-3 px-4 whitespace-nowrap text-right text-slate-300">
                      {rec !== undefined && rec !== null ? `${(rec * 100).toFixed(1)}%` : '—'}
                    </td>

                    {/* Training Duration */}
                    <td className="py-3 px-4 whitespace-nowrap text-right text-slate-400">
                      {(model.training_duration_seconds * 1000).toFixed(1)} ms
                    </td>

                    {/* Prediction Duration */}
                    <td className="py-3 px-4 whitespace-nowrap text-right text-slate-400">
                      {(model.prediction_duration_seconds * 1000).toFixed(1)} ms
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Failed Models notification if any */}
        {failed_models.length > 0 && (
          <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-800/40 text-xs text-rose-300 space-y-1">
            <span className="font-semibold uppercase tracking-wider block">Failed Classifiers:</span>
            {failed_models.map((f, i) => (
              <p key={i}>
                <span className="font-mono font-bold">{f.algorithm_id}</span>: {f.error}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
