"""
eligibility.py — Eligibility evaluation against the four strict criteria.

Maps ArtifactDiscoveryResult to a canonical EligibilityResult with reason codes
from docs/specs/artifact-schemas.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts._utils.artifact_discovery import ArtifactDiscoveryResult
from scripts._utils.csv_parser import ModelCandidate

ELIGIBILITY_REASON_CODES: frozenset[str] = frozenset({
    "OK_ELIGIBLE",
    "ERR_INPUT_MISSING_REQUIRED_FIELD",
    "ERR_INPUT_INVALID_TIMESTAMP",
    "ERR_REPO_UNREACHABLE",
    "ERR_REPO_FORBIDDEN",
    "ERR_REF_RESOLUTION_FAILED",
    "ERR_NO_SUPPORTED_ARTIFACTS",
    "ERR_ARTIFACT_FETCH_FAILED",
    "ERR_ARTIFACT_PARSE_FAILED",
    "ERR_MODEL_ARTIFACT_MAPPING_AMBIGUOUS",
})


@dataclass
class EligibilityResult:
    eligible: bool
    reason_code: str
    reason_detail: str

    def __post_init__(self) -> None:
        assert self.reason_code in ELIGIBILITY_REASON_CODES, (
            f"Unknown reason_code: {self.reason_code!r}"
        )


def make_eligible() -> EligibilityResult:
    return EligibilityResult(eligible=True, reason_code="OK_ELIGIBLE", reason_detail="")


def make_ineligible(reason_code: str, reason_detail: str = "") -> EligibilityResult:
    return EligibilityResult(eligible=False, reason_code=reason_code, reason_detail=reason_detail)


def evaluate_eligibility(
    candidate: ModelCandidate,
    discovery: ArtifactDiscoveryResult,
) -> EligibilityResult:
    """
    Apply the four strict eligibility criteria in order.

    Returns EligibilityResult. Never raises.

    Evaluation order (early-return on first failure):
    1. Repository forbidden (403)
    2. Repository unreachable
    3. Artifact fetch failed
    4. No supported artifacts found
    5. All artifacts failed parse
    6. Ambiguous model-artifact mapping
    7. → ELIGIBLE
    """
    if discovery.error_code == "ERR_REPO_FORBIDDEN":
        return make_ineligible(
            "ERR_REPO_FORBIDDEN",
            discovery.error_detail or "Repository returned HTTP 403",
        )

    if not discovery.reachable:
        return make_ineligible(
            "ERR_REPO_UNREACHABLE",
            discovery.error_detail or "Repository is not reachable",
        )

    # Propagate any specific error code recorded by discovery (takes priority over
    # condition-based checks to ensure the most precise reason code is reported).
    if discovery.error_code is not None:
        return make_ineligible(
            discovery.error_code,
            discovery.error_detail or "",
        )

    # Condition-based fallbacks when discovery didn't set a specific error_code
    if not discovery.artifacts_found and not discovery.artifact_parse_failures:
        return make_ineligible(
            "ERR_NO_SUPPORTED_ARTIFACTS",
            "No recognized dependency artifacts found",
        )

    if not discovery.artifacts_found and discovery.artifact_parse_failures:
        return make_ineligible(
            "ERR_ARTIFACT_PARSE_FAILED",
            "All artifacts failed parse validation",
        )

    return make_eligible()
