"""Data Analysis Service for ClassifyAI.

Provides exploratory data analysis (EDA), column classification (numeric vs categorical),
missing value diagnostics, duplicate detection, target candidacy scoring,
and class imbalance evaluation for tabular classification datasets.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class DatasetAnalysisResult:
    """Summary metrics and exploratory profile of an uploaded dataset."""

    row_count: int
    column_count: int
    columns: List[str]
    dtypes: Dict[str, str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    unsupported_columns: List[str]
    missing_values_per_column: Dict[str, int]
    total_missing_values: int
    duplicate_row_count: int
    unique_values_per_column: Dict[str, int]
    target_candidates: List[str]
    sample_preview: List[Dict[str, Any]]
    summary_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to a plain dictionary for API serialization."""
        return asdict(self)


@dataclass
class TargetAnalysisResult:
    """Detailed classification profile of the user-selected target column."""

    target_column: str
    num_classes: int
    classes: List[str]
    class_distribution: Dict[str, int]
    class_percentages: Dict[str, float]
    is_multiclass: bool
    is_imbalanced: bool
    imbalance_ratio: float
    minority_class: str
    majority_class: str
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to a plain dictionary for API serialization."""
        return asdict(self)


def identify_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Segregate DataFrame columns into numerical, categorical, and unsupported types.

    Uses pandas.api.types to remain robust across modern pandas 3.x extension types
    (such as StringDtype) and standard numpy dtypes.

    Args:
        df: Input pandas DataFrame.

    Returns:
        Dict[str, List[str]]: Categorized column names.
    """
    numeric_cols: List[str] = []
    categorical_cols: List[str] = []
    unsupported_cols: List[str] = []

    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_bool_dtype(dtype):
            categorical_cols.append(col)
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            unsupported_cols.append(col)
        elif pd.api.types.is_numeric_dtype(dtype):
            numeric_cols.append(col)
        elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype):
            categorical_cols.append(col)
        else:
            unsupported_cols.append(col)

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "unsupported": unsupported_cols,
    }


def find_target_candidates(df: pd.DataFrame, col_types: Dict[str, List[str]]) -> List[str]:
    """Identify column candidates most likely to serve as the classification target.

    Heuristics:
    - Discrete columns with between 2 and 20 unique values.
    - Categorical or boolean columns.
    - Non-constant columns (unique count > 1).
    - Excludes columns where unique count equals row count (e.g. ID, UUID).

    Args:
        df: Input DataFrame.
        col_types: Categorized column lists.

    Returns:
        List[str]: Ranked list of potential target column names.
    """
    candidates = []
    n_rows = len(df)

    # Priority 1: Categorical or Boolean columns with 2-20 classes
    for col in col_types["categorical"]:
        n_unique = df[col].nunique(dropna=True)
        if 2 <= n_unique <= min(20, max(2, n_rows // 2)):
            candidates.append(col)

    # Priority 2: Numerical columns with small integer ranges (e.g., 0/1, 1-5 ratings)
    for col in col_types["numeric"]:
        n_unique = df[col].nunique(dropna=True)
        if 2 <= n_unique <= 10 and n_unique < n_rows:
            if col not in candidates:
                candidates.append(col)

    # If no obvious candidates, suggest columns with lowest unique counts (> 1)
    if not candidates:
        ranked_by_unique = sorted(
            [c for c in df.columns if 2 <= df[c].nunique(dropna=True) <= 20],
            key=lambda c: df[c].nunique(dropna=True),
        )
        candidates.extend(ranked_by_unique)

    return candidates


def analyze_dataset(df: pd.DataFrame) -> DatasetAnalysisResult:
    """Perform comprehensive exploratory data analysis on the provided DataFrame.

    Args:
        df: Input pandas DataFrame.

    Returns:
        DatasetAnalysisResult: Structured statistical and diagnostic summary.
    """
    n_rows, n_cols = df.shape
    col_types = identify_column_types(df)

    dtypes_dict = {col: str(df[col].dtype) for col in df.columns}
    missing_dict = {col: int(df[col].isna().sum()) for col in df.columns}
    total_missing = sum(missing_dict.values())
    unique_dict = {col: int(df[col].nunique(dropna=True)) for col in df.columns}
    duplicate_rows = int(df.duplicated().sum())

    target_candidates = find_target_candidates(df, col_types)

    # Generate 5-row preview safely handling NaN/Infinity for valid JSON serialization
    preview_df = df.head(5).copy()
    preview_records = preview_df.replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict(orient="records")

    summary_notes: List[str] = []
    if duplicate_rows > 0:
        summary_notes.append(f"Detected {duplicate_rows} duplicate row(s). Consider reviewing dataset deduplication.")
    if total_missing > 0:
        summary_notes.append(
            f"Found {total_missing} missing value(s) across {sum(1 for v in missing_dict.values() if v > 0)} column(s)."
        )
    if col_types["unsupported"]:
        summary_notes.append(
            f"Detected unsupported column type(s): {col_types['unsupported']}. These may require specialized parsing."
        )

    return DatasetAnalysisResult(
        row_count=n_rows,
        column_count=n_cols,
        columns=list(df.columns),
        dtypes=dtypes_dict,
        numeric_columns=col_types["numeric"],
        categorical_columns=col_types["categorical"],
        unsupported_columns=col_types["unsupported"],
        missing_values_per_column=missing_dict,
        total_missing_values=total_missing,
        duplicate_row_count=duplicate_rows,
        unique_values_per_column=unique_dict,
        target_candidates=target_candidates,
        sample_preview=preview_records,
        summary_notes=summary_notes,
    )


def validate_target_suitability(df: pd.DataFrame, target_column: str) -> None:
    """Validate that the specified column is valid and suitable for classification tasks.

    Args:
        df: Input DataFrame.
        target_column: Name of the proposed target column.

    Raises:
        ValueError: If the target column is missing, constant, continuous regression-like,
                    or contains insufficient samples per class.
    """
    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' was not found in the dataset. Available columns: {list(df.columns)}"
        )

    series = df[target_column].dropna()

    if len(series) == 0:
        raise ValueError(f"Target column '{target_column}' contains only missing values.")

    unique_classes = series.unique()
    n_unique = len(unique_classes)

    if n_unique < 2:
        raise ValueError(
            f"Target column '{target_column}' has only {n_unique} unique class ({list(unique_classes)}). "
            f"Classification requires at least 2 distinct classes."
        )

    # Detect regression continuous target masquerading as classification
    if pd.api.types.is_float_dtype(series.dtype) and n_unique > 20:
        unique_ratio = n_unique / len(series)
        if unique_ratio > 0.2:
            raise ValueError(
                f"Target column '{target_column}' appears to be a continuous numerical variable "
                f"({n_unique} unique float values). ClassifyAI is designed for discrete classification, not continuous regression."
            )

    # Check for excessive classes (e.g., unique IDs)
    if n_unique == len(df):
        raise ValueError(
            f"Target column '{target_column}' has a unique value on every row (100% unique cardinality). "
            f"This looks like an ID or primary key column, not a valid classification target."
        )

    # Check that each class has at least 2 samples for train/test partition and CV splitting
    class_counts = series.value_counts()
    singleton_classes = class_counts[class_counts < 2].index.tolist()
    if singleton_classes:
        raise ValueError(
            f"The following class label(s) in target column '{target_column}' have fewer than 2 samples: "
            f"{singleton_classes}. Stratified cross-validation requires at least 2 samples per class."
        )


def analyze_target_column(df: pd.DataFrame, target_column: str) -> TargetAnalysisResult:
    """Perform detailed class distribution and imbalance analysis on the target column.

    Imbalance Criterion:
    - Imbalance ratio = count(majority_class) / count(minority_class).
    - If ratio >= 2.5 or minority class makes up < 20% of total samples, the target is
      classified as imbalanced.

    Args:
        df: Input DataFrame.
        target_column: Validated target column name.

    Returns:
        TargetAnalysisResult: Class distribution metrics and educational advice.
    """
    validate_target_suitability(df, target_column)

    series = df[target_column].dropna()
    class_counts = series.value_counts()

    total_valid = len(series)
    num_classes = len(class_counts)
    is_multiclass = num_classes > 2

    # String keys for JSON serialization
    distribution_dict = {str(k): int(v) for k, v in class_counts.items()}
    percentages_dict = {str(k): round((int(v) / total_valid) * 100.0, 2) for k, v in class_counts.items()}

    majority_class = str(class_counts.index[0])
    minority_class = str(class_counts.index[-1])
    majority_count = class_counts.iloc[0]
    minority_count = class_counts.iloc[-1]

    imbalance_ratio = float(round(float(majority_count) / max(int(minority_count), 1), 2))
    minority_percentage = float((float(minority_count) / float(total_valid)) * 100.0)

    is_imbalanced = bool((imbalance_ratio >= 2.5) or (minority_percentage < 20.0))
    is_multiclass = bool(num_classes > 2)

    recommendations: List[str] = []
    if is_imbalanced:
        recommendations.append(
            f"Class imbalance detected (Majority/Minority ratio: {imbalance_ratio}:1). "
            f"Accuracy alone may be misleading; evaluate Balanced Accuracy and Macro-F1."
        )
    if is_multiclass:
        recommendations.append(
            f"Multiclass dataset with {num_classes} categories. Evaluating Macro and Weighted F1-scores."
        )
    else:
        recommendations.append(
            "Binary classification task. Evaluating Accuracy, Precision, Recall, F1, and ROC-AUC."
        )

    return TargetAnalysisResult(
        target_column=target_column,
        num_classes=num_classes,
        classes=[str(c) for c in class_counts.index],
        class_distribution=distribution_dict,
        class_percentages=percentages_dict,
        is_multiclass=is_multiclass,
        is_imbalanced=is_imbalanced,
        imbalance_ratio=imbalance_ratio,
        minority_class=minority_class,
        majority_class=majority_class,
        recommendations=recommendations,
    )
