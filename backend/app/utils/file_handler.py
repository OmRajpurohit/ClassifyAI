"""File handling and CSV dataset loading utilities.

Provides secure file validation, size limits, and robust CSV parsing
to guard against corrupted inputs, excessive memory usage, and malformed files.
"""

import io
import os
import re
from typing import Tuple
import pandas as pd

# Default upload limit: 10 MB to prevent memory exhaustion
DEFAULT_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def sanitize_filename(filename: str) -> str:
    """Sanitize user-provided filename to prevent path traversal attacks.

    Args:
        filename: Raw filename provided by client.

    Returns:
        str: Safe basename containing only alphanumeric, underscore, dot, and dash.
    """
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean_name)
    return clean_name or "uploaded_dataset.csv"


def validate_csv_contents(file_bytes: bytes, max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES) -> Tuple[pd.DataFrame, str]:
    """Validate raw file bytes and parse into a Pandas DataFrame.

    Performs security and sanity checks:
    - Validates file size against maximum threshold.
    - Ensures non-empty payload.
    - Decodes text with UTF-8 fallback to latin1.
    - Parses CSV and rejects zero-row or zero-column datasets.

    Args:
        file_bytes: Raw bytes from the uploaded file.
        max_size_bytes: Maximum permitted size in bytes.

    Returns:
        Tuple[pd.DataFrame, str]: (Parsed DataFrame, Success/status message).

    Raises:
        ValueError: If file fails size limits, encoding, or structural validation.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty (0 bytes). Please upload a valid CSV file.")

    if len(file_bytes) > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise ValueError(
            f"File size exceeds maximum permitted limit of {max_mb:.1f} MB. "
            f"Uploaded size: {len(file_bytes) / (1024 * 1024):.2f} MB."
        )

    # Attempt decoding with UTF-8 first, fallback to latin-1 for international characters
    try:
        decoded_text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            decoded_text = file_bytes.decode("latin-1")
        except Exception as exc:
            raise ValueError("Unable to decode file. Please ensure the CSV is UTF-8 or Latin-1 encoded.") from exc

    # Parse with pandas
    try:
        df = pd.read_csv(io.StringIO(decoded_text))
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV file: {str(exc)}") from exc

    if df.empty:
        raise ValueError("The parsed CSV dataset contains no data rows.")

    if df.shape[1] < 2:
        raise ValueError(
            f"Classification requires at least 2 columns (1 feature and 1 target). Found {df.shape[1]} column."
        )

    return df, f"Successfully loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns."
