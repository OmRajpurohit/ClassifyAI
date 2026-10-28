"""Integration and unit tests for ClassifierAgent.

Verifies:
- Configuration validation and constraint checking.
- Autonomous end-to-end experiment orchestration across multiple algorithms.
- Winner selection based strictly on computed metrics.
- Held-out test evaluation, confusion matrix generation, and feature importances.
- Inference / prediction with the winning fitted pipeline on unseen data.
- Multiclass task orchestration.
- Default execution across all registered algorithms.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification

from app.agents.classifier_agent import ClassifierAgent, ExperimentConfig


@pytest.fixture
def synthetic_binary_dataset():
    """Generates a tabular binary dataset with mixed features and missing values."""
    X_arr, y_arr = make_classification(
        n_samples=80,
        n_features=5,
        n_informative=3,
        n_redundant=1,
        n_classes=2,
        random_state=42,
    )
    df = pd.DataFrame(X_arr, columns=[f"feature_{i}" for i in range(5)])
    # Add a categorical column
    df["category"] = ["type_A" if i % 2 == 0 else "type_B" for i in range(len(df))]
    # Add target column with human-readable string labels
    df["target"] = ["class_positive" if label == 1 else "class_negative" for label in y_arr]
    # Introduce small missing values
    df.loc[0, "feature_0"] = np.nan
    df.loc[1, "category"] = None
    return df


@pytest.fixture
def synthetic_multiclass_dataset():
    """Generates a 3-class tabular dataset."""
    X_arr, y_arr = make_classification(
        n_samples=90,
        n_features=6,
        n_informative=4,
        n_classes=3,
        random_state=42,
    )
    df = pd.DataFrame(X_arr, columns=[f"col_{i}" for i in range(6)])
    df["label"] = [f"class_{c}" for c in y_arr]
    return df


def test_agent_config_validation():
    """Ensure invalid configurations raise explicit ValueError exceptions."""
    # 1. Missing target
    with pytest.raises(ValueError, match="target_column name must be specified"):
        ExperimentConfig(target_column="").validate()

    # 2. Unsupported metric
    with pytest.raises(ValueError, match="Unsupported primary_metric"):
        ExperimentConfig(target_column="target", primary_metric="non_existent_metric").validate()

    # 3. Invalid fold count
    with pytest.raises(ValueError, match="folds must be between 2 and 10"):
        ExperimentConfig(target_column="target", cv_folds=1).validate()

    # 4. Invalid test size
    with pytest.raises(ValueError, match="Test size proportion must be between 0.0 and 0.5"):
        ExperimentConfig(target_column="target", test_size=0.8).validate()

    # 5. Unknown algorithm
    with pytest.raises(ValueError, match="is not recognized"):
        ExperimentConfig(target_column="target", selected_algorithms=["unknown_model"]).validate()


def test_agent_runs_binary_experiment(synthetic_binary_dataset):
    """Ensure the agent orchestrates a full experiment and returns a valid winner."""
    agent = ClassifierAgent(random_state=42)
    config = ExperimentConfig(
        target_column="target",
        selected_algorithms=["random_forest", "logistic_regression", "decision_tree"],
        primary_metric="f1_weighted",
        cv_folds=3,
        test_size=0.2,
    )

    result = agent.run_experiment(synthetic_binary_dataset, config)

    # 1. Verification of experiment lifecycle
    assert result.status == "completed"
    assert result.experiment_id is not None
    assert len(result.agent_logs) > 5

    # 2. Dataset and Target Profiling
    assert result.dataset_summary.row_count == 80
    assert result.target_analysis.num_classes == 2

    # 3. Model Ranking and Selection
    assert len(result.ranking.ranked_models) == 3
    assert result.ranking.winner is not None
    assert result.ranking.winner.primary_score > 0.0
    assert result.ranking.winner.algorithm_id in ["random_forest", "logistic_regression", "decision_tree"]

    # 4. Held-Out Test Evaluation
    assert result.winning_model_details is not None
    assert result.winning_model_details["has_test_evaluation"] is True
    assert "accuracy" in result.winning_model_details["test_metrics"]

    # 5. Confusion Matrix
    cm = result.winning_model_details["confusion_matrix"]
    assert len(cm["labels"]) == 2
    assert len(cm["matrix"]) == 2

    # 6. Feature Importances
    importances = result.winning_model_details["feature_importances"]
    assert len(importances) > 0


def test_agent_predict_on_unseen_data(synthetic_binary_dataset):
    """Ensure the agent's fitted winning pipeline produces valid inference predictions."""
    agent = ClassifierAgent(random_state=42)
    config = ExperimentConfig(
        target_column="target",
        selected_algorithms=["random_forest"],
        primary_metric="accuracy",
        cv_folds=3,
        test_size=0.2,
    )

    result = agent.run_experiment(synthetic_binary_dataset, config)

    # Create new query sample
    new_data = pd.DataFrame({
        "feature_0": [0.5, -1.2],
        "feature_1": [1.1, 0.3],
        "feature_2": [-0.8, 1.5],
        "feature_3": [0.2, -0.4],
        "feature_4": [1.0, 0.0],
        "category": ["type_A", "type_B"],
    })

    pred_res = agent.predict(result, new_data)

    assert pred_res["prediction_count"] == 2
    assert len(pred_res["predictions"]) == 2
    for pred in pred_res["predictions"]:
        assert pred in ["class_positive", "class_negative"]

    # Verify probability distribution
    assert pred_res["probabilities"] is not None
    assert len(pred_res["probabilities"]) == 2
    for row in pred_res["probabilities"]:
        total_p = sum(row.values())
        assert pytest.approx(total_p, abs=1e-2) == 1.0


def test_agent_multiclass_experiment(synthetic_multiclass_dataset):
    """Ensure agent correctly manages multiclass datasets and produces 3x3 confusion matrices."""
    agent = ClassifierAgent(random_state=42)
    config = ExperimentConfig(
        target_column="label",
        selected_algorithms=["gradient_boosting", "knn"],
        primary_metric="f1_macro",
        cv_folds=3,
        test_size=0.2,
    )

    result = agent.run_experiment(synthetic_multiclass_dataset, config)

    assert result.status == "completed"
    assert result.target_analysis.is_multiclass is True
    assert result.target_analysis.num_classes == 3

    # Check 3-class confusion matrix
    cm = result.winning_model_details["confusion_matrix"]
    assert len(cm["labels"]) == 3
    assert len(cm["matrix"]) == 3
    assert len(cm["matrix"][0]) == 3


def test_agent_evaluates_all_algorithms_by_default(synthetic_binary_dataset):
    """Ensure omitting algorithm list evaluates all 6 registered algorithms."""
    agent = ClassifierAgent(random_state=42)
    config = ExperimentConfig(
        target_column="target",
        selected_algorithms=None,  # All algorithms!
        primary_metric="balanced_accuracy",
        cv_folds=2,
        test_size=0.1,
    )

    result = agent.run_experiment(synthetic_binary_dataset, config)

    assert result.status == "completed"
    total_evaluated = len(result.ranking.ranked_models) + len(result.ranking.failed_models)
    assert total_evaluated == 6
    assert result.ranking.winner is not None
