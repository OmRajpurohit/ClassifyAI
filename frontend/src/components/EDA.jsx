import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { Activity, AlertTriangle, BarChart3, Database, Hash } from 'lucide-react';
import { getDatasetEda } from '../services/api';

const COLORS = ['#2dd4bf', '#38bdf8', '#818cf8', '#c084fc', '#fbbf24', '#fb7185', '#34d399'];
const chartCard = 'glass-card rounded-2xl p-5 space-y-4 min-w-0';
const tooltipStyle = { backgroundColor: '#090d16', borderColor: '#334155', borderRadius: 10, fontSize: 12 };

export default function EDA({ dataset, target, setError }) {
  const [eda, setEda] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!dataset?.dataset_id || !target) return;
    let active = true;
    setLoading(true);
    getDatasetEda(dataset.dataset_id, target)
      .then(data => { if (active) setEda(data); })
      .catch(err => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [dataset?.dataset_id, target]);

  if (!dataset) return <div className={chartCard}><h2 className="text-lg font-semibold">Exploratory data analysis</h2><p className="text-sm text-slate-400">Add a dataset to explore its distributions, missing values, and target balance.</p></div>;
  if (loading || !eda) return <div className={chartCard}><p className="text-sm text-slate-400">Preparing dataset visualizations…</p></div>;
  const numericEntries = Object.entries(eda.numeric_distributions || {});
  const categoricalEntries = Object.entries(eda.categorical_distributions || {});
  const missing = (eda.missing_values || []).filter(item => item.count > 0);
  const summary = [
    { label: 'Rows', value: eda.row_count, icon: Database, color: 'text-teal-300' },
    { label: 'Columns', value: eda.column_count, icon: Hash, color: 'text-sky-300' },
    { label: 'Missing cells', value: (eda.missing_values || []).reduce((sum, item) => sum + item.count, 0), icon: AlertTriangle, color: 'text-amber-300' },
    { label: 'Duplicate rows', value: eda.duplicate_rows, icon: Activity, color: 'text-violet-300' },
  ];

  return <section className="space-y-5 animate-fade-in">
    <header className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
      <div><p className="text-xs uppercase tracking-[.18em] text-teal-300 font-semibold">Dataset workspace / EDA</p><h1 className="text-2xl font-bold text-white mt-1">Explore your data</h1><p className="text-sm text-slate-400 mt-1">Quick visual checks to understand distributions, data quality, and class balance.</p></div>
      <span className="text-xs text-slate-400 px-3 py-2 rounded-lg bg-slate-900 border border-slate-800">{dataset.filename}</span>
    </header>
    <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">{summary.map(item => <div key={item.label} className="glass-card rounded-xl p-4 flex items-center gap-3"><item.icon className={`w-4 h-4 ${item.color}`} /><div><p className="text-xs text-slate-400">{item.label}</p><p className="text-lg font-semibold text-white">{Number(item.value).toLocaleString()}</p></div></div>)}</div>
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <div className={chartCard}><div><h2 className="font-semibold text-slate-100">Target class balance</h2><p className="text-xs text-slate-400 mt-1">Number of rows in each class for <b className="text-slate-200">{target}</b>.</p></div><div className="h-64">{eda.target_distribution?.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={eda.target_distribution} margin={{ top: 8, right: 12, left: -18, bottom: 8 }}><CartesianGrid stroke="#1e293b" vertical={false} /><XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 11 }} /><YAxis allowDecimals={false} tick={{ fill: '#94a3b8', fontSize: 11 }} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="count" name="Rows" radius={[5, 5, 0, 0]}>{eda.target_distribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Bar></BarChart></ResponsiveContainer> : <p className="text-sm text-slate-500">No target values to chart.</p>}</div><p className="text-[11px] text-slate-500">Use this to spot classes that may be underrepresented.</p></div>
      <div className={chartCard}><div><h2 className="font-semibold text-slate-100">Missing values by column</h2><p className="text-xs text-slate-400 mt-1">Columns with missing cells may need imputation.</p></div><div className="h-64">{missing.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={missing} margin={{ top: 8, right: 12, left: -18, bottom: 30 }}><CartesianGrid stroke="#1e293b" vertical={false} /><XAxis dataKey="column" angle={-20} textAnchor="end" interval={0} tick={{ fill: '#94a3b8', fontSize: 10 }} /><YAxis allowDecimals={false} tick={{ fill: '#94a3b8', fontSize: 11 }} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="count" name="Missing cells" fill="#fbbf24" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer> : <div className="h-full flex items-center justify-center text-sm text-emerald-300">No missing values found</div>}</div><p className="text-[11px] text-slate-500">Missing cells are shown before preprocessing.</p></div>
      {numericEntries.map(([column, data]) => <div className={chartCard} key={column}><div><h2 className="font-semibold text-slate-100">{column} distribution</h2><p className="text-xs text-slate-400 mt-1">Numeric values grouped into ranges.</p></div><div className="h-60">{data.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 8, right: 12, left: -18, bottom: 8 }}><CartesianGrid stroke="#1e293b" vertical={false} /><XAxis dataKey="range" tick={{ fill: '#94a3b8', fontSize: 9 }} /><YAxis allowDecimals={false} tick={{ fill: '#94a3b8', fontSize: 11 }} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="count" name="Rows" fill="#2dd4bf" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer> : <p className="text-sm text-slate-500">No numeric values to chart.</p>}</div></div>)}
      {categoricalEntries.map(([column, data]) => <div className={chartCard} key={column}><div><h2 className="font-semibold text-slate-100">{column} categories</h2><p className="text-xs text-slate-400 mt-1">Most frequent values (up to 12 categories).</p></div><div className="h-60">{data.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 8, right: 12, left: -18, bottom: 28 }}><CartesianGrid stroke="#1e293b" vertical={false} /><XAxis dataKey="label" angle={-20} textAnchor="end" interval={0} tick={{ fill: '#94a3b8', fontSize: 9 }} /><YAxis allowDecimals={false} tick={{ fill: '#94a3b8', fontSize: 11 }} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="count" name="Rows" radius={[4, 4, 0, 0]}>{data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Bar></BarChart></ResponsiveContainer> : <p className="text-sm text-slate-500">No category values to chart.</p>}</div></div>)}
    </div>
    {!numericEntries.length && !categoricalEntries.length && <div className={chartCard}><BarChart3 className="w-5 h-5 text-teal-300"/><p className="text-sm text-slate-400">No supported numeric or categorical columns were found.</p></div>}
  </section>;
}
