"""Pydantic Request and Response Schemas for ClassifyAI REST APIs.

Provides strict validation, data serialization, and auto-generated Swagger documentation
for dataset uploads, exploratory profiling, classification runs, and model inference.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# System & Meta Schemas
# -----------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check endpoint response schema."""

    status: str = Field(..., examples=["ok"])
    version: str = Field(..., examples=["1.0.0"])
    algorithms_count: int = Field(..., examples=[6])
    supported_metrics: List[str]


class AlgorithmInfo(BaseModel):
    """Metadata describing an individual classification algorithm."""

    id: str = Field(..., examples=["random_forest"])
    display_name: str = Field(..., examples=["Random Forest"])
    description: str = Field(..., examples=["Ensemble of bagging decision trees."])
    requires_scaling: bool = Field(..., examples=[False])
    supports_feature_importances: bool = Field(..., examples=[True])


# -----------------------------------------------------------------------------
# Dataset Schemas
# -----------------------------------------------------------------------------

class DatasetPreviewResponse(BaseModel):
    """Schema returned after dataset upload and exploratory profiling."""

    dataset_id: str = Field(..., description="Unique UUID referencing the uploaded dataset")
    filename: str = Field(..., examples=["customer_churn.csv"])
    row_count: int = Field(..., examples=[1000])
    column_count: int = Field(..., examples=[12])
    columns: List[str]
    dtypes: Dict[str, str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    unsupported_columns: List[str]
    missing_values_per_column: Dict[str, int]
    total_missing_values: int
    duplicate_row_count: int
    unique_values_per_column: Dict[str, int]
    target_candidates: List[str]
    sample_preview: List[Dict[str, Any]]
    summary_notes: List[str]


class TargetAnalysisRequest(BaseModel):
    """Request payload to validate a specific column as the classification target."""

    dataset_id: str
    target_column: str


class TargetAnalysisResponse(BaseModel):
    """Schema describing class distribution and imbalance metrics for a selected target."""

    target_column: str
    num_classes: int
    classes: List[str]
    class_distribution: Dict[str, int]
    class_percentages: Dict[str, float]
    is_multiclass: bool
    is_imbalanced: bool
    imbalance_ratio: float
    minority_class: str
    majority_class: str
    recommendations: List[str]


# -----------------------------------------------------------------------------
# Classification Experiment Schemas
# -----------------------------------------------------------------------------

class ClassificationRunRequest(BaseModel):
    """Configuration payload submitted to trigger a classification experiment."""

    dataset_id: str = Field(..., description="UUID of the previously uploaded dataset")
    target_column: str = Field(..., description="Name of the classification target column")
    selected_algorithms: Optional[List[str]] = Field(
        None,
        description="List of algorithm IDs to evaluate. If omitted or empty, all 6 algorithms are run.",
        examples=[["logistic_regression", "random_forest", "gradient_boosting"]],
    )
    primary_metric: str = Field(
        "f1_weighted",
        description="Metric used to rank and select the winning classifier.",
        examples=["f1_weighted"],
    )
    cv_folds: int = Field(
        5,
        ge=2,
        le=10,
        description="Number of Stratified K-Fold cross-validation splits (2 to 10).",
    )
    test_size: float = Field(
        0.2,
        ge=0.0,
        le=0.5,
        description="Proportion of dataset reserved for final held-out test evaluation (0.0 to 0.5).",
    )
    random_state: int = Field(
        42,
        description="Seed used across all random number generators for strict reproducibility.",
    )


class MetricScoreSummary(BaseModel):
    """Mean and standard deviation for a metric across CV folds."""

    mean: Optional[float]
    std: Optional[float]
    fold_values: Optional[List[Optional[float]]] = None


class RankedModelResponse(BaseModel):
    """Leaderboard entry for an individual evaluated classifier."""

    rank: int
    algorithm_id: str
    algorithm_name: str
    primary_metric: str
    primary_score: float
    primary_score_std: float
    all_metrics: Dict[str, Dict[str, Optional[float]]]
    training_duration_seconds: float
    prediction_duration_seconds: float
    is_winner: bool


class ConfusionMatrixData(BaseModel):
    """Interactive confusion matrix data."""

    matrix: List[List[int]]
    labels: List[str]


class FeatureImportanceItem(BaseModel):
    """Individual feature importance score."""

    feature: str
    importance: float


class WinningModelDetails(BaseModel):
    """Performance evaluation of the winning pipeline on the held-out test split."""

    has_test_evaluation: bool
    test_metrics: Optional[Dict[str, Optional[float]]]
    confusion_matrix: Optional[ConfusionMatrixData]
    feature_importances: Optional[List[FeatureImportanceItem]]
    notes: List[str]


class ExperimentResultsResponse(BaseModel):
    """Comprehensive structured experiment report delivered to the frontend."""

    experiment_id: str
    created_at: str
    status: str
    config: Dict[str, Any]
    dataset_summary: Dict[str, Any]
    target_analysis: Dict[str, Any]
    ranked_models: List[RankedModelResponse]
    failed_models: List[Dict[str, str]]
    winner: Optional[RankedModelResponse]
    runner_up: Optional[RankedModelResponse]
    score_difference: Optional[float]
    is_statistically_ambiguous: bool
    poor_performance_warning: Optional[str]
    summary_explanation: str
    winning_model_details: Optional[WinningModelDetails]
    classes: List[str]
    agent_logs: List[str]


# -----------------------------------------------------------------------------
# Prediction / Inference Schemas
# -----------------------------------------------------------------------------

class PredictionRequest(BaseModel):
    """Inference payload containing one or more feature row instances to classify."""

    instances: List[Dict[str, Any]] = Field(
        ...,
        description="List of feature dictionaries corresponding to dataset column names.",
        examples=[[{"age": 35, "income": 65000, "credit_score": 720, "loan_amount": 15000}]],
    )


class PredictionResponse(BaseModel):
    """Inference output produced by the winning pipeline."""

    experiment_id: str
    prediction_count: int
    predictions: List[str]
    probabilities: Optional[List[Dict[str, float]]]
    classes: List[str]


class ErrorResponse(BaseModel):
    """Standardized error response schema."""

    detail: str
