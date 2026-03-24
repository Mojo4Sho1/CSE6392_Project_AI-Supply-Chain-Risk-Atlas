"""
Integration tests for ingest_repo_artifacts.py (T-013).

All network calls are mocked. Tests verify:
- eligible path produces valid manifest_index.json
- legacy header CSV exits with code 2
- unreachable repo path
- no supported artifacts path
- parse failed path
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

REPO_ROOT = Path(__file__).parent.parent.parent
FIXTURES = Path(__file__).parent.parent / "fixtures"
SCRIPT = str(REPO_ROOT / "scripts" / "ingest_repo_artifacts.py")
SNAPSHOT_TS = "2026-03-23T00:00:00Z"


def _make_ok_response(content: bytes = b"torch\nnumpy\n") -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.ok = True
    resp.status_code = 200
    resp.content = content
    resp.json.return_value = {"default_branch": "master", "sha": "abc123def456"}
    return resp


def _make_404_response() -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.ok = False
    resp.status_code = 404
    return resp


def _run_script(*extra_args, input_csv=None, output_root=None):
    """Run the ingest script via subprocess from the repo root."""
    if input_csv is None:
        input_csv = str(FIXTURES / "valid_candidates.csv")
    cmd = [
        sys.executable, SCRIPT,
        "--input", input_csv,
        "--output-root", str(output_root),
        "--snapshot-timestamp", SNAPSHOT_TS,
    ] + list(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


class TestIngestScript:
    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, SCRIPT, "--help"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        assert result.returncode == 0
        assert "--input" in result.stdout
        assert "--output-root" in result.stdout
        assert "--snapshot-timestamp" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--log-level" in result.stdout

    def test_legacy_header_exits_2(self, tmp_path):
        result = _run_script(
            input_csv=str(FIXTURES / "legacy_header.csv"),
            output_root=tmp_path,
        )
        assert result.returncode == 2

    def test_bad_timestamp_exits_2(self, tmp_path):
        result = _run_script(
            input_csv=str(FIXTURES / "bad_timestamp.csv"),
            output_root=tmp_path,
        )
        assert result.returncode == 2

    def test_bad_likes_exits_2(self, tmp_path):
        result = _run_script(
            input_csv=str(FIXTURES / "bad_likes.csv"),
            output_root=tmp_path,
        )
        assert result.returncode == 2


class TestIngestIntegration:
    """Tests using mocked network calls to verify manifest outputs."""

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_eligible_manifest_produced(self, mock_resolve, mock_fetch, tmp_path):
        """Eligible candidate produces a valid manifest_index.json."""
        mock_resolve.return_value = ("master", "abc123def456", "none")
        mock_fetch.side_effect = [
            _make_ok_response(),           # repo reachable
            _make_ok_response(b"torch\n"), # artifact fetch
        ]

        from scripts.ingest_repo_artifacts import run
        import argparse
        args = argparse.Namespace(
            input=str(FIXTURES / "valid_candidates.csv"),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )
        exit_code = run(args)
        assert exit_code == 0

        # Verify manifest exists
        manifests = list(tmp_path.glob("manifests/*/manifest_index.json"))
        assert len(manifests) == 1

        manifest = json.loads(manifests[0].read_text(encoding="utf-8"))

        # Required schema fields
        assert manifest["schema_version"] == "1.0"
        assert manifest["hf_model_id"] == "google-bert/bert-base-uncased"
        assert "model_id" in manifest
        assert manifest["model_id"].startswith("google-bert--bert-base-uncased--")
        assert manifest["source_repo_url"] == "https://github.com/google-research/bert"
        assert manifest["snapshot_timestamp_utc"] == SNAPSHOT_TS
        assert "generated_at_utc" in manifest
        assert manifest["generated_at_utc"].endswith("Z")

        # Eligibility
        assert manifest["eligibility"]["eligible"] is True
        assert manifest["eligibility"]["reason_code"] == "OK_ELIGIBLE"

        # Provenance
        assert manifest["provenance"]["input_row_number"] == 1
        assert manifest["provenance"]["runner"] == "ingest_repo_artifacts.py"

        # Resolved reference
        assert manifest["resolved_reference"]["repo_commit_sha"] == "abc123def456"

        # Artifact fetch
        assert len(manifest["artifact_fetch"]["artifacts_found"]) == 1
        assert manifest["artifact_fetch"]["artifacts_found"][0]["ecosystem"] == "PyPI"

        # JSON format: trailing newline
        raw = manifests[0].read_bytes()
        assert raw.endswith(b"\n")

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_ineligible_manifest_produced(self, mock_resolve, mock_fetch, tmp_path):
        """Ineligible candidate still produces manifest with eligible=false."""
        mock_resolve.return_value = ("main", "unknown", "api_error")
        mock_fetch.return_value = None  # all fetch attempts fail → unreachable

        from scripts.ingest_repo_artifacts import run
        import argparse
        args = argparse.Namespace(
            input=str(FIXTURES / "valid_candidates.csv"),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )
        exit_code = run(args)
        assert exit_code == 0  # ineligibility is NOT a non-zero exit

        manifests = list(tmp_path.glob("manifests/*/manifest_index.json"))
        assert len(manifests) == 1

        manifest = json.loads(manifests[0].read_text())
        assert manifest["eligibility"]["eligible"] is False
        assert manifest["eligibility"]["reason_code"] == "ERR_REPO_UNREACHABLE"

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_dry_run_no_files_written(self, mock_resolve, mock_fetch, tmp_path):
        """--dry-run processes candidates but writes no files."""
        mock_resolve.return_value = ("master", "abc123", "none")
        mock_fetch.side_effect = [
            _make_ok_response(),
            _make_ok_response(b"torch\n"),
        ]

        from scripts.ingest_repo_artifacts import run
        import argparse
        args = argparse.Namespace(
            input=str(FIXTURES / "valid_candidates.csv"),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=True,
            log_level="WARNING",
        )
        exit_code = run(args)
        assert exit_code == 0

        manifests = list(tmp_path.glob("manifests/*/manifest_index.json"))
        assert len(manifests) == 0

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_manifest_is_deterministic(self, mock_resolve, mock_fetch, tmp_path):
        """Running the same input twice produces identical JSON (except generated_at_utc)."""
        mock_resolve.return_value = ("master", "abc123def456", "none")

        from scripts.ingest_repo_artifacts import run
        import argparse

        results = []
        for i in range(2):
            mock_fetch.side_effect = [
                _make_ok_response(),
                _make_ok_response(b"torch\n"),
            ]
            out_dir = tmp_path / f"run{i}"
            args = argparse.Namespace(
                input=str(FIXTURES / "valid_candidates.csv"),
                output_root=str(out_dir),
                snapshot_timestamp=SNAPSHOT_TS,
                dry_run=False,
                log_level="WARNING",
            )
            run(args)
            manifests = list(out_dir.glob("manifests/*/manifest_index.json"))
            data = json.loads(manifests[0].read_text())
            # Remove timestamp field for comparison
            del data["generated_at_utc"]
            results.append(data)

        assert results[0] == results[1]

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_no_artifacts_manifest_ineligible(self, mock_resolve, mock_fetch, tmp_path):
        """No supported artifacts → ERR_NO_SUPPORTED_ARTIFACTS in manifest."""
        mock_resolve.return_value = ("main", "sha123", "none")
        # repo reachable, all probes → 404
        mock_fetch.side_effect = [_make_ok_response()] + [_make_404_response()] * 9

        from scripts.ingest_repo_artifacts import run
        import argparse
        args = argparse.Namespace(
            input=str(FIXTURES / "no_artifacts.csv"),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )
        exit_code = run(args)
        assert exit_code == 0

        manifests = list(tmp_path.glob("manifests/*/manifest_index.json"))
        assert len(manifests) == 1
        manifest = json.loads(manifests[0].read_text())
        assert manifest["eligibility"]["eligible"] is False
        assert manifest["eligibility"]["reason_code"] == "ERR_NO_SUPPORTED_ARTIFACTS"
