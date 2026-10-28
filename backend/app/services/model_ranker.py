"""Model Ranking and Tie-Breaking Service for ClassifyAI.

Responsibilities:
- Ranks evaluated models based on a user-selected primary evaluation metric.
- Supports metric directionality (higher-is-better vs lower-is-better).
- Applies deterministic, multi-tiered tie-breaking rules.
- Detects score variability overlaps between the winner and runner-up.
- Assesses model performance against trivial majority-class baseline.
- Generates transparent, human-readable explanations suitable for college presentations.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from app.services.model_evaluator import ModelEvaluationResult, SUPPORTED_METRICS

# Metric direction mapping (True for maximization, False for minimization)
HIGHER_IS_BETTER_MAP: Dict[str, bool] = {
    "accuracy": True,
    "balanced_accuracy": True,
    "f1_weighted": True,
    "f1_macro": True,
    "precision_weighted": True,
    "recall_weighted": True,
    "roc_auc": True,
    "training_duration_seconds": False,
    "prediction_duration_seconds": False,
}


@dataclass
class RankedModel:
    """Represents a single evaluated model placed in the ranked leaderboard."""

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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ranked model entry to a dictionary."""
        return asdict(self)


@dataclass
class RankingResult:
    """Full outcome of the model ranking and selection process."""

    primary_metric: str
    primary_metric_display: str
    ranked_models: List[RankedModel]
    failed_models: List[Dict[str, str]]
    winner: Optional[RankedModel]
    runner_up: Optional[RankedModel]
    score_difference: Optional[float]
    is_statistically_ambiguous: bool
    poor_performance_warning: Optional[str]
    summary_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ranking result to a dictionary for API delivery."""
        return {
            "primary_metric": self.primary_metric,
            "primary_metric_display": self.primary_metric_display,
            "ranked_models": [m.to_dict() for m in self.ranked_models],
            "failed_models": self.failed_models,
            "winner": self.winner.to_dict() if self.winner else None,
            "runner_up": self.runner_up.to_dict() if self.runner_up else None,
            "score_difference": self.score_difference,
            "is_statistically_ambiguous": self.is_statistically_ambiguous,
            "poor_performance_warning": self.poor_performance_warning,
            "summary_explanation": self.summary_explanation,
        }


def extract_metric_value(
    model: ModelEvaluationResult,
    metric_key: str,
    default: float = 0.0,
) -> float:
    """Safely extract the mean value of a metric from a ModelEvaluationResult."""
    summary = model.metrics.get(metric_key)
    if summary and summary.mean is not None:
        return float(summary.mean)
    return default


def extract_metric_std(
    model: ModelEvaluationResult,
    metric_key: str,
    default: float = 0.0,
) -> float:
    """Safely extract the standard deviation of a metric from a ModelEvaluationResult."""
    summary = model.metrics.get(metric_key)
    if summary and summary.std is not None:
        return float(summary.std)
    return default


def rank_models(
    evaluated_models: List[ModelEvaluationResult],
    primary_metric: str = "f1_weighted",
    majority_class_baseline: Optional[float] = None,
) -> RankingResult:
    """Rank evaluated classifiers using the user's primary metric with multi-tier tie-breaking.

    Tie-Breaking Architecture:
    1. Primary Metric Mean (higher is better, or lower is better if configured).
    2. Primary Metric Stability: Lower standard deviation (models with consistent cross-validation folds win).
    3. Secondary Metric: Balanced Accuracy.
    4. Tertiary Metric: F1-Score (Weighted).
    5. Computational Efficiency: Shorter training time (prefer lighter models when scores are equivalent).

    Academic Insights:
    ------------------
    - If the score difference between #1 and #2 is less than the cross-validation standard deviation,
      we report that the top two models perform comparably without claiming absolute statistical superiority.
    - If the top score fails to exceed the trivial majority-class baseline, a warning is raised.

    Args:
        evaluated_models: List of ModelEvaluationResult from cross-validation.
        primary_metric: Key of the metric chosen for ranking.
        majority_class_baseline: Proportion of the dataset's majority class.

    Returns:
        RankingResult: Ranked list, winner identification, and educational analysis.
    """
    if primary_metric not in SUPPORTED_METRICS:
        primary_metric = "f1_weighted"

    higher_is_better = HIGHER_IS_BETTER_MAP.get(primary_metric, True)
    display_name = SUPPORTED_METRICS.get(primary_metric, primary_metric)

    # 1. Separate successful from failed evaluations
    successful_models: List[ModelEvaluationResult] = []
    failed_models: List[Dict[str, str]] = []

    for model in evaluated_models:
        if model.status == "success" and primary_metric in model.metrics and model.metrics[primary_metric].mean is not None:
            successful_models.append(model)
        else:
            failed_models.append({
                "algorithm_id": model.algorithm_id,
                "algorithm_name": model.algorithm_name,
                "error_message": model.error_message or f"Metric '{primary_metric}' was unavailable.",
            })

    if not successful_models:
        return RankingResult(
            primary_metric=primary_metric,
            primary_metric_display=display_name,
            ranked_models=[],
            failed_models=failed_models,
            winner=None,
            runner_up=None,
            score_difference=None,
            is_statistically_ambiguous=False,
            poor_performance_warning="All evaluated models failed or produced unavailable metrics.",
            summary_explanation="No models completed cross-validation successfully. Review dataset formatting or error logs.",
        )

    # 2. Multi-tier deterministic sorting
    def sort_key(model: ModelEvaluationResult) -> Tuple[float, float, float, float, float]:
        score = extract_metric_value(model, primary_metric, 0.0)
        std = extract_metric_std(model, primary_metric, 0.0)
        bal_acc = extract_metric_value(model, "balanced_accuracy", 0.0)
        f1_w = extract_metric_value(model, "f1_weighted", 0.0)
        train_time = model.training_duration_seconds

        # Invert score if higher is better so standard ascending sort puts best first
        primary_val = -score if higher_is_better else score
        # Lower std is preferred (more consistent)
        stability_val = std
        # Higher secondary metrics are preferred
        bal_acc_val = -bal_acc
        f1_val = -f1_w
        # Shorter training time is preferred
        time_val = train_time

        return (primary_val, stability_val, bal_acc_val, f1_val, time_val)

    sorted_models = sorted(successful_models, key=sort_key)

    # 3. Construct RankedModel instances
    ranked_list: List[RankedModel] = []
    for rank_idx, m in enumerate(sorted_models, start=1):
        metrics_dict: Dict[str, Dict[str, Optional[float]]] = {}
        for k, v in m.metrics.items():
            metrics_dict[k] = {
                "mean": round(v.mean, 4) if v.mean is not None else None,
                "std": round(v.std, 4) if v.std is not None else None,
            }

        ranked_list.append(
            RankedModel(
                rank=rank_idx,
                algorithm_id=m.algorithm_id,
                algorithm_name=m.algorithm_name,
                primary_metric=primary_metric,
                primary_score=round(extract_metric_value(m, primary_metric, 0.0), 4),
                primary_score_std=round(extract_metric_std(m, primary_metric, 0.0), 4),
                all_metrics=metrics_dict,
                training_duration_seconds=round(m.training_duration_seconds, 4),
                prediction_duration_seconds=round(m.prediction_duration_seconds, 4),
                is_winner=(rank_idx == 1),
            )
        )

    winner = ranked_list[0]
    runner_up = ranked_list[1] if len(ranked_list) > 1 else None

    # 4. Statistical variance analysis
    score_diff: Optional[float] = None
    is_ambiguous = False
    if runner_up is not None:
        score_diff = round(abs(winner.primary_score - runner_up.primary_score), 4)
        # Check if difference is within the uncertainty bounds (sum of standard deviations)
        if score_diff < max(winner.primary_score_std, runner_up.primary_score_std):
            is_ambiguous = True

    # 5. Baseline comparison and poor performance detection
    poor_perf_warning: Optional[str] = None
    if majority_class_baseline is not None and primary_metric in ("accuracy", "balanced_accuracy"):
        if winner.primary_score <= (majority_class_baseline + 0.03):
            poor_perf_warning = (
                f"Warning: Top-performing model achieved {winner.primary_score:.4f} {display_name}, "
                f"which is comparable to a trivial ZeroR/majority-class baseline ({majority_class_baseline:.4f}). "
                f"Features may have limited predictive power for this target."
            )

    # 6. Structured human-readable summary
    summary_parts = [
        f"{winner.algorithm_name} ranked #1 with a mean {display_name} of {winner.primary_score:.4f} "
        f"(±{winner.primary_score_std:.4f}) across cross-validation folds."
    ]
    if runner_up:
        summary_parts.append(
            f"It outperformed {runner_up.algorithm_name} (score: {runner_up.primary_score:.4f}) by a margin of {score_diff:.4f}."
        )
        if is_ambiguous:
            summary_parts.append(
                "Note: The score margin is within the cross-validation standard deviation, indicating both algorithms perform comparably."
            )
    else:
        summary_parts.append("Only one model completed evaluation.")

    return RankingResult(
        primary_metric=primary_metric,
        primary_metric_display=display_name,
        ranked_models=ranked_list,
        failed_models=failed_models,
        winner=winner,
        runner_up=runner_up,
        score_difference=score_diff,
        is_statistically_ambiguous=is_ambiguous,
        poor_performance_warning=poor_perf_warning,
        summary_explanation=" ".join(summary_parts),
    )
