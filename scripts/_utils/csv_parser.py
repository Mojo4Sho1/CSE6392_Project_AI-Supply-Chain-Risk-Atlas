"""
csv_parser.py — CSV parser with strict v1 schema validation.

Validates the 9-column v1 schema from docs/specs/data-sourcing-and-eligibility.md.
Rejects legacy column names with exit-2-mapped CSVContractError.
"""

import csv
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS: frozenset[str] = frozenset({
    "hf_model_id",
    "source_repo_url",
    "snapshot_timestamp_utc",
    "hf_downloads_at_snapshot",
    "hf_likes_at_snapshot",
})

OPTIONAL_COLUMNS: frozenset[str] = frozenset({
    "dependency_artifact",
    "dependency_artifact_url",
    "selection_rationale",
    "curation_notes",
})

LEGACY_COLUMNS: frozenset[str] = frozenset({
    "ranking_signal",
    "selection_method",
    "eligible",
    "selection_source",
})

V1_COLUMNS: frozenset[str] = REQUIRED_COLUMNS | OPTIONAL_COLUMNS

_TS_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class CSVContractError(Exception):
    """
    Raised when CSV violates the v1 input contract.
    Caller maps to exit code 2.
    """

    def __init__(self, message: str, reason_code: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


@dataclass
class ModelCandidate:
    hf_model_id: str
    source_repo_url: str
    snapshot_timestamp_utc: str
    hf_downloads_at_snapshot: int
    hf_likes_at_snapshot: int
    dependency_artifact: str | None
    dependency_artifact_url: str | None
    selection_rationale: str | None
    curation_notes: str | None
    input_row_number: int  # 1-based data row index (excludes header)


def parse_csv(path: str | Path) -> list[ModelCandidate]:
    """
    Parse and validate data/models.csv against the v1 schema.

    Raises CSVContractError on any contract violation.
    Returns rows sorted by hf_model_id ascending.
    """
    path = Path(path)
    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = list(reader.fieldnames or [])
            _validate_header(columns)
            candidates: list[ModelCandidate] = []
            for row_idx, row in enumerate(reader, start=1):
                candidate = _parse_row(row, row_idx)
                candidates.append(candidate)
    except CSVContractError:
        raise
    except OSError as e:
        raise CSVContractError(
            f"Cannot read CSV file '{path}': {e}",
            reason_code="ERR_INPUT_MISSING_REQUIRED_FIELD",
        ) from e

    candidates.sort(key=lambda c: c.hf_model_id)
    return candidates


def _validate_header(columns: list[str]) -> None:
    """
    Raises CSVContractError if legacy columns present or required columns missing.
    Emits WARNING for unknown non-legacy extra columns.
    """
    col_set = set(columns)

    found_legacy = col_set & LEGACY_COLUMNS
    if found_legacy:
        raise CSVContractError(
            f"CSV contains legacy columns not allowed in v1 schema: {sorted(found_legacy)}. "
            "Remove these columns before processing.",
            reason_code="ERR_INPUT_MISSING_REQUIRED_FIELD",
        )

    missing_required = REQUIRED_COLUMNS - col_set
    if missing_required:
        raise CSVContractError(
            f"CSV is missing required columns: {sorted(missing_required)}",
            reason_code="ERR_INPUT_MISSING_REQUIRED_FIELD",
        )

    unknown = col_set - V1_COLUMNS
    if unknown:
        logger.warning("CSV contains unrecognized columns (ignored): %s", sorted(unknown))


def _parse_row(row: dict[str, str], row_num: int) -> ModelCandidate:
    """Parse and validate a single CSV data row."""

    hf_model_id = _require_field(row, "hf_model_id", row_num)
    source_repo_url = _require_field(row, "source_repo_url", row_num)
    snapshot_ts = _require_field(row, "snapshot_timestamp_utc", row_num)
    _validate_timestamp(snapshot_ts, "snapshot_timestamp_utc", row_num)

    downloads_raw = _require_field(row, "hf_downloads_at_snapshot", row_num)
    likes_raw = _require_field(row, "hf_likes_at_snapshot", row_num)

    downloads = _parse_integer_field(downloads_raw, "hf_downloads_at_snapshot", row_num)
    likes = _parse_integer_field(likes_raw, "hf_likes_at_snapshot", row_num)

    return ModelCandidate(
        hf_model_id=hf_model_id,
        source_repo_url=source_repo_url,
        snapshot_timestamp_utc=snapshot_ts,
        hf_downloads_at_snapshot=downloads,
        hf_likes_at_snapshot=likes,
        dependency_artifact=_optional_field(row, "dependency_artifact"),
        dependency_artifact_url=_optional_field(row, "dependency_artifact_url"),
        selection_rationale=_optional_field(row, "selection_rationale"),
        curation_notes=_optional_field(row, "curation_notes"),
        input_row_number=row_num,
    )


def _require_field(row: dict[str, str], field: str, row_num: int) -> str:
    value = row.get(field, "").strip()
    if not value:
        raise CSVContractError(
            f"Row {row_num}: required field '{field}' is missing or empty",
            reason_code="ERR_INPUT_MISSING_REQUIRED_FIELD",
        )
    return value


def _optional_field(row: dict[str, str], field: str) -> str | None:
    value = row.get(field, "").strip()
    return value if value else None


def _parse_integer_field(raw: str, field_name: str, row_num: int) -> int:
    """
    Parse integer or human-readable shorthand like '2.59k', '7.54k'.
    Raises CSVContractError if unparseable or negative.
    """
    raw = raw.strip()
    try:
        if raw.lower().endswith("k"):
            value = round(float(raw[:-1]) * 1000)
        else:
            value = int(raw)
    except ValueError as e:
        raise CSVContractError(
            f"Row {row_num}: field '{field_name}' has unparseable value '{raw}'",
            reason_code="ERR_INPUT_MISSING_REQUIRED_FIELD",
        ) from e

    if value < 0:
        raise CSVContractError(
            f"Row {row_num}: field '{field_name}' must be non-negative, got {value}",
            reason_code="ERR_INPUT_MISSING_REQUIRED_FIELD",
        )
    return value


def _validate_timestamp(raw: str, field_name: str, row_num: int) -> str:
    """
    Validate UTC ISO-8601 with Z suffix.
    Returns the string unchanged if valid.
    Raises CSVContractError if malformed.
    """
    if not _TS_PATTERN.match(raw):
        raise CSVContractError(
            f"Row {row_num}: field '{field_name}' must be UTC ISO-8601 with Z suffix "
            f"(e.g. '2026-03-20T18:33:20Z'), got '{raw}'",
            reason_code="ERR_INPUT_INVALID_TIMESTAMP",
        )
    try:
        datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as e:
        raise CSVContractError(
            f"Row {row_num}: field '{field_name}' contains invalid date/time: '{raw}'",
            reason_code="ERR_INPUT_INVALID_TIMESTAMP",
        ) from e
    return raw
