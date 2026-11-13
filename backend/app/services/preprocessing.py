"""Data Preprocessing Service for ClassifyAI.

Constructs modular Scikit-Learn ColumnTransformers and Pipelines for:
- Median imputation for numerical features.
- Most-frequent imputation and One-Hot Encoding for categorical features.
- Standard scaling conditionally enabled based on algorithm requirements.
- Target label encoding and decoding.
- Strict isolation of preprocessing within training partitions to eliminate data leakage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from app.services.data_analyzer import identify_column_types, validate_target_suitability


class TargetEncoder:
    """Manages encoding and decoding of target classification labels.

    Wraps Scikit-Learn's LabelEncoder to convert arbitrary target types
    (strings, booleans, floating categories) into canonical zero-indexed integers [0, 1, ..., C-1],
    while preserving mapping dictionaries for API response serialization.
    """

    def __init__(self) -> None:
        self.encoder = LabelEncoder()
        self.is_fitted = False
        self.classes_: List[str] = []

    def fit_transform(self, y: Union[pd.Series, np.ndarray]) -> np.ndarray:
        """Fit the label encoder and return integer-encoded target array."""
        # Convert all labels to string representation to avoid mixed-type comparison issues
        y_str = pd.Series(y).astype(str).to_numpy()
        encoded = self.encoder.fit_transform(y_str)
        self.classes_ = [str(c) for c in self.encoder.classes_]
        self.is_fitted = True
        return encoded

    def transform(self, y: Union[pd.Series, np.ndarray]) -> np.ndarray:
        """Transform labels using the fitted encoder."""
        if not self.is_fitted:
            raise RuntimeError("TargetEncoder has not been fitted yet.")
        y_str = pd.Series(y).astype(str).to_numpy()
        return self.encoder.transform(y_str)

    def inverse_transform(self, y_encoded: Union[List[int], np.ndarray]) -> np.ndarray:
        """Convert integer class indices back to their original string labels."""
        if not self.is_fitted:
            raise RuntimeError("TargetEncoder has not been fitted yet.")
        return self.encoder.inverse_transform(np.asarray(y_encoded))

    @property
    def class_to_index(self) -> Dict[str, int]:
        """Mapping from original string label to integer index."""
        return {str(cls_name): idx for idx, cls_name in enumerate(self.classes_)}

    @property
    def index_to_class(self) -> Dict[int, str]:
        """Mapping from integer index to original string label."""
        return {idx: str(cls_name) for idx, cls_name in enumerate(self.classes_)}


@dataclass
class PreparedData:
    """Clean container for separated feature matrix, target array, and column metadata."""

    X: pd.DataFrame
    y_raw: pd.Series
    y_encoded: np.ndarray
    numeric_features: List[str]
    categorical_features: List[str]
    target_encoder: TargetEncoder
    dropped_rows_count: int = 0
    preprocessing_notes: List[str] = field(default_factory=list)


def prepare_features_and_target(df: pd.DataFrame, target_column: str) -> PreparedData:
    """Validate, clean, and separate the raw DataFrame into features X and target y.

    Key Safety Checks:
    - Verifies target column existence and classification suitability.
    - Explicitly prevents target column from contaminating feature matrix X.
    - Rejects datasets where any feature column is 100% missing (NaN).
    - Detects and handles rows with missing target labels (reports row drops).
    - Classifies remaining features into numeric and categorical subsets.

    Args:
        df: Input raw DataFrame.
        target_column: User-selected target column.

    Returns:
        PreparedData: Structured container with X, encoded y, and feature lists.

    Raises:
        ValueError: If target is unsuitable or feature columns are 100% missing.
    """
    validate_target_suitability(df, target_column)

    notes: List[str] = []
    initial_rows = len(df)

    # 1. Handle missing target labels
    target_missing_mask = df[target_column].isna()
    dropped_target_na = int(target_missing_mask.sum())
    if dropped_target_na > 0:
        df_clean = df[~target_missing_mask].copy()
        notes.append(
            f"Removed {dropped_target_na} row(s) containing missing target values in '{target_column}'."
        )
    else:
        df_clean = df.copy()

    # 2. Separate X and y (strictly isolate target)
    y_raw = df_clean[target_column]
    X = df_clean.drop(columns=[target_column])

    if X.shape[1] == 0:
        raise ValueError("No feature columns remaining after removing the target column.")

    # 3. Check for entirely empty feature columns (100% NaN)
    for col in X.columns:
        if X[col].isna().all():
            raise ValueError(
                f"Feature column '{col}' contains 100% missing values. Empty columns cannot be imputed."
            )

    # 4. Identify feature column types in X
    col_types = identify_column_types(X)
    numeric_features = col_types["numeric"]
    categorical_features = col_types["categorical"]

    if not numeric_features and not categorical_features:
        raise ValueError("Dataset does not contain any usable numerical or categorical features.")

    # 5. Fit target encoder
    target_encoder = TargetEncoder()
    y_encoded = target_encoder.fit_transform(y_raw)

    notes.append(
        f"Prepared {len(X)} instances with {len(numeric_features)} numerical and "
        f"{len(categorical_features)} categorical feature(s)."
    )

    return PreparedData(
        X=X,
        y_raw=y_raw,
        y_encoded=y_encoded,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        target_encoder=target_encoder,
        dropped_rows_count=dropped_target_na,
        preprocessing_notes=notes,
    )


def build_column_transformer(
    numeric_features: List[str],
    categorical_features: List[str],
    requires_scaling: bool = True,
) -> ColumnTransformer:
    """Build a Scikit-Learn ColumnTransformer for automated feature preprocessing.

    Architecture:
    - Numerical Pipeline:
        1. SimpleImputer(strategy="median") -> Robust against skewed distributions and outliers.
        2. StandardScaler() -> Conditionally included only if `requires_scaling` is True
           (essential for Logistic Regression, KNN, SVM; omitted for Decision Tree, Random Forest, GBDT).
    - Categorical Pipeline:
        1. SimpleImputer(strategy="most_frequent") -> Imputes missing categories with mode.
        2. OneHotEncoder(handle_unknown="ignore", sparse_output=False) ->
           Encodes nominal features into dense binary vectors; safely ignores unknown categories at inference.

    Args:
        numeric_features: List of numerical column names.
        categorical_features: List of categorical column names.
        requires_scaling: If True, adds StandardScaler to the numeric pipeline.

    Returns:
        ColumnTransformer: Configured,  unfitted Scikit-learn ColumnTransformer.
    """
    transformers = []

    # 1. Numerical branch
    if numeric_features:
        numeric_steps: List[Tuple[str, BaseEstimator]] = [
            ("imputer", SimpleImputer(strategy="median"))
        ]
        if requires_scaling:
            numeric_steps.append(("scaler", StandardScaler()))

        numeric_pipeline = Pipeline(steps=numeric_steps)
        transformers.append(("num", numeric_pipeline, numeric_features))

    # 2. Categorical branch
    if categorical_features:
        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]
        )
        transformers.append(("cat", categorical_pipeline, categorical_features))

    # remainder="drop" ensures any untracked or unexpected columns are ignored safely
    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_classification_pipeline(
    estimator: BaseEstimator,
    numeric_features: List[str],
    categorical_features: List[str],
    requires_scaling: bool = True,
) -> Pipeline:
    """Construct an end-to-end Scikit-Learn Pipeline combining preprocessing and classifier.
    Educational Significance:
    -------------------------
    Encapsulating preprocessing and estimator inside a single `Pipeline` guarantees
    that all transformations (imputation, scaling, one-hot encoding) are fitted
    EXCLUSIVELY on the training partition or cross-validation training fold.
    This completely eliminates data leakage!

    Args:
        estimator: An unfitted Scikit-learn classifier instance.
        numeric_features: List of numerical column names.
        categorical_features: List of categorical column names.
        requires_scaling: Whether the model benefits from feature scaling.

    Returns:
        Pipeline: End-to-end trainable Scikit-learn Pipeline.
    """
    preprocessor = build_column_transformer(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        requires_scaling=requires_scaling,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", estimator),
        ]
    )


# Backward-compatible alias
build_preprocessor = build_column_transformer
