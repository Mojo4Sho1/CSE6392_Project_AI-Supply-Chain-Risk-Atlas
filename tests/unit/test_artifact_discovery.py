"""Unit tests for artifact discovery module (T-009)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from scripts._utils.artifact_discovery import (
    ArtifactDiscoveryResult,
    FetchedArtifact,
    blob_url_to_raw_url,
    discover_artifacts,
    parse_github_repo_url,
    probe_artifacts,
)


class TestBlobUrlToRawUrl:
    def test_master_branch(self):
        blob = "https://github.com/google-research/bert/blob/master/requirements.txt"
        expected = "https://raw.githubusercontent.com/google-research/bert/master/requirements.txt"
        assert blob_url_to_raw_url(blob) == expected

    def test_main_branch(self):
        blob = "https://github.com/openai/CLIP/blob/main/requirements.txt"
        expected = "https://raw.githubusercontent.com/openai/CLIP/main/requirements.txt"
        assert blob_url_to_raw_url(blob) == expected

    def test_nested_path(self):
        blob = "https://github.com/deepseek-ai/DeepSeek-V3/blob/main/inference/requirements.txt"
        expected = "https://raw.githubusercontent.com/deepseek-ai/DeepSeek-V3/main/inference/requirements.txt"
        assert blob_url_to_raw_url(blob) == expected

    def test_non_github_raises(self):
        with pytest.raises(ValueError):
            blob_url_to_raw_url("https://gitlab.com/owner/repo/blob/main/file.txt")

    def test_non_blob_url_raises(self):
        with pytest.raises(ValueError):
            blob_url_to_raw_url("https://github.com/owner/repo/tree/main/file.txt")

    def test_pyproject_toml(self):
        blob = "https://github.com/Stability-AI/generative-models/blob/main/pyproject.toml"
        raw = blob_url_to_raw_url(blob)
        assert "raw.githubusercontent.com" in raw
        assert "pyproject.toml" in raw


class TestParseGithubRepoUrl:
    def test_basic_url(self):
        owner, repo = parse_github_repo_url("https://github.com/google-research/bert")
        assert owner == "google-research"
        assert repo == "bert"

    def test_trailing_slash(self):
        owner, repo = parse_github_repo_url("https://github.com/openai/CLIP/")
        assert owner == "openai"
        assert repo == "CLIP"

    def test_git_suffix(self):
        owner, repo = parse_github_repo_url("https://github.com/owner/repo.git")
        assert repo == "repo"

    def test_non_github_raises(self):
        with pytest.raises(ValueError):
            parse_github_repo_url("https://gitlab.com/owner/repo")

    def test_deepseek_url(self):
        owner, repo = parse_github_repo_url("https://github.com/deepseek-ai/DeepSeek-V3")
        assert owner == "deepseek-ai"
        assert repo == "DeepSeek-V3"


class TestDiscoverArtifacts:
    def _make_ok_response(self, content: bytes = b"torch\nnumpy\n") -> MagicMock:
        resp = MagicMock(spec=requests.Response)
        resp.ok = True
        resp.status_code = 200
        resp.content = content
        return resp

    def _make_not_found_response(self) -> MagicMock:
        resp = MagicMock(spec=requests.Response)
        resp.ok = False
        resp.status_code = 404
        return resp

    def _make_forbidden_response(self) -> MagicMock:
        resp = MagicMock(spec=requests.Response)
        resp.ok = False
        resp.status_code = 403
        return resp

    def _make_session(self) -> MagicMock:
        session = MagicMock(spec=requests.Session)
        session.headers = {}
        return session

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_eligible_with_hint_url(self, mock_resolve, mock_fetch):
        mock_resolve.return_value = ("master", "abc123def456", "none")
        # First call: repo reachability check → ok
        # Second call: hint artifact fetch → ok
        mock_fetch.side_effect = [
            self._make_ok_response(),           # repo reachable
            self._make_ok_response(b"torch\n"), # artifact fetch
        ]
        session = self._make_session()
        result = discover_artifacts(
            source_repo_url="https://github.com/google-research/bert",
            dependency_artifact_url="https://github.com/google-research/bert/blob/master/requirements.txt",
            dependency_artifact="requirements.txt (root)",
            session=session,
            log=MagicMock(),
        )
        assert result.reachable is True
        assert result.error_code is None
        assert len(result.artifacts_found) == 1
        assert result.artifacts_found[0].ecosystem == "PyPI"
        assert result.repo_commit_sha == "abc123def456"

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_repo_forbidden(self, mock_resolve, mock_fetch):
        mock_resolve.return_value = ("main", "unknown", "api_error")
        mock_fetch.return_value = self._make_forbidden_response()
        result = discover_artifacts(
            source_repo_url="https://github.com/private/repo",
            dependency_artifact_url=None,
            dependency_artifact=None,
            session=self._make_session(),
            log=MagicMock(),
        )
        assert result.error_code == "ERR_REPO_FORBIDDEN"
        assert result.reachable is False

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_repo_unreachable(self, mock_resolve, mock_fetch):
        mock_fetch.return_value = None  # all attempts failed
        result = discover_artifacts(
            source_repo_url="https://github.com/nonexistent/repo",
            dependency_artifact_url=None,
            dependency_artifact=None,
            session=self._make_session(),
            log=MagicMock(),
        )
        assert result.error_code == "ERR_REPO_UNREACHABLE"

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_no_supported_artifacts_probe(self, mock_resolve, mock_fetch):
        mock_resolve.return_value = ("main", "sha123", "none")
        # repo reachable, all artifact probes → 404
        mock_fetch.side_effect = [
            self._make_ok_response(),       # repo reachable
        ] + [self._make_not_found_response()] * 9  # all 9 recognized artifacts
        result = discover_artifacts(
            source_repo_url="https://github.com/no-artifacts/repo",
            dependency_artifact_url=None,
            dependency_artifact=None,
            session=self._make_session(),
            log=MagicMock(),
        )
        assert result.error_code == "ERR_NO_SUPPORTED_ARTIFACTS"

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_hint_fetch_failed_returns_error(self, mock_resolve, mock_fetch):
        mock_resolve.return_value = ("main", "sha123", "none")
        mock_fetch.side_effect = [
            self._make_ok_response(),       # repo reachable
            self._make_not_found_response(), # hint artifact → 404
        ]
        result = discover_artifacts(
            source_repo_url="https://github.com/owner/repo",
            dependency_artifact_url="https://github.com/owner/repo/blob/main/requirements.txt",
            dependency_artifact="requirements.txt",
            session=self._make_session(),
            log=MagicMock(),
        )
        assert result.error_code == "ERR_ARTIFACT_FETCH_FAILED"

    @patch("scripts._utils.artifact_discovery.fetch_with_retry")
    @patch("scripts._utils.artifact_discovery.resolve_default_branch")
    def test_parse_failed_corrupt_pyproject(self, mock_resolve, mock_fetch):
        corrupt_toml = b"[[[invalid toml"
        mock_resolve.return_value = ("main", "sha123", "none")
        mock_fetch.side_effect = [
            self._make_ok_response(),            # repo reachable
            self._make_ok_response(corrupt_toml), # hint artifact → bad content
        ]
        result = discover_artifacts(
            source_repo_url="https://github.com/owner/repo",
            dependency_artifact_url="https://github.com/owner/repo/blob/main/pyproject.toml",
            dependency_artifact="pyproject.toml",
            session=self._make_session(),
            log=MagicMock(),
        )
        assert result.error_code == "ERR_ARTIFACT_PARSE_FAILED"
        assert len(result.artifact_parse_failures) == 1

    def test_invalid_repo_url_returns_unreachable(self):
        result = discover_artifacts(
            source_repo_url="https://not-github.com/owner/repo",
            dependency_artifact_url=None,
            dependency_artifact=None,
            session=self._make_session(),
            log=MagicMock(),
        )
        assert result.error_code == "ERR_REPO_UNREACHABLE"
