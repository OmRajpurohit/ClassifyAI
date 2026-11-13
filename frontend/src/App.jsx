import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DatasetUpload from './components/DatasetUpload';
import DatasetOverview from './components/DatasetOverview';
import TargetAnalysis from './components/TargetAnalysis';
import ExperimentConfig from './components/ExperimentConfig';
import AgentExecutionLogs from './components/AgentExecutionLogs';
import Leaderboard from './components/Leaderboard';
import PerformanceCharts from './components/PerformanceCharts';
import ConfusionMatrix from './components/ConfusionMatrix';
import FeatureImportance from './components/FeatureImportance';
import PredictionPlayground from './components/PredictionPlayground';
import EDA from './components/EDA';
import { getHealth, runClassification, getPreprocessingPreview } from './services/api';
import { Activity, AlertCircle, BarChart3, Check, Database, Eye, FlaskConical, SlidersHorizontal, Upload, X } from 'lucide-react';

const WORKFLOW = [
  { id: 'dataset', label: 'Add dataset', icon: Upload },
  { id: 'eda', label: 'EDA', icon: BarChart3 },
  { id: 'preprocessing', label: 'Preprocessing', icon: FlaskConical },
  { id: 'preview', label: 'Preview data', icon: Eye },
  { id: 'models', label: 'Select models', icon: SlidersHorizontal },
  { id: 'results', label: 'Results', icon: Activity },
];

export default function App() {
  const [health, setHealth] = useState(null);
  const [activeStep, setActiveStep] = useState('dataset');
  const [dataset, setDataset] = useState(null);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [droppedColumns, setDroppedColumns] = useState([]);
  const [processedPreview, setProcessedPreview] = useState(null);
  const [targetAnalysis, setTargetAnalysis] = useState(null);
  const [experimentConfig, setExperimentConfig] = useState({
    selected_algorithms: [
      'random_forest',
      'gradient_boosting',
      'logistic_regression',
      'svm',
      'knn',
      'decision_tree',
    ],
    primary_metric: 'f1_weighted',
    cv_folds: 5,
    test_size: 0.2,
    random_state: 42,
  });

  const [isLoadingDataset, setIsLoadingDataset] = useState(false);
  const [isRunningExperiment, setIsRunningExperiment] = useState(false);
  const [experimentResults, setExperimentResults] = useState(null);
  const [liveLogs, setLiveLogs] = useState([]);
  const [error, setError] = useState(null);
  useEffect(() => {
    if (!dataset?.dataset_id || !selectedTarget) return;
    let active = true;
    getPreprocessingPreview(dataset.dataset_id, selectedTarget, droppedColumns).then(v => { if (active) setProcessedPreview(v); }).catch(e => setError(e.message));
    return () => { active = false; };
  }, [dataset?.dataset_id, selectedTarget, droppedColumns]);

  // Poll health on mount
  useEffect(() => {
    async function checkSystemHealth() {
      try {
        const data = await getHealth();
        setHealth(data);
      } catch (err) {
        setHealth({ status: 'offline', error: err.message });
      }
    }
    checkSystemHealth();
  }, []);

  // When a new dataset is uploaded
  const handleDatasetUploaded = (data) => {
    setDataset(data);
    setExperimentResults(null);
    setLiveLogs([]);
    setError(null);
    setActiveStep('eda');

    // Default target column to the first candidate, or the last column
    if (data.target_candidates && data.target_candidates.length > 0) {
      setSelectedTarget(data.target_candidates[0]);
    } else if (data.columns && data.columns.length > 0) {
      setSelectedTarget(data.columns[data.columns.length - 1]);
    }
  };

  // Reset to initial state
  const handleReset = () => {
    setDataset(null);
    setSelectedTarget('');
    setTargetAnalysis(null);
    setExperimentResults(null);
    setLiveLogs([]);
    setError(null);
    setActiveStep('dataset');
  };

  // Run Classification Experiment
  const handleRunExperiment = async () => {
    if (!dataset?.dataset_id || !selectedTarget) {
      setError('Please upload a dataset and select a target column first.');
      return;
    }

    try {
      setIsRunningExperiment(true);
      setError(null);
      setExperimentResults(null);

      // Initial animated simulated agent logs while waiting for backend
      setLiveLogs([
        'Initializing ClassifyAI Autonomous Agent...',
        `Selected Target: "${selectedTarget}" across ${dataset.row_count} records.`,
        'Verifying schema isolation & constructing anti-leakage preprocessing pipelines...',
        `Building ${experimentConfig.cv_folds}-Fold Stratified Cross-Validation splits...`,
        `Training & benchmarking ${experimentConfig.selected_algorithms.length} candidate classifiers...`,
      ]);

      const payload = {
        dataset_id: dataset.dataset_id,
        target_column: selectedTarget,
        dropped_columns: droppedColumns,
        selected_algorithms: experimentConfig.selected_algorithms,
        primary_metric: experimentConfig.primary_metric,
        cv_folds: experimentConfig.cv_folds,
        test_size: experimentConfig.test_size,
        random_state: experimentConfig.random_state,
      };

      const results = await runClassification(payload);
      setExperimentResults(results);
      setActiveStep('results');

      // Use the actual server agent logs
      if (results.agent_logs && results.agent_logs.length > 0) {
        setLiveLogs(results.agent_logs);
      }
    } catch (err) {
      setError(err.message || 'Classification experiment encountered an error.');
      setLiveLogs((prev) => [...prev, `[ERROR] Experiment failed: ${err.message}`]);
    } finally {
      setIsRunningExperiment(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-teal-500/30 selection:text-teal-200">
      {/* Navigation Header */}
      <Header
        health={health}
        onReset={dataset ? handleReset : null}
        isRunning={isRunningExperiment}
      />

      {/* Main Body Content Container */}
      <main className="flex-1 w-full max-w-[1600px] mx-auto px-3 sm:px-5 lg:px-7 py-5">
        <div className="flex flex-col lg:flex-row gap-5 items-start">
          <aside className="w-full lg:w-60 lg:shrink-0 lg:sticky lg:top-5 glass-card rounded-2xl p-3">
            <div className="px-3 py-3 border-b border-slate-800 mb-2"><p className="text-[10px] uppercase tracking-[.18em] font-bold text-teal-300">Workspace</p><p className="text-sm font-semibold text-white mt-1">Model workflow</p></div>
            <nav className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-1 gap-1" aria-label="Project workflow">
              {WORKFLOW.map((step, index) => {
                const Icon = step.icon;
                const blocked = step.id !== 'dataset' && !dataset;
                const complete = step.id === 'dataset' ? !!dataset : step.id === 'eda' ? !!dataset : step.id === 'preprocessing' ? !!processedPreview : step.id === 'preview' ? !!processedPreview : step.id === 'models' ? !!targetAnalysis : step.id === 'results' ? !!experimentResults : false;
                return <button key={step.id} type="button" disabled={blocked} onClick={() => setActiveStep(step.id)} className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${activeStep === step.id ? 'bg-teal-400/10 text-teal-200 border border-teal-400/20' : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent'}`}>
                  <span className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${activeStep === step.id ? 'bg-teal-400/15' : 'bg-slate-900 group-hover:bg-slate-800'}`}>{complete && step.id !== 'dataset' ? <Check className="w-3.5 h-3.5 text-emerald-400"/> : <Icon className="w-3.5 h-3.5"/>}</span>
                  <span className="min-w-0"><span className="block text-xs font-semibold">{step.label}</span><span className="hidden lg:block text-[10px] opacity-60 mt-0.5">Step {index + 1}</span></span>
                </button>;
              })}
            </nav>
            <div className="hidden lg:block mt-4 rounded-xl bg-slate-950/70 border border-slate-800 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-500">Current dataset</p><p className="text-xs text-slate-300 mt-1 truncate">{dataset?.filename || 'No dataset added yet'}</p>{dataset && <p className="text-[10px] text-slate-500 mt-1">{dataset.row_count?.toLocaleString()} rows · {dataset.column_count} columns</p>}</div>
          </aside>

          <div className="flex-1 min-w-0 w-full space-y-5">
        {/* Error Notification Toast */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/80 text-rose-300 text-sm flex items-start justify-between gap-3 animate-fade-in">
            <div className="flex items-start space-x-2.5">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-rose-400" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => setError(null)}
              className="p-1 rounded text-rose-400 hover:text-rose-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {activeStep === 'dataset' && (
          <DatasetUpload
            onDatasetUploaded={handleDatasetUploaded}
            isLoading={isLoadingDataset}
            setIsLoading={setIsLoadingDataset}
            setError={setError}
          />
        )}

        {dataset && activeStep === 'eda' && <EDA dataset={dataset} target={selectedTarget} setError={setError} />}

        {dataset && activeStep === 'preprocessing' && <div className="space-y-5">
            <div><p className="text-xs uppercase tracking-[.18em] text-teal-300 font-semibold">Step 3</p><h1 className="text-2xl font-bold mt-1">Preprocessing & feature selection</h1><p className="text-sm text-slate-400 mt-1">Choose your target and review how missing values and feature columns are handled.</p></div>
            <TargetAnalysis
              dataset={dataset}
              selectedTarget={selectedTarget}
              setSelectedTarget={setSelectedTarget}
              targetAnalysis={targetAnalysis}
              setTargetAnalysis={setTargetAnalysis}
              setError={setError}
            />
            <DatasetOverview dataset={dataset} target={selectedTarget} droppedColumns={droppedColumns} setDroppedColumns={setDroppedColumns} processedPreview={processedPreview} />
          </div>}

        {dataset && activeStep === 'preview' && <div className="space-y-5">
          <div><p className="text-xs uppercase tracking-[.18em] text-teal-300 font-semibold">Step 4</p><h1 className="text-2xl font-bold mt-1">Processed data preview</h1><p className="text-sm text-slate-400 mt-1">The first rows after preview imputation, with selected columns removed.</p></div>
          <ProcessedDataPreview dataset={dataset} preview={processedPreview} loading={!processedPreview} />
        </div>}

        {dataset && activeStep === 'models' && <div className="space-y-5">
            <div><p className="text-xs uppercase tracking-[.18em] text-teal-300 font-semibold">Step 5</p><h1 className="text-2xl font-bold mt-1">Choose models and evaluation settings</h1><p className="text-sm text-slate-400 mt-1">Select classifiers and start the experiment when your target is ready.</p></div>
            <ExperimentConfig
              config={experimentConfig}
              setConfig={setExperimentConfig}
              onRunExperiment={handleRunExperiment}
              isRunning={isRunningExperiment}
              disabled={!selectedTarget || !targetAnalysis}
            />
        </div>}

        {dataset && activeStep === 'results' && <div className="space-y-5">
          <div><p className="text-xs uppercase tracking-[.18em] text-teal-300 font-semibold">Step 6</p><h1 className="text-2xl font-bold mt-1">Experiment results</h1></div>
          {(isRunningExperiment || liveLogs.length > 0) && (
              <AgentExecutionLogs
                logs={liveLogs}
                isRunning={isRunningExperiment}
              />
            )}

            {experimentResults && (
              <div className="space-y-8 pt-4 animate-slide-up">
                {/* Winner Showcase & Leaderboard Table */}
                <Leaderboard results={experimentResults} />

                {/* Performance Comparison Charts */}
                <PerformanceCharts results={experimentResults} />

                {/* Confusion Matrix & Feature Importances Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <ConfusionMatrix
                    winningDetails={experimentResults.winning_model_details}
                    classes={experimentResults.classes}
                  />

                  <FeatureImportance
                    winningDetails={experimentResults.winning_model_details}
                    algorithmName={experimentResults.winner?.algorithm_name || 'Winning Classifier'}
                  />
                </div>

                {/* Interactive Inference Playground */}
                <PredictionPlayground
                  experimentId={experimentResults.experiment_id}
                  datasetSummary={experimentResults.dataset_summary}
                  targetColumn={selectedTarget}
                  winner={experimentResults.winner}
                  classes={experimentResults.classes}
                />
              </div>
            )}
          {!experimentResults && !isRunningExperiment && <div className="glass-card rounded-2xl p-8 text-center"><p className="font-semibold text-slate-200">No experiment results yet</p><p className="text-sm text-slate-400 mt-1">Configure and run models to see their results here.</p><button onClick={() => setActiveStep('models')} className="mt-4 px-4 py-2 rounded-lg bg-teal-400 text-slate-950 text-sm font-semibold">Go to model selection</button></div>}
        </div>}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>ClassifyAI — Autonomous Machine Learning Classifier Agent</span>
          <span>FastAPI • Scikit-Learn • React • Tailwind CSS • Recharts</span>
        </div>
      </footer>
    </div>
  );
}

function ProcessedDataPreview({ dataset, preview, loading }) {
  const columns = preview?.columns || [];
  return <div className="glass-card rounded-2xl p-5 space-y-4"><div><h2 className="font-semibold text-slate-100">First five processed rows</h2><p className="text-xs text-slate-400 mt-1">Target: {dataset ? 'selected in preprocessing' : '—'} · {columns.length} features included</p></div>
    {loading ? <p className="text-sm text-slate-400">Loading preview…</p> : <div className="overflow-x-auto rounded-xl border border-slate-800"><table className="w-full text-left text-xs text-slate-300"><thead className="bg-slate-900 text-slate-400"><tr><th className="p-3">#</th>{columns.map(col => <th key={col} className="p-3 whitespace-nowrap">{col}</th>)}</tr></thead><tbody>{(preview?.sample_preview || []).map((row, i) => <tr key={i} className="border-t border-slate-800"><td className="p-3 text-slate-500">{i + 1}</td>{columns.map(col => <td key={col} className="p-3 whitespace-nowrap">{row[col] ?? 'null'}</td>)}</tr>)}</tbody></table></div>}
    {preview?.note && <p className="text-xs text-slate-500">{preview.note}</p>}
  </div>;
}
