"""K-Nearest Neighbors (KNN) Classifier Factory.

Academic Overview:
------------------
K-Nearest Neighbors is a non-parametric, instance-based (lazy learning) algorithm.
Unlike eager learning algorithms, KNN does not construct an explicit internal model
during training; instead, it stores the entire training dataset in memory.

During inference for a new point x:
1. Calculates the geometric distance between x and every training instance.
2. Identifies the k closest instances (neighbors).
3. Assigns x the class label by majority vote among those k neighbors.

Distance Metric (Minkowski with p=2, equivalent to Euclidean distance):
    d(x, z) = sqrt( sum_{j=1}^D (x_j - z_j)^2 )

Strengths:
    - Highly intuitive and completely non-parametric (makes no functional assumptions).
    - Adaptable to complex, non-linear decision boundaries.
    - Zero training phase computational overhead.

Weaknesses:
    - Extremely sensitive to feature scale (unscaled features dominate distance calculations).
    - High computational complexity during prediction: O(N * D) per query point.
    - Suffers from the "curse of dimensionality" as feature count increases.
"""

from typing import Any, Optional
from sklearn.base import BaseEstimator
from sklearn.neighbors import KNeighborsClassifier

# Metadata for registry and agent orchestration
ALGORITHM_ID = "knn"
DISPLAY_NAME = "K-Nearest Neighbors"
DESCRIPTION = "Instance-based lazy classifier determining labels by Euclidean neighborhood voting."
REQUIRES_SCALING = True
SUPPORTS_FEATURE_IMPORTANCES = False  # Pure distance-based, no intrinsic feature weighting


def get_classifier(random_state: Optional[int] = 42, **kwargs: Any) -> BaseEstimator:
    """Create and return a configured KNeighborsClassifier estimator.

    Args:
        random_state: Unused by KNeighborsClassifier (deterministic algorithm),
            retained here to ensure a consistent factory signature across all algorithms.
        **kwargs: Additional hyperparameters passed to KNeighborsClassifier.

    Returns:
        BaseEstimator: Configured Scikit-learn KNeighborsClassifier instance.
    """
    # Note: random_state is accepted for interface consistency, but KNN has no stochastic component.
    _ = random_state

    # n_neighbors=5 is an empirical standard: odd number avoids 50-50 ties in binary classification
    # weights='uniform' assigns equal voting weight to all k neighbors
    # metric='minkowski' with p=2 defaults to standard Euclidean distance
    params = {
        "n_neighbors": 5,
        "weights": "uniform",
        "metric": "minkowski",
        "p": 2,
    }
    params.update(kwargs)
    return KNeighborsClassifier(**params)
