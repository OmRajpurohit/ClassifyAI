"""Exploratory data analysis summaries used by the EDA API and dashboard."""

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from app.services.data_analyzer import identify_column_types


def build_eda_summary(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """Build chart-ready distributions, missingness, and dataset quality counts.

    Numeric values are grouped into histogram bins. Categorical charts are limited
    to their twelve most frequent values to keep the dashboard readable.
    """
    types = identify_column_types(df)
    numeric_distributions: Dict[str, List[Dict[str, Any]]] = {}
    for col in types["numeric"]:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        if values.empty:
            numeric_distributions[col] = []
            continue
        bin_count = min(12, max(4, int(len(values) ** 0.5)))
        counts, edges = np.histogram(values, bins=bin_count)
        numeric_distributions[col] = [
            {"range": f"{edges[i]:.3g}–{edges[i + 1]:.3g}", "count": int(counts[i])}
            for i in range(len(counts))
        ]

    categorical_distributions = {
        col: [
            {"label": str(value), "count": int(count)}
            for value, count in df[col].fillna("(Missing)").value_counts().head(12).items()
        ]
        for col in types["categorical"]
    }
    target_distribution = (
        [
            {"label": str(value), "count": int(count)}
            for value, count in df[target_column].fillna("(Missing)").value_counts().items()
        ]
        if target_column in df.columns
        else []
    )

    return {
        "numeric_distributions": numeric_distributions,
        "categorical_distributions": categorical_distributions,
        "missing_values": [
            {"column": col, "count": int(count)} for col, count in df.isna().sum().items()
        ],
        "target_distribution": target_distribution,
        "duplicate_rows": int(df.duplicated().sum()),
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
    }
