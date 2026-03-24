"""Unit tests for model_id normalization (T-007)."""

import hashlib

import pytest

from scripts._utils.model_id import normalize_model_id, sha1_hex8


class TestSha1Hex8:
    def test_returns_8_chars(self):
        result = sha1_hex8("google-bert/bert-base-uncased")
        assert len(result) == 8

    def test_hex_characters_only(self):
        result = sha1_hex8("anything")
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self):
        assert sha1_hex8("foo") == sha1_hex8("foo")

    def test_matches_hashlib(self):
        raw = "google-bert/bert-base-uncased"
        expected = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
        assert sha1_hex8(raw) == expected

    def test_uses_original_not_normalized(self):
        # SHA-1 must be computed over the ORIGINAL string, not lowercased
        upper = "Google-BERT/Bert-Base"
        lower = "google-bert/bert-base"
        assert sha1_hex8(upper) != sha1_hex8(lower)


class TestNormalizeModelId:
    def _slug(self, hf_model_id: str) -> str:
        """Return slug portion (before trailing --<hash8>)."""
        result = normalize_model_id(hf_model_id)
        return result.rsplit("--", 1)[0]

    def _hash_part(self, hf_model_id: str) -> str:
        """Return hash portion (after last --)."""
        result = normalize_model_id(hf_model_id)
        return result.rsplit("--", 1)[1]

    def test_basic_slash_becomes_double_dash(self):
        assert self._slug("google-bert/bert-base-uncased") == "google-bert--bert-base-uncased"

    def test_lowercase(self):
        assert self._slug("deepseek-ai/DeepSeek-V3") == "deepseek-ai--deepseek-v3"

    def test_multiple_slashes(self):
        assert self._slug("openai-community/gpt2") == "openai-community--gpt2"

    def test_dots_preserved(self):
        slug = self._slug("stabilityai/stable-diffusion-xl-base-1.0")
        assert slug == "stabilityai--stable-diffusion-xl-base-1.0"

    def test_empty_string_becomes_model(self):
        assert self._slug("") == "model"

    def test_only_slashes_becomes_model(self):
        assert self._slug("///") == "model"

    def test_illegal_chars_replaced_with_dash(self):
        slug = self._slug("test/model@v1.0")
        assert "@" not in slug

    def test_repeated_dashes_collapsed(self):
        # Two hyphens from two adjacent illegal chars should collapse to one
        slug = self._slug("test/mo--del")
        assert "---" not in slug

    def test_separator_not_collapsed(self):
        # The '--' namespace separator from '/' must NOT be collapsed to '-'
        slug = self._slug("owner/repo")
        assert slug == "owner--repo"

    def test_hash_is_sha1_of_original(self):
        original = "google-bert/bert-base-uncased"
        expected_hash = hashlib.sha1(original.encode("utf-8")).hexdigest()[:8]
        assert self._hash_part(original) == expected_hash

    def test_hash_uses_original_case(self):
        mixed = "deepseek-ai/DeepSeek-V3"
        expected_hash = hashlib.sha1(mixed.encode("utf-8")).hexdigest()[:8]
        assert self._hash_part(mixed) == expected_hash

    def test_output_format(self):
        result = normalize_model_id("google-bert/bert-base-uncased")
        parts = result.split("--")
        assert len(parts) >= 2
        assert len(parts[-1]) == 8  # hash is 8 hex chars

    def test_deterministic(self):
        hf_id = "facebook/dinov2-base"
        assert normalize_model_id(hf_id) == normalize_model_id(hf_id)

    def test_all_csv_models_produce_valid_output(self):
        """Smoke test: all 13 CSV model IDs produce non-empty, unique outputs."""
        model_ids = [
            "google-bert/bert-base-uncased",
            "openai-community/gpt2",
            "openai/clip-vit-base-patch32",
            "google/vit-base-patch16-224",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "facebook/dinov2-base",
            "deepseek-ai/DeepSeek-V3",
            "facebook/detr-resnet-50",
            "deepseek-ai/deepseek-coder-6.7b-instruct",
            "facebook/musicgen-small",
            "facebook/deit-base-patch16-224",
            "deepseek-ai/Janus-Pro-7B",
            "suno/bark-small",
        ]
        results = [normalize_model_id(m) for m in model_ids]
        assert len(set(results)) == len(results), "Collision detected — model_ids not unique"
        for r in results:
            assert r, "Empty model_id"
            assert not r.startswith("-"), f"Leading dash: {r}"
            assert not r.endswith("-"), f"Trailing dash: {r}"

    def test_leading_trailing_dashes_stripped(self):
        # A model_id that starts/ends with illegal chars should have them stripped
        slug = self._slug("-test-/repo-")
        assert not slug.startswith("-")
        assert not slug.endswith("-")

    @pytest.mark.parametrize("hf_id,expected_slug", [
        ("google-bert/bert-base-uncased", "google-bert--bert-base-uncased"),
        ("openai-community/gpt2", "openai-community--gpt2"),
        ("deepseek-ai/DeepSeek-V3", "deepseek-ai--deepseek-v3"),
        ("facebook/dinov2-base", "facebook--dinov2-base"),
        ("suno/bark-small", "suno--bark-small"),
    ])
    def test_parametrized_slug(self, hf_id, expected_slug):
        assert self._slug(hf_id) == expected_slug
