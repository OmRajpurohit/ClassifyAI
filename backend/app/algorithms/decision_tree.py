"""Decision Tree Classifier Factory.

Academic Overview:
------------------
Decision Trees are non-parametric supervised learning models that predict the target
class by learning simple hierarchical decision rules inferred from data features.

The feature space is recursively partitioned into axis-aligned rectangular regions.
At each internal node, the algorithm evaluates splits across all features to find
the threshold that maximizes criterion purity (e.g., Gini Impurity or Information Gain/Entropy).

Gini Impurity formula:
    I_G(p) = 1 - sum_{i=1}^C (p_i^2)

Strengths:
    - Highly intuitive and visual decision rules.
    - Naturally handles non-linear interactions without feature transformation.
    - Scale-invariant: monotone feature transformations do not alter split decisions.

Weaknesses:
    - Prone to severe overfitting if depth is unconstrained.
    - High variance: small perturbations in the training data can yield drastically different trees.
"""

from typing import Any, Optional
from sklearn.base import BaseEstimator
from sklearn.tree import DecisionTreeClassifier

# Metadata for registry and agent orchestration
ALGORITHM_ID = "decision_tree"
DISPLAY_NAME = "Decision Tree"
DESCRIPTION = "Hierarchical rule-based tree model partitioning feature space by impurity criteria."
REQUIRES_SCALING = False
SUPPORTS_FEATURE_IMPORTANCES = True  # Via Gini/entropy feature_importances_


def get_classifier(random_state: Optional[int] = 42, **kwargs: Any) -> BaseEstimator:
    """Create and return a configured DecisionTreeClassifier estimator.

    Args:
        random_state: Controls randomness of feature subsampling when splitting nodes.
        **kwargs: Additional hyperparameters passed to DecisionTreeClassifier.

    Returns:
        BaseEstimator: Configured Scikit-learn DecisionTreeClassifier instance.
    """
    # criterion='gini' computes Gini impurity to measure split quality efficiently
    # max_depth=None allows leaves to expand until pure or min_samples_split is reached
    # min_samples_split=2 specifies minimum samples required to split an internal node
    # min_samples_leaf=1 guarantees at least one sample at each terminal leaf
    params = {
        "criterion": "gini",
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "random_state": random_state,
    }
    params.update(kwargs)
    return DecisionTreeClassifier(**params)
