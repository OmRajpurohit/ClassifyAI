# ClassifyAI — Autonomous Machine Learning Classifier Selection Agent

**ClassifyAI** is an intelligent, rule-based machine learning orchestration agent paired with a modern interactive React dashboard. It automates exploratory data profiling, anti-leakage preprocessing, cross-validated model benchmarking, deterministic model ranking, and holdout evaluation for tabular classification tasks.

---

## 🌟 Key Features

### 1. 🤖 Autonomous ML Orchestration Agent
- **Automated Data Type Inference**: Distinguishes numeric and categorical features automatically.
- **Strict Anti-Leakage Pipelines**: Encapsulates imputation, standard scaling, and one-hot encoding strictly within each cross-validation fold using `scikit-learn` Pipelines and `ColumnTransformer`.
- **Imbalance-Aware Validation**: Detects class imbalances and automatically applies `StratifiedKFold` cross-validation to maintain consistent class proportions across splits.
- **6 Benchmarked Classifiers**:
  - **Random Forest** (Bagging ensemble, Gini impurity feature importances)
  - **Gradient Boosting** (Sequential residual boosting)
  - **Logistic Regression** (L2-regularized probabilistic linear model)
  - **Support Vector Machine** (Non-linear RBF kernel)
  - **K-Nearest Neighbors** (Instance-based majority voting)
  - **Decision Tree** (White-box tree partitioner)
- **Deterministic Ranking**: Ranks candidates by CV primary score (e.g. `f1_weighted`), breaks ties by standard deviation, and flags statistical ambiguity if models score within a 1% margin.
- **Held-Out Test Split**: Evaluates the champion model on an isolated test split, calculating a confusion matrix and predictive feature importances.

### 2. ⚡ Modern Interactive React Dashboard (Phase 6)
- **Drag & Drop CSV Ingestion**: Upload any tabular dataset or load the bundled benchmark with 1-click.
- **Exploratory Data Profiling**: Real-time summary of row/column counts, missing values, duplicates, and candidate target columns.
- **Target Imbalance Visualizer**: Interactive class breakdown progress bars, imbalance ratios, and agent optimization tactics.
- **Interactive Leaderboard**:
  - Champion trophy showcase with natural-language agent explanation.
  - Formatted leaderboard table with primary metric, accuracy, precision, recall, training time, and latency.
- **Interactive Visual Charts**:
  - Recharts side-by-side performance comparison across metrics and training latency.
  - Held-out test confusion matrix heatmap.
  - Top predictive feature importances horizontal bar chart.
- **Interactive Inference Playground**:
  - Real-time test-drive form pre-filled with dataset instances.
  - Instant classification outputs with class probability distribution gauges.
- **Live Agent Audit Trail**:
  - Terminal-style log drawer exposing every autonomous pipeline decision.

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.13)
- **Node.js**: v18+ (tested on Node v24)
- **npm**: 9+ (tested on npm 11)

---

### Step 1: Start the FastAPI Backend

```bash
# Navigate to backend and activate virtual environment
cd backend
..\venv\Scripts\activate   # On Windows (or source ../venv/bin/activate on Unix)

# Install dependencies if not already installed
pip install -r requirements.txt

# Launch FastAPI development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend API will be live at:
- **Root API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

### Step 2: Start the React Frontend Dashboard

Open a separate terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Vite development server
npm run dev
```

The interactive dashboard will launch at:
- **Local Dashboard**: `http://localhost:5173`

---

## 🧪 Running Automated Tests

Run the full suite of 61 unit and integration tests covering preprocessing, algorithms, the agent, ranking, and API endpoints:

```bash
# Run pytest from project root
.\venv\Scripts\pytest
```

---

## 📁 Repository Structure

```text
ClassifyAI/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── classifier_agent.py      # Core autonomous ML agent
│   │   ├── algorithms/                  # 6 classification algorithm definitions
│   │   ├── api/
│   │   │   └── routes.py                # FastAPI endpoints
│   │   ├── schemas/
│   │   │   └── responses.py             # Pydantic models & validation
│   │   ├── services/
│   │   │   ├── data_analyzer.py         # EDA & target imbalance analysis
│   │   │   ├── model_evaluator.py       # Cross-validation & metric computation
│   │   │   ├── model_ranker.py          # Deterministic leaderboard ranking
│   │   │   ├── model_trainer.py         # Pipeline fitting & prediction
│   │   │   └── preprocessing.py         # Leakage-free ColumnTransformers
│   │   ├── utils/
│   │   └── main.py                      # FastAPI entrypoint & CORS
│   ├── tests/                           # 61 pytest test cases
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx               # System health & actions
│   │   │   ├── DatasetUpload.jsx        # Drag-drop & sample dataset loader
│   │   │   ├── DatasetOverview.jsx      # EDA metrics & sample preview
│   │   │   ├── TargetAnalysis.jsx       # Target selector & class breakdown
│   │   │   ├── ExperimentConfig.jsx     # Algorithm & CV hyperparameter picker
│   │   │   ├── AgentExecutionLogs.jsx   # Live terminal audit log
│   │   │   ├── Leaderboard.jsx          # Champion showcase & ranked table
│   │   │   ├── PerformanceCharts.jsx    # Recharts benchmark comparison
│   │   │   ├── ConfusionMatrix.jsx      # Test confusion matrix heatmap
│   │   │   ├── FeatureImportance.jsx    # Attributions bar chart
│   │   │   └── PredictionPlayground.jsx # Live interactive inference studio
│   │   ├── services/
│   │   │   └── api.js                   # API client & sample benchmark
│   │   ├── App.jsx                      # Main dashboard layout & state
│   │   └── index.css                    # Tailwind CSS & styling
│   ├── package.json
│   └── vite.config.js
└── sample_data/
    └── sample_classification.csv        # Credit approval benchmark dataset
```

---

## 🛡️ Architecture & Methodological Safeguards

1. **Anti-Leakage Imputation & Scaling**:
   All imputers (`SimpleImputer`) and scalers (`StandardScaler`) are encapsulated in an `sklearn.pipeline.Pipeline`. They are fitted **only** on the training folds and applied to validation/test folds without exposing test distribution statistics.
2. **Stratified Sampling**:
   To prevent target class dropouts in minority classes, cross-validation is performed using `StratifiedKFold`.
3. **Reproducibility**:
   A deterministic `random_state` is threaded into splits and stochastic models (Random Forest, Gradient Boosting, Logistic Regression).
