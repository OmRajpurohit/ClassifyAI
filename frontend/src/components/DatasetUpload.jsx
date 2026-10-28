import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Sparkles, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { uploadDataset, SAMPLE_DATASET_CSV } from '../services/api';

export default function DatasetUpload({ onDatasetUploaded, isLoading, setIsLoading, setError }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Only CSV (.csv) files are supported for tabular classification.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const data = await uploadDataset(file, file.name);
      onDatasetUploaded(data);
    } catch (err) {
      setError(err.message || 'Failed to upload dataset.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleLoadSample = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const blob = new Blob([SAMPLE_DATASET_CSV], { type: 'text/csv' });
      const sampleFile = new File([blob], 'sample_classification.csv', { type: 'text/csv' });
      const data = await uploadDataset(sampleFile, 'sample_classification.csv');
      onDatasetUploaded(data);
    } catch (err) {
      setError(err.message || 'Failed to load sample dataset.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Hero Welcome Banner */}
      <div className="text-center space-y-3 pt-6 pb-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Rule-Based Intelligent Classifier Selector</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
          Automated Machine Learning <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-300">Classification</span>
        </h1>
        <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
          Upload any tabular dataset. The agent automatically detects schema types, constructs anti-leakage pipelines, trains & ranks 6 classification models via Stratified CV, and selects the champion classifier.
        </p>
      </div>

      {/* Main Drag-Drop Box */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        className={`glass-card rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all border-2 border-dashed ${
          isDragging
            ? 'border-teal-400 bg-teal-500/5 scale-[1.01]'
            : 'border-slate-700/80 hover:border-slate-500/80 hover:bg-slate-900/60'
        } ${isLoading ? 'pointer-events-none opacity-60' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400 group-hover:scale-110 transition-transform">
            {isLoading ? (
              <div className="w-8 h-8 border-3 border-teal-400 border-t-transparent rounded-full animate-spin" />
            ) : (
              <UploadCloud className="w-8 h-8" />
            )}
          </div>

          <div className="space-y-1">
            <p className="text-lg font-semibold text-slate-200">
              {isLoading ? 'Profiling and analyzing CSV...' : 'Drag & drop your CSV dataset here'}
            </p>
            <p className="text-xs sm:text-sm text-slate-400">
              or <span className="text-teal-400 underline underline-offset-2">browse files</span> from your computer
            </p>
          </div>

          <div className="flex items-center space-x-4 text-xs text-slate-500 pt-2">
            <span>• Max file size: 50MB</span>
            <span>• Supported: .CSV</span>
            <span>• Tabular classification</span>
          </div>
        </div>
      </div>

      {/* Quick Sample Dataset Bar */}
      <div className="glass-card rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-200">Want to test immediately?</h4>
            <p className="text-xs text-slate-400">
              Load our benchmark Credit & Loan Approval dataset (50 rows, mixed categorical & numeric features).
            </p>
          </div>
        </div>

        <button
          onClick={handleLoadSample}
          disabled={isLoading}
          className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs transition-all shadow-md shadow-teal-500/20 disabled:opacity-50"
        >
          <span>Load Sample Dataset</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Capabilities Overview Pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
        <div className="glass-card rounded-xl p-3 flex items-start space-x-2.5">
          <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
          <div>
            <h5 className="text-xs font-semibold text-slate-200">Anti-Leakage Preprocessing</h5>
            <p className="text-[11px] text-slate-400">Imputation, one-hot encoding, and standard scaling fit strictly within each fold.</p>
          </div>
        </div>
        <div className="glass-card rounded-xl p-3 flex items-start space-x-2.5">
          <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
          <div>
            <h5 className="text-xs font-semibold text-slate-200">6 Classifiers Evaluated</h5>
            <p className="text-[11px] text-slate-400">Random Forest, Gradient Boosting, SVM, Logistic Regression, KNN & Decision Tree.</p>
          </div>
        </div>
        <div className="glass-card rounded-xl p-3 flex items-start space-x-2.5">
          <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
          <div>
            <h5 className="text-xs font-semibold text-slate-200">Interactive Playground</h5>
            <p className="text-[11px] text-slate-400">Test drive the winning pipeline immediately with custom input instances.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
