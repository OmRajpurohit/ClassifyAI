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
import { getHealth, runClassification } from './services/api';
import { AlertCircle, X, Sparkles, Database, CheckCircle, ArrowRight } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [dataset, setDataset] = useState(null);
  const [selectedTarget, setSelectedTarget] = useState('');
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
        selected_algorithms: experimentConfig.selected_algorithms,
        primary_metric: experimentConfig.primary_metric,
        cv_folds: experimentConfig.cv_folds,
        test_size: experimentConfig.test_size,
        random_state: experimentConfig.random_state,
      };

      const results = await runClassification(payload);
      setExperimentResults(results);

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
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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

        {/* Step 1: Upload Dataset (when no dataset loaded) */}
        {!dataset && (
          <DatasetUpload
            onDatasetUploaded={handleDatasetUploaded}
            isLoading={isLoadingDataset}
            setIsLoading={setIsLoadingDataset}
            setError={setError}
          />
        )}

        {/* Step 2: Dataset Loaded -> Configuration & Workflow */}
        {dataset && (
          <div className="space-y-8 animate-fade-in">
            {/* Dataset Profiling Overview */}
            <DatasetOverview dataset={dataset} />

            {/* Target Column Selection & Imbalance Analysis */}
            <TargetAnalysis
              dataset={dataset}
              selectedTarget={selectedTarget}
              setSelectedTarget={setSelectedTarget}
              targetAnalysis={targetAnalysis}
              setTargetAnalysis={setTargetAnalysis}
              setError={setError}
            />

            {/* Algorithm & Metric Configuration */}
            <ExperimentConfig
              config={experimentConfig}
              setConfig={setExperimentConfig}
              onRunExperiment={handleRunExperiment}
              isRunning={isRunningExperiment}
              disabled={!selectedTarget || !targetAnalysis}
            />

            {/* Real-time / Historic Agent Execution Logs */}
            {(isRunningExperiment || liveLogs.length > 0) && (
              <AgentExecutionLogs
                logs={liveLogs}
                isRunning={isRunningExperiment}
              />
            )}

            {/* Step 3: Experiment Results & Visualizations */}
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
          </div>
        )}
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
