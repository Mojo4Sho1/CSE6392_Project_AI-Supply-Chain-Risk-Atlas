"""
artifact_discovery.py — Repository artifact acquisition with hint support.

Fetches dependency artifacts from GitHub repositories using:
1. dependency_artifact_url hint (direct fetch) when provided
2. Probing known artifact filenames at repo root as fallback

All errors are encoded in the result dataclass; this module never raises.
"""

import json
import logging
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

RECOGNIZED_ARTIFACTS: dict[str, str] = {
    "requirements.txt": "PyPI",
    "pyproject.toml": "PyPI",
    "poetry.lock": "PyPI",
    "Pipfile": "PyPI",
    "Pipfile.lock": "PyPI",
    "package.json": "npm",
    "package-lock.json": "npm",
    "yarn.lock": "npm",
    "pnpm-lock.yaml": "npm",
}

ARTIFACT_TYPES: dict[str, str] = {
    "requirements.txt": "requirements",
    "pyproject.toml": "pyproject",
    "poetry.lock": "lock",
    "Pipfile": "pipfile",
    "Pipfile.lock": "lock",
    "package.json": "package_manifest",
    "package-lock.json": "lock",
    "yarn.lock": "lock",
    "pnpm-lock.yaml": "lock",
}


@dataclass
class FetchedArtifact:
    path: str           # relative path within repo (e.g., "requirements.txt")
    raw_url: str        # full raw content URL used to fetch
    ecosystem: str
    artifact_type: str
    content: bytes | None
    fetch_status: str   # "ok", "not_found", "error", "forbidden"
    error_detail: str | None


@dataclass
class ArtifactDiscoveryResult:
    repo_url: str
    resolved_ref: str
    repo_commit_sha: str        # or "unknown"
    repo_commit_sha_reason: str # "none" when SHA known, else reason string
    resolution_strategy: str
    artifacts_found: list[FetchedArtifact] = field(default_factory=list)
    artifact_parse_failures: list[dict] = field(default_factory=list)
    reachable: bool = False
    error_code: str | None = None
    error_detail: str | None = None


def blob_url_to_raw_url(blob_url: str) -> str:
    """
    Convert a GitHub blob URL to a raw.githubusercontent.com URL.

    Input:  https://github.com/{owner}/{repo}/blob/{ref}/{path...}
    Output: https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path...}

    Raises ValueError if the URL is not a recognized GitHub blob URL.
    """
    parsed = urlparse(blob_url)
    if parsed.netloc != "github.com":
        raise ValueError(f"Not a github.com URL: {blob_url!r}")
    parts = parsed.path.lstrip("/").split("/", 4)
    if len(parts) < 5 or parts[2] != "blob":
        raise ValueError(f"Not a GitHub blob URL (expected /owner/repo/blob/ref/path): {blob_url!r}")
    owner, repo, _, ref, path_rest = parts
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path_rest}"


def parse_github_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Extract (owner, repo_name) from a GitHub repository URL.
    Handles trailing slashes and .git suffix.

    Raises ValueError if not a parseable GitHub URL.
    """
    parsed = urlparse(repo_url)
    if parsed.netloc not in ("github.com", "www.github.com"):
        raise ValueError(f"Not a github.com URL: {repo_url!r}")
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.lstrip("/").split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Cannot parse owner/repo from GitHub URL: {repo_url!r}")
    return parts[0], parts[1]


def resolve_default_branch(
    owner: str,
    repo: str,
    session: requests.Session,
    log: logging.Logger,
) -> tuple[str, str, str]:
    """
    Returns (default_branch, commit_sha, sha_reason).

    Calls GitHub API to get default branch, then resolves HEAD commit SHA.
    On any failure: returns ("HEAD", "unknown", <reason_string>).
    """
    repo_api_url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = fetch_with_retry(repo_api_url, session, log)
    if resp is None or not resp.ok:
        log.warning("Could not resolve default branch for %s/%s; using HEAD", owner, repo)
        return "HEAD", "unknown", "api_error"

    try:
        branch = resp.json().get("default_branch", "main")
    except Exception:
        branch = "main"

    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    resp2 = fetch_with_retry(commits_url, session, log)
    if resp2 is None or not resp2.ok:
        log.warning("Could not resolve commit SHA for %s/%s@%s", owner, repo, branch)
        return branch, "unknown", "api_error"

    try:
        sha = resp2.json().get("sha", "unknown")
        sha_reason = "none" if sha != "unknown" else "api_missing_sha"
    except Exception:
        sha = "unknown"
        sha_reason = "api_error"

    return branch, sha, sha_reason


def fetch_with_retry(
    url: str,
    session: requests.Session,
    log: logging.Logger,
    max_attempts: int = 3,
    backoff_seconds: tuple[float, ...] = (1.0, 2.0, 4.0),
) -> requests.Response | None:
    """
    Fetch URL with exponential backoff on transient errors (429, 5xx, ConnectionError).

    Returns the Response immediately on 403/404 (definitive, no retry).
    Returns None if all attempts exhausted.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.get(url, timeout=30)
        except requests.ConnectionError as e:
            log.warning("Attempt %d/%d: connection error fetching %s: %s", attempt, max_attempts, url, e)
            if attempt < max_attempts:
                time.sleep(backoff_seconds[attempt - 1])
            continue
        except requests.RequestException as e:
            log.warning("Attempt %d/%d: request error fetching %s: %s", attempt, max_attempts, url, e)
            if attempt < max_attempts:
                time.sleep(backoff_seconds[attempt - 1])
            continue

        # Definitive responses — do not retry
        if resp.status_code in (403, 404):
            return resp

        # Transient — retry
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            log.warning(
                "Attempt %d/%d: transient HTTP %d for %s",
                attempt, max_attempts, resp.status_code, url,
            )
            if attempt < max_attempts:
                time.sleep(backoff_seconds[attempt - 1])
            continue

        # All other codes (200, 201, 301, etc.) — return immediately
        return resp

    log.error("All %d attempts failed for %s", max_attempts, url)
    return None


def _extract_repo_relative_path(raw_url: str) -> str:
    """
    Extract the repo-relative path from a raw.githubusercontent.com URL.
    e.g. https://raw.githubusercontent.com/owner/repo/branch/path/to/file
    → path/to/file
    """
    parsed = urlparse(raw_url)
    parts = parsed.path.lstrip("/").split("/", 3)
    if len(parts) >= 4:
        return parts[3]
    return PurePosixPath(parsed.path).name


def _check_parse(artifact: FetchedArtifact) -> tuple[str, dict | None]:
    """
    Perform minimal parse-validity check on artifact content.

    Returns ("parsed", None) or ("not_parsed", failure_dict).
    Failure dict has keys: path, error_code, error_detail.
    """
    if artifact.content is None:
        return "not_parsed", {
            "path": artifact.path,
            "error_code": "ERR_ARTIFACT_PARSE_FAILED",
            "error_detail": "No content fetched",
        }

    filename = PurePosixPath(artifact.path).name

    if filename == "pyproject.toml":
        try:
            tomllib.loads(artifact.content.decode("utf-8"))
            return "parsed", None
        except Exception as e:
            return "not_parsed", {
                "path": artifact.path,
                "error_code": "ERR_ARTIFACT_PARSE_FAILED",
                "error_detail": f"TOML parse error: {e}",
            }

    if filename == "package.json":
        try:
            json.loads(artifact.content)
            return "parsed", None
        except Exception as e:
            return "not_parsed", {
                "path": artifact.path,
                "error_code": "ERR_ARTIFACT_PARSE_FAILED",
                "error_detail": f"JSON parse error: {e}",
            }

    if filename == "Pipfile":
        try:
            tomllib.loads(artifact.content.decode("utf-8"))
            return "parsed", None
        except Exception as e:
            return "not_parsed", {
                "path": artifact.path,
                "error_code": "ERR_ARTIFACT_PARSE_FAILED",
                "error_detail": f"TOML parse error: {e}",
            }

    # All other artifacts: UTF-8 decodable is sufficient
    try:
        artifact.content.decode("utf-8")
        return "parsed", None
    except UnicodeDecodeError as e:
        return "not_parsed", {
            "path": artifact.path,
            "error_code": "ERR_ARTIFACT_PARSE_FAILED",
            "error_detail": f"UTF-8 decode error: {e}",
        }


def probe_artifacts(
    owner: str,
    repo: str,
    branch: str,
    session: requests.Session,
    log: logging.Logger,
) -> list[FetchedArtifact]:
    """
    Probe all recognized artifact filenames at repo root via raw.githubusercontent.com.
    Returns list of successfully fetched artifacts (fetch_status == "ok").
    """
    found = []
    for filename, ecosystem in RECOGNIZED_ARTIFACTS.items():
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filename}"
        resp = fetch_with_retry(raw_url, session, log)
        if resp is None:
            log.debug("Probe: no response for %s", raw_url)
            continue
        if resp.status_code == 200:
            log.debug("Probe: found %s at %s", filename, raw_url)
            found.append(FetchedArtifact(
                path=filename,
                raw_url=raw_url,
                ecosystem=ecosystem,
                artifact_type=ARTIFACT_TYPES.get(filename, "unknown"),
                content=resp.content,
                fetch_status="ok",
                error_detail=None,
            ))
        elif resp.status_code == 404:
            log.debug("Probe: not found %s", filename)
        elif resp.status_code == 403:
            log.debug("Probe: forbidden %s", filename)
        else:
            log.debug("Probe: unexpected status %d for %s", resp.status_code, raw_url)
    return found


def discover_artifacts(
    source_repo_url: str,
    dependency_artifact_url: str | None,
    dependency_artifact: str | None,
    session: requests.Session,
    log: logging.Logger,
) -> ArtifactDiscoveryResult:
    """
    Main entry point for artifact discovery.

    Returns ArtifactDiscoveryResult. Never raises — errors encoded in result.
    """
    result = ArtifactDiscoveryResult(
        repo_url=source_repo_url,
        resolved_ref="unknown",
        repo_commit_sha="unknown",
        repo_commit_sha_reason="not_attempted",
        resolution_strategy="default_branch_head",
    )

    # Step 1: Validate repo URL and check reachability
    try:
        owner, repo_name = parse_github_repo_url(source_repo_url)
    except ValueError as e:
        log.error("Cannot parse GitHub repo URL: %s", e)
        result.error_code = "ERR_REPO_UNREACHABLE"
        result.error_detail = str(e)
        return result

    repo_resp = fetch_with_retry(source_repo_url, session, log)
    if repo_resp is None:
        result.error_code = "ERR_REPO_UNREACHABLE"
        result.error_detail = "All fetch attempts failed (connection error or timeout)"
        return result
    if repo_resp.status_code == 403:
        result.reachable = False
        result.error_code = "ERR_REPO_FORBIDDEN"
        result.error_detail = f"HTTP 403 for {source_repo_url}"
        return result
    if repo_resp.status_code == 404:
        result.reachable = False
        result.error_code = "ERR_REPO_UNREACHABLE"
        result.error_detail = f"HTTP 404 for {source_repo_url}"
        return result
    if not repo_resp.ok:
        result.reachable = False
        result.error_code = "ERR_REPO_UNREACHABLE"
        result.error_detail = f"HTTP {repo_resp.status_code} for {source_repo_url}"
        return result

    result.reachable = True

    # Step 2: Resolve default branch and commit SHA
    branch, sha, sha_reason = resolve_default_branch(owner, repo_name, session, log)
    result.resolved_ref = branch
    result.repo_commit_sha = sha
    result.repo_commit_sha_reason = sha_reason

    # Step 3: Fetch artifacts
    if dependency_artifact_url:
        # Strategy A: hint URL provided — fetch it directly
        try:
            raw_url = blob_url_to_raw_url(dependency_artifact_url)
        except ValueError:
            # Not a blob URL; treat as direct raw URL and attempt
            raw_url = dependency_artifact_url

        resp = fetch_with_retry(raw_url, session, log)
        if resp is None or resp.status_code != 200:
            status_code = resp.status_code if resp is not None else "no_response"
            result.error_code = "ERR_ARTIFACT_FETCH_FAILED"
            result.error_detail = (
                f"Hint artifact URL returned HTTP {status_code}: {raw_url}"
            )
            return result

        filename = PurePosixPath(raw_url).name
        ecosystem = RECOGNIZED_ARTIFACTS.get(filename)
        if ecosystem is None:
            result.error_code = "ERR_NO_SUPPORTED_ARTIFACTS"
            result.error_detail = (
                f"Hint artifact '{filename}' is not a recognized dependency artifact"
            )
            return result

        rel_path = _extract_repo_relative_path(raw_url)
        artifacts_found = [FetchedArtifact(
            path=rel_path,
            raw_url=raw_url,
            ecosystem=ecosystem,
            artifact_type=ARTIFACT_TYPES.get(filename, "unknown"),
            content=resp.content,
            fetch_status="ok",
            error_detail=None,
        )]
    else:
        # Strategy B: no hint — probe all recognized artifacts at root
        artifacts_found = probe_artifacts(owner, repo_name, branch, session, log)
        if not artifacts_found:
            result.error_code = "ERR_NO_SUPPORTED_ARTIFACTS"
            result.error_detail = "No recognized dependency artifacts found at repository root"
            return result

    # Step 4: Parse-check each artifact
    parsed_artifacts: list[FetchedArtifact] = []
    for artifact in artifacts_found:
        parse_status, failure = _check_parse(artifact)
        if parse_status == "parsed":
            parsed_artifacts.append(artifact)
        else:
            result.artifact_parse_failures.append(failure)
            log.warning("Artifact parse failed: %s", failure)

    if not parsed_artifacts:
        result.error_code = "ERR_ARTIFACT_PARSE_FAILED"
        result.error_detail = "All fetched artifacts failed parse validation"
        return result

    # Step 5: Ambiguity check (v1: multiple root artifacts of different types is OK;
    # ambiguous = same filename at multiple paths with conflicting ecosystems)
    seen: dict[tuple[str, str], str] = {}
    ambiguous = False
    for a in parsed_artifacts:
        key = (PurePosixPath(a.path).name, a.ecosystem)
        if key in seen and seen[key] != a.path:
            ambiguous = True
            break
        seen[key] = a.path

    if ambiguous:
        result.error_code = "ERR_MODEL_ARTIFACT_MAPPING_AMBIGUOUS"
        result.error_detail = "Multiple conflicting paths for the same artifact filename/ecosystem"
        return result

    result.artifacts_found = parsed_artifacts
    return result
