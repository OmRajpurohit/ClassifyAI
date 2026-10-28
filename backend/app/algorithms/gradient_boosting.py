"""Gradient Boosting Classifier Factory.

Academic Overview:
------------------
Gradient Boosting is a powerful ensemble method that builds base estimators (typically
shallow decision trees, known as decision stumps) sequentially in an additive manner.

Unlike Bagging (Random Forest), which builds trees independently in parallel to reduce
variance, Gradient Boosting builds trees sequentially to reduce bias:
1. Starts with an initial base prediction (e.g. log-odds of positive class).
2. Computes pseudo-residuals (the negative gradient of the loss function with respect
   to predicted values).
3. Fits a new decision tree to predict these residuals.
4. Updates the model by adding the newly fitted tree multiplied by a shrinkage factor
   (learning rate).
5. Repeats until convergence or maximum iterations are met.

Strengths:
    - Frequently achieves state-of-the-art predictive accuracy on tabular data.
    - Naturally handles heterogenous features, missing non-linearities, and interactions.
    - Invariant to monotonic feature transformations (no feature scaling required).

Weaknesses:
    - Prone to overfitting if learning rate and tree depth are not carefully controlled.
    - Sequential nature makes training slower than parallelized bagging (Random Forest).
"""

from typing import Any, Optional
from sklearn.base import BaseEstimator
from sklearn.ensemble import GradientBoostingClassifier

# Metadata for registry and agent orchestration
ALGORITHM_ID = "gradient_boosting"
DISPLAY_NAME = "Gradient Boosting"
DESCRIPTION = "Sequential boosting ensemble fitting shallow trees to loss pseudo-residuals."
REQUIRES_SCALING = False
SUPPORTS_FEATURE_IMPORTANCES = True  # Via Gini importance / mean impurity decrease


def get_classifier(random_state: Optional[int] = 42, **kwargs: Any) -> BaseEstimator:
    """Create and return a configured GradientBoostingClassifier estimator.

    Args:
        random_state: Controls the random seed for subsampling and tree splitting.
        **kwargs: Additional hyperparameters passed to GradientBoostingClassifier.

    Returns:
        BaseEstimator: Configured Scikit-learn GradientBoostingClassifier instance.
    """
    # n_estimators=100 provides adequate boosting iterations for convergence
    # learning_rate=0.1 shrinks each tree's contribution to prevent overfitting (shrinkage)
    # max_depth=3 constrains trees to be shallow weak learners, avoiding high-order interactions
    params = {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 3,
        "random_state": random_state,
    }
    params.update(kwargs)
    return GradientBoostingClassifier(**params)
