"""Unit tests for ClassifyAI classification algorithms and registry.

Verifies:
- All required classifiers are registered.
- Every factory returns a valid Scikit-learn estimator instance.
- Every classifier conforms to the standard Scikit-learn estimator API (fit, predict).
- Probability estimates (predict_proba) work across all models.
"""

import pytest
from sklearn.base import BaseEstimator, ClassifierMixin, is_classifier
from sklearn.datasets import make_classification

from app.algorithms import (
    CLASSIFIER_REGISTRY,
    build_classifier,
    get_classifier_metadata,
    list_available_algorithms,
)

EXPECTED_ALGORITHMS = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "knn",
    "svm",
    "gradient_boosting",
]


@pytest.fixture
def synthetic_binary_data():
    """Generates a small reproducible binary classification dataset."""
    X, y = make_classification(
        n_samples=60,
        n_features=6,
        n_informative=4,
        n_redundant=1,
        n_classes=2,
        random_state=42,
    )
    return X, y


def test_registry_contains_all_required_algorithms():
    """Ensure all six specified algorithms are properly registered in the registry."""
    registered_keys = set(CLASSIFIER_REGISTRY.keys())
    for algo_id in EXPECTED_ALGORITHMS:
        assert algo_id in registered_keys, f"Missing registered algorithm: {algo_id}"


def test_list_available_algorithms():
    """Ensure the algorithm listing returns properly structured metadata dictionaries."""
    algo_list = list_available_algorithms()
    assert len(algo_list) == len(EXPECTED_ALGORITHMS)
    for item in algo_list:
        assert "id" in item
        assert "display_name" in item
        assert "description" in item
        assert "requires_scaling" in item
        assert "supports_feature_importances" in item


def test_unknown_algorithm_raises_error():
    """Ensure querying an unregistered algorithm ID raises a descriptive ValueError."""
    with pytest.raises(ValueError, match="Unknown algorithm ID"):
        get_classifier_metadata("non_existent_algorithm")


@pytest.mark.parametrize("algo_id", EXPECTED_ALGORITHMS)
def test_classifier_factory_returns_valid_estimator(algo_id):
    """Ensure each algorithm factory returns a valid Scikit-learn ClassifierMixin."""
    estimator = build_classifier(algo_id, random_state=42)
    assert isinstance(estimator, BaseEstimator), f"{algo_id} is not a BaseEstimator"
    assert is_classifier(estimator), f"{algo_id} is not recognized as a Scikit-learn classifier"


@pytest.mark.parametrize("algo_id", EXPECTED_ALGORITHMS)
def test_classifier_fit_and_predict(algo_id, synthetic_binary_data):
    """Ensure each instantiated classifier can fit and predict on synthetic tabular data."""
    X, y = synthetic_binary_data
    estimator = build_classifier(algo_id, random_state=42)

    # Train estimator
    estimator.fit(X, y)

    # Predictions check
    preds = estimator.predict(X)
    assert len(preds) == len(y)
    assert set(preds).issubset({0, 1})

    # Probability prediction check (essential for ROC-AUC and soft voting)
    assert hasattr(estimator, "predict_proba"), f"{algo_id} must support predict_proba"
    probas = estimator.predict_proba(X)
    assert probas.shape == (len(y), 2)
    # Probabilities should sum to 1 across classes for each instance
    for row in probas:
        assert pytest.approx(row.sum(), abs=1e-5) == 1.0
