"""Unit tests for eligibility evaluation (T-010)."""

import pytest

from scripts._utils.artifact_discovery import ArtifactDiscoveryResult, FetchedArtifact
from scripts._utils.csv_parser import ModelCandidate
from scripts._utils.eligibility import (
    ELIGIBILITY_REASON_CODES,
    EligibilityResult,
    evaluate_eligibility,
    make_eligible,
    make_ineligible,
)


def _make_candidate() -> ModelCandidate:
    return ModelCandidate(
        hf_model_id="test/model",
        source_repo_url="https://github.com/test/model",
        snapshot_timestamp_utc="2026-03-20T00:00:00Z",
        hf_downloads_at_snapshot=1000,
        hf_likes_at_snapshot=10,
        dependency_artifact=None,
        dependency_artifact_url=None,
        selection_rationale=None,
        curation_notes=None,
        input_row_number=1,
    )


def _make_artifact() -> FetchedArtifact:
    return FetchedArtifact(
        path="requirements.txt",
        raw_url="https://raw.githubusercontent.com/test/model/main/requirements.txt",
        ecosystem="PyPI",
        artifact_type="requirements",
        content=b"torch\n",
        fetch_status="ok",
        error_detail=None,
    )


def _make_discovery(**kwargs) -> ArtifactDiscoveryResult:
    defaults = dict(
        repo_url="https://github.com/test/model",
        resolved_ref="main",
        repo_commit_sha="abc123",
        repo_commit_sha_reason="none",
        resolution_strategy="default_branch_head",
        artifacts_found=[_make_artifact()],
        artifact_parse_failures=[],
        reachable=True,
        error_code=None,
        error_detail=None,
    )
    defaults.update(kwargs)
    return ArtifactDiscoveryResult(**defaults)


class TestMakeEligible:
    def test_returns_eligible(self):
        result = make_eligible()
        assert result.eligible is True
        assert result.reason_code == "OK_ELIGIBLE"

    def test_reason_code_in_canonical_set(self):
        assert make_eligible().reason_code in ELIGIBILITY_REASON_CODES


class TestMakeIneligible:
    def test_returns_ineligible(self):
        result = make_ineligible("ERR_REPO_UNREACHABLE", "test")
        assert result.eligible is False
        assert result.reason_code == "ERR_REPO_UNREACHABLE"

    def test_unknown_reason_code_raises(self):
        with pytest.raises(AssertionError):
            make_ineligible("MADE_UP_CODE")


class TestEvaluateEligibility:
    def test_eligible_happy_path(self):
        candidate = _make_candidate()
        discovery = _make_discovery()
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is True
        assert result.reason_code == "OK_ELIGIBLE"

    def test_forbidden_repo(self):
        candidate = _make_candidate()
        discovery = _make_discovery(
            reachable=False,
            error_code="ERR_REPO_FORBIDDEN",
            error_detail="HTTP 403",
            artifacts_found=[],
        )
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is False
        assert result.reason_code == "ERR_REPO_FORBIDDEN"

    def test_unreachable_repo(self):
        candidate = _make_candidate()
        discovery = _make_discovery(
            reachable=False,
            error_code="ERR_REPO_UNREACHABLE",
            error_detail="Connection failed",
            artifacts_found=[],
        )
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is False
        assert result.reason_code == "ERR_REPO_UNREACHABLE"

    def test_artifact_fetch_failed(self):
        candidate = _make_candidate()
        discovery = _make_discovery(
            reachable=True,
            error_code="ERR_ARTIFACT_FETCH_FAILED",
            error_detail="HTTP 404",
            artifacts_found=[],
        )
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is False
        assert result.reason_code == "ERR_ARTIFACT_FETCH_FAILED"

    def test_no_supported_artifacts(self):
        candidate = _make_candidate()
        discovery = _make_discovery(
            reachable=True,
            error_code="ERR_NO_SUPPORTED_ARTIFACTS",
            artifacts_found=[],
        )
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is False
        assert result.reason_code == "ERR_NO_SUPPORTED_ARTIFACTS"

    def test_artifact_parse_failed(self):
        candidate = _make_candidate()
        discovery = _make_discovery(
            reachable=True,
            error_code="ERR_ARTIFACT_PARSE_FAILED",
            artifacts_found=[],
            artifact_parse_failures=[{"path": "pyproject.toml", "error_code": "ERR_ARTIFACT_PARSE_FAILED", "error_detail": "bad TOML"}],
        )
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is False
        assert result.reason_code == "ERR_ARTIFACT_PARSE_FAILED"

    def test_ambiguous_mapping(self):
        candidate = _make_candidate()
        discovery = _make_discovery(
            reachable=True,
            error_code="ERR_MODEL_ARTIFACT_MAPPING_AMBIGUOUS",
            artifacts_found=[],
        )
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is False
        assert result.reason_code == "ERR_MODEL_ARTIFACT_MAPPING_AMBIGUOUS"

    def test_reason_code_always_canonical(self):
        """All evaluation outcomes use canonical reason codes."""
        candidate = _make_candidate()
        for code in ELIGIBILITY_REASON_CODES:
            if code == "OK_ELIGIBLE":
                continue
            if code in ("ERR_INPUT_MISSING_REQUIRED_FIELD", "ERR_INPUT_INVALID_TIMESTAMP",
                        "ERR_REF_RESOLUTION_FAILED"):
                # These are CSV-level codes, not produced by evaluate_eligibility directly
                continue
            discovery = _make_discovery(
                reachable=(code not in ("ERR_REPO_UNREACHABLE", "ERR_REPO_FORBIDDEN")),
                error_code=code,
                artifacts_found=[],
            )
            result = evaluate_eligibility(candidate, discovery)
            assert result.reason_code in ELIGIBILITY_REASON_CODES

    def test_eligible_with_multiple_artifacts(self):
        """Multiple artifacts found → still eligible."""
        candidate = _make_candidate()
        artifacts = [
            _make_artifact(),
            FetchedArtifact(
                path="pyproject.toml",
                raw_url="https://raw.githubusercontent.com/test/model/main/pyproject.toml",
                ecosystem="PyPI",
                artifact_type="pyproject",
                content=b'[build-system]\nrequires = ["setuptools"]\n',
                fetch_status="ok",
                error_detail=None,
            ),
        ]
        discovery = _make_discovery(artifacts_found=artifacts)
        result = evaluate_eligibility(candidate, discovery)
        assert result.eligible is True
