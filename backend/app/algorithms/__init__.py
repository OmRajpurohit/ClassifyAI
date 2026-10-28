"""Classifier Registry and Factory Dispatcher.

This module provides a centralized registry mapping stable algorithm identifiers
to their respective factory functions and metadata.

Design Rationale:
-----------------
Using a registry pattern decouples algorithm definitions from the orchestration agent.
To register a new algorithm in ClassifyAI:
1. Create a new module in `app/algorithms/<name>.py` with a `get_classifier` factory.
2. Register the module in `CLASSIFIER_REGISTRY` here.
The agent and frontend can immediately discover and execute the new algorithm without
requiring modifications to orchestration, evaluation, or ranking logic.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from sklearn.base import BaseEstimator

from app.algorithms import (
    decision_tree,
    gradient_boosting,
    knn,
    logistic_regression,
    random_forest,
    svm,
)


@dataclass(frozen=True)
class ClassifierMetadata:
    """Holds metadata and factory handle for a registered classification algorithm."""

    id: str
    display_name: str
    description: str
    requires_scaling: bool
    supports_feature_importances: bool
    factory: Callable[..., BaseEstimator]


# Central registry dictionary mapping algorithm ID strings to their ClassifierMetadata
CLASSIFIER_REGISTRY: Dict[str, ClassifierMetadata] = {
    logistic_regression.ALGORITHM_ID: ClassifierMetadata(
        id=logistic_regression.ALGORITHM_ID,
        display_name=logistic_regression.DISPLAY_NAME,
        description=logistic_regression.DESCRIPTION,
        requires_scaling=logistic_regression.REQUIRES_SCALING,
        supports_feature_importances=logistic_regression.SUPPORTS_FEATURE_IMPORTANCES,
        factory=logistic_regression.get_classifier,
    ),
    decision_tree.ALGORITHM_ID: ClassifierMetadata(
        id=decision_tree.ALGORITHM_ID,
        display_name=decision_tree.DISPLAY_NAME,
        description=decision_tree.DESCRIPTION,
        requires_scaling=decision_tree.REQUIRES_SCALING,
        supports_feature_importances=decision_tree.SUPPORTS_FEATURE_IMPORTANCES,
        factory=decision_tree.get_classifier,
    ),
    random_forest.ALGORITHM_ID: ClassifierMetadata(
        id=random_forest.ALGORITHM_ID,
        display_name=random_forest.DISPLAY_NAME,
        description=random_forest.DESCRIPTION,
        requires_scaling=random_forest.REQUIRES_SCALING,
        supports_feature_importances=random_forest.SUPPORTS_FEATURE_IMPORTANCES,
        factory=random_forest.get_classifier,
    ),
    knn.ALGORITHM_ID: ClassifierMetadata(
        id=knn.ALGORITHM_ID,
        display_name=knn.DISPLAY_NAME,
        description=knn.DESCRIPTION,
        requires_scaling=knn.REQUIRES_SCALING,
        supports_feature_importances=knn.SUPPORTS_FEATURE_IMPORTANCES,
        factory=knn.get_classifier,
    ),
    svm.ALGORITHM_ID: ClassifierMetadata(
        id=svm.ALGORITHM_ID,
        display_name=svm.DISPLAY_NAME,
        description=svm.DESCRIPTION,
        requires_scaling=svm.REQUIRES_SCALING,
        supports_feature_importances=svm.SUPPORTS_FEATURE_IMPORTANCES,
        factory=svm.get_classifier,
    ),
    gradient_boosting.ALGORITHM_ID: ClassifierMetadata(
        id=gradient_boosting.ALGORITHM_ID,
        display_name=gradient_boosting.DISPLAY_NAME,
        description=gradient_boosting.DESCRIPTION,
        requires_scaling=gradient_boosting.REQUIRES_SCALING,
        supports_feature_importances=gradient_boosting.SUPPORTS_FEATURE_IMPORTANCES,
        factory=gradient_boosting.get_classifier,
    ),
}


def register_classifier(metadata: ClassifierMetadata) -> None:
    """Register a new classifier in the registry at runtime.

    Args:
        metadata: An instance of ClassifierMetadata describing the algorithm and factory.
    """
    CLASSIFIER_REGISTRY[metadata.id] = metadata


def get_classifier_metadata(algorithm_id: str) -> ClassifierMetadata:
    """Retrieve metadata for a specified algorithm ID.

    Args:
        algorithm_id: Unique string identifier of the algorithm.

    Returns:
        ClassifierMetadata: Metadata object containing name, factory, scaling flags, etc.

    Raises:
        ValueError: If algorithm_id is not registered.
    """
    if algorithm_id not in CLASSIFIER_REGISTRY:
        available = list(CLASSIFIER_REGISTRY.keys())
        raise ValueError(
            f"Unknown algorithm ID: '{algorithm_id}'. Available algorithms are: {available}"
        )
    return CLASSIFIER_REGISTRY[algorithm_id]


def build_classifier(
    algorithm_id: str,
    random_state: Optional[int] = 42,
    **kwargs: Any,
) -> BaseEstimator:
    """Instantiate a classifier using its registered factory.

    Args:
        algorithm_id: Unique string identifier of the algorithm.
        random_state: Optional random seed for reproducible initialization.
        **kwargs: Additional hyperparameters passed to the algorithm's factory.

    Returns:
        BaseEstimator: An instantiated, un-fitted Scikit-learn estimator.
    """
    metadata = get_classifier_metadata(algorithm_id)
    return metadata.factory(random_state=random_state, **kwargs)


def list_available_algorithms() -> List[Dict[str, Any]]:
    """List all registered algorithms in a format suitable for API serialization.

    Returns:
        List[Dict[str, Any]]: Metadata list suitable for frontend consumption.
    """
    return [
        {
            "id": meta.id,
            "display_name": meta.display_name,
            "description": meta.description,
            "requires_scaling": meta.requires_scaling,
            "supports_feature_importances": meta.supports_feature_importances,
        }
        for meta in CLASSIFIER_REGISTRY.values()
    ]


__all__ = [
    "CLASSIFIER_REGISTRY",
    "ClassifierMetadata",
    "register_classifier",
    "get_classifier_metadata",
    "build_classifier",
    "list_available_algorithms",
]
