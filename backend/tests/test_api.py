"""Integration tests for FastAPI REST API endpoints.

Verifies:
- System health and algorithm discovery endpoints.
- CSV dataset upload, validation, and exploratory profiling.
- Target column selection and imbalance analysis.
- Classification experiment execution via the agent.
- Experiment results retrieval by UUID.
- Model inference / prediction endpoint with probability outputs.
- Comprehensive HTTP status codes and error handling (400, 404, 422).
"""

import io
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_CSV = """age,income,credit_score,loan_amount,employment_type,education_level,loan_approved
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
"""


# -----------------------------------------------------------------------------
# System & Discovery Endpoints
# -----------------------------------------------------------------------------

def test_root_endpoint():
    """Ensure root path returns 200 OK and docs links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "/docs" in data["docs_url"]


def test_health_endpoint():
    """Ensure /api/health reports system status and registered algorithm count."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["algorithms_count"] == 6
    assert "f1_weighted" in data["supported_metrics"]


def test_algorithms_endpoint():
    """Ensure /api/algorithms lists metadata for all 6 algorithms."""
    response = client.get("/api/algorithms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    algo_ids = [item["id"] for item in data]
    assert "random_forest" in algo_ids
    assert "logistic_regression" in algo_ids
    assert "svm" in algo_ids


# -----------------------------------------------------------------------------
# Dataset Endpoints
# -----------------------------------------------------------------------------

def test_dataset_preview_success():
    """Ensure uploading a valid CSV returns a dataset_id and exploratory stats."""
    csv_bytes = SAMPLE_CSV.encode("utf-8")
    files = {"file": ("test_dataset.csv", io.BytesIO(csv_bytes), "text/csv")}

    response = client.post("/api/dataset/preview", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "dataset_id" in data
    assert data["row_count"] == 20
    assert data["column_count"] == 7
    assert "loan_approved" in data["target_candidates"]
    assert len(data["sample_preview"]) == 5


def test_dataset_preview_invalid_extension():
    """Ensure non-CSV uploads are rejected with 400 Bad Request."""
    files = {"file": ("data.txt", io.BytesIO(b"hello world"), "text/plain")}
    response = client.post("/api/dataset/preview", files=files)
    assert response.status_code == 400
    assert "Only CSV files" in response.json()["detail"]


def test_target_analysis_success():
    """Ensure target analysis calculates class distribution for an uploaded dataset."""
    # 1. Upload dataset first
    csv_bytes = SAMPLE_CSV.encode("utf-8")
    files = {"file": ("test_dataset.csv", io.BytesIO(csv_bytes), "text/csv")}
    upload_res = client.post("/api/dataset/preview", files=files)
    dataset_id = upload_res.json()["dataset_id"]

    # 2. Analyze target
    payload = {"dataset_id": dataset_id, "target_column": "loan_approved"}
    target_res = client.post("/api/dataset/target-analysis", json=payload)
    assert target_res.status_code == 200
    data = target_res.json()
    assert data["num_classes"] == 2
    assert "1" in data["class_distribution"]
    assert "0" in data["class_distribution"]


def test_target_analysis_not_found_dataset():
    """Ensure querying an unknown dataset_id returns 404 Not Found."""
    payload = {"dataset_id": "non-existent-uuid", "target_column": "loan_approved"}
    response = client.post("/api/dataset/target-analysis", json=payload)
    assert response.status_code == 404


# -----------------------------------------------------------------------------
# Classification Experiment Endpoints
# -----------------------------------------------------------------------------

def test_full_classification_lifecycle():
    """Ensure the complete workflow from upload to run, results, and predict works."""
    # 1. Upload dataset
    csv_bytes = SAMPLE_CSV.encode("utf-8")
    files = {"file": ("loan_data.csv", io.BytesIO(csv_bytes), "text/csv")}
    upload_res = client.post("/api/dataset/preview", files=files)
    dataset_id = upload_res.json()["dataset_id"]

    # 2. Run classification experiment
    run_payload = {
        "dataset_id": dataset_id,
        "target_column": "loan_approved",
        "selected_algorithms": ["decision_tree", "random_forest"],
        "primary_metric": "accuracy",
        "cv_folds": 2,
        "test_size": 0.2,
        "random_state": 42,
    }
    run_res = client.post("/api/classification/run", json=run_payload)
    assert run_res.status_code == 200
    exp_data = run_res.json()

    assert exp_data["status"] == "completed"
    assert "experiment_id" in exp_data
    experiment_id = exp_data["experiment_id"]
    assert exp_data["winner"] is not None
    assert len(exp_data["ranked_models"]) == 2
    assert len(exp_data["agent_logs"]) > 0

    # 3. Retrieve results via GET
    results_res = client.get(f"/api/classification/results/{experiment_id}")
    assert results_res.status_code == 200
    fetched_data = results_res.json()
    assert fetched_data["experiment_id"] == experiment_id
    assert fetched_data["winner"]["algorithm_id"] == exp_data["winner"]["algorithm_id"]

    # 4. Perform real-time inference via POST predict
    pred_payload = {
        "instances": [
            {
                "age": 30,
                "income": 50000,
                "credit_score": 680,
                "loan_amount": 12000,
                "employment_type": "salaried",
                "education_level": "bachelor",
            },
            {
                "age": 22,
                "income": 20000,
                "credit_score": 550,
                "loan_amount": 4000,
                "employment_type": "unemployed",
                "education_level": "high_school",
            },
        ]
    }
    pred_res = client.post(f"/api/classification/predict/{experiment_id}", json=pred_payload)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert pred_data["prediction_count"] == 2
    assert len(pred_data["predictions"]) == 2
    assert pred_data["predictions"][0] in ["0", "1"]
    assert pred_data["probabilities"] is not None


def test_get_non_existent_experiment():
    """Ensure requesting unknown experiment returns 404."""
    response = client.get("/api/classification/results/unknown-id-12345")
    assert response.status_code == 404


def test_predict_non_existent_experiment():
    """Ensure predicting with unknown experiment returns 404."""
    response = client.post(
        "/api/classification/predict/unknown-id-12345",
        json={"instances": [{"age": 25}]},
    )
    assert response.status_code == 404
