"""
model_id.py — Deterministic model_id normalization utility.

Implements the 7-step algorithm from docs/specs/artifact-schemas.md.
"""

import hashlib
import re


def sha1_hex8(raw: str) -> str:
    """Return first 8 hex chars of SHA-1 over raw encoded as UTF-8."""
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]


def normalize_model_id(hf_model_id: str) -> str:
    """
    Apply the 7-step deterministic normalization algorithm from spec.

    Returns '<slug>--<first8hex of SHA-1(hf_model_id)>'.
    Never raises; always returns a non-empty string.

    Steps:
    1. Lowercase
    2. Replace '/' with sentinel (NUL) to protect '--' separator through step 4
    3. Replace chars outside [a-z0-9._-NUL] with '-'
    4. Collapse repeated '-' to single '-'
    5. Restore sentinel back to '--'
    6. Trim leading/trailing '-'; if empty use 'model'
    7. Append '--' + first 8 hex chars of SHA-1(original hf_model_id)
    """
    _SENTINEL = "\x00"

    s = hf_model_id.lower()
    s = s.replace("/", _SENTINEL)
    s = re.sub(r"[^a-z0-9._\-\x00]", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    s = s.replace(_SENTINEL, "--")
    s = s.strip("-")
    if not s:
        s = "model"

    return f"{s}--{sha1_hex8(hf_model_id)}"
