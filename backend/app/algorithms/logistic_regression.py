"""Logistic Regression Classifier Factory.

Academic Overview:
------------------
Logistic Regression is a foundational linear model for binary and multiclass
classification. Despite its name, it performs classification by passing a linear
combination of input features through the logistic sigmoid function (for binary
classification) or softmax function (for multiclass classification).

Mathematical intuition:
    P(y = 1 | x) = 1 / (1 + exp(- (w^T * x + b)))

Where:
    - w is the learned weight vector (coefficients).
    - b is the bias/intercept term.
    - x is the input feature vector.

Strengths:
    - Highly interpretable coefficients (log-odds impact of features).
    - Fast training and low memory footprint.
    - Outputs calibrated class probabilities.

Weaknesses:
    - Assumes linear decision boundary between classes.
    - Sensitive to multicollinearity and feature scale differences.
"""

from typing import Any, Optional
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression

# Metadata for registry and agent orchestration
ALGORITHM_ID = "logistic_regression"
DISPLAY_NAME = "Logistic Regression"
DESCRIPTION = "Linear probabilistic model using logistic/softmax function for classification."
REQUIRES_SCALING = True
SUPPORTS_FEATURE_IMPORTANCES = True  # Via model coefficients (coef_)


def get_classifier(random_state: Optional[int] = 42, **kwargs: Any) -> BaseEstimator:
    """Create and return a configured LogisticRegression estimator.

    Args:
        random_state: Seed used by the random number generator for reproducible solver convergence.
        **kwargs: Additional hyperparameters passed directly to LogisticRegression.

    Returns:
        BaseEstimator: Configured Scikit-learn LogisticRegression instance.
    """
    # max_iter=1000 ensures solver converges on unscaled or complex datasets without warnings
    # solver='lbfgs' is the standard robust quasi-Newton optimizer supporting multinomial loss
    # C=1.0 is inverse regularization strength; smaller values specify stronger regularization
    params = {
        "max_iter": 1000,
        "solver": "lbfgs",
        "C": 1.0,
        "random_state": random_state,
    }
    # Allow overriding default hyperparameters if specified
    params.update(kwargs)
    return LogisticRegression(**params)
