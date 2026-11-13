"""Classifier Selection Agent for ClassifyAI.

This module implements the core rule-based Machine Learning Orchestration Agent.

Educational Significance:
-------------------------
A common question in student vivas is:
"What is the difference between a simple comparison script and an ML Agent?"

A simple comparison script blindly runs code sequentially and crashes on unexpected inputs.
In contrast, this Orchestration Agent:
1. Validates experiment specifications and guards against invalid configurations.
2. Performs exploratory profiling to inspect feature types, missingness, and cardinality.
3. Automatically reasons about algorithm requirements (e.g., selectively enabling feature scaling
   for distance/gradient algorithms while skipping it for tree ensembles).
4. Dynamically adapts cross-validation folds based on class representation bounds.
5. Employs defensive execution: isolates individual model failures without aborting the experiment.
6. Applies deterministic multi-tier ranking rules rather than naive single-number sorting.
7. Checks statistical ambiguity and detects when models fail to beat a trivial majority baseline.
8. Retrains the winning pipeline on training data and validates against untouched held-out data.
9. Produces step-by-step reasoning logs explaining every operational decision.
"""

from dataclasses import dataclass, field
import datetime
import uuid
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

from app.algorithms import (
    CLASSIFIER_REGISTRY,
    get_classifier_metadata,
)
from app.services.data_analyzer import (
    DatasetAnalysisResult,
    TargetAnalysisResult,
    analyze_dataset,
    analyze_target_column,
)
from app.services.model_evaluator import (
    ModelEvaluationResult,
    SUPPORTED_METRICS,
    evaluate_pipeline_cv,
)
from app.services.model_ranker import RankingResult, rank_models
from app.services.model_trainer import (
    partition_dataset,
    train_and_evaluate_test_split,
)
from app.services.preprocessing import (
    PreparedData,
    TargetEncoder,
    build_classification_pipeline,
    prepare_features_and_target,
)


@dataclass
class ExperimentConfig:
    """Experiment configuration parameters provided by user or frontend."""

    target_column: str
    selected_algorithms: Optional[List[str]] = None  # None = evaluate all registered algorithms
    primary_metric: str = "f1_weighted"
    cv_folds: int = 5
    test_size: float = 0.2
    random_state: int = 42
    dropped_columns: List[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate configuration settings and boundary constraints."""
        if not self.target_column or not isinstance(self.target_column, str):
            raise ValueError("A valid target_column name must be specified.")

        if self.primary_metric not in SUPPORTED_METRICS:
            valid_metrics = list(SUPPORTED_METRICS.keys())
            raise ValueError(
                f"Unsupported primary_metric '{self.primary_metric}'. Supported metrics: {valid_metrics}"
            )

        if not (2 <= self.cv_folds <= 10):
            raise ValueError(f"Cross-validation folds must be between 2 and 10. Received: {self.cv_folds}")

        if not (0.0 <= self.test_size <= 0.5):
            raise ValueError(f"Test size proportion must be between 0.0 and 0.5. Received: {self.test_size}")

        if self.selected_algorithms is not None:
            if len(self.selected_algorithms) == 0:
                raise ValueError("At least one algorithm must be selected for evaluation.")
            registered = set(CLASSIFIER_REGISTRY.keys())
            for algo in self.selected_algorithms:
                if algo not in registered:
                    raise ValueError(
                        f"Requested algorithm '{algo}' is not recognized. Registered algorithms: {list(registered)}"
                    )


@dataclass
class ExperimentResult:
    """Complete, self-contained record of an executed classification experiment."""

    experiment_id: str
    created_at: str
    status: str  # "completed" or "failed"
    config: Dict[str, Any]
    dataset_summary: DatasetAnalysisResult
    target_analysis: TargetAnalysisResult
    ranking: RankingResult
    winning_model_details: Optional[Dict[str, Any]]
    target_encoder: TargetEncoder
    agent_logs: List[str] = field(default_factory=list)
    fitted_pipeline: Optional[BaseEstimator] = None  # Retained in memory for inference

    def to_dict(self) -> Dict[str, Any]:
        """Convert experiment result to a JSON-serializable dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "status": self.status,
            "config": self.config,
            "dataset_summary": self.dataset_summary.to_dict(),
            "target_analysis": self.target_analysis.to_dict(),
            "ranking": self.ranking.to_dict(),
            "winning_model_details": self.winning_model_details,
            "classes": self.target_encoder.classes_,
            "agent_logs": self.agent_logs,
        }


class ClassifierAgent:
    """Autonomous rule-based Machine Learning Agent for classifier selection."""

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.logs: List[str] = []

    def _log(self, message: str) -> None:
        """Record an timestamped event in the agent execution trace."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def run_experiment(
        self,
        df: pd.DataFrame,
        config: ExperimentConfig,
    ) -> ExperimentResult:
        """Execute the end-to-end classifier evaluation and selection experiment.

        Execution Steps:
        1. Validate configuration.
        2. Perform exploratory dataset analysis and target profiling.
        3. Isolate target and construct preprocessing specifications.
        4. Partition data into training and held-out test splits.
        5. Evaluate requested classifiers using Stratified Cross-Validation.
        6. Apply multi-tier deterministic ranking to identify the winner.
        7. Fit the winning pipeline and evaluate against held-out test data.
        8. Package structured results with explanations and inference capability.

        Args:
            df: Raw input DataFrame.
            config: User-provided experiment configuration.

        Returns:
            ExperimentResult: Comprehensive results container.
        """
        experiment_id = str(uuid.uuid4())
        self.logs = []
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        self._log(f"Initiated experiment {experiment_id}.")

        # ---------------------------------------------------------------------
        # Step 1: Validate Configuration
        # ---------------------------------------------------------------------
        self._log("Validating experiment configuration and parameters...")
        config.validate()

        # Resolve algorithms list
        if config.selected_algorithms is None or len(config.selected_algorithms) == 0:
            algorithms_to_run = list(CLASSIFIER_REGISTRY.keys())
        else:
            algorithms_to_run = list(config.selected_algorithms)

        self._log(f"Selected {len(algorithms_to_run)} algorithm(s) for evaluation: {algorithms_to_run}")

        # ---------------------------------------------------------------------
        # Step 2: Exploratory Data Analysis & Target Profiling
        # ---------------------------------------------------------------------
        self._log("Analyzing dataset structure, feature dtypes, and missing values...")
        dataset_summary = analyze_dataset(df)
        self._log(
            f"Dataset profiled: {dataset_summary.row_count} rows, {dataset_summary.column_count} columns, "
            f"{dataset_summary.total_missing_values} missing values."
        )

        self._log(f"Validating suitability of target column '{config.target_column}'...")
        target_analysis = analyze_target_column(df, config.target_column)
        self._log(
            f"Target analyzed: {target_analysis.num_classes} classes. "
            f"Imbalanced: {target_analysis.is_imbalanced} (Ratio: {target_analysis.imbalance_ratio}:1)."
        )

        # ---------------------------------------------------------------------
        # Step 3: Feature & Target Preparation (Anti-Leakage Isolation)
        # ---------------------------------------------------------------------
        self._log("Separating features from target and encoding class labels...")
        prepared_data: PreparedData = prepare_features_and_target(df, config.target_column)
        invalid_drops = set(config.dropped_columns) - set(prepared_data.X.columns)
        if invalid_drops:
            raise ValueError(f"Cannot drop unknown or target columns: {sorted(invalid_drops)}")
        if config.dropped_columns:
            prepared_data.X = prepared_data.X.drop(columns=config.dropped_columns)
            prepared_data.numeric_features = [c for c in prepared_data.numeric_features if c not in config.dropped_columns]
            prepared_data.categorical_features = [c for c in prepared_data.categorical_features if c not in config.dropped_columns]
            prepared_data.preprocessing_notes.append(f"Manually excluded feature column(s): {', '.join(config.dropped_columns)}.")
        if not prepared_data.X.shape[1]:
            raise ValueError("At least one feature column must remain after manual column removal.")
        for note in prepared_data.preprocessing_notes:
            self._log(f"Data Prep Note: {note}")

        # ---------------------------------------------------------------------
        # Step 4: Train / Held-Out Test Partitioning
        # ---------------------------------------------------------------------
        self._log(f"Partitioning dataset (Held-out test split: {int(config.test_size * 100)}%)...")
        X_train, X_test, y_train, y_test, split_notes = partition_dataset(
            X=prepared_data.X,
            y=prepared_data.y_encoded,
            test_size=config.test_size,
            random_state=self.random_state,
        )
        for note in split_notes:
            self._log(f"Split Note: {note}")

        # ---------------------------------------------------------------------
        # Step 5: Cross-Validation Model Evaluation
        # ---------------------------------------------------------------------
        self._log(
            f"Beginning Stratified Cross-Validation ({config.cv_folds} folds) "
            f"across {len(algorithms_to_run)} algorithm(s)..."
        )
        evaluated_models: List[ModelEvaluationResult] = []

        for algo_id in algorithms_to_run:
            meta = get_classifier_metadata(algo_id)
            self._log(
                f"Evaluating '{meta.display_name}' (requires_scaling={meta.requires_scaling})..."
            )

            try:
                # Instantiate clean estimator
                estimator = meta.factory(random_state=self.random_state)

                # Assemble anti-leakage pipeline
                pipeline = build_classification_pipeline(
                    estimator=estimator,
                    numeric_features=prepared_data.numeric_features,
                    categorical_features=prepared_data.categorical_features,
                    requires_scaling=meta.requires_scaling,
                )

                # Execute cross-validation strictly on training partition
                eval_res = evaluate_pipeline_cv(
                    pipeline=pipeline,
                    algorithm_id=algo_id,
                    algorithm_name=meta.display_name,
                    X=X_train,
                    y=y_train,
                    n_splits=config.cv_folds,
                    random_state=self.random_state,
                )

                if eval_res.status == "success":
                    primary_summary = eval_res.metrics.get(config.primary_metric)
                    score_str = f"{primary_summary.mean:.4f}" if primary_summary and primary_summary.mean is not None else "N/A"
                    self._log(
                        f"✓ '{meta.display_name}' evaluated successfully. "
                        f"Mean {config.primary_metric}: {score_str} (Duration: {eval_res.training_duration_seconds:.3f}s)."
                    )
                else:
                    self._log(f"✗ '{meta.display_name}' evaluation failed: {eval_res.error_message}")

                evaluated_models.append(eval_res)

            except Exception as exc:
                self._log(f"✗ Critical error evaluating '{meta.display_name}': {str(exc)}")
                evaluated_models.append(
                    ModelEvaluationResult(
                        algorithm_id=algo_id,
                        algorithm_name=meta.display_name,
                        status="failed",
                        metrics={},
                        training_duration_seconds=0.0,
                        prediction_duration_seconds=0.0,
                        error_message=str(exc),
                        cv_folds_used=config.cv_folds,
                        notes=[f"Failed during pipeline construction: {str(exc)}"],
                    )
                )

        # ---------------------------------------------------------------------
        # Step 6: Multi-Tier Deterministic Ranking
        # ---------------------------------------------------------------------
        self._log(f"Ranking models using primary metric: '{config.primary_metric}'...")
        majority_baseline = (
            max(target_analysis.class_percentages.values()) / 100.0
            if target_analysis.class_percentages
            else None
        )

        ranking: RankingResult = rank_models(
            evaluated_models=evaluated_models,
            primary_metric=config.primary_metric,
            majority_class_baseline=majority_baseline,
        )

        if ranking.winner is None:
            self._log("Experiment concluded without a winning model (all evaluations failed).")
            return ExperimentResult(
                experiment_id=experiment_id,
                created_at=created_at,
                status="failed",
                config={
                    "target_column": config.target_column,
                    "selected_algorithms": algorithms_to_run,
                    "primary_metric": config.primary_metric,
                    "cv_folds": config.cv_folds,
                    "test_size": config.test_size,
                },
                dataset_summary=dataset_summary,
                target_analysis=target_analysis,
                ranking=ranking,
                winning_model_details=None,
                target_encoder=prepared_data.target_encoder,
                agent_logs=self.logs,
                fitted_pipeline=None,
            )

        winner = ranking.winner
        self._log(f"🏆 Winning classifier selected: {winner.algorithm_name} (Score: {winner.primary_score:.4f}).")
        if ranking.is_statistically_ambiguous and ranking.runner_up:
            self._log(
                f"Statistical notice: Margin over runner-up {ranking.runner_up.algorithm_name} "
                f"({ranking.score_difference:.4f}) is within standard deviation range."
            )
        if ranking.poor_performance_warning:
            self._log(f"Baseline warning: {ranking.poor_performance_warning}")

        # ---------------------------------------------------------------------
        # Step 7: Train Final Winning Pipeline & Evaluate on Held-Out Test Set
        # ---------------------------------------------------------------------
        self._log(f"Fitting final {winner.algorithm_name} pipeline on entire training partition...")
        winner_meta = get_classifier_metadata(winner.algorithm_id)
        final_estimator = winner_meta.factory(random_state=self.random_state)
        final_pipeline = build_classification_pipeline(
            estimator=final_estimator,
            numeric_features=prepared_data.numeric_features,
            categorical_features=prepared_data.categorical_features,
            requires_scaling=winner_meta.requires_scaling,
        )

        winning_model_details = train_and_evaluate_test_split(
            pipeline=final_pipeline,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            class_names=prepared_data.target_encoder.classes_,
        )

        if winning_model_details["has_test_evaluation"]:
            test_acc = winning_model_details["test_metrics"].get("accuracy", "N/A")
            self._log(f"Evaluated on untouched held-out test split. Test Accuracy: {test_acc}.")

        self._log("Experiment completed successfully.")

        return ExperimentResult(
            experiment_id=experiment_id,
            created_at=created_at,
            status="completed",
            config={
                "target_column": config.target_column,
                "selected_algorithms": algorithms_to_run,
                "primary_metric": config.primary_metric,
                "cv_folds": config.cv_folds,
                "test_size": config.test_size,
            },
            dataset_summary=dataset_summary,
            target_analysis=target_analysis,
            ranking=ranking,
            winning_model_details=winning_model_details,
            target_encoder=prepared_data.target_encoder,
            agent_logs=self.logs,
            fitted_pipeline=final_pipeline,
        )

    def predict(
        self,
        experiment_result: ExperimentResult,
        df_new: pd.DataFrame,
    ) -> Dict[str, Any]:
        """Perform predictions on new incoming data using the experiment's fitted winning pipeline.

        Args:
            experiment_result: Completed experiment containing fitted pipeline and target encoder.
            df_new: New feature instances DataFrame.

        Returns:
            Dict[str, Any]: Predictions with class names, probabilities, and row mappings.
        """
        if experiment_result.fitted_pipeline is None:
            raise RuntimeError("Experiment does not have a fitted pipeline available for prediction.")

        pipeline = experiment_result.fitted_pipeline
        target_encoder = experiment_result.target_encoder

        # Predict discrete integer class indices
        preds_encoded = pipeline.predict(df_new)
        # Convert back to human-readable class names
        class_predictions = target_encoder.inverse_transform(preds_encoded).tolist()

        probabilities = None
        if hasattr(pipeline, "predict_proba"):
            try:
                raw_probas = pipeline.predict_proba(df_new)
                probabilities = [
                    {cls_name: round(float(prob), 4) for cls_name, prob in zip(target_encoder.classes_, row)}
                    for row in raw_probas
                ]
            except Exception:
                probabilities = None

        return {
            "prediction_count": len(df_new),
            "predictions": class_predictions,
            "probabilities": probabilities,
            "classes": target_encoder.classes_,
        }
