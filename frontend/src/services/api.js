/**
 * ClassifyAI API Client
 * Facilitates communication with the FastAPI backend.
 */

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

/**
 * Handle API responses with proper JSON parsing and descriptive errors.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (typeof errorJson.detail === 'string') {
          errorDetail = errorJson.detail;
        } else if (Array.isArray(errorJson.detail)) {
          errorDetail = errorJson.detail.map(d => `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}`).join('; ');
        } else {
          errorDetail = JSON.stringify(errorJson.detail);
        }
      }
    } catch (_) {
      // Keep default text
    }
    const err = new Error(errorDetail);
    err.status = response.status;
    throw err;
  }
  return await response.json();
}

/**
 * Check backend health status and algorithm inventory.
 */
export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse(res);
}

/**
 * Retrieve registered algorithm metadata.
 */
export async function getAlgorithms() {
  const res = await fetch(`${API_BASE}/algorithms`);
  return handleResponse(res);
}

/**
 * Upload a CSV dataset file and receive exploratory profiling.
 * @param {File|Blob} file 
 * @param {string} filename
 */
export async function uploadDataset(file, filename = 'dataset.csv') {
  const formData = new FormData();
  formData.append('file', file, filename);

  const res = await fetch(`${API_BASE}/dataset/preview`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

/**
 * Perform target column imbalance and class distribution analysis.
 * @param {string} datasetId 
 * @param {string} targetColumn 
 */
export async function analyzeTarget(datasetId, targetColumn) {
  const res = await fetch(`${API_BASE}/dataset/target-analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataset_id: datasetId,
      target_column: targetColumn,
    }),
  });
  return handleResponse(res);
}

/**
 * Execute the autonomous classifier selection agent.
 * @param {Object} config 
 */
export async function runClassification(config) {
  const res = await fetch(`${API_BASE}/classification/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  return handleResponse(res);
}

/**
 * Retrieve cached results for an experiment.
 * @param {string} experimentId 
 */
export async function getExperimentResults(experimentId) {
  const res = await fetch(`${API_BASE}/classification/results/${experimentId}`);
  return handleResponse(res);
}

/**
 * Run inference using the winning model pipeline.
 * @param {string} experimentId 
 * @param {Array<Object>} instances 
 */
export async function predict(experimentId, instances) {
  const res = await fetch(`${API_BASE}/classification/predict/${experimentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ instances }),
  });
  return handleResponse(res);
}

/**
 * Embedded sample dataset (Loan Approval classification benchmark)
 * Provides instant demonstration without requiring local file browsing.
 */
export const SAMPLE_DATASET_CSV = `age,income,credit_score,loan_amount,employment_type,education_level,loan_approved
45,65000,720,15000,salaried,bachelor,1
28,32000,610,8000,salaried,high_school,0
36,89000,780,25000,salaried,master,1
52,110000,740,30000,self_employed,doctorate,1
23,24000,580,5000,unemployed,high_school,0
41,72000,690,18000,salaried,bachelor,1
31,48000,650,12000,salaried,bachelor,1
60,95000,710,20000,self_employed,bachelor,1
25,29000,590,7000,unemployed,high_school,0
38,82000,760,22000,salaried,master,1
49,105000,800,35000,salaried,doctorate,1
33,54000,640,14000,salaried,bachelor,0
29,42000,630,10000,salaried,high_school,0
47,91000,750,28000,self_employed,master,1
55,125000,810,40000,salaried,doctorate,1
24,26000,570,6000,unemployed,high_school,0
35,68000,700,16000,salaried,bachelor,1
42,78000,680,20000,salaried,master,1
58,88000,730,24000,salaried,bachelor,1
27,35000,600,9000,salaried,high_school,0
39,85000,770,26000,self_employed,master,1
50,115000,790,32000,salaried,doctorate,1
32,51000,660,13000,salaried,bachelor,1
26,31000,590,7500,unemployed,high_school,0
44,79000,710,21000,salaried,bachelor,1
37,84000,750,23000,salaried,master,1
53,108000,770,30000,salaried,doctorate,1
30,46000,640,11000,salaried,bachelor,0
48,93000,760,27000,self_employed,master,1
56,130000,820,45000,salaried,doctorate,1
22,22000,560,4000,unemployed,high_school,0
43,76000,695,19000,salaried,bachelor,1
34,60000,670,15000,salaried,bachelor,1
59,92000,725,23000,salaried,master,1
29,38000,615,8500,salaried,high_school,0
40,86000,765,25000,self_employed,master,1
51,118000,795,34000,salaried,doctorate,1
33,53000,655,13500,salaried,bachelor,1
25,28000,585,6500,unemployed,high_school,0
46,81000,715,21500,salaried,bachelor,1
42,75000,690,18500,salaried,bachelor,1
35,62000,675,15500,salaried,bachelor,1
61,96000,730,24500,salaried,master,1`;
