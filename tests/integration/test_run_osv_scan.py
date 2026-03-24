"""Integration tests for run_osv_scan.py."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPT = str(REPO_ROOT / "scripts" / "run_osv_scan.py")
SNAPSHOT_TS = "2026-03-24T00:00:00Z"


def _write_manifest(
    manifest_root: Path,
    *,
    hf_model_id: str = "google-bert/bert-base-uncased",
    model_id: str = "google-bert--bert-base-uncased--0342c67c",
    eligible: bool = True,
) -> Path:
    manifest_dir = manifest_root / model_id
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "manifest_index.json"
    manifest = {
        "artifact_fetch": {
            "artifacts_found": [
                {
                    "artifact_type": "requirements",
                    "ecosystem": "PyPI",
                    "parse_status": "parsed",
                    "path": "requirements.txt",
                }
            ]
        },
        "eligibility": {
            "eligible": eligible,
            "reason_code": "OK_ELIGIBLE" if eligible else "ERR_NO_SUPPORTED_ARTIFACTS",
            "reason_detail": "",
        },
        "hf_model_id": hf_model_id,
        "model_id": model_id,
        "provenance": {
            "input_file": "data/models.csv",
            "input_row_number": 1,
            "runner": "ingest_repo_artifacts.py",
            "runner_version": "1.0.0",
        },
        "resolved_reference": {
            "repo_commit_sha": "abc123",
            "repo_commit_sha_reason": "none",
            "requested_ref": "default",
            "resolution_strategy": "default_branch_head",
            "resolved_ref": "main",
        },
        "schema_version": "1.0",
        "source_repo_url": "https://github.com/google-research/bert",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


class TestRunOsvScanCli:
    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, SCRIPT, "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
        assert "--input" in result.stdout
        assert "--output-root" in result.stdout
        assert "--snapshot-timestamp" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--log-level" in result.stdout


class TestRunOsvScanIntegration:
    def test_pyproject_artifact_materializes_synthetic_requirements(self, tmp_path):
        from scripts.run_osv_scan import FetchedArtifactFile, _materialize_scannable_artifact
        from scripts._utils.osv_scan import parse_declared_dependencies

        workspace = tmp_path / "workspace"
        artifact = FetchedArtifactFile(
            path="pyproject.toml",
            ecosystem="PyPI",
            artifact_type="pyproject",
            content=(
                b"[project]\n"
                b"dependencies = [\"fastapi==0.110.0\", \"uvicorn>=0.29.0\"]\n"
            ),
        )
        dependencies = parse_declared_dependencies(
            artifact_path=artifact.path,
            artifact_type=artifact.artifact_type,
            ecosystem=artifact.ecosystem,
            content=artifact.content,
        )

        _materialize_scannable_artifact(
            workspace_dir=workspace,
            artifact_file=artifact,
            declared_dependencies=dependencies,
        )

        synthetic = workspace / "_synthetic_requirements" / "requirements.txt"
        assert synthetic.exists()
        assert synthetic.read_text(encoding="utf-8") == "fastapi==0.110.0\nuvicorn\n"

    @patch("scripts.run_osv_scan.run_scanner")
    @patch("scripts.run_osv_scan.fetch_manifest_artifacts")
    @patch("scripts.run_osv_scan.get_scanner_version")
    def test_eligible_manifest_produces_raw_and_normalized(
        self,
        mock_version,
        mock_fetch_artifacts,
        mock_run_scanner,
        tmp_path,
    ):
        manifests_root = tmp_path / "manifests"
        _write_manifest(manifests_root)

        mock_version.return_value = "2.3.5"
        from scripts.run_osv_scan import FetchedArtifactFile, run

        mock_fetch_artifacts.return_value = [
            FetchedArtifactFile(
                path="requirements.txt",
                ecosystem="PyPI",
                artifact_type="requirements",
                content=b"flask==1.0\nrequests>=2\n",
            )
        ]
        mock_run_scanner.return_value = (
            json.dumps(
                {
                    "results": [
                        {
                            "source": {
                                "path": str(tmp_path / "workspace" / "requirements.txt"),
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
                                            "id": "GHSA-demo-1",
                                            "database_specific": {"severity": "HIGH"},
                                        }
                                    ],
                                },
                                {
                                    "package": {
                                        "ecosystem": "PyPI",
                                        "name": "requests",
                                        "version": "2",
                                    }
                                },
                            ],
                        }
                    ]
                }
            ),
            {
                "results": [
                    {
                        "source": {
                            "path": str(tmp_path / "workspace" / "requirements.txt"),
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
                                        "id": "GHSA-demo-1",
                                        "database_specific": {"severity": "HIGH"},
                                    }
                                ],
                            },
                            {
                                "package": {
                                    "ecosystem": "PyPI",
                                    "name": "requests",
                                    "version": "2",
                                }
                            },
                        ],
                    }
                ]
            },
        )

        args = argparse.Namespace(
            input=str(manifests_root),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 0

        raw_path = tmp_path / "osv" / "google-bert--bert-base-uncased--0342c67c" / "raw.json"
        normalized_path = (
            tmp_path / "osv" / "google-bert--bert-base-uncased--0342c67c" / "normalized.json"
        )
        assert raw_path.exists()
        assert normalized_path.exists()

        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        assert normalized["schema_version"] == "1.0"
        assert normalized["scanner"]["name"] == "osv-scanner"
        assert normalized["scanner"]["version"] == "2.3.5"

        packages = {pkg["name"]: pkg for pkg in normalized["packages"]}
        assert packages["flask"]["vuln_status"] == "vulnerable"
        assert packages["requests"]["vuln_status"] == "unknown"

    @patch("scripts.run_osv_scan.fetch_manifest_artifacts")
    @patch("scripts.run_osv_scan.get_scanner_version")
    def test_pyproject_with_no_dependencies_emits_empty_outputs(
        self,
        mock_version,
        mock_fetch_artifacts,
        tmp_path,
    ):
        manifests_root = tmp_path / "manifests"
        manifest_dir = manifests_root / "stabilityai--stable-diffusion-xl-base-1.0--5eb3438c"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        (manifest_dir / "manifest_index.json").write_text(
            json.dumps(
                {
                    "artifact_fetch": {
                        "artifacts_found": [
                            {
                                "artifact_type": "pyproject",
                                "ecosystem": "PyPI",
                                "parse_status": "parsed",
                                "path": "pyproject.toml",
                            }
                        ]
                    },
                    "eligibility": {
                        "eligible": True,
                        "reason_code": "OK_ELIGIBLE",
                        "reason_detail": "",
                    },
                    "hf_model_id": "stabilityai/stable-diffusion-xl-base-1.0",
                    "model_id": "stabilityai--stable-diffusion-xl-base-1.0--5eb3438c",
                    "provenance": {
                        "input_file": "data/models.csv",
                        "input_row_number": 1,
                        "runner": "ingest_repo_artifacts.py",
                        "runner_version": "1.0.0",
                    },
                    "resolved_reference": {
                        "repo_commit_sha": "abc123",
                        "repo_commit_sha_reason": "none",
                        "requested_ref": "default",
                        "resolution_strategy": "default_branch_head",
                        "resolved_ref": "main",
                    },
                    "schema_version": "1.0",
                    "source_repo_url": "https://github.com/Stability-AI/generative-models",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        mock_version.return_value = "2.3.5"
        from scripts.run_osv_scan import FetchedArtifactFile, run

        mock_fetch_artifacts.return_value = [
            FetchedArtifactFile(
                path="pyproject.toml",
                ecosystem="PyPI",
                artifact_type="pyproject",
                content=b"[project]\nname = 'demo'\nversion = '0.1.0'\n",
            )
        ]

        args = argparse.Namespace(
            input=str(manifests_root),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 0

        normalized_path = (
            tmp_path / "osv" / "stabilityai--stable-diffusion-xl-base-1.0--5eb3438c" / "normalized.json"
        )
        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        assert normalized["packages"] == []

    @patch("scripts.run_osv_scan.get_scanner_version")
    def test_ineligible_manifest_is_skipped(self, mock_version, tmp_path):
        manifests_root = tmp_path / "manifests"
        _write_manifest(
            manifests_root,
            hf_model_id="demo/skip",
            model_id="demo--skip--12345678",
            eligible=False,
        )
        mock_version.return_value = "2.3.5"

        from scripts.run_osv_scan import run

        args = argparse.Namespace(
            input=str(manifests_root),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 0
        assert not (tmp_path / "osv").exists()

    @patch("scripts.run_osv_scan.get_scanner_version")
    def test_dry_run_writes_no_files(self, mock_version, tmp_path):
        manifests_root = tmp_path / "manifests"
        _write_manifest(manifests_root)
        mock_version.return_value = "2.3.5"

        from scripts.run_osv_scan import FetchedArtifactFile, run

        with patch("scripts.run_osv_scan.fetch_manifest_artifacts") as mock_fetch_artifacts:
            with patch("scripts.run_osv_scan.run_scanner") as mock_run_scanner:
                mock_fetch_artifacts.return_value = [
                    FetchedArtifactFile(
                        path="requirements.txt",
                        ecosystem="PyPI",
                        artifact_type="requirements",
                        content=b"flask==1.0\n",
                    )
                ]
                mock_run_scanner.return_value = (
                    '{"results":[{"source":{"path":"requirements.txt","type":"lockfile"},"packages":[]}]}',
                    {"results": [{"source": {"path": "requirements.txt", "type": "lockfile"}, "packages": []}]},
                )

                args = argparse.Namespace(
                    input=str(manifests_root),
                    output_root=str(tmp_path),
                    snapshot_timestamp=SNAPSHOT_TS,
                    dry_run=True,
                    log_level="WARNING",
                )

                assert run(args) == 0
                assert not (tmp_path / "osv").exists()

    def test_bad_manifest_returns_2(self, tmp_path):
        manifests_root = tmp_path / "manifests" / "bad"
        manifests_root.mkdir(parents=True, exist_ok=True)
        (manifests_root / "manifest_index.json").write_text('{"bad": true}\n', encoding="utf-8")

        from scripts.run_osv_scan import run

        args = argparse.Namespace(
            input=str(tmp_path / "manifests"),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 2

    @patch("scripts.run_osv_scan.get_scanner_version", side_effect=FileNotFoundError("missing"))
    def test_missing_scanner_returns_3(self, _mock_version, tmp_path):
        manifests_root = tmp_path / "manifests"
        _write_manifest(manifests_root)

        from scripts.run_osv_scan import run

        args = argparse.Namespace(
            input=str(manifests_root),
            output_root=str(tmp_path),
            snapshot_timestamp=SNAPSHOT_TS,
            dry_run=False,
            log_level="WARNING",
        )

        assert run(args) == 3
