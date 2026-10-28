"""Support Vector Machine (SVM) Classifier Factory.

Academic Overview:
------------------
Support Vector Machines aim to discover the optimal separating hyperplane that
maximizes the margin—the geometric distance between the decision boundary and
the closest data instances from either class (known as Support Vectors).

When classes are not linearly separable in the original input space, SVM employs
the "Kernel Trick" (such as the Radial Basis Function / Gaussian kernel) to implicitly
map inputs into a higher-dimensional space where linear separation becomes feasible.

Radial Basis Function (RBF) Kernel:
    K(x, z) = exp(- gamma * ||x - z||^2)

Strengths:
    - Highly effective in high-dimensional spaces.
    - Robust against overfitting in sparse or high-dimensional domains (via margin maximization).
    - Memory efficient because only support vectors are retained for decision making.

Weaknesses:
    - Computationally expensive for large datasets: training scales quadratically O(N^2) to O(N^3).
    - Requires strict feature normalization/scaling for distance calculations.
    - Non-linear kernels are not directly interpretable via feature coefficients.
"""

from typing import Any, Optional
from sklearn.base import BaseEstimator
from sklearn.svm import SVC

# Metadata for registry and agent orchestration
ALGORITHM_ID = "svm"
DISPLAY_NAME = "Support Vector Machine"
DESCRIPTION = "Maximum-margin hyperplane classifier with non-linear RBF kernel."
REQUIRES_SCALING = True
SUPPORTS_FEATURE_IMPORTANCES = False  # RBF kernel does not expose linear coef_


def get_classifier(random_state: Optional[int] = 42, **kwargs: Any) -> BaseEstimator:
    """Create and return a configured SVC (Support Vector Classifier) estimator.

    Args:
        random_state: Controls pseudo-random number generation for Platt scaling probabilities.
        **kwargs: Additional hyperparameters passed to SVC.

    Returns:
        BaseEstimator: Configured Scikit-learn SVC instance.
    """
    # C=1.0 balances margin maximization against classification error tolerance
    # kernel='rbf' allows finding non-linear decision boundaries
    # gamma='scale' sets gamma = 1 / (n_features * X.var()) for automated scale adaptation
    # probability=True enables Platt scaling (internal 5-fold cross-validation) so predict_proba()
    # is available for ROC-AUC calculations and probability calibration
    params = {
        "C": 1.0,
        "kernel": "rbf",
        "gamma": "scale",
        "probability": True,
        "random_state": random_state,
    }
    params.update(kwargs)
    return SVC(**params)
