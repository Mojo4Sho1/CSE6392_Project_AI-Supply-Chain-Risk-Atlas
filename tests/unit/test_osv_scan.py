"""Unit tests for M2 OSV normalization helpers."""

from pathlib import Path

from scripts._utils.osv_scan import (
    normalize_osv_results,
    parse_declared_dependencies,
    parse_scanner_version,
)


class TestParseScannerVersion:
    def test_extracts_version(self):
        raw = "osv-scanner version: 2.3.5\nosv-scalibr version: 0.4.5\n"
        assert parse_scanner_version(raw) == "2.3.5"


class TestDeclaredDependencies:
    def test_requirements_distinguishes_pinned_and_unpinned(self):
        deps = parse_declared_dependencies(
            artifact_path="requirements.txt",
            artifact_type="requirements",
            ecosystem="PyPI",
            content=b"Flask==1.0\nrequests>=2\n# comment\n",
        )
        assert len(deps) == 2
        assert deps[0].name == "Flask"
        assert deps[0].exact_pin is True
        assert deps[1].name == "requests"
        assert deps[1].exact_pin is False

    def test_pyproject_reads_project_and_poetry_dependencies(self):
        content = b"""
[project]
dependencies = ["fastapi==0.110.0"]

[tool.poetry.dependencies]
python = "^3.11"
uvicorn = "^0.29.0"
pendulum = "3.0.0"
"""
        deps = parse_declared_dependencies(
            artifact_path="pyproject.toml",
            artifact_type="pyproject",
            ecosystem="PyPI",
            content=content,
        )
        exact_by_name = {dep.name: dep.exact_pin for dep in deps}
        assert exact_by_name["fastapi"] is True
        assert exact_by_name["uvicorn"] is False
        assert exact_by_name["pendulum"] is True

    def test_package_json_detects_exact_versions(self):
        deps = parse_declared_dependencies(
            artifact_path="package.json",
            artifact_type="package_manifest",
            ecosystem="npm",
            content=b'{"dependencies":{"react":"18.2.0","next":"^14.1.0"}}',
        )
        exact_by_name = {dep.name: dep.exact_pin for dep in deps}
        assert exact_by_name["react"] is True
        assert exact_by_name["next"] is False


class TestNormalizeOsvResults:
    def test_normalizes_vulnerable_and_unpinned_packages(self, tmp_path):
        workspace = tmp_path / "workspace"
        (workspace / "requirements.txt").parent.mkdir(parents=True, exist_ok=True)
        (workspace / "requirements.txt").write_text("placeholder\n", encoding="utf-8")

        manifest = {
            "artifact_fetch": {
                "artifacts_found": [
                    {
                        "artifact_type": "requirements",
                        "ecosystem": "PyPI",
                        "path": "requirements.txt",
                    }
                ]
            },
            "hf_model_id": "example/model",
            "model_id": "example--model--12345678",
            "resolved_reference": {
                "repo_commit_sha": "abc123",
                "repo_commit_sha_reason": "none",
            },
            "source_repo_url": "https://github.com/example/repo",
        }
        raw_output = {
            "results": [
                {
                    "source": {
                        "path": str(workspace / "requirements.txt"),
                        "type": "lockfile",
                    },
                    "packages": [
                        {
                            "package": {
                                "ecosystem": "PyPI",
                                "name": "flask",
                                "version": "1.0",
                            },
                            "vulnerabilities": [
                                {
                                    "id": "GHSA-aaaa-bbbb-cccc",
                                    "database_specific": {"severity": "HIGH"},
                                    "affected": [
                                        {
                                            "ranges": [
                                                {
                                                    "events": [
                                                        {"introduced": "0"},
                                                        {"fixed": "1.0.1"},
                                                    ]
                                                }
                                            ]
                                        }
                                    ],
                                },
                                {
                                    "id": "CVE-2024-9999",
                                    "aliases": ["GHSA-aaaa-bbbb-cccc"],
                                },
                            ],
                            "groups": [
                                {
                                    "ids": [
                                        "CVE-2024-9999",
                                        "GHSA-aaaa-bbbb-cccc",
                                    ]
                                }
                            ],
                        },
                        {
                            "package": {
                                "ecosystem": "PyPI",
                                "name": "requests",
                                "version": "2",
                            },
                            "vulnerabilities": [
                                {
                                    "id": "GHSA-unpinned-demo",
                                    "database_specific": {"severity": "LOW"},
                                }
                            ],
                        },
                        {
                            "package": {
                                "ecosystem": "PyPI",
                                "name": "urllib3",
                                "version": "2.2.1",
                            }
                        },
                    ],
                }
            ]
        }
        declared_dependencies = parse_declared_dependencies(
            artifact_path="requirements.txt",
            artifact_type="requirements",
            ecosystem="PyPI",
            content=b"Flask==1.0\nrequests>=2\n",
        )

        normalized = normalize_osv_results(
            manifest=manifest,
            raw_output=raw_output,
            scanner_version="2.3.5",
            declared_dependencies=declared_dependencies,
            workspace_root=workspace,
        )

        assert normalized["schema_version"] == "1.0"
        assert normalized["scanner"]["name"] == "osv-scanner"
        assert normalized["scanner"]["version"] == "2.3.5"

        packages = {pkg["name"]: pkg for pkg in normalized["packages"]}

        flask = packages["flask"]
        assert flask["dependency_scope"] == "direct"
        assert flask["manifest_source"] == "requirements.txt"
        assert flask["vuln_status"] == "vulnerable"
        assert flask["vuln_ids"] == ["CVE-2024-9999"]
        assert flask["num_vulns"] == 1
        assert flask["max_severity_bucket"] == "HIGH"
        assert flask["fix_available"] is True

        requests = packages["requests"]
        assert requests["dependency_scope"] == "direct"
        assert requests["vuln_status"] == "unknown"
        assert requests["max_severity_bucket"] == "LOW"

        urllib3 = packages["urllib3"]
        assert urllib3["dependency_scope"] == "transitive"
        assert urllib3["vuln_status"] == "not_vulnerable"
        assert urllib3["manifest_source"] == "requirements.txt"

    def test_unknown_source_falls_back_to_unknown_scope(self, tmp_path):
        manifest = {
            "artifact_fetch": {
                "artifacts_found": [
                    {
                        "artifact_type": "requirements",
                        "ecosystem": "PyPI",
                        "path": "requirements.txt",
                    }
                ]
            },
            "hf_model_id": "example/model",
            "model_id": "example--model--12345678",
            "resolved_reference": {
                "repo_commit_sha": "unknown",
                "repo_commit_sha_reason": "api_error",
            },
            "source_repo_url": "https://github.com/example/repo",
        }
        raw_output = {
            "results": [
                {
                    "source": {"path": "/some/other/path/lockfile.txt", "type": "lockfile"},
                    "packages": [
                        {
                            "package": {
                                "ecosystem": "PyPI",
                                "name": "demo",
                                "version": None,
                            }
                        }
                    ],
                }
            ]
        }

        normalized = normalize_osv_results(
            manifest=manifest,
            raw_output=raw_output,
            scanner_version="2.3.5",
            declared_dependencies=[],
            workspace_root=tmp_path / "workspace",
        )

        demo = normalized["packages"][0]
        assert demo["dependency_scope"] == "unknown"
        assert demo["manifest_source"] == "unknown"
        assert demo["vuln_status"] == "unknown"
