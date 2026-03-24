"""Unit tests for CSV parser with v1 schema validation (T-008)."""

import textwrap
from pathlib import Path

import pytest

from scripts._utils.csv_parser import (
    CSVContractError,
    ModelCandidate,
    _parse_integer_field,
    _validate_timestamp,
    parse_csv,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestParseIntegerField:
    def test_plain_integer(self):
        assert _parse_integer_field("1000", "field", 1) == 1000

    def test_shorthand_k_lowercase(self):
        assert _parse_integer_field("2.59k", "field", 1) == 2590

    def test_shorthand_k_uppercase(self):
        assert _parse_integer_field("7.54K", "field", 1) == 7540

    def test_shorthand_rounds_correctly(self):
        assert _parse_integer_field("3.13k", "field", 1) == 3130

    def test_zero(self):
        assert _parse_integer_field("0", "field", 1) == 0

    def test_whitespace_stripped(self):
        assert _parse_integer_field("  500  ", "field", 1) == 500

    def test_invalid_raises(self):
        with pytest.raises(CSVContractError) as exc:
            _parse_integer_field("not-a-number", "hf_likes_at_snapshot", 3)
        assert exc.value.reason_code == "ERR_INPUT_MISSING_REQUIRED_FIELD"

    def test_negative_raises(self):
        with pytest.raises(CSVContractError):
            _parse_integer_field("-5", "field", 1)

    def test_shorthand_4k(self):
        assert _parse_integer_field("4.01k", "field", 1) == 4010

    def test_shorthand_3_55k(self):
        assert _parse_integer_field("3.55k", "field", 1) == 3550


class TestValidateTimestamp:
    def test_valid_timestamp(self):
        ts = "2026-03-20T18:33:20Z"
        assert _validate_timestamp(ts, "snapshot_timestamp_utc", 1) == ts

    def test_invalid_format_raises(self):
        with pytest.raises(CSVContractError) as exc:
            _validate_timestamp("not-a-timestamp", "snapshot_timestamp_utc", 1)
        assert exc.value.reason_code == "ERR_INPUT_INVALID_TIMESTAMP"

    def test_missing_z_suffix_raises(self):
        with pytest.raises(CSVContractError):
            _validate_timestamp("2026-03-20T18:33:20", "snapshot_timestamp_utc", 1)

    def test_invalid_month_raises(self):
        with pytest.raises(CSVContractError):
            _validate_timestamp("2026-13-20T18:33:20Z", "snapshot_timestamp_utc", 1)

    def test_invalid_day_raises(self):
        with pytest.raises(CSVContractError):
            _validate_timestamp("2026-02-30T18:33:20Z", "snapshot_timestamp_utc", 1)


class TestParseCsv:
    def test_valid_fixture(self):
        candidates = parse_csv(FIXTURES / "valid_candidates.csv")
        assert len(candidates) == 1
        c = candidates[0]
        assert c.hf_model_id == "google-bert/bert-base-uncased"
        assert c.source_repo_url == "https://github.com/google-research/bert"
        assert c.hf_likes_at_snapshot == 2590
        assert c.hf_downloads_at_snapshot == 72509778
        assert c.snapshot_timestamp_utc == "2026-03-20T18:33:20Z"
        assert c.dependency_artifact_url == "https://github.com/google-research/bert/blob/master/requirements.txt"
        assert c.input_row_number == 1

    def test_legacy_header_raises(self):
        with pytest.raises(CSVContractError) as exc:
            parse_csv(FIXTURES / "legacy_header.csv")
        assert exc.value.reason_code == "ERR_INPUT_MISSING_REQUIRED_FIELD"
        assert "ranking_signal" in str(exc.value)

    def test_bad_timestamp_raises(self):
        with pytest.raises(CSVContractError) as exc:
            parse_csv(FIXTURES / "bad_timestamp.csv")
        assert exc.value.reason_code == "ERR_INPUT_INVALID_TIMESTAMP"

    def test_bad_likes_raises(self):
        with pytest.raises(CSVContractError) as exc:
            parse_csv(FIXTURES / "bad_likes.csv")
        assert exc.value.reason_code == "ERR_INPUT_MISSING_REQUIRED_FIELD"

    def test_output_sorted_by_hf_model_id(self, tmp_path):
        csv_content = textwrap.dedent("""\
            hf_model_id,source_repo_url,dependency_artifact,dependency_artifact_url,snapshot_timestamp_utc,hf_downloads_at_snapshot,hf_likes_at_snapshot,selection_rationale,curation_notes
            z-org/z-model,https://github.com/z-org/z-model,,,2026-03-20T00:00:00Z,100,10,,
            a-org/a-model,https://github.com/a-org/a-model,,,2026-03-20T00:00:00Z,200,20,,
            m-org/m-model,https://github.com/m-org/m-model,,,2026-03-20T00:00:00Z,300,30,,
        """)
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        candidates = parse_csv(csv_file)
        ids = [c.hf_model_id for c in candidates]
        assert ids == sorted(ids)

    def test_optional_fields_none_when_empty(self, tmp_path):
        csv_content = textwrap.dedent("""\
            hf_model_id,source_repo_url,dependency_artifact,dependency_artifact_url,snapshot_timestamp_utc,hf_downloads_at_snapshot,hf_likes_at_snapshot,selection_rationale,curation_notes
            test/model,https://github.com/test/model,,,2026-03-20T00:00:00Z,0,0,,
        """)
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        candidates = parse_csv(csv_file)
        c = candidates[0]
        assert c.dependency_artifact is None
        assert c.dependency_artifact_url is None
        assert c.selection_rationale is None
        assert c.curation_notes is None

    def test_missing_required_column_raises(self, tmp_path):
        csv_content = textwrap.dedent("""\
            hf_model_id,source_repo_url,snapshot_timestamp_utc,hf_downloads_at_snapshot
            test/model,https://github.com/test/model,2026-03-20T00:00:00Z,100
        """)
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        with pytest.raises(CSVContractError) as exc:
            parse_csv(csv_file)
        assert "hf_likes_at_snapshot" in str(exc.value)

    def test_empty_required_field_raises(self, tmp_path):
        csv_content = textwrap.dedent("""\
            hf_model_id,source_repo_url,dependency_artifact,dependency_artifact_url,snapshot_timestamp_utc,hf_downloads_at_snapshot,hf_likes_at_snapshot,selection_rationale,curation_notes
            ,https://github.com/test/model,,,2026-03-20T00:00:00Z,100,10,,
        """)
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        with pytest.raises(CSVContractError) as exc:
            parse_csv(csv_file)
        assert "hf_model_id" in str(exc.value)

    def test_input_row_number_1_based(self, tmp_path):
        csv_content = textwrap.dedent("""\
            hf_model_id,source_repo_url,dependency_artifact,dependency_artifact_url,snapshot_timestamp_utc,hf_downloads_at_snapshot,hf_likes_at_snapshot,selection_rationale,curation_notes
            a-org/model1,https://github.com/a/b,,,2026-03-20T00:00:00Z,0,0,,
            b-org/model2,https://github.com/c/d,,,2026-03-20T00:00:00Z,0,0,,
        """)
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        candidates = parse_csv(csv_file)
        # After sort by hf_model_id, a-org comes first
        row_numbers = {c.hf_model_id: c.input_row_number for c in candidates}
        assert 1 in row_numbers.values()
        assert 2 in row_numbers.values()

    def test_all_legacy_columns_rejected(self, tmp_path):
        for legacy_col in ["ranking_signal", "selection_method", "eligible", "selection_source"]:
            csv_content = (
                f"hf_model_id,source_repo_url,snapshot_timestamp_utc,"
                f"hf_downloads_at_snapshot,hf_likes_at_snapshot,{legacy_col}\n"
                f"test/model,https://github.com/x/y,2026-03-20T00:00:00Z,0,0,val\n"
            )
            csv_file = tmp_path / f"legacy_{legacy_col}.csv"
            csv_file.write_text(csv_content)
            with pytest.raises(CSVContractError):
                parse_csv(csv_file)

    def test_real_models_csv(self):
        """Smoke test: the actual data/models.csv parses successfully."""
        repo_root = Path(__file__).parent.parent.parent
        models_csv = repo_root / "data" / "models.csv"
        candidates = parse_csv(models_csv)
        assert len(candidates) == 13
        for c in candidates:
            assert c.hf_model_id
            assert c.source_repo_url
            assert c.hf_downloads_at_snapshot >= 0
            assert c.hf_likes_at_snapshot >= 0
