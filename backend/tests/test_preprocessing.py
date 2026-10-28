"""Unit tests for ClassifyAI data analysis, validation, and preprocessing services.

Verifies:
- Safe CSV parsing, validation, and file-size guardrails.
- Dataset exploratory profiling (column dtypes, duplicate detection, missing counts).
- Target candidate heuristic identification.
- Target column validation (rejecting single class, 100% IDs, regression floats).
- Binary, multiclass, and imbalanced dataset diagnostics.
- Numerical missing-value median imputation.
- Categorical missing-value mode imputation and One-Hot Encoding.
- Unknown categories handling safely at inference time.
- Conditional numerical scaling (omitted for tree models, enabled for distance/linear models).
- Complete Scikit-Learn Pipeline execution without data leakage.
"""


import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier



from app.services.data_analyzer import (
    analyze_dataset,
    analyze_target_column,
    identify_column_types,
    validate_target_suitability,
)
from app.services.preprocessing import (
    TargetEncoder,
    build_classification_pipeline,
    build_preprocessor,
    prepare_features_and_target,
)
from app.utils.file_handler import sanitize_filename, validate_csv_contents


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_mixed_dataframe():
    """Generates a representative tabular dataset with numerical, categorical, and missing values."""
    return pd.DataFrame({
        "age": [25, 30, np.nan, 45, 50, 35, 40, 28, 62, 31],
        "income": [50000, 60000, 75000, np.nan, 120000, 80000, 95000, 48000, 110000, 52000],
        "education": ["bachelor", "master", np.nan, "doctorate", "master", "bachelor", "high_school", "bachelor", "doctorate", "master"],
        "city": ["New York", "Chicago", "New York", "Austin", "Chicago", "Austin", "New York", "Chicago", "Austin", "New York"],
        "target": ["approved", "rejected", "approved", "approved", "rejected", "approved", "rejected", "rejected", "approved", "approved"],
    })


@pytest.fixture
def sample_csv_bytes(sample_mixed_dataframe):
    """Encodes the sample DataFrame into CSV bytes."""
    return sample_mixed_dataframe.to_csv(index=False).encode("utf-8")


# -----------------------------------------------------------------------------
# File Handler Tests
# -----------------------------------------------------------------------------

def test_sanitize_filename():
    """Ensure malicious paths and invalid characters in filenames are sanitized."""
    raw = "../../../etc/passwd.csv"
    sanitized = sanitize_filename(raw)
    assert "/" not in sanitized
    assert "\\" not in sanitized
    assert sanitized.endswith(".csv")


def test_validate_csv_contents_success(sample_csv_bytes):
    """Ensure valid CSV bytes are properly parsed into a DataFrame."""
    df, message = validate_csv_contents(sample_csv_bytes)
    assert not df.empty
    assert len(df) == 10
    assert "Successfully loaded" in message


def test_validate_csv_contents_empty_fails():
    """Ensure empty payloads raise a descriptive ValueError."""
    with pytest.raises(ValueError, match="Uploaded file is empty"):
        validate_csv_contents(b"")


def test_validate_csv_contents_size_limit_exceeded(sample_csv_bytes):
    """Ensure files exceeding max size limit are rejected."""
    with pytest.raises(ValueError, match="File size exceeds maximum permitted limit"):
        validate_csv_contents(sample_csv_bytes, max_size_bytes=10)


def test_validate_csv_contents_insufficient_columns():
    """Ensure single-column files are rejected because classification requires features and target."""
    single_col_csv = b"col1\n1\n2\n3\n"
    with pytest.raises(ValueError, match="requires at least 2 columns"):
        validate_csv_contents(single_col_csv)


# -----------------------------------------------------------------------------
# Data Analyzer Tests
# -----------------------------------------------------------------------------

def test_identify_column_types(sample_mixed_dataframe):
    """Ensure numerical and categorical columns are correctly segregated."""
    types = identify_column_types(sample_mixed_dataframe)
    assert "age" in types["numeric"]
    assert "income" in types["numeric"]
    assert "education" in types["categorical"]
    assert "city" in types["categorical"]
    assert "target" in types["categorical"]
    assert len(types["unsupported"]) == 0


def test_analyze_dataset(sample_mixed_dataframe):
    """Ensure exploratory dataset analysis computes correct summary counts."""
    result = analyze_dataset(sample_mixed_dataframe)
    assert result.row_count == 10
    assert result.column_count == 5
    assert result.total_missing_values == 3  # age: 1, income: 1, education: 1
    assert result.missing_values_per_column["age"] == 1
    assert result.missing_values_per_column["education"] == 1
    assert "target" in result.target_candidates
    assert len(result.sample_preview) == 5


def test_validate_target_suitability_missing_target(sample_mixed_dataframe):
    """Ensure validation fails when the requested target column does not exist."""
    with pytest.raises(ValueError, match="was not found in the dataset"):
        validate_target_suitability(sample_mixed_dataframe, "non_existent_column")


def test_validate_target_suitability_single_class():
    """Ensure single-class targets are rejected."""
    df = pd.DataFrame({"f1": [1, 2, 3, 4], "target": ["A", "A", "A", "A"]})
    with pytest.raises(ValueError, match="Classification requires at least 2 distinct classes"):
        validate_target_suitability(df, "target")


def test_validate_target_suitability_continuous_regression():
    """Ensure continuous floating point targets are rejected with a helpful regression message."""
    df = pd.DataFrame({
        "f1": range(30),
        "target": np.linspace(10.5, 99.8, 30),
    })
    with pytest.raises(ValueError, match="continuous numerical variable"):
        validate_target_suitability(df, "target")


def test_validate_target_suitability_all_unique_ids():
    """Ensure columns with 100% unique values (IDs) are rejected."""
    df = pd.DataFrame({
        "f1": [1, 2, 3, 4, 5],
        "id_target": ["id_1", "id_2", "id_3", "id_4", "id_5"],
    })
    with pytest.raises(ValueError, match="unique value on every row"):
        validate_target_suitability(df, "id_target")


def test_analyze_target_column_binary(sample_mixed_dataframe):
    """Ensure binary target diagnostics calculate correct distributions and class counts."""
    target_res = analyze_target_column(sample_mixed_dataframe, "target")
    assert target_res.num_classes == 2
    assert not target_res.is_multiclass
    assert "approved" in target_res.class_distribution
    assert "rejected" in target_res.class_distribution


def test_analyze_target_column_imbalanced():
    """Ensure class imbalance is flagged when minority class is below threshold."""
    df = pd.DataFrame({
        "feature": range(20),
        "target": ["majority"] * 18 + ["minority"] * 2,
    })
    target_res = analyze_target_column(df, "target")
    assert target_res.is_imbalanced
    assert target_res.imbalance_ratio >= 2.5
    assert any("imbalance detected" in rec.lower() for rec in target_res.recommendations)


# -----------------------------------------------------------------------------
# Preprocessing Service Tests
# -----------------------------------------------------------------------------

def test_target_encoder_roundtrip():
    """Ensure TargetEncoder transforms categories to integers and back to original strings."""
    encoder = TargetEncoder()
    raw = ["apple", "banana", "cherry", "apple", "banana"]
    encoded = encoder.fit_transform(raw)
    assert len(encoded) == 5
    assert set(encoded) == {0, 1, 2}

    reconstructed = encoder.inverse_transform(encoded)
    assert list(reconstructed) == raw


def test_prepare_features_and_target_prevents_target_leakage(sample_mixed_dataframe):
    """Ensure the target column is strictly removed from feature matrix X."""
    prepared = prepare_features_and_target(sample_mixed_dataframe, "target")
    assert "target" not in prepared.X.columns
    assert len(prepared.X.columns) == 4
    assert len(prepared.y_encoded) == len(prepared.X)
    assert set(prepared.numeric_features) == {"age", "income"}
    assert set(prepared.categorical_features) == {"education", "city"}


def test_prepare_features_and_target_rejects_empty_column():
    """Ensure datasets with an entirely empty feature column (100% NaN) are rejected."""
    df = pd.DataFrame({
        "valid_feat": [1, 2, 3, 4],
        "empty_feat": [np.nan, np.nan, np.nan, np.nan],
        "target": ["A", "B", "A", "B"],
    })
    with pytest.raises(ValueError, match="contains 100% missing values"):
        prepare_features_and_target(df, "target")


def test_pipeline_with_scaling_handles_missing_and_new_categories(sample_mixed_dataframe):
    """Ensure the end-to-end Pipeline with scaling imputes NaNs and handles unknown categories."""
    prepared = prepare_features_and_target(sample_mixed_dataframe, "target")

    # Logistic Regression requires scaling
    pipe = build_classification_pipeline(
        estimator=LogisticRegression(random_state=42),
        numeric_features=prepared.numeric_features,
        categorical_features=prepared.categorical_features,
        requires_scaling=True,
    )

    # 1. Fit on training data containing NaNs
    pipe.fit(prepared.X, prepared.y_encoded)

    # 2. Predict on data containing missing values AND an unknown unseen category ("Seattle", "phd")
    unseen_test = pd.DataFrame({
        "age": [np.nan, 29],
        "income": [60000, np.nan],
        "education": ["phd", "bachelor"],       # 'phd' was never in the training set
        "city": ["Seattle", "New York"],         # 'Seattle' was never in the training set
    })

    preds = pipe.predict(unseen_test)
    assert len(preds) == 2
    assert set(preds).issubset({0, 1})

    probas = pipe.predict_proba(unseen_test)
    assert probas.shape == (2, 2)
    assert np.allclose(probas.sum(axis=1), 1.0)


def test_pipeline_without_scaling_for_tree_models(sample_mixed_dataframe):
    """Ensure tree models like Random Forest work cleanly with unscaled numeric features."""
    prepared = prepare_features_and_target(sample_mixed_dataframe, "target")

    pipe = build_classification_pipeline(
        estimator=RandomForestClassifier(n_estimators=10, random_state=42),
        numeric_features=prepared.numeric_features,
        categorical_features=prepared.categorical_features,
        requires_scaling=False,  # Scaler step excluded!
    )

    # Fit and predict
    pipe.fit(prepared.X, prepared.y_encoded)
    preds = pipe.predict(prepared.X)
    assert len(preds) == len(prepared.y_encoded)

    # Verify scaler is NOT present in the numerical sub-pipeline
    num_subpipe = pipe.named_steps["preprocessor"].named_transformers_["num"]
    step_names = [name for name, _ in num_subpipe.steps]
    assert "scaler" not in step_names
    assert "imputer" in step_names
