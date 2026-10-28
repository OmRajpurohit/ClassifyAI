"""Random Forest Classifier Factory.

Academic Overview:
------------------
Random Forest is an ensemble meta-estimator that fits multiple decision tree
classifiers on various sub-samples of the dataset and uses averaging/majority voting
to improve predictive accuracy and strictly control over-fitting.

It combines two core randomization techniques:
1. Bagging (Bootstrap Aggregation): Each tree is trained on an independently drawn
   bootstrap sample of the training dataset.
2. Random Feature Subspaces: At each candidate split, only a random subset of features
   (typically sqrt(total_features)) is considered, decorrelating individual trees.

Strengths:
    - Substantially reduces variance compared to individual decision trees.
    - Robust against outliers and noise.
    - Scale-invariant and handles high-dimensional datasets well.
    - Yields reliable feature importance metrics.

Weaknesses:
    - Less interpretable than a single decision tree.
    - Higher inference time and memory usage as the number of trees grows.
"""

from typing import Any, Optional
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier

# Metadata for registry and agent orchestration
ALGORITHM_ID = "random_forest"
DISPLAY_NAME = "Random Forest"
DESCRIPTION = "Ensemble of bagging decision trees with random feature sub-selection."
REQUIRES_SCALING = False
SUPPORTS_FEATURE_IMPORTANCES = True  # Via mean decrease in impurity (MDI)


def get_classifier(random_state: Optional[int] = 42, **kwargs: Any) -> BaseEstimator:
    """Create and return a configured RandomForestClassifier estimator.

    Args:
        random_state: Controls both the randomness of bootstrapping and feature selection.
        **kwargs: Additional hyperparameters passed to RandomForestClassifier.

    Returns:
        BaseEstimator: Configured Scikit-learn RandomForestClassifier instance.
    """
    # n_estimators=100 provides a well-balanced tradeoff between ensemble stability and speed
    # max_depth=None lets individual trees grow deep while bagging dampens overall variance
    # n_jobs=-1 enables parallel CPU processing across all available cores for training
    params = {
        "n_estimators": 100,
        "criterion": "gini",
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "n_jobs": -1,
        "random_state": random_state,
    }
    params.update(kwargs)
    return RandomForestClassifier(**params)
