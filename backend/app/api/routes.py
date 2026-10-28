"""FastAPI REST API Routes for ClassifyAI.

Endpoints:
- GET  /api/health                       -> System health, version, and supported algorithms.
- GET  /api/algorithms                   -> List available algorithms and scaling metadata.
- POST /api/dataset/preview              -> Upload and preview CSV dataset with exploratory profile.
- POST /api/dataset/target-analysis      -> Validate and analyze class distribution for a target.
- POST /api/classification/run           -> Execute autonomous agent experiment.
- GET  /api/classification/results/{id}  -> Fetch experiment results and leaderboard.
- POST /api/classification/predict/{id}  -> Run inference on new data instances using winning model.
"""

from typing import Dict, List, Optional, Tuple
import uuid
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder

from app.agents.classifier_agent import ClassifierAgent, ExperimentConfig, ExperimentResult
from app.algorithms import list_available_algorithms
from app.schemas.responses import (
    AlgorithmInfo,
    ClassificationRunRequest,
    DatasetPreviewResponse,
    ExperimentResultsResponse,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    TargetAnalysisRequest,
    TargetAnalysisResponse,
)
from app.services.data_analyzer import analyze_dataset, analyze_target_column
from app.services.model_evaluator import SUPPORTED_METRICS
from app.utils.file_handler import sanitize_filename, validate_csv_contents

router = APIRouter(prefix="/api", tags=["ClassifyAI"])

# In-memory session registries (sufficient for local academic demo)
# Note: Results and uploaded datasets do not persist across server restarts.
DATASET_STORE: Dict[str, Tuple[str, pd.DataFrame]] = {}
EXPERIMENT_STORE: Dict[str, ExperimentResult] = {}
AGENT_INSTANCE = ClassifierAgent(random_state=42)


# -----------------------------------------------------------------------------
# System & Discovery Endpoints
# -----------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return system status, version, and count of registered algorithms."""
    algorithms = list_available_algorithms()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        algorithms_count=len(algorithms),
        supported_metrics=list(SUPPORTED_METRICS.keys()),
    )


@router.get("/algorithms", response_model=List[AlgorithmInfo])
def get_algorithms() -> List[AlgorithmInfo]:
    """Retrieve metadata for all registered classification algorithms."""
    return [AlgorithmInfo(**meta) for meta in list_available_algorithms()]


# -----------------------------------------------------------------------------
# Dataset Ingestion & Profiling Endpoints
# -----------------------------------------------------------------------------

@router.post("/dataset/preview", response_model=DatasetPreviewResponse)
async def preview_dataset(file: UploadFile = File(...)) -> DatasetPreviewResponse:
    """Upload a CSV dataset and receive exploratory data analysis and preview rows.

    Saves the dataset in the server-side session store with a unique `dataset_id`.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files (.csv) are currently supported.",
        )

    safe_filename = sanitize_filename(file.filename)

    try:
        file_bytes = await file.read()
        df, _ = validate_csv_contents(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred reading the file: {str(exc)}",
        )

    # Generate exploratory analysis profile
    dataset_summary = analyze_dataset(df)

    dataset_id = str(uuid.uuid4())
    DATASET_STORE[dataset_id] = (safe_filename, df)

    return DatasetPreviewResponse(
        dataset_id=dataset_id,
        filename=safe_filename,
        row_count=dataset_summary.row_count,
        column_count=dataset_summary.column_count,
        columns=dataset_summary.columns,
        dtypes=dataset_summary.dtypes,
        numeric_columns=dataset_summary.numeric_columns,
        categorical_columns=dataset_summary.categorical_columns,
        unsupported_columns=dataset_summary.unsupported_columns,
        missing_values_per_column=dataset_summary.missing_values_per_column,
        total_missing_values=dataset_summary.total_missing_values,
        duplicate_row_count=dataset_summary.duplicate_row_count,
        unique_values_per_column=dataset_summary.unique_values_per_column,
        target_candidates=dataset_summary.target_candidates,
        sample_preview=dataset_summary.sample_preview,
        summary_notes=dataset_summary.summary_notes,
    )


@router.post("/dataset/target-analysis", response_model=TargetAnalysisResponse)
def analyze_target(payload: TargetAnalysisRequest) -> TargetAnalysisResponse:
    """Validate a target column and compute class distribution and imbalance metrics."""
    if payload.dataset_id not in DATASET_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{payload.dataset_id}' not found. Please upload the dataset again.",
        )

    _, df = DATASET_STORE[payload.dataset_id]

    try:
        target_result = analyze_target_column(df, payload.target_column)
        return TargetAnalysisResponse(**target_result.to_dict())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# -----------------------------------------------------------------------------
# Classification Experiment Endpoints
# -----------------------------------------------------------------------------

@router.post("/classification/run", response_model=ExperimentResultsResponse)
def run_classification_experiment(payload: ClassificationRunRequest) -> ExperimentResultsResponse:
    """Launch the rule-based ML Orchestration Agent to evaluate models and select the best classifier."""
    if payload.dataset_id not in DATASET_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{payload.dataset_id}' not found. Please upload the dataset again.",
        )

    _, df = DATASET_STORE[payload.dataset_id]

    config = ExperimentConfig(
        target_column=payload.target_column,
        selected_algorithms=payload.selected_algorithms,
        primary_metric=payload.primary_metric,
        cv_folds=payload.cv_folds,
        test_size=payload.test_size,
        random_state=payload.random_state,
    )

    try:
        # Run autonomous agent
        experiment_result: ExperimentResult = AGENT_INSTANCE.run_experiment(df, config)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Experiment encountered an unhandled exception: {str(exc)}",
        )

    # Store experiment for future retrieval and predictions
    EXPERIMENT_STORE[experiment_result.experiment_id] = experiment_result

    ranking_dict = jsonable_encoder(experiment_result.ranking.to_dict())

    return ExperimentResultsResponse(
        experiment_id=experiment_result.experiment_id,
        created_at=experiment_result.created_at,
        status=experiment_result.status,
        config=jsonable_encoder(experiment_result.config),
        dataset_summary=jsonable_encoder(experiment_result.dataset_summary.to_dict()),
        target_analysis=jsonable_encoder(experiment_result.target_analysis.to_dict()),
        ranked_models=ranking_dict["ranked_models"],
        failed_models=ranking_dict["failed_models"],
        winner=ranking_dict["winner"],
        runner_up=ranking_dict["runner_up"],
        score_difference=ranking_dict["score_difference"],
        is_statistically_ambiguous=bool(ranking_dict["is_statistically_ambiguous"]),
        poor_performance_warning=ranking_dict["poor_performance_warning"],
        summary_explanation=ranking_dict["summary_explanation"],
        winning_model_details=jsonable_encoder(experiment_result.winning_model_details),
        classes=experiment_result.target_encoder.classes_,
        agent_logs=experiment_result.agent_logs,
    )


@router.get("/classification/results/{experiment_id}", response_model=ExperimentResultsResponse)
def get_experiment_results(experiment_id: str) -> ExperimentResultsResponse:
    """Retrieve full results and leaderboard for a completed experiment."""
    if experiment_id not in EXPERIMENT_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' was not found. Experiments are stored in-memory and reset on server restart.",
        )

    experiment_result = EXPERIMENT_STORE[experiment_id]
    ranking_dict = jsonable_encoder(experiment_result.ranking.to_dict())

    return ExperimentResultsResponse(
        experiment_id=experiment_result.experiment_id,
        created_at=experiment_result.created_at,
        status=experiment_result.status,
        config=jsonable_encoder(experiment_result.config),
        dataset_summary=jsonable_encoder(experiment_result.dataset_summary.to_dict()),
        target_analysis=jsonable_encoder(experiment_result.target_analysis.to_dict()),
        ranked_models=ranking_dict["ranked_models"],
        failed_models=ranking_dict["failed_models"],
        winner=ranking_dict["winner"],
        runner_up=ranking_dict["runner_up"],
        score_difference=ranking_dict["score_difference"],
        is_statistically_ambiguous=bool(ranking_dict["is_statistically_ambiguous"]),
        poor_performance_warning=ranking_dict["poor_performance_warning"],
        summary_explanation=ranking_dict["summary_explanation"],
        winning_model_details=jsonable_encoder(experiment_result.winning_model_details),
        classes=experiment_result.target_encoder.classes_,
        agent_logs=experiment_result.agent_logs,
    )


# -----------------------------------------------------------------------------
# Inference / Prediction Endpoint
# -----------------------------------------------------------------------------

@router.post("/classification/predict/{experiment_id}", response_model=PredictionResponse)
def predict_with_winning_model(
    experiment_id: str,
    payload: PredictionRequest,
) -> PredictionResponse:
    """Predict class labels and probabilities for new data instances using the winning model."""
    if experiment_id not in EXPERIMENT_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' was not found.",
        )

    experiment_result = EXPERIMENT_STORE[experiment_id]
    if experiment_result.fitted_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested experiment does not have a trained model available for prediction.",
        )

    if not payload.instances:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'instances' list must contain at least one row dictionary.",
        )

    try:
        df_new = pd.DataFrame(payload.instances)
        pred_dict = AGENT_INSTANCE.predict(experiment_result, df_new)

        return PredictionResponse(
            experiment_id=experiment_id,
            prediction_count=pred_dict["prediction_count"],
            predictions=pred_dict["predictions"],
            probabilities=pred_dict["probabilities"],
            classes=pred_dict["classes"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(exc)}",
        )
